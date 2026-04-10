from __future__ import annotations

from app.domain.auth import AuthenticatedUser
from app.repositories.admin_repository import AdminRepository
from app.schemas.admin import (
    AdminUserListResponse,
    AdminUserSummary,
    UserActivityLogEntry,
    UserActivityLogListResponse,
)


class AdminService:
    def __init__(self, repository: AdminRepository) -> None:
        self.repository = repository

    def list_users(self, *, current_user: AuthenticatedUser) -> AdminUserListResponse:
        items = self.repository.list_users(current_user.organization_id)
        return AdminUserListResponse(
            items=[AdminUserSummary.model_validate(item) for item in items]
        )

    def list_user_activity(
        self,
        *,
        current_user: AuthenticatedUser,
        limit: int = 200,
    ) -> UserActivityLogListResponse:
        items = self.repository.list_user_activity(current_user.organization_id, limit=limit)
        return UserActivityLogListResponse(
            items=[UserActivityLogEntry.model_validate(item) for item in items]
        )
