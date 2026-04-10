from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, Field, field_validator

from app.domain.enums import ArtifactType, RunStatus
from app.schemas.common import ApiModel, JsonDict, to_camel


class RunExecutionOptions(ApiModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        use_enum_values=True,
        extra="allow",
    )

    deterministic: bool = True
    random_seed: int = 0
    requested_modules: list[str] = Field(default_factory=list)
    timeout_seconds: int = Field(default=120, ge=1, le=86_400)
    metadata: JsonDict = Field(default_factory=dict)

    @field_validator("requested_modules")
    @classmethod
    def normalize_requested_modules(cls, value: list[str]) -> list[str]:
        normalized: list[str] = []
        for module in value:
            candidate = module.strip()
            if candidate and candidate not in normalized:
                normalized.append(candidate)
        return normalized


def dump_execution_options(options: RunExecutionOptions) -> JsonDict:
    return options.model_dump(mode="json", by_alias=True, exclude_none=True)


class RunCreate(ApiModel):
    scenario_id: UUID
    idempotency_key: str | None = Field(default=None, max_length=100)
    execution_options: RunExecutionOptions = Field(default_factory=RunExecutionOptions)

    @field_validator("idempotency_key")
    @classmethod
    def normalize_idempotency_key(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class RunArtifact(ApiModel):
    id: UUID
    artifact_type: ArtifactType
    label: str
    content_type: str
    storage_key: str
    byte_size: int | None = None
    checksum_sha256: str | None = None
    metadata: JsonDict = Field(default_factory=dict)
    created_at: datetime


class RunDetail(ApiModel):
    id: UUID
    organization_id: UUID
    project_id: UUID
    scenario_id: UUID
    status: RunStatus
    engine_name: str
    engine_version: str
    input_schema_version: str
    parameter_set_version: int
    soil_sample_version: int
    input_hash: str
    result_hash: str | None = None
    queued_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    canceled_at: datetime | None = None
    failure_code: str | None = None
    failure_message: str | None = None
    created_at: datetime
    updated_at: datetime


class RunStatusResponse(ApiModel):
    id: UUID
    status: RunStatus
    queued_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    canceled_at: datetime | None = None
    failure_code: str | None = None
    failure_message: str | None = None


class RunListResponse(ApiModel):
    items: list[RunDetail]
    next_cursor: str | None = None
    has_more: bool = False

class RunResultsResponse(ApiModel):
    id: UUID
    status: RunStatus
    engine_name: str
    engine_version: str
    parameter_set_version: int
    soil_sample_version: int
    input_hash: str
    result_hash: str | None = None
    failure_code: str | None = None
    failure_message: str | None = None
    input_snapshot: JsonDict
    result_summary: JsonDict | None = None
    artifacts: list[RunArtifact] = Field(default_factory=list)
