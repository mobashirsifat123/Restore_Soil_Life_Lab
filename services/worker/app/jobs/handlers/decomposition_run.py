from __future__ import annotations

import logging

from app.jobs.payloads import DecompositionRunPayload, JobEnvelope

logger = logging.getLogger(__name__)


def handle_decomposition_run(
    *,
    envelope: JobEnvelope,
    payload: DecompositionRunPayload,
    status_store,
    artifact_service,
    engine_executor,
) -> None:
    logger.info(
        "decomposition_run_received",
        extra={"job_id": str(envelope.job_id), "run_id": str(payload.run_id)},
    )
    raise NotImplementedError("Wire decomposition execution with the same safety rules as runs.")
