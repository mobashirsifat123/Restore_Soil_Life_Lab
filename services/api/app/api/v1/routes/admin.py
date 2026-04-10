from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.dependencies.auth import CurrentUser, require_admin_user
from app.api.dependencies.services import get_admin_service
from app.schemas.admin import AdminUserListResponse, UserActivityLogListResponse
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["admin"])
AdminServiceDependency = Annotated[AdminService, Depends(get_admin_service)]


@router.get(
    "/users",
    response_model=AdminUserListResponse,
    operation_id="admin_listUsers",
    summary="List organization users for the admin panel",
    dependencies=[require_admin_user()],
)
def list_users(
    current_user: CurrentUser,
    admin_service: AdminServiceDependency,
) -> AdminUserListResponse:
    return admin_service.list_users(current_user=current_user)


@router.get(
    "/user-log",
    response_model=UserActivityLogListResponse,
    operation_id="admin_listUserActivity",
    summary="List recent user activity for the admin panel",
    dependencies=[require_admin_user()],
)
def list_user_activity(
    current_user: CurrentUser,
    admin_service: AdminServiceDependency,
    limit: int = Query(default=200, ge=1, le=500),
) -> UserActivityLogListResponse:
    return admin_service.list_user_activity(current_user=current_user, limit=limit)
