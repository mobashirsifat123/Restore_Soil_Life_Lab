from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import RequestContextMiddleware
from app.db.session import check_database_connection
from app.schemas.system import HealthCheck, HealthResponse


def create_application() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.api_name,
        version=settings.api_version,
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_tags=[
            {"name": "auth", "description": "Authentication, session, and caller identity."},
            {"name": "projects", "description": "Project CRUD and project-scoped access."},
            {"name": "soil-samples", "description": "Soil sample CRUD under projects."},
            {"name": "scenarios", "description": "Versioned simulation scenario APIs."},
            {"name": "runs", "description": "Simulation run submission and results retrieval."},
            {"name": "system", "description": "Operational health and diagnostics."},
        ],
    )

    if settings.allowed_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.allowed_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
            allow_headers=["*"],
        )

    app.add_middleware(RequestContextMiddleware)
    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get(
        "/healthz",
        response_model=HealthResponse,
        tags=["system"],
        operation_id="system_healthz",
        summary="Unversioned health check",
    )
    def healthz() -> HealthResponse:
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

    return app


app = create_application()
