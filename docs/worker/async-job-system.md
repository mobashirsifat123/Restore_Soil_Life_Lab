# Async Job System Design

## Purpose

This document defines the worker architecture for long-running scientific jobs that must execute outside the web app and outside synchronous API request flow.

It covers:

1. job types and queue design
2. run lifecycle transitions
3. failure and retry strategy
4. idempotency rules
5. timeout and cancellation
6. status persistence
7. API, worker, and simulation engine interaction
8. artifact writing and references
9. logging, tracing, and monitoring
10. test strategy

## Architecture Overview

Use this execution shape:

```text
FastAPI API -> PostgreSQL run/report row -> Redis stream message -> Worker supervisor
  -> isolated subprocess execution -> object storage artifacts -> PostgreSQL status update
```

Principles:

- the database row is the source of truth for status
- Redis is the delivery mechanism, not the source of truth
- delivery is at-least-once, so processing must be idempotent
- scientific execution should run in a fresh subprocess, not inside the long-lived worker process
- artifact metadata is not complete until both object storage and DB rows succeed

## Job Types And Queue Design

### Job Types

Start with three explicit job types:

- `simulation.run.execute`
- `decomposition.run.execute`
- `report.generate`

These are modeled in:

- [payloads.py](/Users/mobashirsifat/Desktop/bio_lab/services/worker/app/jobs/payloads.py)

### Queue Design

Use Redis Streams, not simple lists.

Recommended streams:

- `jobs:simulation`
- `jobs:decomposition`
- `jobs:report`

Use one consumer group per worker deployment:

- consumer group name: worker service name, for example `bio-worker`
- consumer name: worker instance ID, for example `worker-prod-3`

Why Redis Streams:

- pending message tracking
- replay and dead-letter support
- reclaiming stale messages with `XAUTOCLAIM`
- better operational introspection than simple list pop

### Dispatch Reliability

Recommended production pattern:

- create the run or report row in PostgreSQL
- write an outbox record in the same DB transaction
- a lightweight dispatcher publishes the outbox record to Redis Streams
- mark the outbox record delivered only after Redis publish succeeds

Why:

Without an outbox, there is a failure window between DB commit and Redis publish where a run can remain `queued` in PostgreSQL but never actually reach a worker.

If you defer the outbox for MVP, add a recovery sweeper that periodically finds `queued` rows with no active queue job and republishes them safely.

### Payload Envelope

Every message should contain:

- `jobId`
- `jobType`
- `schemaVersion`
- `queueName`
- `priority`
- `enqueuedAt`
- `availableAt`
- `dedupeKey`
- typed `payload`

Business payload should contain:

- organization and project IDs
- run or report ID
- initiated user ID when relevant
- trace ID and request ID
- timeout
- attempt count
- max attempts
- input hash or render inputs

Important:

The queue payload is advisory. The persisted run or report record remains authoritative.

## Recommended Folder Structure For `services/worker`

```text
services/worker/
├── pyproject.toml
├── .env.example
└── app/
    ├── main.py
    ├── core/
    │   ├── config.py
    │   └── logging.py
    ├── jobs/
    │   ├── payloads.py
    │   ├── registry.py
    │   └── handlers/
    │       ├── simulation_run.py
    │       ├── decomposition_run.py
    │       └── report_generation.py
    ├── queue/
    │   └── redis_streams.py
    ├── runners/
    │   └── worker_runner.py
    ├── services/
    │   ├── artifact_service.py
    │   ├── execution_service.py
    │   └── status_store.py
    └── telemetry/
        └── metrics.py
```

Current scaffold files:

- [main.py](/Users/mobashirsifat/Desktop/bio_lab/services/worker/app/main.py)
- [payloads.py](/Users/mobashirsifat/Desktop/bio_lab/services/worker/app/jobs/payloads.py)
- [worker_runner.py](/Users/mobashirsifat/Desktop/bio_lab/services/worker/app/runners/worker_runner.py)
- [redis_streams.py](/Users/mobashirsifat/Desktop/bio_lab/services/worker/app/queue/redis_streams.py)

## API, Worker, And Simulation Engine Interaction

### API Responsibilities

When a user submits a run:

1. validate auth and org access
2. load the scenario and referenced scientific inputs
3. build a canonical `input_snapshot_json`
4. compute `input_hash`
5. create the `simulation_runs` row with status `queued`
6. enqueue a Redis stream message referencing the run

For reports:

1. validate run and project access
2. create the `reports` row with status `queued`
3. enqueue a report generation message

### Worker Responsibilities

1. reserve a message from Redis Streams
2. lock or lease the backing row in PostgreSQL
3. confirm the row is eligible for execution
4. mark the row `running`
5. load authoritative input snapshot from PostgreSQL
6. execute the scientific engine or renderer in a subprocess
7. write artifacts
8. finalize the row as `succeeded`, `failed`, or `canceled`
9. ack the Redis message

### Simulation Engine Responsibilities

The simulation engine:

- accepts a pure input snapshot
- returns structured result data
- knows nothing about Redis, SQLAlchemy, FastAPI, or HTTP
- should be deterministic for the same snapshot and engine version unless randomness is explicitly modeled

## Run Lifecycle Transitions

Persisted statuses:

- `draft`
- `queued`
- `running`
- `succeeded`
- `failed`
- `cancel_requested`
- `canceled`

Recommended execution semantics:

```text
API submit:
draft -> queued

Worker start:
queued -> running

Normal completion:
running -> succeeded

Permanent failure:
queued|running -> failed

User cancellation:
queued|running -> cancel_requested -> canceled
```

Rules:

- only the API creates rows
- only workers transition to execution or terminal states
- workers must refuse to process terminal rows
- every state transition must update the corresponding timestamp

## Status Update Persistence Model

The business row is authoritative:

- `simulation_runs` for simulation and decomposition jobs
- `reports` for report generation jobs

Recommended persisted execution fields:

- `status`
- `attempt_count`
- `worker_id`
- `queue_name`
- `queue_job_id`
- `last_heartbeat_at`
- `lease_expires_at`
- `next_retry_at`
- `failure_code`
- `failure_message`
- `failure_details_json`
- `queued_at`
- `started_at`
- `completed_at`
- `canceled_at`
- `updated_at`

MVP note:

If you do not want a separate `job_attempts` table yet, keep detailed attempt history in structured logs and store only the latest attempt metadata on the row.

Post-MVP:

Add `job_attempts` or `run_events` if you need fine-grained forensic history.

## Failure And Retry Strategy

### Retryable Failures

Examples:

- transient Redis errors
- transient PostgreSQL connectivity errors
- object storage timeouts
- worker crash mid-run
- subprocess killed by infrastructure issues

### Non-Retryable Failures

Examples:

- invalid input snapshot
- missing scenario or run row
- unsupported engine version
- schema mismatch that code cannot recover from
- deterministic scientific validation failure

### Retry Policy

Suggested defaults:

- simulations: max 3 attempts
- decomposition: max 3 attempts
- reports: max 5 attempts

Backoff:

- exponential with jitter
- baseline schedule: `30s`, `120s`, `480s`
- cap max delay at `15m`

On retry:

1. mark the row with new attempt metadata and `next_retry_at`
2. enqueue a new message with incremented `attempt`
3. ack the old message only after the new enqueue succeeds

On final failure:

1. mark the row `failed`
2. persist failure details
3. copy the original message to a dead-letter stream
4. ack the main stream message

## Idempotency Rules

### API-Level Idempotency

Use a unique idempotency key on run submission:

- unique per project or per organization, depending on product semantics

This prevents duplicate run records from repeated client submits.

### Worker-Level Idempotency

Exactly-once execution is not guaranteed. Design for at-least-once.

Rules:

1. business identity is `run_id` or `report_id`, not Redis message ID
2. worker must load the DB row and exit if the row is already terminal
3. artifacts use deterministic keys such as `runs/{run_id}/result.json`
4. metadata rows for artifacts must be inserted with uniqueness rules or upsert behavior
5. the worker should always read `input_snapshot_json` from PostgreSQL, not from the message body alone
6. finalization must be transactionally safe: do not mark success before artifact metadata is durable

## Timeout And Cancellation Approach

### Timeout

Use two layers:

1. soft timeout in worker logic for graceful shutdown
2. hard timeout via subprocess kill

Reason:

Scientific code may ignore cooperative cancellation or hang inside native libraries.

Recommended defaults:

- simulations: `30m`
- decomposition: `60m`
- reports: `10m`

### Cancellation

Use cooperative cancellation:

1. API sets `cancel_requested`
2. worker checks the row before start and between phases
3. if execution runs in a subprocess, worker terminates the subprocess on cancellation
4. worker marks the row `canceled`

### Lease And Heartbeat

While a job is running:

- update `last_heartbeat_at` regularly
- keep `lease_expires_at` ahead of the heartbeat

If a worker dies:

- another worker uses `XAUTOCLAIM` to reclaim stale messages
- it checks whether the DB lease expired before retrying

## Artifact Writing And References

Artifacts should include:

- raw result JSON
- summary JSON
- plots or images if generated
- CSV exports
- report PDFs
- diagnostic bundles if failures occur

Recommended object keys:

- `runs/{run_id}/result.json`
- `runs/{run_id}/summary.json`
- `runs/{run_id}/plots/{name}.png`
- `reports/{report_id}/report.pdf`

Write process:

1. generate artifact bytes or JSON
2. upload to object storage
3. verify upload result, checksum, and byte size
4. insert or upsert `run_artifacts` metadata row
5. finalize the run or report row

Never insert artifact metadata before upload success.

## Example Job Payload Schema

Current code shape:

- [payloads.py](/Users/mobashirsifat/Desktop/bio_lab/services/worker/app/jobs/payloads.py)

Example:

```json
{
  "jobId": "0195f3e4-4b9c-7f76-ae9d-c0df2b238f4a",
  "jobType": "simulation.run.execute",
  "schemaVersion": "1.0",
  "queueName": "jobs:simulation",
  "priority": "normal",
  "enqueuedAt": "2026-03-31T12:00:00Z",
  "payload": {
    "jobType": "simulation.run.execute",
    "organizationId": "0195f3e4-4a86-7d13-bb2a-d5428b76f010",
    "projectId": "0195f3e4-4a86-7d13-bb2a-d5428b76f020",
    "runId": "0195f3e4-4b9c-7f76-ae9d-c0df2b238f4a",
    "scenarioId": "0195f3e4-4a86-7d13-bb2a-d5428b76f7f0",
    "initiatedByUserId": "0195f3e4-4a86-7d13-bb2a-d5428b76f030",
    "traceId": "trace-123",
    "requestId": "req-123",
    "engineName": "soil-engine",
    "engineVersion": "0.1.0",
    "inputSchemaVersion": "1.0",
    "attempt": 1,
    "maxAttempts": 3,
    "timeoutSeconds": 1800,
    "idempotencyKey": "project-123-scenario-4",
    "inputHash": "abc123",
    "executionOptions": {
      "priority": "normal"
    }
  }
}
```

## Example Worker Runner Skeleton

Current code:

- [worker_runner.py](/Users/mobashirsifat/Desktop/bio_lab/services/worker/app/runners/worker_runner.py)

The core loop should:

1. ensure streams and consumer groups exist
2. reserve messages from Redis
3. periodically claim stale messages
4. dispatch to typed handlers
5. ack on success
6. requeue or dead-letter on failure

## Pseudocode For Processing A Simulation Run

```python
def process_simulation_run(message):
    envelope = parse_job(message)
    run_id = envelope.payload.run_id

    with db.transaction():
        run = select_run_for_update(run_id)
        if run.status in TERMINAL_STATES:
            ack(message)
            return

        if run.status == "cancel_requested":
            mark_canceled(run)
            ack(message)
            return

        mark_running(
            run,
            worker_id=current_worker_id,
            attempt_count=run.attempt_count + 1,
            started_at=now(),
            last_heartbeat_at=now(),
            lease_expires_at=now() + lease_duration,
        )

    input_snapshot = load_input_snapshot(run_id)

    try:
        result = execute_in_subprocess(
            run_id=run_id,
            input_snapshot=input_snapshot,
            timeout_seconds=envelope.payload.timeout_seconds,
        )

        result_key = f"runs/{run_id}/result.json"
        summary_key = f"runs/{run_id}/summary.json"

        result_meta = upload_json(result_key, result.raw_result)
        summary_meta = upload_json(summary_key, result.summary)

        with db.transaction():
            upsert_artifact(run_id, "result_json", result_meta)
            upsert_artifact(run_id, "summary_json", summary_meta)
            mark_succeeded(
                run,
                result_hash=result.result_hash,
                result_summary_json=result.summary,
                completed_at=now(),
            )

        ack(message)

    except RetryableError as exc:
        schedule_retry(run_id, exc, next_attempt=envelope.payload.attempt + 1)
        requeue_with_backoff(message)
        ack(message)

    except CancellationRequested:
        terminate_subprocess_if_needed()
        mark_canceled(run_id)
        ack(message)

    except Exception as exc:
        persist_failure(run_id, exc)
        dead_letter(message, reason=str(exc))
        ack(message)
```

## Logging, Tracing, And Monitoring Recommendations

### Structured Logs

Every log line should include:

- `worker_id`
- `job_id`
- `job_type`
- `queue_name`
- `run_id` or `report_id`
- `organization_id`
- `attempt`
- `trace_id`
- `request_id`
- `engine_version`

### Tracing

Propagate trace context from API to job payload:

- API writes `trace_id` into the envelope
- worker starts a new span linked to the API trace
- child execution can create nested spans for engine execution and artifact upload

### Metrics

At minimum track:

- queue depth
- queue lag
- reserved vs acked vs dead-lettered message counts
- job duration by job type
- retry count by job type
- timeout count by job type
- success/failure ratio
- stale message reclaim count
- artifact upload latency

### Alerts

Create alerts for:

- dead-letter stream growth
- jobs stuck in `running` past timeout plus grace
- queue lag above threshold
- repeated failures for the same engine version
- worker heartbeat missing

## Test Strategy

### Unit Tests

Test:

- payload parsing and schema validation
- retry classification
- backoff calculation
- allowed state transitions
- deterministic artifact key generation

Current example test:

- [test_job_payloads.py](/Users/mobashirsifat/Desktop/bio_lab/services/worker/tests/unit/test_job_payloads.py)

### Integration Tests

Test with real Redis and Postgres:

- enqueue -> consume -> ack flow
- stale message reclaim with `XAUTOCLAIM`
- retry scheduling
- terminal failure path
- cancellation path

### Crash And Timeout Tests

Test:

- worker crashes after setting `running`
- child subprocess exceeds timeout
- child subprocess ignores cooperative cancel

The system should recover without duplicate terminal artifacts.

### End-To-End Tests

Test:

- API creates run
- worker executes
- artifact metadata persists
- run transitions to `succeeded`
- results endpoint returns expected payload

## Rules For Safe Retries And Reproducibility

1. Always treat PostgreSQL state as authoritative over Redis message state.
2. Never trust queue payload alone for scientific inputs; reload the stored snapshot from the run row.
3. Always use deterministic artifact keys based on business IDs.
4. Never mark a run `succeeded` before all required artifacts are durable and metadata rows exist.
5. Never process a terminal row again; ack and exit.
6. Never retry deterministic validation errors.
7. Always increment attempt metadata before executing a retry.
8. Always emit the engine version and input hash into logs and persisted rows.
9. Always run scientific execution in a subprocess with a hard timeout.
10. Always make cancellation cooperative but enforceable via subprocess termination.

## Recommended Next Implementation Steps

1. implement the `simulation_runs` and `reports` execution columns needed by the worker
2. implement `RedisStreamsQueue`
3. implement `StatusStore` against PostgreSQL
4. implement `ExecutionService` subprocess supervision
5. wire `POST /api/v1/runs` to publish a `JobEnvelope`
6. add one end-to-end integration test for submit -> execute -> results
