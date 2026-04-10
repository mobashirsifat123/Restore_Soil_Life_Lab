from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.auth import AuthenticatedUser, get_current_user
from app.api.dependencies.services import get_project_service
from app.core.config import get_settings
from app.domain.enums import ProjectStatus
from app.domain.permissions import Permissions
from app.services.project_service import ProjectService


@dataclass(slots=True)
class ProjectRecord:
    id: UUID
    organization_id: UUID
    name: str
    slug: str
    description: str | None
    status: ProjectStatus
    metadata_json: dict
    created_by_user_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class FakeProjectRepository:
    def __init__(self) -> None:
        self.items: dict[UUID, ProjectRecord] = {}

    def seed(
        self,
        *,
        organization_id: UUID,
        name: str,
        slug: str,
        description: str | None = None,
        status: ProjectStatus = ProjectStatus.ACTIVE,
        metadata_json: dict | None = None,
        created_by_user_id: UUID | None = None,
    ) -> ProjectRecord:
        now = datetime.now(UTC)
        project = ProjectRecord(
            id=uuid4(),
            organization_id=organization_id,
            name=name,
            slug=slug,
            description=description,
            status=status,
            metadata_json=metadata_json or {},
            created_by_user_id=created_by_user_id or uuid4(),
            created_at=now,
            updated_at=now,
        )
        self.items[project.id] = project
        return project

    def list_for_organization(self, organization_id: UUID, *, limit: int, cursor: str | None):
        projects = [
            item
            for item in self.items.values()
            if item.organization_id == organization_id and item.deleted_at is None
        ]
        projects.sort(key=lambda item: (item.created_at, item.id.hex), reverse=True)
        return projects[:limit]

    def get_by_id(self, organization_id: UUID, project_id: UUID):
        project = self.items.get(project_id)
        if (
            project is None
            or project.organization_id != organization_id
            or project.deleted_at is not None
        ):
            return None
        return project

    def slug_exists(
        self,
        organization_id: UUID,
        slug: str,
        exclude_project_id: UUID | None = None,
    ) -> bool:
        for project in self.items.values():
            if project.organization_id != organization_id or project.deleted_at is not None:
                continue
            if exclude_project_id is not None and project.id == exclude_project_id:
                continue
            if project.slug == slug:
                return True
        return False

    def create(
        self,
        *,
        organization_id: UUID,
        created_by_user_id: UUID,
        name: str,
        slug: str,
        description: str | None,
        metadata_json: dict,
    ):
        if self.slug_exists(organization_id, slug):
            raise AssertionError("ProjectService should resolve a unique slug before create().")
        return self.seed(
            organization_id=organization_id,
            name=name,
            slug=slug,
            description=description,
            metadata_json=metadata_json,
            created_by_user_id=created_by_user_id,
        )

    def update(self, project: ProjectRecord, *, updates: dict):
        for field, value in updates.items():
            setattr(project, field, value)
        project.updated_at = datetime.now(UTC)
        self.items[project.id] = project
        return project

    def soft_delete(self, organization_id: UUID, project_id: UUID, deleted_by_user_id: UUID):
        project = self.get_by_id(organization_id, project_id)
        if project is None:
            return None
        deleted_at = datetime.now(UTC)
        project.status = ProjectStatus.ARCHIVED
        project.deleted_at = deleted_at
        project.updated_at = deleted_at
        self.items[project.id] = project
        return project


def build_user(
    *,
    organization_id: UUID,
    permissions: set[str],
) -> AuthenticatedUser:
    return AuthenticatedUser(
        user_id=UUID("00000000-0000-7000-0000-000000000001"),
        organization_id=organization_id,
        email="scientist@example.com",
        full_name="Project Scientist",
        roles=["org_admin"],
        permissions=permissions,
    )


@pytest.fixture
def project_client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/bio_lab")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("DEBUG_AUTH_ENABLED", "true")
    get_settings.cache_clear()
    from app.main import create_application

    repository = FakeProjectRepository()
    organization_id = UUID("00000000-0000-7000-0000-000000000101")
    current_user = build_user(
        organization_id=organization_id,
        permissions={Permissions.PROJECT_READ, Permissions.PROJECT_WRITE},
    )

    app = create_application()
    app.dependency_overrides[get_project_service] = lambda: ProjectService(repository)
    app.dependency_overrides[get_current_user] = lambda: current_user

    with TestClient(app) as client:
        yield SimpleNamespace(
            client=client,
            repository=repository,
            current_user=current_user,
            organization_id=organization_id,
            app=app,
        )

    app.dependency_overrides.clear()
    get_settings.cache_clear()


def test_create_project_returns_created_project(project_client) -> None:
    response = project_client.client.post(
        "/api/v1/projects",
        json={
            "name": "Northern Regeneration Pilot",
            "description": "Baseline client workspace",
            "metadata": {"client": "Acme Farms"},
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "Northern Regeneration Pilot"
    assert payload["slug"] == "northern-regeneration-pilot"
    assert payload["status"] == "active"
    assert payload["organizationId"] == str(project_client.organization_id)
    assert payload["metadata"] == {"client": "Acme Farms"}


def test_create_project_generates_incremented_slug_when_name_conflicts(project_client) -> None:
    project_client.repository.seed(
        organization_id=project_client.organization_id,
        name="Northern Regeneration Pilot",
        slug="northern-regeneration-pilot",
        created_by_user_id=project_client.current_user.user_id,
    )

    response = project_client.client.post(
        "/api/v1/projects",
        json={"name": "Northern Regeneration Pilot", "metadata": {}},
    )

    assert response.status_code == 201
    assert response.json()["slug"] == "northern-regeneration-pilot-2"


def test_list_projects_returns_only_active_projects_for_current_organization(
    project_client,
) -> None:
    retained = project_client.repository.seed(
        organization_id=project_client.organization_id,
        name="Retained",
        slug="retained",
    )
    deleted = project_client.repository.seed(
        organization_id=project_client.organization_id,
        name="Deleted",
        slug="deleted",
    )
    deleted.deleted_at = datetime.now(UTC)
    project_client.repository.seed(
        organization_id=uuid4(),
        name="Other Organization",
        slug="other-organization",
    )

    response = project_client.client.get("/api/v1/projects")

    assert response.status_code == 200
    payload = response.json()
    assert payload["nextCursor"] is None
    assert [item["id"] for item in payload["items"]] == [str(retained.id)]


def test_get_project_detail_returns_single_project(project_client) -> None:
    project = project_client.repository.seed(
        organization_id=project_client.organization_id,
        name="Project Atlas",
        slug="project-atlas",
        description="Detailed project view",
        metadata_json={"phase": "baseline"},
    )

    response = project_client.client.get(f"/api/v1/projects/{project.id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == str(project.id)
    assert payload["description"] == "Detailed project view"
    assert payload["metadata"] == {"phase": "baseline"}


def test_update_project_supports_slug_description_status_and_metadata_changes(
    project_client,
) -> None:
    existing = project_client.repository.seed(
        organization_id=project_client.organization_id,
        name="Northern Regeneration Pilot",
        slug="northern-regeneration-pilot",
        description="Original description",
        metadata_json={"phase": "baseline"},
    )
    project_client.repository.seed(
        organization_id=project_client.organization_id,
        name="Existing Slug Owner",
        slug="renamed-project",
    )

    response = project_client.client.patch(
        f"/api/v1/projects/{existing.id}",
        json={
            "name": "Renamed Project",
            "slug": "renamed-project",
            "description": None,
            "status": "archived",
            "metadata": {"phase": "archived"},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "Renamed Project"
    assert payload["slug"] == "renamed-project-2"
    assert payload["description"] is None
    assert payload["status"] == "archived"
    assert payload["metadata"] == {"phase": "archived"}


def test_delete_project_soft_deletes_and_archives_record(project_client) -> None:
    project = project_client.repository.seed(
        organization_id=project_client.organization_id,
        name="Archive Me",
        slug="archive-me",
    )

    response = project_client.client.delete(f"/api/v1/projects/{project.id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == str(project.id)
    assert payload["deleted"] is True
    assert payload["deletedAt"] is not None
    assert project_client.repository.items[project.id].deleted_at is not None
    assert project_client.repository.items[project.id].status == ProjectStatus.ARCHIVED


def test_create_project_returns_permission_denied_error_when_user_lacks_write_access(
    project_client,
) -> None:
    project_client.app.dependency_overrides[get_current_user] = lambda: build_user(
        organization_id=project_client.organization_id,
        permissions={Permissions.PROJECT_READ},
    )

    response = project_client.client.post(
        "/api/v1/projects",
        json={"name": "Forbidden Project", "metadata": {}},
    )

    assert response.status_code == 403
    payload = response.json()
    assert payload["error"]["code"] == "permission_denied"
    assert payload["error"]["details"]["requiredPermission"] == Permissions.PROJECT_WRITE


def test_get_project_returns_not_found_error(project_client) -> None:
    response = project_client.client.get(f"/api/v1/projects/{uuid4()}")

    assert response.status_code == 404
    payload = response.json()
    assert payload["error"]["code"] == "project_not_found"
    assert payload["error"]["message"] == "Project not found."


def test_create_project_returns_validation_error_envelope(project_client) -> None:
    response = project_client.client.post(
        "/api/v1/projects",
        json={"name": "ab", "metadata": {}},
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "validation_error"
    assert payload["error"]["issues"][0]["field"] == "body.name"
