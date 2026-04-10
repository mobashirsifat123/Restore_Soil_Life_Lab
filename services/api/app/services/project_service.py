from __future__ import annotations

from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.core.errors import AppError
from app.domain.auth import AuthenticatedUser
from app.repositories.project_repository import ProjectRepository
from app.schemas.common import DeleteResponse
from app.schemas.project import ProjectCreate, ProjectDetail, ProjectListResponse, ProjectUpdate
from app.services.serializers import serialize_project
from app.utils.slugs import slugify


class ProjectService:
    def __init__(self, repository: ProjectRepository) -> None:
        self.repository = repository

    def _resolve_unique_slug(
        self,
        *,
        organization_id,
        slug_source: str,
        exclude_project_id: UUID | None = None,
    ) -> str:
        base_slug = slugify(slug_source)
        slug = base_slug
        counter = 2
        while self.repository.slug_exists(
            organization_id,
            slug,
            exclude_project_id=exclude_project_id,
        ):
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    def list_projects(
        self,
        *,
        current_user: AuthenticatedUser,
        limit: int,
        cursor: str | None,
    ) -> ProjectListResponse:
        items = self.repository.list_for_organization(
            current_user.organization_id,
            limit=limit,
            cursor=cursor,
        )
        return ProjectListResponse(
            items=[serialize_project(item) for item in items],
            next_cursor=None,
        )

    def create_project(
        self,
        *,
        current_user: AuthenticatedUser,
        payload: ProjectCreate,
    ) -> ProjectDetail:
        slug = self._resolve_unique_slug(
            organization_id=current_user.organization_id,
            slug_source=payload.slug or payload.name,
        )

        try:
            project = self.repository.create(
                organization_id=current_user.organization_id,
                created_by_user_id=current_user.user_id,
                name=payload.name,
                slug=slug,
                description=payload.description,
                metadata_json=payload.metadata,
            )
        except IntegrityError as exc:
            raise AppError(
                status_code=409,
                code="project_conflict",
                message="A project with the same slug already exists.",
            ) from exc
        return serialize_project(project)

    def get_project(self, *, current_user: AuthenticatedUser, project_id: UUID) -> ProjectDetail:
        project = self.repository.get_by_id(current_user.organization_id, project_id)
        if project is None:
            raise AppError(status_code=404, code="project_not_found", message="Project not found.")
        return serialize_project(project)

    def update_project(
        self,
        *,
        current_user: AuthenticatedUser,
        project_id: UUID,
        payload: ProjectUpdate,
    ) -> ProjectDetail:
        project = self.repository.get_by_id(current_user.organization_id, project_id)
        if project is None:
            raise AppError(status_code=404, code="project_not_found", message="Project not found.")

        updates: dict[str, object] = {}
        if "name" in payload.model_fields_set:
            updates["name"] = payload.name
        if "description" in payload.model_fields_set:
            updates["description"] = payload.description
        if "status" in payload.model_fields_set:
            updates["status"] = payload.status
        if "metadata" in payload.model_fields_set:
            updates["metadata_json"] = payload.metadata or {}

        should_rebuild_slug = (
            "slug" in payload.model_fields_set or "name" in payload.model_fields_set
        )
        if should_rebuild_slug:
            slug_source = payload.slug or payload.name or project.name
            updates["slug"] = self._resolve_unique_slug(
                organization_id=current_user.organization_id,
                slug_source=slug_source,
                exclude_project_id=project.id,
            )

        if not updates:
            return serialize_project(project)

        try:
            project = self.repository.update(project, updates=updates)
        except IntegrityError as exc:
            raise AppError(
                status_code=409,
                code="project_conflict",
                message="Project update would violate a uniqueness constraint.",
            ) from exc
        return serialize_project(project)

    def delete_project(
        self,
        *,
        current_user: AuthenticatedUser,
        project_id: UUID,
    ) -> DeleteResponse:
        project = self.repository.soft_delete(
            current_user.organization_id,
            project_id,
            current_user.user_id,
        )
        if project is None:
            raise AppError(status_code=404, code="project_not_found", message="Project not found.")
        return DeleteResponse(id=project.id, deleted_at=project.deleted_at)
