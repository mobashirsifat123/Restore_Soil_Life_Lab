from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas.common import ApiModel


class AdminUserSummary(ApiModel):
    id: UUID
    organization_id: UUID
    email: str
    full_name: str | None = None
    role: str
    is_active: bool
    created_at: datetime
    last_login_at: datetime | None = None


class AdminUserListResponse(ApiModel):
    items: list[AdminUserSummary] = Field(default_factory=list)


class UserActivityLogEntry(ApiModel):
    happened_at: datetime
    activity_type: str
    activity_label: str
    user_id: UUID | None = None
    user_email: str | None = None
    details: str | None = None


class UserActivityLogListResponse(ApiModel):
    items: list[UserActivityLogEntry] = Field(default_factory=list)
