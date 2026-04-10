from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_settings
from app.db.session import check_database_connection
from app.schemas.system import HealthCheck, HealthResponse

router = APIRouter(prefix="/system", tags=["system"])


@router.get(
    "/health",
    response_model=HealthResponse,
    operation_id="system_getHealth",
    summary="Get API health and readiness checks",
)
def get_health() -> HealthResponse:
    settings = get_settings()
    db_ok = check_database_connection()

    return HealthResponse(
        status="ok" if db_ok else "degraded",
        service=settings.api_name,
        environment=settings.api_env,
        version=settings.api_version,
        checks={
            "database": HealthCheck(
                ok=db_ok,
                detail="Database connection succeeded." if db_ok else "Database connection failed.",
            )
        },
    )
