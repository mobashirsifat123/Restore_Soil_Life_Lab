from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from uuid import UUID

from app.core.config import get_settings
from app.core.errors import AppError
from app.domain.auth import AuthenticatedUser
from app.jobs.contracts import JobEnvelope
from app.jobs.publisher import JobPublisher
from app.repositories.cms_repository import CmsRepository
from app.repositories.run_repository import RunRepository
from app.schemas.run import (
    RunCreate,
    RunDetail,
    RunListResponse,
    RunResultsResponse,
    RunStatusResponse,
    dump_execution_options,
)
from app.services.input_snapshot_builder import build_run_input_snapshot, compute_input_hash
from app.services.serializers import serialize_run, serialize_run_results, serialize_run_status


class RunService:
    def __init__(
        self,
        repository: RunRepository,
        publisher: JobPublisher,
        cms_repository: CmsRepository | None = None,
    ) -> None:
        self.repository = repository
        self.publisher = publisher
        self.cms_repository = cms_repository

    def create_run(self, *, current_user: AuthenticatedUser, payload: RunCreate) -> RunDetail:
        settings = get_settings()
        execution_options = dump_execution_options(payload.execution_options)
        existing = self.repository.find_by_idempotency_key(
            organization_id=current_user.organization_id,
            scenario_id=payload.scenario_id,
            idempotency_key=payload.idempotency_key,
        )
        if existing is not None:
            return serialize_run(existing)

        scenario = self.repository.get_scenario_bundle(
            current_user.organization_id,
            payload.scenario_id,
        )
        if scenario is None:
            raise AppError(
                status_code=404,
                code="scenario_not_found",
                message="Scenario not found.",
            )

        input_snapshot = build_run_input_snapshot(
            scenario=scenario,
            execution_options=execution_options,
            input_schema_version=settings.simulation_input_schema_version,
        )

        active_formula = (
            self.cms_repository.get_active_formula() if self.cms_repository is not None else None
        )
        if active_formula and active_formula.formula_json.get("equations"):
            input_snapshot["scenario"]["configuration"]["equations"] = active_formula.formula_json["equations"]

        input_hash = compute_input_hash(input_snapshot)

        run = self.repository.create(
            organization_id=current_user.organization_id,
            project_id=scenario.project_id,
            scenario_id=scenario.id,
            created_by_user_id=current_user.user_id,
            engine_name=settings.simulation_engine_name,
            engine_version=settings.simulation_engine_version,
            input_schema_version=settings.simulation_input_schema_version,
            input_hash=input_hash,
            execution_options_json=execution_options,
            input_snapshot_json=input_snapshot,
            queue_name=settings.simulation_queue_name,
            idempotency_key=payload.idempotency_key,
        )

        envelope = JobEnvelope(
            job_type="simulation.run.execute",
            queue_name=settings.simulation_queue_name,
            payload={
                "job_type": "simulation.run.execute",
                "organization_id": str(run.organization_id),
                "project_id": str(run.project_id),
                "initiated_by_user_id": str(current_user.user_id),
                "run_id": str(run.id),
                "scenario_id": str(run.scenario_id),
                "engine_name": run.engine_name,
                "engine_version": run.engine_version,
                "input_schema_version": run.input_schema_version,
                "parameter_set_version": int(input_snapshot["parameterSet"]["version"]),
                "soil_sample_version": int(input_snapshot["soilSample"]["version"]),
                "attempt": 1,
                "max_attempts": 3,
                "timeout_seconds": int(execution_options.get("timeoutSeconds", 120)),
                "idempotency_key": payload.idempotency_key,
                "input_hash": run.input_hash,
                "execution_options": execution_options,
            },
        )

        try:
            self.publisher.publish(envelope)
        except Exception as exc:  # noqa: BLE001
            if settings.run_inline_fallback_enabled and hasattr(self.repository, "mark_running"):
                self._execute_run_inline(run)
                return serialize_run(self.repository.get_by_id(current_user.organization_id, run.id))
            self.repository.mark_enqueue_failed(run, message=str(exc))
            raise AppError(
                status_code=503,
                code="run_enqueue_failed",
                message="Simulation run was created but could not be queued for execution.",
                details={
                    "runId": str(run.id),
                    "scenarioId": str(run.scenario_id),
                    "queueName": settings.simulation_queue_name,
                },
            ) from exc
        return serialize_run(run)

    def _execute_run_inline(self, run) -> None:
        self.repository.mark_running(run, worker_id="api-inline-fallback")

        repository_root = Path(__file__).resolve().parents[4]
        artifacts_root = repository_root / ".data" / "artifacts" / "bio-lab-dev"

        try:
            with tempfile.TemporaryDirectory(prefix=f"inline-run-{run.id}-") as temp_dir:
                temp_path = Path(temp_dir)
                input_path = temp_path / "input.json"
                output_path = temp_path / "output.json"
                input_path.write_text(
                    json.dumps(run.input_snapshot_json, ensure_ascii=True, indent=2, sort_keys=True),
                    encoding="utf-8",
                )

                command = [
                    "bash",
                    str(repository_root / "scripts" / "python-project.sh"),
                    "services/simulation-engine",
                    "python",
                    "-m",
                    "soil_engine.cli",
                    "run",
                    "--input",
                    str(input_path),
                    "--output",
                    str(output_path),
                ]
                completed = subprocess.run(
                    command,
                    cwd=repository_root,
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=int(run.execution_options_json.get("timeoutSeconds", 120)),
                )
                if completed.returncode != 0:
                    raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "inline simulation failed")
                if not output_path.exists():
                    raise RuntimeError("inline simulation completed without an output artifact")

                result_payload = json.loads(output_path.read_text(encoding="utf-8"))
                artifacts = self._write_inline_artifacts(
                    run_id=run.id,
                    artifacts_root=artifacts_root,
                    result_payload=result_payload,
                    stdout=completed.stdout,
                    stderr=completed.stderr,
                )
                self.repository.mark_succeeded(
                    run,
                    result_hash=result_payload["provenance"]["resultHash"],
                    result_summary_json=result_payload.get("summary"),
                    engine_version=result_payload["provenance"]["engineVersion"],
                    artifacts=artifacts,
                )
        except Exception as exc:  # noqa: BLE001
            self.repository.mark_failed(
                run,
                failure_code="inline_execution_failed",
                failure_message=str(exc),
            )
            raise AppError(
                status_code=503,
                code="run_inline_execution_failed",
                message="Simulation run failed during inline fallback execution.",
                details={"runId": str(run.id)},
            ) from exc

    def _write_inline_artifacts(
        self,
        *,
        run_id,
        artifacts_root: Path,
        result_payload: dict,
        stdout: str,
        stderr: str,
    ) -> list[dict]:
        def write_bytes(relative_key: str, data: bytes, content_type: str) -> dict:
            destination = artifacts_root / relative_key
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
            return {
                "storage_key": relative_key,
                "byte_size": len(data),
                "checksum_sha256": hashlib.sha256(data).hexdigest(),
                "content_type": content_type,
            }

        result_key = f"runs/{run_id}/result.json"
        result_bytes = json.dumps(result_payload, ensure_ascii=True, indent=2, sort_keys=True).encode("utf-8")
        result_meta = write_bytes(result_key, result_bytes, "application/json")

        summary_key = f"runs/{run_id}/summary.json"
        summary_bytes = json.dumps(
            {"summary": result_payload.get("summary"), "provenance": result_payload.get("provenance")},
            ensure_ascii=True,
            indent=2,
            sort_keys=True,
        ).encode("utf-8")
        summary_meta = write_bytes(summary_key, summary_bytes, "application/json")

        log_key = f"runs/{run_id}/diagnostics.log"
        log_bytes = f"[stdout]\n{stdout}\n\n[stderr]\n{stderr}\n".encode()
        log_meta = write_bytes(log_key, log_bytes, "text/plain")

        return [
            {
                "artifact_type": "result_json",
                "label": "Simulation result JSON",
                "metadata": {},
                **result_meta,
            },
            {
                "artifact_type": "summary_json",
                "label": "Simulation summary JSON",
                "metadata": {},
                **summary_meta,
            },
            {
                "artifact_type": "log_bundle",
                "label": "Simulation diagnostics log",
                "metadata": {},
                **log_meta,
            },
        ]

    def get_run(self, *, current_user: AuthenticatedUser, run_id: UUID) -> RunDetail:
        run = self.repository.get_by_id(current_user.organization_id, run_id)
        if run is None:
            raise AppError(
                status_code=404,
                code="run_not_found",
                message="Run not found.",
                details={"runId": str(run_id)},
            )
        return serialize_run(run)

    def list_runs(self, *, current_user: AuthenticatedUser, limit: int = 25) -> RunListResponse:
        runs = self.repository.list_for_organization(current_user.organization_id, limit=limit)
        items = [serialize_run(run) for run in runs]
        return RunListResponse(items=items)

    def get_run_status(self, *, current_user: AuthenticatedUser, run_id: UUID) -> RunStatusResponse:
        run = self.repository.get_by_id(current_user.organization_id, run_id)
        if run is None:
            raise AppError(
                status_code=404,
                code="run_not_found",
                message="Run not found.",
                details={"runId": str(run_id)},
            )
        return serialize_run_status(run)

    def get_run_results(
        self,
        *,
        current_user: AuthenticatedUser,
        run_id: UUID,
    ) -> RunResultsResponse:
        run = self.repository.get_by_id(current_user.organization_id, run_id)
        if run is None:
            raise AppError(
                status_code=404,
                code="run_not_found",
                message="Run not found.",
                details={"runId": str(run_id)},
            )
        artifacts = self.repository.list_artifacts(current_user.organization_id, run_id)
        return serialize_run_results(run, artifacts)
