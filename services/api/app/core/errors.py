from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.error import ErrorDetail, ErrorResponse, ValidationIssue


class AppError(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def _json_error(
    *,
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
    issues: list[ValidationIssue] | None = None,
) -> JSONResponse:
    payload = ErrorResponse(
        error=ErrorDetail(code=code, message=message, details=details or {}, issues=issues or []),
        request_id=_request_id(request),
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump(by_alias=True))


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        return _json_error(
            request=request,
            status_code=exc.status_code,
            code=exc.code,
            message=exc.message,
            details=exc.details,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        issues = [
            ValidationIssue(
                field=".".join(str(part) for part in error["loc"]),
                message=error["msg"],
                type=error["type"],
            )
            for error in exc.errors()
        ]
        return _json_error(
            request=request,
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            code="validation_error",
            message="Request validation failed.",
            issues=issues,
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        return _json_error(
            request=request,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="internal_server_error",
            message="An unexpected error occurred.",
        )
