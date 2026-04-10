from datetime import UTC, datetime
from uuid import uuid4

from app.jobs.handlers.simulation_run import handle_simulation_run
from app.jobs.payloads import JobEnvelope, JobPriority, JobType, SimulationRunPayload


class FakeStatusStore:
    def __init__(self) -> None:
        self.started = False
        self.succeeded = False

    def start_simulation_run(self, *, run_id, attempt):
        self.started = True
        return {
            "id": run_id,
            "organization_id": uuid4(),
            "input_snapshot_json": {"inputSchemaVersion": "1.0.0"},
        }

    def mark_run_succeeded(self, *, run_id, organization_id, result_payload, artifacts):
        self.succeeded = True
        self.run_id = run_id
        self.organization_id = organization_id
        self.result_payload = result_payload
        self.artifacts = artifacts


class FakeArtifactService:
    def write_run_artifacts(self, *, run_id, result_payload, stdout, stderr):
        self.run_id = run_id
        self.result_payload = result_payload
        self.stdout = stdout
        self.stderr = stderr
        return ["artifact-1"]


class FakeExecutionService:
    def execute_simulation(self, *, run_id, input_snapshot, timeout_seconds):
        self.run_id = run_id
        self.input_snapshot = input_snapshot
        self.timeout_seconds = timeout_seconds
        return {
            "result": {
                "provenance": {"resultHash": "abc123", "engineVersion": "0.1.0"},
                "summary": {"nodeCount": 1},
            },
            "stdout": "completed",
            "stderr": "",
        }


def test_handle_simulation_run_processes_happy_path():
    run_id = uuid4()
    organization_id = uuid4()
    payload = SimulationRunPayload(
        organization_id=organization_id,
        project_id=uuid4(),
        initiated_by_user_id=uuid4(),
        run_id=run_id,
        scenario_id=uuid4(),
        engine_name="soil-engine",
        engine_version="0.1.0",
        input_schema_version="1.0.0",
        input_hash="hash",
        execution_options={},
        timeout_seconds=120,
    )
    envelope = JobEnvelope(
        job_id=uuid4(),
        job_type=JobType.SIMULATION_RUN,
        queue_name="jobs:simulation",
        priority=JobPriority.NORMAL,
        enqueued_at=datetime.now(UTC),
        payload=payload,
    )
    status_store = FakeStatusStore()
    artifact_service = FakeArtifactService()
    execution_service = FakeExecutionService()

    handle_simulation_run(
        envelope=envelope,
        payload=payload,
        status_store=status_store,
        artifact_service=artifact_service,
        engine_executor=execution_service,
    )

    assert status_store.started is True
    assert status_store.succeeded is True
    assert execution_service.run_id == run_id
    assert status_store.run_id == run_id
    assert status_store.organization_id == organization_id
    assert status_store.artifacts == ["artifact-1"]
