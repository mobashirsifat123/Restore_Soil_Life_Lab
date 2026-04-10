from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.domain.enums import ProjectStatus
from app.schemas.common import ApiModel, CursorPage, JsonDict


class ProjectCreate(ApiModel):
    name: str = Field(min_length=3, max_length=255)
    slug: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    metadata: JsonDict = Field(default_factory=dict)


class ProjectUpdate(ApiModel):
    name: str | None = Field(default=None, min_length=3, max_length=255)
    slug: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    status: ProjectStatus | None = None
    metadata: JsonDict | None = None


class ProjectDetail(ApiModel):
    id: UUID
    organization_id: UUID
    name: str
    slug: str
    description: str | None = None
    status: ProjectStatus
    metadata: JsonDict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(CursorPage):
    items: list[ProjectDetail]
