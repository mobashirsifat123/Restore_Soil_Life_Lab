from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.auth import AuthenticatedUser, get_current_user
from app.api.dependencies.services import get_run_service
from app.core.config import get_settings
from app.domain.enums import ArtifactType, RunStatus
from app.domain.permissions import Permissions
from app.services.run_service import RunService


@dataclass(slots=True)
class ArtifactRecord:
    id: UUID
    artifact_type: ArtifactType
    label: str
    content_type: str
    storage_key: str
    byte_size: int | None
    checksum_sha256: str | None
    metadata_json: dict
    created_at: datetime


@dataclass(slots=True)
class RunRecord:
    id: UUID
    organization_id: UUID
    project_id: UUID
    scenario_id: UUID
    status: RunStatus
    engine_name: str
    engine_version: str
    input_schema_version: str
    input_hash: str
    execution_options_json: dict
    input_snapshot_json: dict
    queue_name: str
    idempotency_key: str | None
    result_hash: str | None
    result_summary_json: dict | None
    queued_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    canceled_at: datetime | None
    failure_code: str | None
    failure_message: str | None
    created_at: datetime
    updated_at: datetime


class FakeRunRepository:
    def __init__(self) -> None:
        self.scenarios: dict[UUID, object] = {}
        self.runs: dict[UUID, RunRecord] = {}
        self.artifacts_by_run_id: dict[UUID, list[ArtifactRecord]] = {}

    def seed_scenario(
        self,
        *,
        organization_id: UUID,
        project_id: UUID,
        scenario_id: UUID | None = None,
        parameter_set_version: int = 3,
        soil_sample_version: int = 2,
    ):
        resolved_scenario_id = scenario_id or uuid4()
        soil_sample_version_id = uuid4()
        scenario = SimpleNamespace(
            id=resolved_scenario_id,
            organization_id=organization_id,
            project_id=project_id,
            stable_key=uuid4(),
            version=2,
            name="Baseline scenario",
            scenario_config_json={"horizonDays": 30},
            soil_sample_id=uuid4(),
            soil_sample_version_id=soil_sample_version_id,
            soil_sample=SimpleNamespace(
                id=uuid4(),
                sample_code="SAMPLE-001",
                measurements_json={"ph": 6.4},
                location_json={"siteName": "North Field"},
                metadata_json={},
            ),
            soil_sample_version=SimpleNamespace(
                id=soil_sample_version_id,
                version=soil_sample_version,
                sample_code="SAMPLE-001",
                measurements_json={"ph": 6.4},
                location_json={"siteName": "North Field"},
                metadata_json={},
            ),
            food_web_definition=SimpleNamespace(
                id=uuid4(),
                stable_key=uuid4(),
                version=5,
                nodes_json=[
                    {
                        "key": "detritus",
                        "label": "Detritus",
                        "trophicGroup": "detritus",
                        "biomassCarbon": 12.0,
                        "isDetritus": True,
                        "metadata": {},
                    }
                ],
                links_json=[],
                metadata_json={},
            ),
            parameter_set=SimpleNamespace(
                id=uuid4(),
                stable_key=uuid4(),
                version=parameter_set_version,
                name="Baseline parameters",
                parameters_json={"respirationRate": 0.12},
                metadata_json={},
            ),
            project=SimpleNamespace(id=project_id),
        )
        self.scenarios[resolved_scenario_id] = scenario
        return scenario

    def seed_run(
        self,
        *,
        organization_id: UUID,
        project_id: UUID,
        scenario_id: UUID,
        status: RunStatus,
        input_snapshot_json: dict,
        engine_version: str = "0.1.0",
        result_hash: str | None = None,
        result_summary_json: dict | None = None,
        failure_code: str | None = None,
        failure_message: str | None = None,
    ) -> RunRecord:
        now = datetime.now(UTC)
        run = RunRecord(
            id=uuid4(),
            organization_id=organization_id,
            project_id=project_id,
            scenario_id=scenario_id,
            status=status,
            engine_name="soil-engine",
            engine_version=engine_version,
            input_schema_version="1.0.0",
            input_hash="input-hash",
            execution_options_json={},
            input_snapshot_json=input_snapshot_json,
            queue_name="jobs:simulation",
            idempotency_key=None,
            result_hash=result_hash,
            result_summary_json=result_summary_json,
            queued_at=now,
            started_at=(
                now
                if status in {RunStatus.RUNNING, RunStatus.SUCCEEDED, RunStatus.FAILED}
                else None
            ),
            completed_at=now if status in {RunStatus.SUCCEEDED, RunStatus.FAILED} else None,
            canceled_at=None,
            failure_code=failure_code,
            failure_message=failure_message,
            created_at=now,
            updated_at=now,
        )
        self.runs[run.id] = run
        return run

    def find_by_idempotency_key(
        self,
        *,
        organization_id: UUID,
        scenario_id: UUID,
        idempotency_key: str | None,
    ):
        if not idempotency_key:
            return None
        for run in self.runs.values():
            if (
                run.organization_id == organization_id
                and run.scenario_id == scenario_id
                and run.idempotency_key == idempotency_key
            ):
                return run
        return None

    def get_scenario_bundle(self, organization_id: UUID, scenario_id: UUID):
        scenario = self.scenarios.get(scenario_id)
        if scenario is None or scenario.organization_id != organization_id:
            return None
        return scenario

    def create(
        self,
        *,
        organization_id: UUID,
        project_id: UUID,
        scenario_id: UUID,
        created_by_user_id: UUID,
        engine_name: str,
        engine_version: str,
        input_schema_version: str,
        input_hash: str,
        execution_options_json: dict,
        input_snapshot_json: dict,
        queue_name: str,
        idempotency_key: str | None,
    ) -> RunRecord:
        now = datetime.now(UTC)
        run = RunRecord(
            id=uuid4(),
            organization_id=organization_id,
            project_id=project_id,
            scenario_id=scenario_id,
            status=RunStatus.QUEUED,
            engine_name=engine_name,
            engine_version=engine_version,
            input_schema_version=input_schema_version,
            input_hash=input_hash,
            execution_options_json=execution_options_json,
            input_snapshot_json=input_snapshot_json,
            queue_name=queue_name,
            idempotency_key=idempotency_key,
            result_hash=None,
            result_summary_json=None,
            queued_at=now,
            started_at=None,
            completed_at=None,
            canceled_at=None,
            failure_code=None,
            failure_message=None,
            created_at=now,
            updated_at=now,
        )
        self.runs[run.id] = run
        return run

    def mark_enqueue_failed(self, run: RunRecord, *, message: str) -> RunRecord:
        failed_at = datetime.now(UTC)
        run.status = RunStatus.FAILED
        run.failure_code = "queue_publish_failed"
        run.failure_message = message
        run.completed_at = failed_at
        run.updated_at = failed_at
        self.runs[run.id] = run
        return run

    def get_by_id(self, organization_id: UUID, run_id: UUID):
        run = self.runs.get(run_id)
        if run is None or run.organization_id != organization_id:
            return None
        return run

    def list_artifacts(self, organization_id: UUID, run_id: UUID):
        run = self.runs.get(run_id)
        if run is None or run.organization_id != organization_id:
            return []
        return list(self.artifacts_by_run_id.get(run_id, []))


class FakePublisher:
    def __init__(self) -> None:
        self.published = []
        self.failure_message: str | None = None

    def publish(self, envelope) -> None:
        if self.failure_message is not None:
            raise RuntimeError(self.failure_message)
        self.published.append(envelope)


def build_user(*, organization_id: UUID, permissions: set[str]) -> AuthenticatedUser:
    return AuthenticatedUser(
        user_id=UUID("00000000-0000-7000-0000-000000000001"),
        organization_id=organization_id,
        email="scientist@example.com",
        full_name="Run Scientist",
        roles=["org_admin"],
        permissions=permissions,
    )


@pytest.fixture
def run_client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/bio_lab")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("DEBUG_AUTH_ENABLED", "true")
    get_settings.cache_clear()
    from app.main import create_application

    repository = FakeRunRepository()
    publisher = FakePublisher()
    organization_id = UUID("00000000-0000-7000-0000-000000000101")
    project_id = uuid4()
    scenario = repository.seed_scenario(
        organization_id=organization_id,
        project_id=project_id,
    )
    current_user = build_user(
        organization_id=organization_id,
        permissions={Permissions.RUN_READ, Permissions.RUN_SUBMIT},
    )

    app = create_application()
    app.dependency_overrides[get_run_service] = lambda: RunService(repository, publisher)
    app.dependency_overrides[get_current_user] = lambda: current_user

    with TestClient(app) as client:
        yield SimpleNamespace(
            client=client,
            repository=repository,
            publisher=publisher,
            current_user=current_user,
            organization_id=organization_id,
            project_id=project_id,
            scenario=scenario,
            app=app,
        )

    app.dependency_overrides.clear()
    get_settings.cache_clear()


def test_submit_run_creates_record_persists_snapshot_and_enqueues_job(run_client) -> None:
    response = run_client.client.post(
        "/api/v1/runs",
        json={
            "scenarioId": str(run_client.scenario.id),
            "idempotencyKey": "baseline-run-001",
            "executionOptions": {
                "requestedModules": ["flux", "stability"],
                "timeoutSeconds": 300,
            },
        },
    )

    assert response.status_code == 202
    payload = response.json()
    assert payload["scenarioId"] == str(run_client.scenario.id)
    assert payload["status"] == "queued"
    assert payload["engineVersion"] == "0.1.0"
    assert payload["parameterSetVersion"] == 3
    expected_soil_sample_version = run_client.scenario.soil_sample_version.version
    assert payload["soilSampleVersion"] == expected_soil_sample_version

    created_run = run_client.repository.runs[UUID(payload["id"])]
    assert created_run.input_snapshot_json["parameterSet"]["version"] == 3
    assert created_run.input_snapshot_json["soilSample"]["version"] == expected_soil_sample_version
    assert "sampleVersionId" not in created_run.input_snapshot_json["soilSample"]
    assert (
        created_run.input_snapshot_json["scenario"]["configuration"]["primarySoilSampleVersionId"]
        == str(run_client.scenario.soil_sample_version.id)
    )
    assert created_run.input_snapshot_json["scenario"]["scenarioId"] == str(run_client.scenario.id)

    assert len(run_client.publisher.published) == 1
    envelope = run_client.publisher.published[0]
    assert envelope.payload["job_type"] == "simulation.run.execute"
    assert envelope.payload["run_id"] == payload["id"]
    assert envelope.payload["parameter_set_version"] == 3
    assert envelope.payload["soil_sample_version"] == expected_soil_sample_version
    assert envelope.payload["timeout_seconds"] == 300


def test_submit_run_returns_existing_run_for_same_idempotency_key(run_client) -> None:
    first_response = run_client.client.post(
        "/api/v1/runs",
        json={
            "scenarioId": str(run_client.scenario.id),
            "idempotencyKey": "dedupe-1",
        },
    )
    second_response = run_client.client.post(
        "/api/v1/runs",
        json={
            "scenarioId": str(run_client.scenario.id),
            "idempotencyKey": "dedupe-1",
        },
    )

    assert first_response.status_code == 202
    assert second_response.status_code == 202
    assert second_response.json()["id"] == first_response.json()["id"]
    assert len(run_client.publisher.published) == 1


def test_submit_run_returns_not_found_for_unknown_scenario(run_client) -> None:
    response = run_client.client.post(
        "/api/v1/runs",
        json={"scenarioId": str(uuid4())},
    )

    assert response.status_code == 404
    payload = response.json()
    assert payload["error"]["code"] == "scenario_not_found"
    assert payload["error"]["message"] == "Scenario not found."


def test_submit_run_returns_structured_error_when_queue_publish_fails(run_client) -> None:
    run_client.publisher.failure_message = "redis unavailable"

    response = run_client.client.post(
        "/api/v1/runs",
        json={"scenarioId": str(run_client.scenario.id)},
    )

    assert response.status_code == 503
    payload = response.json()
    assert payload["error"]["code"] == "run_enqueue_failed"
    run_id = UUID(payload["error"]["details"]["runId"])
    failed_run = run_client.repository.runs[run_id]
    assert failed_run.status == RunStatus.FAILED
    assert failed_run.failure_code == "queue_publish_failed"
    assert failed_run.failure_message == "redis unavailable"


def test_get_run_status_returns_current_lifecycle_state(run_client) -> None:
    run = run_client.repository.seed_run(
        organization_id=run_client.organization_id,
        project_id=run_client.project_id,
        scenario_id=run_client.scenario.id,
        status=RunStatus.RUNNING,
        input_snapshot_json={
            "parameterSet": {"version": 3},
            "soilSample": {"version": 2},
        },
    )

    response = run_client.client.get(f"/api/v1/runs/{run.id}/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == str(run.id)
    assert payload["status"] == "running"
    assert payload["startedAt"] is not None


def test_get_run_results_returns_metadata_summary_and_artifacts(run_client) -> None:
    run = run_client.repository.seed_run(
        organization_id=run_client.organization_id,
        project_id=run_client.project_id,
        scenario_id=run_client.scenario.id,
        status=RunStatus.SUCCEEDED,
        input_snapshot_json={
            "parameterSet": {"version": 7},
            "soilSample": {"version": 42},
            "scenario": {"scenarioId": str(run_client.scenario.id)},
        },
        result_hash="result-hash-001",
        result_summary_json={"nodeCount": 3},
    )
    run_client.repository.artifacts_by_run_id[run.id] = [
        ArtifactRecord(
            id=uuid4(),
            artifact_type=ArtifactType.RESULT_JSON,
            label="result.json",
            content_type="application/json",
            storage_key="runs/result.json",
            byte_size=512,
            checksum_sha256="abc123",
            metadata_json={"kind": "result"},
            created_at=datetime.now(UTC),
        )
    ]

    response = run_client.client.get(f"/api/v1/runs/{run.id}/results")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "succeeded"
    assert payload["parameterSetVersion"] == 7
    assert payload["soilSampleVersion"] == 42
    assert payload["resultHash"] == "result-hash-001"
    assert payload["resultSummary"] == {"nodeCount": 3}
    assert payload["artifacts"][0]["artifactType"] == "result_json"


def test_submit_run_returns_permission_denied_without_write_access(run_client) -> None:
    run_client.app.dependency_overrides[get_current_user] = lambda: build_user(
        organization_id=run_client.organization_id,
        permissions={Permissions.RUN_READ},
    )

    response = run_client.client.post(
        "/api/v1/runs",
        json={"scenarioId": str(run_client.scenario.id)},
    )

    assert response.status_code == 403
    payload = response.json()
    assert payload["error"]["code"] == "permission_denied"
    assert payload["error"]["details"]["requiredPermission"] == Permissions.RUN_SUBMIT
