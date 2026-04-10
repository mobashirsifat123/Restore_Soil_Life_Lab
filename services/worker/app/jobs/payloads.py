from __future__ import annotations

from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class JobType(StrEnum):
    SIMULATION_RUN = "simulation.run.execute"
    DECOMPOSITION_RUN = "decomposition.run.execute"
    REPORT_GENERATION = "report.generate"


class JobPriority(StrEnum):
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class BaseJobPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    organization_id: UUID
    project_id: UUID
    initiated_by_user_id: UUID | None = None
    trace_id: str | None = None
    request_id: str | None = None


class SimulationRunPayload(BaseJobPayload):
    job_type: Literal[JobType.SIMULATION_RUN] = JobType.SIMULATION_RUN
    run_id: UUID
    scenario_id: UUID
    engine_name: str
    engine_version: str
    input_schema_version: str
    parameter_set_version: int | None = None
    soil_sample_version: int | None = None
    attempt: int = 1
    max_attempts: int = 3
    timeout_seconds: int = 1800
    idempotency_key: str | None = None
    input_hash: str
    execution_options: dict[str, Any] = Field(default_factory=dict)


class DecompositionRunPayload(BaseJobPayload):
    job_type: Literal[JobType.DECOMPOSITION_RUN] = JobType.DECOMPOSITION_RUN
    run_id: UUID
    scenario_id: UUID
    engine_name: str
    engine_version: str
    input_schema_version: str
    attempt: int = 1
    max_attempts: int = 3
    timeout_seconds: int = 3600
    input_hash: str
    execution_options: dict[str, Any] = Field(default_factory=dict)


class ReportGenerationPayload(BaseJobPayload):
    job_type: Literal[JobType.REPORT_GENERATION] = JobType.REPORT_GENERATION
    report_id: UUID
    primary_run_id: UUID | None = None
    template_key: str
    template_version: str
    attempt: int = 1
    max_attempts: int = 5
    timeout_seconds: int = 600
    render_options: dict[str, Any] = Field(default_factory=dict)


JobPayload = Annotated[
    SimulationRunPayload | DecompositionRunPayload | ReportGenerationPayload,
    Field(discriminator="job_type"),
]


class JobEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_id: UUID
    job_type: JobType
    schema_version: str = "1.0"
    queue_name: str
    priority: JobPriority = JobPriority.NORMAL
    enqueued_at: datetime
    available_at: datetime | None = None
    dedupe_key: str | None = None
    payload: JobPayload

    def next_attempt(self, *, delay_seconds: int) -> JobEnvelope:
        next_payload = self.payload.model_copy(update={"attempt": self.payload.attempt + 1})
        return self.model_copy(
            update={
                "available_at": datetime.now(UTC) + timedelta(seconds=delay_seconds),
                "payload": next_payload,
            }
        )
