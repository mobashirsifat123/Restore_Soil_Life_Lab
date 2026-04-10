from __future__ import annotations

from typing import Any

from pydantic import Field

from app.schemas.common import ApiModel


class ValidationIssue(ApiModel):
    field: str
    message: str
    type: str


class ErrorDetail(ApiModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    issues: list[ValidationIssue] = Field(default_factory=list)


class ErrorResponse(ApiModel):
    error: ErrorDetail
    request_id: str | None = None
