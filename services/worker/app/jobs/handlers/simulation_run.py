from __future__ import annotations

import logging

from app.jobs.payloads import JobEnvelope, SimulationRunPayload

logger = logging.getLogger(__name__)


def handle_simulation_run(
    *,
    envelope: JobEnvelope,
    payload: SimulationRunPayload,
    status_store,
    artifact_service,
    engine_executor,
) -> None:
    logger.info(
        "simulation_run_received",
        extra={
            "job_id": str(envelope.job_id),
            "run_id": str(payload.run_id),
            "attempt": payload.attempt,
        },
    )

    claimed_run = status_store.start_simulation_run(run_id=payload.run_id, attempt=payload.attempt)
    if claimed_run is None:
        logger.info(
            "simulation_run_skipped",
            extra={"run_id": str(payload.run_id), "attempt": payload.attempt},
        )
        return

    execution_result = engine_executor.execute_simulation(
        run_id=payload.run_id,
        input_snapshot=claimed_run["input_snapshot_json"],
        timeout_seconds=payload.timeout_seconds,
    )
    result_payload = execution_result["result"]
    artifacts = artifact_service.write_run_artifacts(
        run_id=payload.run_id,
        result_payload=result_payload,
        stdout=execution_result["stdout"],
        stderr=execution_result["stderr"],
    )
    status_store.mark_run_succeeded(
        run_id=payload.run_id,
        organization_id=payload.organization_id,
        result_payload=result_payload,
        artifacts=artifacts,
    )
    logger.info(
        "simulation_run_succeeded",
        extra={
            "job_id": str(envelope.job_id),
            "run_id": str(payload.run_id),
            "attempt": payload.attempt,
        },
    )
