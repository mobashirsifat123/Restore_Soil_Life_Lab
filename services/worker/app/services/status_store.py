from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import create_engine, text

from app.jobs.payloads import JobEnvelope
from app.services.artifact_service import StoredArtifact


class StatusStore:
    """
    Authoritative state persistence contract.

    For MVP, the source of truth should be:
    - `simulation_runs` for simulation and decomposition jobs
    - `reports` for report generation jobs

    Recommended columns to persist on those records:
    - `status`
    - `attempt_count`
    - `worker_id`
    - `last_heartbeat_at`
    - `lease_expires_at`
    - `queue_name`
    - `failure_code`
    - `failure_message`
    - `failure_details_json`
    - `started_at`
    - `completed_at`
    - `canceled_at`
    - `updated_at`
    """

    def __init__(self, *, database_url: str, worker_id: str) -> None:
        self.database_url = database_url
        self.worker_id = worker_id
        self.engine = create_engine(database_url, pool_pre_ping=True)

    def is_retryable_failure(self, exc: Exception) -> bool:
        return not isinstance(exc, ValueError)

    def can_retry(self, envelope: JobEnvelope) -> bool:
        payload = envelope.payload
        return payload.attempt < payload.max_attempts

    def compute_retry_delay(self, envelope: JobEnvelope) -> int:
        attempt = envelope.payload.attempt
        return min(30 * (2 ** (attempt - 1)), 900)

    def start_simulation_run(self, *, run_id, attempt: int) -> dict[str, Any] | None:
        with self.engine.begin() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT id, organization_id, status, input_snapshot_json
                    FROM simulation_runs
                    WHERE id = :run_id
                    FOR UPDATE
                    """
                ),
                {"run_id": run_id},
            ).mappings().one_or_none()

            if row is None:
                raise ValueError(f"Run {run_id} was not found.")
            if row["status"] != "queued":
                return None

            connection.execute(
                text(
                    """
                    UPDATE simulation_runs
                    SET status = 'running',
                        started_at = COALESCE(started_at, NOW()),
                        updated_at = NOW(),
                        worker_id = :worker_id,
                        attempt_count = :attempt,
                        failure_code = NULL,
                        failure_message = NULL,
                        failure_details_json = '{}'::jsonb
                    WHERE id = :run_id
                    """
                ),
                {
                    "run_id": run_id,
                    "worker_id": self.worker_id,
                    "attempt": attempt,
                },
            )
            return dict(row)

    def mark_run_succeeded(
        self,
        *,
        run_id,
        organization_id,
        result_payload: dict[str, Any],
        artifacts: list[StoredArtifact],
    ) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                text(
                    """
                    UPDATE simulation_runs
                    SET status = 'succeeded',
                        result_hash = :result_hash,
                        result_summary_json = CAST(:result_summary_json AS jsonb),
                        engine_version = :engine_version,
                        completed_at = NOW(),
                        updated_at = NOW(),
                        failure_code = NULL,
                        failure_message = NULL,
                        failure_details_json = '{}'::jsonb
                    WHERE id = :run_id
                    """
                ),
                {
                    "run_id": run_id,
                    "result_hash": result_payload["provenance"]["resultHash"],
                    "result_summary_json": json.dumps(result_payload.get("summary", {})),
                    "engine_version": result_payload["provenance"]["engineVersion"],
                },
            )
            for artifact in artifacts:
                connection.execute(
                    text(
                        """
                        DELETE FROM run_artifacts
                        WHERE run_id = :run_id
                          AND artifact_type = :artifact_type
                        """
                    ),
                    {
                        "run_id": run_id,
                        "artifact_type": artifact.artifact_type,
                    },
                )
                connection.execute(
                    text(
                        """
                        INSERT INTO run_artifacts (
                            organization_id,
                            run_id,
                            artifact_type,
                            label,
                            content_type,
                            storage_key,
                            byte_size,
                            checksum_sha256,
                            metadata_json
                        ) VALUES (
                            :organization_id,
                            :run_id,
                            :artifact_type,
                            :label,
                            :content_type,
                            :storage_key,
                            :byte_size,
                            :checksum_sha256,
                            CAST(:metadata_json AS jsonb)
                        )
                        """
                    ),
                    {
                        "organization_id": organization_id,
                        "run_id": run_id,
                        "artifact_type": artifact.artifact_type,
                        "label": artifact.label,
                        "content_type": artifact.content_type,
                        "storage_key": artifact.storage_key,
                        "byte_size": artifact.byte_size,
                        "checksum_sha256": artifact.checksum_sha256,
                        "metadata_json": json.dumps(artifact.metadata),
                    },
                )

    def mark_retry_scheduled(self, *, envelope: JobEnvelope, exc: Exception, delay_seconds: int) -> None:
        run_id = getattr(envelope.payload, "run_id", None)
        if run_id is None:
            raise ValueError("Retry scheduling persistence is only implemented for run-based jobs.")

        with self.engine.begin() as connection:
            connection.execute(
                text(
                    """
                    UPDATE simulation_runs
                    SET status = 'queued',
                        updated_at = NOW(),
                        failure_code = :failure_code,
                        failure_message = :failure_message,
                        failure_details_json = CAST(:failure_details_json AS jsonb)
                    WHERE id = :run_id
                    """
                ),
                {
                    "run_id": run_id,
                    "failure_code": "retry_scheduled",
                    "failure_message": str(exc),
                    "failure_details_json": json.dumps({"delaySeconds": delay_seconds}),
                },
            )

    def mark_terminal_failure(self, *, envelope: JobEnvelope, exc: Exception) -> None:
        run_id = getattr(envelope.payload, "run_id", None)
        if run_id is None:
            raise ValueError("Terminal failure persistence is only implemented for run-based jobs.")

        with self.engine.begin() as connection:
            connection.execute(
                text(
                    """
                    UPDATE simulation_runs
                    SET status = 'failed',
                        updated_at = NOW(),
                        completed_at = NOW(),
                        failure_code = :failure_code,
                        failure_message = :failure_message,
                        failure_details_json = CAST(:failure_details_json AS jsonb)
                    WHERE id = :run_id
                    """
                ),
                {
                    "run_id": run_id,
                    "failure_code": exc.__class__.__name__.lower(),
                    "failure_message": str(exc),
                    "failure_details_json": json.dumps(
                        {
                            "workerId": self.worker_id,
                            "failedAt": datetime.now(UTC).isoformat(),
                        }
                    ),
                },
            )
