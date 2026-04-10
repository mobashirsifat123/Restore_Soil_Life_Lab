# Quality Strategy

## Purpose

This document defines the initial quality strategy for the scientific SaaS platform.

Quality goals:

- scientific correctness
- reproducibility
- reliability under async execution
- auditability
- safe product iteration

The platform must treat a simulation result as both a product output and a scientific record. Testing, observability, and release controls should reflect that standard.

## Quality Principles

1. Correctness beats breadth.
   Prefer a smaller, deeply verified MVP over a wide surface with weak guarantees.

2. Reproducibility is a feature.
   The same canonical input and engine version should produce the same output and hashes unless a change is intentional and versioned.

3. PostgreSQL is the source of truth.
   Redis is a transport and cache layer, not a durable record of workflow state.

4. OpenAPI is the external contract.
   Frontend integration should happen through the generated client, not hand-written request code.

5. Observability starts on day one.
   Every request, run, job, and artifact path should be traceable.

6. Critical paths get end-to-end verification.
   The thin vertical slice must be continuously exercised from browser to worker to result retrieval.

## Testing Strategy By Layer

## 1. Frontend: `apps/web`

### Test pyramid

- static checks
  - TypeScript `tsc --noEmit`
  - ESLint
  - Tailwind class linting if adopted
- unit tests
  - utility functions
  - data formatters
  - query key factories
  - form mappers
- component tests
  - React Testing Library for UI primitives and feature components
  - form validation behavior
  - loading, error, empty, and success states
- feature integration tests
  - page-level tests with mocked generated API client or MSW
  - route guards and auth boundary behavior
- end-to-end tests
  - Playwright against real API, DB, Redis, and worker in CI/staging

### Frontend must-have tests from day one

- project creation form success and validation failure
- soil sample creation form success and validation failure
- scenario form success and validation failure
- run status page states: queued, running, succeeded, failed
- results page renders summary metrics and metadata

### Frontend later

- visual regression snapshots for premium marketing pages
- accessibility audits integrated into CI
- browser compatibility matrix beyond Chromium

## 2. API: `services/api`

### Test pyramid

- unit tests
  - business rules in services
  - permission checks
  - schema validation helpers
  - run lifecycle transition guards
- repository tests
  - SQLAlchemy queries against real PostgreSQL
  - org scoping
  - soft-delete filtering
  - unique constraints and version queries
- API integration tests
  - FastAPI `TestClient` or `httpx.AsyncClient`
  - auth dependency wiring
  - status codes and error envelope shape
  - OpenAPI schema generation smoke test
- contract tests
  - OpenAPI schema validation against implemented endpoints
  - generated client compatibility checks

### API must-have tests from day one

- `POST /api/v1/projects`
- `POST /api/v1/projects/{id}/soil-samples`
- `POST /api/v1/projects/{id}/scenarios`
- `POST /api/v1/runs`
- `GET /api/v1/runs/{id}`
- `GET /api/v1/runs/{id}/results`
- permission-denied coverage for org isolation
- invalid-state transition coverage for runs

### API later

- fuzzing with Schemathesis across the full OpenAPI surface
- property-based validation tests for complex scientific payloads

## 3. Worker: `services/worker`

### Test pyramid

- unit tests
  - payload parsing
  - retry policy logic
  - cancellation handling
  - idempotency key behavior
- handler tests
  - simulation-run handler with fake status store and fake artifact service
  - report handler with fake renderer
- integration tests
  - real Redis stream
  - real PostgreSQL status updates
  - simulation engine subprocess invocation
- resiliency tests
  - duplicate delivery
  - worker restart mid-job
  - timeout and cancellation

### Worker must-have tests from day one

- a queued run transitions to running then succeeded
- a failed engine invocation transitions to failed with error metadata
- redelivered job does not create duplicate artifacts or duplicate finalization
- cancellation requested before start prevents execution

### Worker later

- chaos testing for Redis disconnects and DB failover behavior
- throughput saturation tests with multiple worker instances

## 4. Simulation Engine: `services/simulation-engine`

### Test pyramid

- unit tests
  - deterministic math helpers
  - input canonicalization
  - module-level placeholder algorithms
- regression tests
  - golden input fixtures with expected output snapshots
  - expected `input_hash` and `result_hash`
- property/invariant tests
  - finite outputs
  - stable shape guarantees
  - no negative values where scientifically invalid
- differential tests
  - compare against trusted reference implementations when they exist
- benchmark tests
  - runtime and memory measurements on representative scenario sizes

### Simulation engine must-have tests from day one

- deterministic repeatability for identical input
- stable serialization and hash generation
- placeholder module outputs are present for requested modules
- CLI entrypoint produces valid output artifact

### Simulation engine later

- reference-data validation against published examples or domain expert fixtures
- Monte Carlo or sensitivity test suites where stochastic methods are introduced

## 5. Database And Migrations

### Required tests

- migration upgrade from empty database to head
- migration smoke test on non-empty fixture data
- downgrade tests for early migrations when practical
- schema constraint tests for unique indexes and foreign keys
- query performance smoke tests for critical indexes

### Day-one rule

Every migration must run in CI against a fresh PostgreSQL container.

## 6. Cross-System End-To-End Tests

### Critical flows

1. thin vertical slice
   - sign in placeholder
   - create project
   - add soil sample
   - create scenario
   - submit run
   - worker processes run
   - status updates appear
   - results page renders outputs and audit metadata

2. failure flow
   - submit run with intentionally failing scenario fixture
   - worker marks run failed
   - UI shows failure state and retry guidance

3. RBAC flow
   - user from org A cannot read project or run from org B

4. idempotency flow
   - repeated run submission with same client idempotency key does not create duplicate runs

### Execution model

- run Playwright against a real local stack in CI
- use deterministic placeholder simulation for PR builds
- run one broader smoke suite on staging after deploy

## Contract Testing Between Frontend And API

## Contract source of truth

- FastAPI-generated OpenAPI schema published from `services/api`
- generated TypeScript client in `packages/api-client`

## Required contract checks

1. OpenAPI schema generation check
   - fail CI if schema cannot be generated

2. generated client drift check
   - regenerate client in CI
   - fail if generated output differs from committed files

3. breaking-change detection
   - compare current schema to main branch schema
   - fail on backward-incompatible changes unless explicitly approved

4. endpoint conformance check
   - run API integration tests that assert actual responses match documented shapes

5. frontend compile verification
   - frontend must typecheck against the generated client with no local type overrides

## Suggested tooling

- `openapi-python-client` or FastAPI schema export for backend spec generation
- `openapi-typescript-codegen` or `orval` for frontend client generation
- `oasdiff` or equivalent for schema diffing
- `schemathesis` for later schema-driven test expansion

## End-To-End Test Strategy

## Tooling

- Playwright for browser E2E
- Docker Compose stack for API, DB, Redis, worker, and mocked object storage
- seeded test fixtures for org, user, and permissions

## Test environments

- PR environment
  - minimal deterministic stack
  - placeholder engine
  - critical-path tests only

- nightly environment
  - broader workflow coverage
  - larger fixtures
  - failure injection tests

- staging
  - smoke tests after deployment
  - release candidate verification

## Rules

- E2E tests should assert visible UX states and persisted backend state for runs
- E2E tests should not rely on arbitrary sleep; poll UI or API state transitions
- E2E data must be isolated per run using generated org/project names

## Simulation-Engine Correctness Strategy

## Verification layers

1. canonical fixture tests
   - small reference inputs with fully checked outputs

2. golden file tests
   - serialize result JSON
   - compare to approved snapshots when outputs change intentionally

3. scientific invariants
   - no invalid NaN or infinite values
   - stability metrics within expected bounds
   - matrix dimensions and node counts remain consistent

4. differential validation
   - compare selected calculations to an external reference implementation or notebook where available

5. benchmark baselines
   - track runtime for small, medium, and large scenarios

## Change-control rule

Any intentional change to scientific output must include:

- updated engine version
- updated fixture expectations
- explanation in PR
- explicit reviewer approval from the scientific owner or designated maintainer

## Reproducibility Verification Strategy

## Required reproducibility controls

- canonical input serialization
- `input_hash` derived from scientific payload only
- engine version persisted on every run
- parameter-set version persisted on every run
- deterministic seed stored whenever stochastic logic is introduced
- result artifact hash stored after completion

## Required reproducibility tests

1. same input, same engine version, same seed
   - same `input_hash`
   - same `result_hash`
   - same summary outputs

2. same input, different engine version
   - same `input_hash`
   - different provenance, potentially different `result_hash`

3. worker retry on same run
   - no duplicate final records
   - final artifact reference remains stable

4. rerun from stored snapshot
   - can reconstruct execution from persisted run payload and artifact references

## Persistence model for reproducibility

Store in PostgreSQL:

- `input_snapshot_json`
- `input_hash`
- `engine_version`
- `parameter_set_version`
- lifecycle timestamps
- status
- error metadata
- result summary JSON
- artifact metadata

Store in object storage:

- full result JSON
- large time-series data
- dense matrices
- rendered reports
- diagnostic logs when needed

## Performance Testing Recommendations

## API performance

- use `k6` or `Locust`
- measure p50, p95, and error rate
- focus first on:
  - create project
  - list runs
  - get run status
  - get run results

Targets for MVP:

- p95 read endpoints under 300 ms on staging-sized fixtures
- p95 write endpoints under 500 ms excluding async job completion

## Worker performance

- measure queue lag
- median and p95 job duration by job type
- success rate and retry rate
- concurrent worker throughput under controlled load

## Simulation engine performance

- benchmark small, medium, and large scenarios
- track runtime and memory
- define a budget per job class

Initial budget guidance:

- placeholder thin-slice runs complete within 10 seconds in CI
- production-target simple runs complete within 60 seconds unless explicitly background-batch only

## Frontend performance

- Lighthouse for marketing pages
- Web Vitals for app shell
- bundle-size monitoring

Initial targets:

- marketing Lighthouse performance >= 90 in CI preview checks
- largest route JS bundle budgets enforced for platform routes

## Observability Architecture

## Logging

Use structured JSON logs across API, worker, and engine subprocess wrappers.

Required fields:

- timestamp
- level
- service
- environment
- request_id
- trace_id
- organization_id
- user_id when available
- project_id when available
- run_id when available
- job_id when available
- artifact_key when available
- engine_version when available

## Metrics

Expose Prometheus-compatible metrics or OpenTelemetry metrics for:

- API request count, latency, error rate
- DB query latency for key operations
- Redis queue depth and consumer lag
- job success, failure, retry, timeout, cancellation counts
- run state transition counts
- simulation duration by module
- report generation duration

## Tracing

Use OpenTelemetry from day one where feasible.

Trace boundaries:

- Next.js request to API call
- FastAPI request lifecycle
- API enqueue event
- worker dequeue and processing
- simulation subprocess execution
- object storage writes

The minimum acceptable tracing path is:

- `web -> api -> worker -> simulation engine wrapper -> artifact write`

## Error monitoring

Recommended stack:

- Sentry for frontend, API, and worker exceptions
- Prometheus + Grafana for metrics and dashboards
- Tempo or Jaeger later for trace visualization if not using a managed APM

## Alerts from day one

- API error rate spike
- worker failure rate spike
- worker queue lag over threshold
- repeated run failures for same engine version
- migration failure during deployment

## CI Workflow Design

## Pull request workflow

### Job 1: static quality

- frontend lint
- frontend typecheck
- backend lint
- backend typecheck if configured
- worker lint
- simulation engine lint

### Job 2: unit tests

- frontend unit/component tests
- API unit tests
- worker unit tests
- simulation engine unit/regression tests

### Job 3: schema and codegen

- export OpenAPI schema
- validate schema
- regenerate TypeScript client
- fail on diff
- run schema breaking-change check against main

### Job 4: integration tests

- PostgreSQL-backed API integration tests
- Redis-backed worker integration tests
- migration upgrade smoke test

### Job 5: critical E2E

- thin vertical slice Playwright flow

### Job 6: benchmark smoke

- simulation engine benchmark sanity check
- fail only on extreme regressions at first

## Main branch workflow

- rerun PR gates
- publish build artifacts
- publish OpenAPI schema artifact
- publish benchmark results
- deploy to staging
- run staging smoke suite

## Nightly workflow

- broader E2E coverage
- performance test suite
- extended worker resiliency tests
- longer-running simulation regression suite

## Sample Quality Gates For Pull Requests

Every PR must satisfy:

- all linters pass
- all typechecks pass
- unit tests pass
- API integration tests pass for touched backend code
- migration smoke test passes if schema changed
- generated client is up to date if OpenAPI changed
- no undocumented breaking API changes
- critical thin-slice E2E passes if touched code is user-facing or async-flow-related
- simulation regression tests pass if engine code changed
- benchmark regression is within threshold for engine changes

Additional mandatory reviewer gates:

- scientific reviewer approval for engine output changes
- platform reviewer approval for migration and queue changes
- frontend reviewer approval for design-system or route-shell changes

## Release Checklist

## Before release

- verify all required CI checks are green
- confirm migrations have been reviewed
- confirm OpenAPI schema and generated client are in sync
- confirm engine version bump for scientific output changes
- confirm rollback plan for schema changes
- verify staging smoke tests passed
- verify alerting and dashboards are healthy

## During release

- deploy API and worker with version tags
- run migrations in controlled step
- confirm worker consumers are on compatible code before enabling new job types
- watch queue lag, run failure rate, and API error rate

## After release

- run thin-slice smoke flow in staging or production-safe environment
- inspect first successful run artifact and metadata
- verify Sentry is quiet for new release
- verify no codegen mismatch on deployed API schema

## Rollback Recommendations

- prefer forward-fix for non-breaking UI issues
- keep worker and API compatible across at least one adjacent version
- treat destructive migrations as exceptional and gated
- support worker pause capability so bad jobs stop being consumed during incident response
- keep release artifacts and engine package versions traceable to run provenance

## Must Have From Day One Vs Later

## Must have from day one

- unit tests in every service
- API integration tests with real PostgreSQL
- worker integration tests with real Redis
- simulation determinism tests
- thin-slice Playwright E2E
- OpenAPI generation and client drift check
- migration smoke test
- structured logging with request and run identifiers
- basic metrics and Sentry error monitoring
- release checklist and rollback procedure

## Add soon after MVP

- broader contract fuzzing
- benchmark trend tracking dashboard
- staging canary release automation
- accessibility test automation
- visual regression for marketing pages
- load testing in CI-on-demand or nightly

## Later

- chaos testing
- multi-region or disaster recovery drills
- long-horizon scientific benchmark archive
- automatic trace-based anomaly detection

## Recommended Initial Tooling

- frontend unit/component: Vitest, React Testing Library
- E2E: Playwright
- backend and worker tests: Pytest
- property tests: Hypothesis
- API schema testing: Schemathesis later
- performance: k6 or Locust, `pytest-benchmark`, `asv` later
- observability: OpenTelemetry, Prometheus, Grafana, Sentry

## First 30-Day Implementation Priorities

1. establish CI jobs for lint, typecheck, unit, integration, and thin-slice E2E
2. add OpenAPI export and generated-client drift gate
3. add deterministic simulation-engine regression fixtures
4. instrument API and worker with structured logs and request/run IDs
5. add Prometheus metrics and Sentry across API and worker
6. create staging smoke workflow and release checklist in repo

If the team does these six things early, the platform will have a strong quality base without overbuilding the process before the product exists.
