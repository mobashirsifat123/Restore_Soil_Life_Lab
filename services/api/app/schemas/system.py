from __future__ import annotations

from app.schemas.common import ApiModel


class HealthCheck(ApiModel):
    ok: bool
    detail: str


class HealthResponse(ApiModel):
    status: str
    service: str
    environment: str
    version: str
    checks: dict[str, HealthCheck]
