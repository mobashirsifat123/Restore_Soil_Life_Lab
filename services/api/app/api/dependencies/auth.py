from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request

from app.api.dependencies.services import get_auth_service
from app.core.errors import AppError
from app.domain.auth import AuthenticatedUser
from app.services.auth_service import AuthService

AuthServiceDependency = Annotated[AuthService, Depends(get_auth_service)]


def get_current_user(
    request: Request,
    auth_service: AuthServiceDependency,
) -> AuthenticatedUser:
    return auth_service.authenticate_request(request)


CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]


def get_optional_user(
    request: Request,
    auth_service: AuthServiceDependency,
) -> AuthenticatedUser | None:
    try:
        return auth_service.authenticate_request(request)
    except AppError as error:
        if error.status_code == 401:
            return None
        raise


OptionalCurrentUser = Annotated[AuthenticatedUser | None, Depends(get_optional_user)]


def require_permission(permission: str):
    def dependency(current_user: CurrentUser) -> AuthenticatedUser:
        if "*" in current_user.permissions or permission in current_user.permissions:
            return current_user
        raise AppError(
            status_code=403,
            code="permission_denied",
            message=f"Permission '{permission}' is required for this operation.",
            details={"requiredPermission": permission},
        )

    return Depends(dependency)


def require_admin_user():
    def dependency(current_user: CurrentUser) -> AuthenticatedUser:
        if "org_admin" in current_user.roles:
            return current_user
        raise AppError(
            status_code=403,
            code="admin_required",
            message="Administrator access is required for this operation.",
        )

    return Depends(dependency)
