from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class JobEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_id: UUID = Field(default_factory=uuid4)
    job_type: Literal["simulation.run.execute"]
    schema_version: str = "1.0"
    queue_name: str
    enqueued_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    payload: dict[str, Any]
