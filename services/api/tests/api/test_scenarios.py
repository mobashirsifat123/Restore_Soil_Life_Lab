from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.auth import AuthenticatedUser, get_current_user
from app.api.dependencies.services import get_scenario_service
from app.core.config import get_settings
from app.domain.enums import ScenarioStatus
from app.domain.permissions import Permissions
from app.schemas.scenario import (
    ScenarioSoilSampleReference,
    build_stored_scenario_config,
)
from app.services.scenario_service import ScenarioService


@dataclass(slots=True)
class FakeDefinition:
    id: UUID
    stable_key: UUID
    version: int


@dataclass(slots=True)
class FakeSoilSample:
    organization_id: UUID
    project_id: UUID
    current_version_id: UUID
    current_version: int


@dataclass(slots=True)
class ScenarioRecord:
    id: UUID
    organization_id: UUID
    project_id: UUID
    stable_key: UUID
    version: int
    name: str
    description: str | None
    status: ScenarioStatus
    soil_sample_id: UUID
    soil_sample_version_id: UUID
    food_web_definition_id: UUID
    parameter_set_id: UUID
    scenario_config_json: dict
    created_at: datetime
    updated_at: datetime
    food_web_definition: FakeDefinition
    parameter_set: FakeDefinition
    deleted_at: datetime | None = None


class FakeScenarioRepository:
    def __init__(self) -> None:
        self.projects: dict[UUID, UUID] = {}
        self.soil_samples: dict[UUID, FakeSoilSample] = {}
        self.scenarios: dict[UUID, ScenarioRecord] = {}

    def seed_project(self, *, organization_id: UUID, project_id: UUID | None = None) -> UUID:
        resolved_project_id = project_id or uuid4()
        self.projects[resolved_project_id] = organization_id
        return resolved_project_id

    def seed_soil_sample(
        self,
        *,
        organization_id: UUID,
        project_id: UUID,
        soil_sample_id: UUID | None = None,
    ) -> UUID:
        resolved_soil_sample_id = soil_sample_id or uuid4()
        self.soil_samples[resolved_soil_sample_id] = FakeSoilSample(
            organization_id=organization_id,
            project_id=project_id,
            current_version_id=uuid4(),
            current_version=1,
        )
        return resolved_soil_sample_id

    def seed_scenario(
        self,
        *,
        organization_id: UUID,
        project_id: UUID,
        soil_sample_id: UUID,
        name: str = "Baseline scenario",
        description: str | None = "Scenario description",
        status: ScenarioStatus = ScenarioStatus.ACTIVE,
        scenario_config_json: dict | None = None,
        version: int = 1,
        soil_sample_version_id: UUID | None = None,
    ) -> ScenarioRecord:
        now = datetime.now(UTC)
        food_web_definition = FakeDefinition(id=uuid4(), stable_key=uuid4(), version=1)
        parameter_set = FakeDefinition(id=uuid4(), stable_key=uuid4(), version=1)
        record = ScenarioRecord(
            id=uuid4(),
            organization_id=organization_id,
            project_id=project_id,
            stable_key=uuid4(),
            version=version,
            name=name,
            description=description,
            status=status,
            soil_sample_id=soil_sample_id,
            soil_sample_version_id=soil_sample_version_id
            or self.soil_samples[soil_sample_id].current_version_id,
            food_web_definition_id=food_web_definition.id,
            parameter_set_id=parameter_set.id,
            scenario_config_json=scenario_config_json or {},
            created_at=now,
            updated_at=now,
            food_web_definition=food_web_definition,
            parameter_set=parameter_set,
        )
        self.scenarios[record.id] = record
        return record

    def project_exists(self, organization_id: UUID, project_id: UUID) -> bool:
        return self.projects.get(project_id) == organization_id

    def soil_samples_exist(
        self,
        organization_id: UUID,
        project_id: UUID,
        soil_sample_ids: list[UUID],
    ) -> bool:
        if not soil_sample_ids:
            return False
        for soil_sample_id in soil_sample_ids:
            soil_sample = self.soil_samples.get(soil_sample_id)
            if soil_sample is None:
                return False
            if (
                soil_sample.organization_id != organization_id
                or soil_sample.project_id != project_id
            ):
                return False
        return True

    def resolve_soil_sample_references(
        self,
        organization_id: UUID,
        project_id: UUID,
        references: list[dict],
    ) -> list[dict]:
        normalized_references: list[dict] = []
        for reference in references:
            soil_sample = self.soil_samples.get(reference["soil_sample_id"])
            if soil_sample is None:
                raise LookupError("soil_sample_not_found")
            if (
                soil_sample.organization_id != organization_id
                or soil_sample.project_id != project_id
            ):
                raise LookupError("soil_sample_not_found")
            version_id = reference.get("soil_sample_version_id") or soil_sample.current_version_id
            if version_id != soil_sample.current_version_id:
                raise LookupError("soil_sample_version_not_found")
            normalized_references.append(
                {
                    "soil_sample_id": reference["soil_sample_id"],
                    "soil_sample_version_id": version_id,
                    "role": reference.get("role"),
                    "weight": reference.get("weight"),
                    "metadata": reference.get("metadata") or {},
                }
            )
        return normalized_references

    def list_for_project(
        self,
        organization_id: UUID,
        project_id: UUID,
        *,
        limit: int,
        cursor: str | None,
    ):
        items = [
            scenario
            for scenario in self.scenarios.values()
            if scenario.organization_id == organization_id
            and scenario.project_id == project_id
            and scenario.deleted_at is None
        ]
        items.sort(key=lambda item: (item.created_at, item.id.hex), reverse=True)
        return items[:limit]

    def get_by_id(self, organization_id: UUID, scenario_id: UUID):
        scenario = self.scenarios.get(scenario_id)
        if (
            scenario is None
            or scenario.organization_id != organization_id
            or scenario.deleted_at is not None
        ):
            return None
        return scenario

    def create(self, organization_id: UUID, project_id: UUID, created_by_user_id: UUID, payload):
        if not self.project_exists(organization_id, project_id):
            raise LookupError("project_not_found")

        return self.seed_scenario(
            organization_id=organization_id,
            project_id=project_id,
            soil_sample_id=payload.soil_sample_id,
            soil_sample_version_id=payload.soil_sample_version_id,
            name=payload.name,
            description=payload.description,
            scenario_config_json=payload.scenario_config,
        )

    def update(
        self,
        scenario: ScenarioRecord,
        *,
        payload,
        updated_by_user_id: UUID,
        increment_version: bool,
    ):
        if payload.food_web is not None:
            scenario.food_web_definition = FakeDefinition(
                id=uuid4(),
                stable_key=scenario.food_web_definition.stable_key,
                version=scenario.food_web_definition.version + 1,
            )
            scenario.food_web_definition_id = scenario.food_web_definition.id

        if payload.parameter_set is not None:
            scenario.parameter_set = FakeDefinition(
                id=uuid4(),
                stable_key=scenario.parameter_set.stable_key,
                version=scenario.parameter_set.version + 1,
            )
            scenario.parameter_set_id = scenario.parameter_set.id

        if payload.name is not None:
            scenario.name = payload.name
        if "description" in payload.model_fields_set:
            scenario.description = payload.description
        if payload.status is not None:
            scenario.status = payload.status
        if payload.soil_sample_id is not None:
            scenario.soil_sample_id = payload.soil_sample_id
        if payload.soil_sample_version_id is not None:
            scenario.soil_sample_version_id = payload.soil_sample_version_id
        if payload.scenario_config is not None:
            scenario.scenario_config_json = payload.scenario_config
        if increment_version:
            scenario.version += 1

        scenario.updated_at = datetime.now(UTC)
        self.scenarios[scenario.id] = scenario
        return scenario

    def soft_delete(self, organization_id: UUID, scenario_id: UUID, deleted_by_user_id: UUID):
        scenario = self.get_by_id(organization_id, scenario_id)
        if scenario is None:
            return None
        deleted_at = datetime.now(UTC)
        scenario.status = ScenarioStatus.ARCHIVED
        scenario.deleted_at = deleted_at
        scenario.updated_at = deleted_at
        self.scenarios[scenario.id] = scenario
        return scenario


def build_user(*, organization_id: UUID, permissions: set[str]) -> AuthenticatedUser:
    return AuthenticatedUser(
        user_id=UUID("00000000-0000-7000-0000-000000000001"),
        organization_id=organization_id,
        email="scientist@example.com",
        full_name="Scenario Scientist",
        roles=["org_admin"],
        permissions=permissions,
    )


@pytest.fixture
def scenario_client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/bio_lab")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("DEBUG_AUTH_ENABLED", "true")
    get_settings.cache_clear()
    from app.main import create_application

    repository = FakeScenarioRepository()
    organization_id = UUID("00000000-0000-7000-0000-000000000101")
    project_id = repository.seed_project(organization_id=organization_id)
    primary_soil_sample_id = repository.seed_soil_sample(
        organization_id=organization_id,
        project_id=project_id,
    )
    secondary_soil_sample_id = repository.seed_soil_sample(
        organization_id=organization_id,
        project_id=project_id,
    )
    current_user = build_user(
        organization_id=organization_id,
        permissions={Permissions.SCENARIO_READ, Permissions.SCENARIO_WRITE},
    )

    app = create_application()
    app.dependency_overrides[get_scenario_service] = lambda: ScenarioService(repository)
    app.dependency_overrides[get_current_user] = lambda: current_user

    with TestClient(app) as client:
        yield SimpleNamespace(
            client=client,
            repository=repository,
            current_user=current_user,
            organization_id=organization_id,
            project_id=project_id,
            primary_soil_sample_id=primary_soil_sample_id,
            secondary_soil_sample_id=secondary_soil_sample_id,
            app=app,
        )

    app.dependency_overrides.clear()
    get_settings.cache_clear()


def test_create_scenario_returns_created_scenario_with_sample_references(scenario_client) -> None:
    response = scenario_client.client.post(
        f"/api/v1/projects/{scenario_client.project_id}/scenarios",
        json={
            "name": "Baseline scenario",
            "description": "Initial model calibration",
            "soilSampleId": str(scenario_client.primary_soil_sample_id),
            "soilSampleReferences": [
                {
                    "soilSampleId": str(scenario_client.secondary_soil_sample_id),
                    "role": "comparison",
                    "weight": 0.5
                }
            ],
            "foodWeb": {
                "name": "Baseline food web",
                "nodes": [
                    {
                        "key": "detritus",
                        "label": "Detritus",
                        "trophicGroup": "detritus",
                        "biomassCarbon": 12.0,
                        "isDetritus": True,
                        "metadata": {}
                    }
                ],
                "links": [],
                "metadata": {}
            },
            "parameterSet": {
                "name": "Baseline parameters",
                "parameters": {
                    "respirationRate": 0.12
                },
                "metadata": {}
            },
            "scenarioConfig": {
                "parameterization": {
                    "respirationMultiplier": 1.1
                },
                "executionDefaults": {
                    "requestedModules": ["flux", "stability"]
                },
                "horizonDays": 30
            }
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["projectId"] == str(scenario_client.project_id)
    assert payload["soilSampleId"] == str(scenario_client.primary_soil_sample_id)
    assert payload["soilSampleVersionId"] == str(
        scenario_client.repository.soil_samples[
            scenario_client.primary_soil_sample_id
        ].current_version_id
    )
    assert len(payload["soilSampleReferences"]) == 2
    assert payload["soilSampleReferences"][0]["soilSampleId"] == str(
        scenario_client.primary_soil_sample_id
    )
    assert payload["soilSampleReferences"][0]["soilSampleVersionId"] == str(
        scenario_client.repository.soil_samples[
            scenario_client.primary_soil_sample_id
        ].current_version_id
    )
    assert payload["scenarioConfig"]["horizonDays"] == 30
    assert payload["status"] == "active"


def test_list_scenarios_returns_project_scenarios_only(scenario_client) -> None:
    retained = scenario_client.repository.seed_scenario(
        organization_id=scenario_client.organization_id,
        project_id=scenario_client.project_id,
        soil_sample_id=scenario_client.primary_soil_sample_id,
    )
    deleted = scenario_client.repository.seed_scenario(
        organization_id=scenario_client.organization_id,
        project_id=scenario_client.project_id,
        soil_sample_id=scenario_client.primary_soil_sample_id,
    )
    deleted.deleted_at = datetime.now(UTC)
    other_project_id = scenario_client.repository.seed_project(
        organization_id=scenario_client.organization_id,
    )
    other_soil_sample_id = scenario_client.repository.seed_soil_sample(
        organization_id=scenario_client.organization_id,
        project_id=other_project_id,
    )
    scenario_client.repository.seed_scenario(
        organization_id=scenario_client.organization_id,
        project_id=other_project_id,
        soil_sample_id=other_soil_sample_id,
    )

    response = scenario_client.client.get(
        f"/api/v1/projects/{scenario_client.project_id}/scenarios"
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["nextCursor"] is None
    assert [item["id"] for item in payload["items"]] == [str(retained.id)]


def test_get_scenario_returns_detail(scenario_client) -> None:
    scenario = scenario_client.repository.seed_scenario(
        organization_id=scenario_client.organization_id,
        project_id=scenario_client.project_id,
        soil_sample_id=scenario_client.primary_soil_sample_id,
        scenario_config_json=build_stored_scenario_config(
            scenario_config={"horizonDays": 30},
            soil_sample_references=[
                ScenarioSoilSampleReference(
                    soil_sample_id=scenario_client.primary_soil_sample_id,
                    soil_sample_version_id=(
                        scenario_client.repository.soil_samples[
                            scenario_client.primary_soil_sample_id
                        ].current_version_id
                    ),
                )
            ],
            primary_soil_sample_id=scenario_client.primary_soil_sample_id,
            primary_soil_sample_version_id=(
                scenario_client.repository.soil_samples[
                    scenario_client.primary_soil_sample_id
                ].current_version_id
            ),
        ),
    )

    response = scenario_client.client.get(f"/api/v1/scenarios/{scenario.id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == str(scenario.id)
    assert payload["soilSampleVersionId"] == str(scenario.soil_sample_version_id)
    assert payload["scenarioConfig"]["horizonDays"] == 30


def test_update_scenario_supports_sample_refs_status_and_config_version_bump(
    scenario_client,
) -> None:
    scenario = scenario_client.repository.seed_scenario(
        organization_id=scenario_client.organization_id,
        project_id=scenario_client.project_id,
        soil_sample_id=scenario_client.primary_soil_sample_id,
        scenario_config_json=build_stored_scenario_config(
            scenario_config={"horizonDays": 30},
            soil_sample_references=[
                ScenarioSoilSampleReference(
                    soil_sample_id=scenario_client.primary_soil_sample_id,
                    soil_sample_version_id=(
                        scenario_client.repository.soil_samples[
                            scenario_client.primary_soil_sample_id
                        ].current_version_id
                    ),
                )
            ],
            primary_soil_sample_id=scenario_client.primary_soil_sample_id,
            primary_soil_sample_version_id=(
                scenario_client.repository.soil_samples[
                    scenario_client.primary_soil_sample_id
                ].current_version_id
            ),
        ),
    )

    response = scenario_client.client.patch(
        f"/api/v1/scenarios/{scenario.id}",
        json={
            "name": "Updated scenario",
            "description": None,
            "status": "archived",
            "soilSampleReferences": [
                {
                    "soilSampleId": str(scenario_client.secondary_soil_sample_id),
                    "role": "primary"
                }
            ],
            "scenarioConfig": {
                "parameterization": {
                    "respirationMultiplier": 1.25
                },
                "executionDefaults": {
                    "requestedModules": ["flux"]
                }
            }
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "Updated scenario"
    assert payload["description"] is None
    assert payload["status"] == "archived"
    assert payload["soilSampleId"] == str(scenario_client.secondary_soil_sample_id)
    assert payload["soilSampleVersionId"] == str(
        scenario_client.repository.soil_samples[
            scenario_client.secondary_soil_sample_id
        ].current_version_id
    )
    assert payload["soilSampleReferences"][0]["soilSampleId"] == str(
        scenario_client.secondary_soil_sample_id
    )
    assert payload["soilSampleReferences"][0]["soilSampleVersionId"] == str(
        scenario_client.repository.soil_samples[
            scenario_client.secondary_soil_sample_id
        ].current_version_id
    )
    assert payload["scenarioConfig"]["parameterization"]["respirationMultiplier"] == 1.25
    assert payload["version"] == 2


def test_delete_scenario_soft_deletes_and_archives(scenario_client) -> None:
    scenario = scenario_client.repository.seed_scenario(
        organization_id=scenario_client.organization_id,
        project_id=scenario_client.project_id,
        soil_sample_id=scenario_client.primary_soil_sample_id,
    )

    response = scenario_client.client.delete(f"/api/v1/scenarios/{scenario.id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == str(scenario.id)
    assert payload["deleted"] is True
    assert scenario_client.repository.scenarios[scenario.id].deleted_at is not None
    assert scenario_client.repository.scenarios[scenario.id].status == ScenarioStatus.ARCHIVED


def test_create_scenario_returns_not_found_for_unknown_soil_sample(scenario_client) -> None:
    response = scenario_client.client.post(
        f"/api/v1/projects/{scenario_client.project_id}/scenarios",
        json={
            "name": "Broken scenario",
            "soilSampleId": str(uuid4()),
            "foodWeb": {
                "name": "Baseline food web",
                "nodes": [
                    {
                        "key": "detritus",
                        "label": "Detritus",
                        "trophicGroup": "detritus",
                        "biomassCarbon": 12.0,
                        "isDetritus": True
                    }
                ],
                "links": []
            },
            "parameterSet": {
                "name": "Baseline parameters",
                "parameters": {}
            }
        },
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "soil_sample_not_found"


def test_create_scenario_returns_permission_denied_without_write_access(scenario_client) -> None:
    scenario_client.app.dependency_overrides[get_current_user] = lambda: build_user(
        organization_id=scenario_client.organization_id,
        permissions={Permissions.SCENARIO_READ},
    )

    response = scenario_client.client.post(
        f"/api/v1/projects/{scenario_client.project_id}/scenarios",
        json={
            "name": "Forbidden scenario",
            "soilSampleId": str(scenario_client.primary_soil_sample_id),
            "foodWeb": {
                "name": "Baseline food web",
                "nodes": [
                    {
                        "key": "detritus",
                        "label": "Detritus",
                        "trophicGroup": "detritus",
                        "biomassCarbon": 12.0,
                        "isDetritus": True
                    }
                ],
                "links": []
            },
            "parameterSet": {
                "name": "Baseline parameters",
                "parameters": {}
            }
        },
    )

    assert response.status_code == 403
    payload = response.json()
    assert payload["error"]["code"] == "permission_denied"
    assert payload["error"]["details"]["requiredPermission"] == Permissions.SCENARIO_WRITE


def test_get_scenario_returns_not_found_error(scenario_client) -> None:
    response = scenario_client.client.get(f"/api/v1/scenarios/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "scenario_not_found"


def test_create_scenario_returns_validation_error_for_duplicate_sample_refs(
    scenario_client,
) -> None:
    response = scenario_client.client.post(
        f"/api/v1/projects/{scenario_client.project_id}/scenarios",
        json={
            "name": "Invalid scenario",
            "soilSampleReferences": [
                {"soilSampleId": str(scenario_client.primary_soil_sample_id)},
                {"soilSampleId": str(scenario_client.primary_soil_sample_id)}
            ],
            "foodWeb": {
                "name": "Baseline food web",
                "nodes": [
                    {
                        "key": "detritus",
                        "label": "Detritus",
                        "trophicGroup": "detritus",
                        "biomassCarbon": 12.0,
                        "isDetritus": True
                    }
                ],
                "links": []
            },
            "parameterSet": {
                "name": "Baseline parameters",
                "parameters": {}
            }
        },
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "validation_error"
    assert payload["error"]["issues"][0]["field"] == "body"
