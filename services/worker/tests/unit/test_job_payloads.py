from datetime import UTC, datetime
from uuid import uuid4

from app.jobs.payloads import JobEnvelope, JobPriority, JobType, SimulationRunPayload


def test_simulation_run_payload_parses() -> None:
    payload = SimulationRunPayload(
        organization_id=uuid4(),
        project_id=uuid4(),
        initiated_by_user_id=uuid4(),
        run_id=uuid4(),
        scenario_id=uuid4(),
        engine_name="soil-engine",
        engine_version="0.1.0",
        input_schema_version="1.0",
        input_hash="abc123",
    )

    envelope = JobEnvelope(
        job_id=uuid4(),
        job_type=JobType.SIMULATION_RUN,
        queue_name="jobs:simulation",
        priority=JobPriority.NORMAL,
        enqueued_at=datetime.now(UTC),
        payload=payload,
    )

    assert envelope.payload.run_id == payload.run_id
    assert envelope.job_type == JobType.SIMULATION_RUN
