from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.models import RunArtifact, SimulationRun, SimulationScenario
from app.domain.enums import ArtifactType, RunStatus


class RunRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_scenario_bundle(
        self,
        organization_id: UUID,
        scenario_id: UUID,
    ) -> SimulationScenario | None:
        statement = (
            select(SimulationScenario)
            .options(
                joinedload(SimulationScenario.soil_sample),
                joinedload(SimulationScenario.soil_sample_version),
                joinedload(SimulationScenario.food_web_definition),
                joinedload(SimulationScenario.parameter_set),
                joinedload(SimulationScenario.project),
            )
            .where(
                SimulationScenario.organization_id == organization_id,
                SimulationScenario.id == scenario_id,
                SimulationScenario.deleted_at.is_(None),
            )
        )
        return self.session.scalar(statement)

    def find_by_idempotency_key(
        self,
        *,
        organization_id: UUID,
        scenario_id: UUID,
        idempotency_key: str | None,
    ) -> SimulationRun | None:
        if not idempotency_key:
            return None
        statement = select(SimulationRun).where(
            SimulationRun.organization_id == organization_id,
            SimulationRun.scenario_id == scenario_id,
            SimulationRun.idempotency_key == idempotency_key,
        )
        return self.session.scalar(statement)

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
    ) -> SimulationRun:
        now = datetime.now(UTC)
        run = SimulationRun(
            organization_id=organization_id,
            project_id=project_id,
            scenario_id=scenario_id,
            engine_name=engine_name,
            engine_version=engine_version,
            input_schema_version=input_schema_version,
            input_hash=input_hash,
            execution_options_json=execution_options_json,
            input_snapshot_json=input_snapshot_json,
            queue_name=queue_name,
            idempotency_key=idempotency_key,
            created_by_user_id=created_by_user_id,
            queued_at=now,
        )
        self.session.add(run)
        self.session.commit()
        self.session.refresh(run)
        return run

    def mark_enqueue_failed(self, run: SimulationRun, *, message: str) -> SimulationRun:
        run.status = RunStatus.FAILED
        run.failure_code = "queue_publish_failed"
        run.failure_message = message
        run.completed_at = datetime.now(UTC)
        run.updated_at = datetime.now(UTC)
        self.session.add(run)
        self.session.commit()
        self.session.refresh(run)
        return run

    def mark_running(self, run: SimulationRun, *, worker_id: str) -> SimulationRun:
        now = datetime.now(UTC)
        run.status = RunStatus.RUNNING
        run.started_at = run.started_at or now
        run.updated_at = now
        run.worker_id = worker_id
        run.attempt_count = max(run.attempt_count, 1)
        run.failure_code = None
        run.failure_message = None
        run.failure_details_json = {}
        self.session.add(run)
        self.session.commit()
        self.session.refresh(run)
        return run

    def mark_succeeded(
        self,
        run: SimulationRun,
        *,
        result_hash: str,
        result_summary_json: dict | None,
        engine_version: str,
        artifacts: list[dict],
    ) -> SimulationRun:
        now = datetime.now(UTC)
        run.status = RunStatus.SUCCEEDED
        run.result_hash = result_hash
        run.result_summary_json = result_summary_json
        run.engine_version = engine_version
        run.completed_at = now
        run.updated_at = now
        run.failure_code = None
        run.failure_message = None
        run.failure_details_json = {}
        self.session.add(run)

        self.session.query(RunArtifact).filter(RunArtifact.run_id == run.id).delete()
        for artifact in artifacts:
            self.session.add(
                RunArtifact(
                    organization_id=run.organization_id,
                    run_id=run.id,
                    artifact_type=ArtifactType(artifact["artifact_type"]),
                    label=artifact["label"],
                    content_type=artifact["content_type"],
                    storage_key=artifact["storage_key"],
                    byte_size=artifact["byte_size"],
                    checksum_sha256=artifact["checksum_sha256"],
                    metadata_json=artifact.get("metadata", {}),
                )
            )

        self.session.commit()
        self.session.refresh(run)
        return run

    def mark_failed(self, run: SimulationRun, *, failure_code: str, failure_message: str) -> SimulationRun:
        now = datetime.now(UTC)
        run.status = RunStatus.FAILED
        run.completed_at = now
        run.updated_at = now
        run.failure_code = failure_code
        run.failure_message = failure_message
        self.session.add(run)
        self.session.commit()
        self.session.refresh(run)
        return run

    def get_by_id(self, organization_id: UUID, run_id: UUID):
        statement = select(SimulationRun).where(
            SimulationRun.organization_id == organization_id,
            SimulationRun.id == run_id,
        )
        return self.session.scalar(statement)

    def list_for_organization(self, organization_id: UUID, limit: int = 25):
        statement = (
            select(SimulationRun)
            .where(SimulationRun.organization_id == organization_id)
            .order_by(SimulationRun.created_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(statement))

    def list_artifacts(self, organization_id: UUID, run_id: UUID):
        statement = (
            select(RunArtifact)
            .where(RunArtifact.organization_id == organization_id, RunArtifact.run_id == run_id)
            .order_by(RunArtifact.created_at.asc())
        )
        return list(self.session.scalars(statement))
