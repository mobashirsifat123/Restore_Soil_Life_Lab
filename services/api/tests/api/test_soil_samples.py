from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.auth import AuthenticatedUser, get_current_user
from app.api.dependencies.services import get_soil_sample_service
from app.core.config import get_settings
from app.domain.permissions import Permissions
from app.services.soil_sample_service import SoilSampleService


@dataclass(slots=True)
class SoilSampleRecord:
    id: UUID
    organization_id: UUID
    project_id: UUID
    sample_code: str
    current_version_id: UUID
    current_version: int
    name: str | None
    description: str | None
    collected_on: date | None
    location_json: dict
    measurements_json: dict
    metadata_json: dict
    created_by_user_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class FakeSoilSampleRepository:
    def __init__(self) -> None:
        self.projects: dict[UUID, UUID] = {}
        self.deleted_projects: set[UUID] = set()
        self.samples: dict[UUID, SoilSampleRecord] = {}

    def seed_project(self, *, organization_id: UUID, project_id: UUID | None = None) -> UUID:
        resolved_project_id = project_id or uuid4()
        self.projects[resolved_project_id] = organization_id
        return resolved_project_id

    def seed_soil_sample(
        self,
        *,
        organization_id: UUID,
        project_id: UUID,
        sample_code: str,
        name: str | None = None,
        description: str | None = None,
        collected_on: date | None = None,
        location_json: dict | None = None,
        measurements_json: dict | None = None,
        metadata_json: dict | None = None,
        created_by_user_id: UUID | None = None,
    ) -> SoilSampleRecord:
        now = datetime.now(UTC)
        sample = SoilSampleRecord(
            id=uuid4(),
            organization_id=organization_id,
            project_id=project_id,
            sample_code=sample_code,
            current_version_id=uuid4(),
            current_version=1,
            name=name,
            description=description,
            collected_on=collected_on,
            location_json=location_json or {},
            measurements_json=measurements_json or {},
            metadata_json=metadata_json or {},
            created_by_user_id=created_by_user_id or uuid4(),
            created_at=now,
            updated_at=now,
        )
        self.samples[sample.id] = sample
        return sample

    def project_exists(self, organization_id: UUID, project_id: UUID) -> bool:
        return (
            self.projects.get(project_id) == organization_id
            and project_id not in self.deleted_projects
        )

    def sample_code_exists(
        self,
        organization_id: UUID,
        project_id: UUID,
        sample_code: str,
        *,
        exclude_soil_sample_id: UUID | None = None,
    ) -> bool:
        for sample in self.samples.values():
            if sample.organization_id != organization_id or sample.project_id != project_id:
                continue
            if sample.deleted_at is not None:
                continue
            if exclude_soil_sample_id is not None and sample.id == exclude_soil_sample_id:
                continue
            if sample.sample_code == sample_code:
                return True
        return False

    def list_for_project(
        self,
        organization_id: UUID,
        project_id: UUID,
        *,
        limit: int,
        cursor: str | None,
    ):
        items = [
            sample
            for sample in self.samples.values()
            if sample.organization_id == organization_id
            and sample.project_id == project_id
            and sample.deleted_at is None
        ]
        items.sort(key=lambda item: (item.created_at, item.id.hex), reverse=True)
        return items[:limit]

    def get_by_id(self, organization_id: UUID, soil_sample_id: UUID):
        sample = self.samples.get(soil_sample_id)
        if (
            sample is None
            or sample.organization_id != organization_id
            or sample.deleted_at is not None
        ):
            return None
        return sample

    def create(
        self,
        *,
        organization_id: UUID,
        project_id: UUID,
        created_by_user_id: UUID,
        payload,
    ):
        if not self.project_exists(organization_id, project_id):
            raise LookupError("project_not_found")
        return self.seed_soil_sample(
            organization_id=organization_id,
            project_id=project_id,
            sample_code=payload.sample_code,
            name=payload.name,
            description=payload.description,
            collected_on=payload.collected_on,
            location_json=payload.location,
            measurements_json=payload.measurements,
            metadata_json=payload.metadata,
            created_by_user_id=created_by_user_id,
        )

    def update(self, soil_sample: SoilSampleRecord, *, updates: dict, created_by_user_id: UUID):
        for field, value in updates.items():
            setattr(soil_sample, field, value)
        soil_sample.current_version += 1
        soil_sample.current_version_id = uuid4()
        soil_sample.updated_at = datetime.now(UTC)
        self.samples[soil_sample.id] = soil_sample
        return soil_sample

    def soft_delete(self, organization_id: UUID, soil_sample_id: UUID, deleted_by_user_id: UUID):
        sample = self.get_by_id(organization_id, soil_sample_id)
        if sample is None:
            return None
        deleted_at = datetime.now(UTC)
        sample.deleted_at = deleted_at
        sample.updated_at = deleted_at
        self.samples[sample.id] = sample
        return sample


def build_user(*, organization_id: UUID, permissions: set[str]) -> AuthenticatedUser:
    return AuthenticatedUser(
        user_id=UUID("00000000-0000-7000-0000-000000000001"),
        organization_id=organization_id,
        email="scientist@example.com",
        full_name="Sample Scientist",
        roles=["org_admin"],
        permissions=permissions,
    )


@pytest.fixture
def soil_sample_client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/bio_lab")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("DEBUG_AUTH_ENABLED", "true")
    get_settings.cache_clear()
    from app.main import create_application

    repository = FakeSoilSampleRepository()
    organization_id = UUID("00000000-0000-7000-0000-000000000101")
    project_id = repository.seed_project(organization_id=organization_id)
    current_user = build_user(
        organization_id=organization_id,
        permissions={Permissions.SAMPLE_READ, Permissions.SAMPLE_WRITE},
    )

    app = create_application()
    app.dependency_overrides[get_soil_sample_service] = lambda: SoilSampleService(repository)
    app.dependency_overrides[get_current_user] = lambda: current_user

    with TestClient(app) as client:
        yield SimpleNamespace(
            client=client,
            repository=repository,
            current_user=current_user,
            organization_id=organization_id,
            project_id=project_id,
            app=app,
        )

    app.dependency_overrides.clear()
    get_settings.cache_clear()


def test_create_soil_sample_returns_created_sample_with_scientific_fields(
    soil_sample_client,
) -> None:
    response = soil_sample_client.client.post(
        f"/api/v1/projects/{soil_sample_client.project_id}/soil-samples",
        json={
            "sampleCode": "S-001",
            "name": "North Field Composite",
            "description": "Composite root-zone sample",
            "collectedOn": "2026-03-01",
            "location": {
                "siteName": "North Field",
                "latitude": 41.382,
                "longitude": -71.103,
                "depthCm": 15
            },
            "measurements": {
                "ph": 6.4,
                "moisturePercent": 18.5,
                "microbialBiomassMgKg": 182.0
            },
            "metadata": {
                "client": "Acme Farms"
            }
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["projectId"] == str(soil_sample_client.project_id)
    assert payload["sampleCode"] == "S-001"
    assert payload["currentVersion"] == 1
    assert payload["location"]["siteName"] == "North Field"
    assert payload["measurements"]["ph"] == 6.4
    assert payload["measurements"]["microbialBiomassMgKg"] == 182.0


def test_list_soil_samples_returns_project_samples_only(soil_sample_client) -> None:
    retained = soil_sample_client.repository.seed_soil_sample(
        organization_id=soil_sample_client.organization_id,
        project_id=soil_sample_client.project_id,
        sample_code="S-001",
    )
    deleted = soil_sample_client.repository.seed_soil_sample(
        organization_id=soil_sample_client.organization_id,
        project_id=soil_sample_client.project_id,
        sample_code="S-002",
    )
    deleted.deleted_at = datetime.now(UTC)
    other_project_id = soil_sample_client.repository.seed_project(
        organization_id=soil_sample_client.organization_id,
    )
    soil_sample_client.repository.seed_soil_sample(
        organization_id=soil_sample_client.organization_id,
        project_id=other_project_id,
        sample_code="S-003",
    )

    response = soil_sample_client.client.get(
        f"/api/v1/projects/{soil_sample_client.project_id}/soil-samples"
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["nextCursor"] is None
    assert [item["id"] for item in payload["items"]] == [str(retained.id)]


def test_list_soil_samples_returns_project_not_found_for_unknown_project(
    soil_sample_client,
) -> None:
    response = soil_sample_client.client.get(f"/api/v1/projects/{uuid4()}/soil-samples")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "project_not_found"


def test_get_soil_sample_returns_detail(soil_sample_client) -> None:
    sample = soil_sample_client.repository.seed_soil_sample(
        organization_id=soil_sample_client.organization_id,
        project_id=soil_sample_client.project_id,
        sample_code="S-001",
        name="Atlas",
        measurements_json={"ph": 6.8},
    )

    response = soil_sample_client.client.get(f"/api/v1/soil-samples/{sample.id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == str(sample.id)
    assert payload["measurements"]["ph"] == 6.8


def test_update_soil_sample_supports_code_clearable_fields_and_nested_data(
    soil_sample_client,
) -> None:
    sample = soil_sample_client.repository.seed_soil_sample(
        organization_id=soil_sample_client.organization_id,
        project_id=soil_sample_client.project_id,
        sample_code="S-001",
        name="North Field",
        description="Initial note",
        collected_on=date(2026, 3, 1),
        location_json={"siteName": "North Field"},
        measurements_json={"ph": 6.2},
        metadata_json={"phase": "baseline"},
    )

    response = soil_sample_client.client.patch(
        f"/api/v1/soil-samples/{sample.id}",
        json={
            "sampleCode": "S-001A",
            "name": None,
            "description": None,
            "collectedOn": None,
            "location": None,
            "measurements": {
                "ph": 6.7,
                "organicMatterPercent": 4.1
            },
            "metadata": {
                "phase": "follow-up"
            }
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["sampleCode"] == "S-001A"
    assert payload["currentVersion"] == 2
    assert payload["name"] is None
    assert payload["description"] is None
    assert payload["collectedOn"] is None
    assert payload["location"] == {}
    assert payload["measurements"]["organicMatterPercent"] == 4.1
    assert payload["metadata"] == {"phase": "follow-up"}


def test_create_soil_sample_returns_conflict_for_duplicate_sample_code(soil_sample_client) -> None:
    soil_sample_client.repository.seed_soil_sample(
        organization_id=soil_sample_client.organization_id,
        project_id=soil_sample_client.project_id,
        sample_code="S-001",
    )

    response = soil_sample_client.client.post(
        f"/api/v1/projects/{soil_sample_client.project_id}/soil-samples",
        json={"sampleCode": "S-001"},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "soil_sample_conflict"


def test_create_soil_sample_returns_permission_denied_without_write_permission(
    soil_sample_client,
) -> None:
    soil_sample_client.app.dependency_overrides[get_current_user] = lambda: build_user(
        organization_id=soil_sample_client.organization_id,
        permissions={Permissions.SAMPLE_READ},
    )

    response = soil_sample_client.client.post(
        f"/api/v1/projects/{soil_sample_client.project_id}/soil-samples",
        json={"sampleCode": "S-001"},
    )

    assert response.status_code == 403
    payload = response.json()
    assert payload["error"]["code"] == "permission_denied"
    assert payload["error"]["details"]["requiredPermission"] == Permissions.SAMPLE_WRITE


def test_get_soil_sample_returns_not_found_error(soil_sample_client) -> None:
    response = soil_sample_client.client.get(f"/api/v1/soil-samples/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "soil_sample_not_found"


def test_create_soil_sample_returns_validation_error_for_future_date(soil_sample_client) -> None:
    response = soil_sample_client.client.post(
        f"/api/v1/projects/{soil_sample_client.project_id}/soil-samples",
        json={
            "sampleCode": "S-001",
            "collectedOn": (date.today() + timedelta(days=1)).isoformat(),
        },
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "validation_error"
    assert payload["error"]["issues"][0]["field"] == "body.collectedOn"
