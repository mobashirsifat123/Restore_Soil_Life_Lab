from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Project
from app.domain.enums import ProjectStatus


class ProjectRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_for_organization(self, organization_id: UUID, *, limit: int, cursor: str | None):
        statement = (
            select(Project)
            .where(Project.organization_id == organization_id, Project.deleted_at.is_(None))
            .order_by(Project.created_at.desc(), Project.id.desc())
            .limit(limit)
        )
        return list(self.session.scalars(statement))

    def get_by_id(self, organization_id: UUID, project_id: UUID):
        statement = select(Project).where(
            Project.organization_id == organization_id,
            Project.id == project_id,
            Project.deleted_at.is_(None),
        )
        return self.session.scalar(statement)

    def slug_exists(
        self,
        organization_id: UUID,
        slug: str,
        exclude_project_id: UUID | None = None,
    ) -> bool:
        statement = select(Project.id).where(
            Project.organization_id == organization_id,
            Project.slug == slug,
            Project.deleted_at.is_(None),
        )
        if exclude_project_id is not None:
            statement = statement.where(Project.id != exclude_project_id)
        return self.session.scalar(statement) is not None

    def create(
        self,
        *,
        organization_id: UUID,
        created_by_user_id: UUID,
        name: str,
        slug: str,
        description: str | None,
        metadata_json: dict,
    ) -> Project:
        project = Project(
            organization_id=organization_id,
            name=name,
            slug=slug,
            description=description,
            metadata_json=metadata_json,
            created_by_user_id=created_by_user_id,
        )
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        return project

    def update(self, project: Project, *, updates: dict) -> Project:
        for field, value in updates.items():
            setattr(project, field, value)
        project.updated_at = datetime.now(UTC)
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        return project

    def soft_delete(self, organization_id: UUID, project_id: UUID, deleted_by_user_id: UUID):
        project = self.get_by_id(organization_id, project_id)
        if project is None:
            return None
        deleted_at = datetime.now(UTC)
        project.status = ProjectStatus.ARCHIVED
        project.deleted_at = deleted_at
        project.updated_at = deleted_at
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        return project
