from __future__ import annotations

import logging

from app.jobs.payloads import JobEnvelope, ReportGenerationPayload

logger = logging.getLogger(__name__)


def handle_report_generation(
    *,
    envelope: JobEnvelope,
    payload: ReportGenerationPayload,
    status_store,
    artifact_service,
    report_renderer,
) -> None:
    logger.info(
        "report_generation_received",
        extra={"job_id": str(envelope.job_id), "report_id": str(payload.report_id)},
    )
    raise NotImplementedError("Wire report rendering, artifact upload, and report status transitions.")
