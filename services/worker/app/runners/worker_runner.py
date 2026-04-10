from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime

from app.core.config import Settings
from app.jobs.payloads import (
    DecompositionRunPayload,
    JobEnvelope,
    ReportGenerationPayload,
    SimulationRunPayload,
)
from app.jobs.registry import get_handler
from app.queue.redis_streams import RedisStreamsQueue
from app.services.artifact_service import ArtifactService
from app.services.execution_service import ExecutionService
from app.services.status_store import StatusStore

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class WorkerRunner:
    queue: RedisStreamsQueue
    status_store: StatusStore
    artifact_service: ArtifactService
    execution_service: ExecutionService
    block_ms: int
    lease_ms: int
    max_messages_per_poll: int
    scheduled_drain_batch_size: int

    @classmethod
    def from_settings(cls, settings: Settings) -> "WorkerRunner":
        queue = RedisStreamsQueue(
            redis_url=settings.redis_url,
            queue_names=settings.queue_names,
            consumer_group=settings.worker_name,
            consumer_name=settings.worker_id,
        )
        return cls(
            queue=queue,
            status_store=StatusStore(database_url=settings.database_url, worker_id=settings.worker_id),
            artifact_service=ArtifactService(
                bucket=settings.object_storage_bucket,
                root_path=settings.artifact_storage_root,
            ),
            execution_service=ExecutionService(
                worker_id=settings.worker_id,
                simulation_engine_command=settings.simulation_engine_command,
                simulation_engine_pythonpath=settings.simulation_engine_pythonpath,
            ),
            block_ms=settings.queue_block_timeout_seconds * 1000,
            lease_ms=settings.job_lease_seconds * 1000,
            max_messages_per_poll=max(1, settings.worker_concurrency),
            scheduled_drain_batch_size=max(10, settings.worker_concurrency * 10),
        )

    def run_forever(self) -> None:
        self.queue.ensure_streams()
        logger.info("worker_started")

        while True:
            self.run_once()

    def run_once(self) -> int:
        moved = self.queue.drain_scheduled(max_count=self.scheduled_drain_batch_size)
        if moved:
            logger.info("scheduled_jobs_released", extra={"message_count": moved})

        self._claim_stale_messages()
        messages = self.queue.reserve(block_ms=self.block_ms, count=self.max_messages_per_poll)
        for message in messages:
            self._process_message(message.queue_name, message.message_id, message.envelope)
        return len(messages)

    def _claim_stale_messages(self) -> None:
        stale_messages = self.queue.claim_stale(
            min_idle_ms=self.lease_ms,
            count=self.max_messages_per_poll,
        )
        for message in stale_messages:
            logger.warning(
                "claimed_stale_message",
                extra={
                    "queue_name": message.queue_name,
                    "message_id": message.message_id,
                    "job_id": str(message.envelope.job_id),
                    "job_type": message.envelope.job_type,
                },
            )
            self._process_message(message.queue_name, message.message_id, message.envelope)

    def _process_message(self, queue_name: str, message_id: str, envelope: JobEnvelope) -> None:
        try:
            if envelope.available_at and envelope.available_at > datetime.now(UTC):
                logger.info(
                    "job_received_before_available_at",
                    extra={
                        "queue_name": queue_name,
                        "message_id": message_id,
                        "job_id": str(envelope.job_id),
                        "job_type": envelope.job_type,
                    },
                )
                self.queue.schedule(envelope=envelope)
                self.queue.ack(queue_name=queue_name, message_id=message_id)
                return

            payload = envelope.payload
            handler = get_handler(envelope.job_type)

            if isinstance(payload, (SimulationRunPayload, DecompositionRunPayload)):
                handler(
                    envelope=envelope,
                    payload=payload,
                    status_store=self.status_store,
                    artifact_service=self.artifact_service,
                    engine_executor=self.execution_service,
                )
            elif isinstance(payload, ReportGenerationPayload):
                handler(
                    envelope=envelope,
                    payload=payload,
                    status_store=self.status_store,
                    artifact_service=self.artifact_service,
                    report_renderer=self.execution_service,
                )
            else:
                raise ValueError(f"Unsupported payload type for job {envelope.job_type}")

            self.queue.ack(queue_name=queue_name, message_id=message_id)
            logger.info(
                "job_completed",
                extra={
                    "queue_name": queue_name,
                    "message_id": message_id,
                    "job_id": str(envelope.job_id),
                    "job_type": envelope.job_type,
                },
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception(
                "job_processing_failed",
                extra={
                    "queue_name": queue_name,
                    "message_id": message_id,
                    "job_type": envelope.job_type,
                    "job_id": str(envelope.job_id),
                },
            )
            self._handle_failure(queue_name=queue_name, message_id=message_id, envelope=envelope, exc=exc)

    def _handle_failure(
        self,
        *,
        queue_name: str,
        message_id: str,
        envelope: JobEnvelope,
        exc: Exception,
    ) -> None:
        retryable = self.status_store.is_retryable_failure(exc)
        if retryable and self.status_store.can_retry(envelope):
            delay_seconds = self.status_store.compute_retry_delay(envelope)
            self.status_store.mark_retry_scheduled(envelope=envelope, exc=exc, delay_seconds=delay_seconds)
            self.queue.requeue_with_backoff(envelope=envelope, delay_seconds=delay_seconds)
            self.queue.ack(queue_name=queue_name, message_id=message_id)
            return

        self.status_store.mark_terminal_failure(envelope=envelope, exc=exc)
        self.queue.dead_letter(
            queue_name=queue_name,
            message_id=message_id,
            envelope=envelope,
            reason=str(exc),
            failure_code=exc.__class__.__name__.lower(),
        )
        self.queue.ack(queue_name=queue_name, message_id=message_id)
