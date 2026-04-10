from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

try:
    from redis import Redis
    from redis.exceptions import ResponseError
except ModuleNotFoundError:  # pragma: no cover - exercised only in stripped local test envs.
    class Redis:  # type: ignore[no-redef]
        @classmethod
        def from_url(cls, *_args, **_kwargs):
            raise ModuleNotFoundError("redis package is required to use RedisStreamsQueue at runtime.")

    class ResponseError(Exception):
        pass

from app.jobs.payloads import JobEnvelope


@dataclass(slots=True)
class ReceivedMessage:
    queue_name: str
    message_id: str
    envelope: JobEnvelope


class RedisStreamsQueue:
    """
    Redis Streams queue adapter with delayed retry scheduling.

    Design notes:
    - immediate work lives in one stream per queue
    - delayed retries are stored in a companion sorted set
    - due delayed messages are moved back into the stream before polling
    - consumers use a group for at-least-once delivery and stale-message claiming
    """

    def __init__(
        self,
        *,
        redis_url: str,
        queue_names: list[str],
        consumer_group: str,
        consumer_name: str,
        redis_client: Redis | None = None,
    ) -> None:
        self.redis_url = redis_url
        self.queue_names = queue_names
        self.consumer_group = consumer_group
        self.consumer_name = consumer_name
        self.redis = redis_client or Redis.from_url(redis_url, decode_responses=True)

    def ensure_streams(self) -> None:
        for queue_name in self.queue_names:
            try:
                self.redis.xgroup_create(queue_name, self.consumer_group, id="0", mkstream=True)
            except ResponseError as exc:
                if "BUSYGROUP" not in str(exc):
                    raise

    def reserve(self, *, block_ms: int, count: int = 1) -> list[ReceivedMessage]:
        response = self.redis.xreadgroup(
            groupname=self.consumer_group,
            consumername=self.consumer_name,
            streams={queue_name: ">" for queue_name in self.queue_names},
            count=count,
            block=block_ms,
        )
        return self._parse_messages(response or [])

    def ack(self, *, queue_name: str, message_id: str) -> None:
        self.redis.xack(queue_name, self.consumer_group, message_id)

    def schedule(self, *, envelope: JobEnvelope) -> None:
        scheduled_at = envelope.available_at or datetime.now(UTC)
        self.redis.zadd(
            self._scheduled_key(envelope.queue_name),
            {envelope.model_dump_json(): scheduled_at.timestamp()},
        )

    def requeue_with_backoff(self, *, envelope: JobEnvelope, delay_seconds: int) -> None:
        self.schedule(envelope=envelope.next_attempt(delay_seconds=delay_seconds))

    def drain_scheduled(self, *, max_count: int = 100, now: datetime | None = None) -> int:
        current_time = now or datetime.now(UTC)
        moved = 0

        for queue_name in self.queue_names:
            scheduled_key = self._scheduled_key(queue_name)
            due_messages = self.redis.zrangebyscore(
                scheduled_key,
                min="-inf",
                max=current_time.timestamp(),
                start=0,
                num=max_count,
            )
            if not due_messages:
                continue

            pipeline = self.redis.pipeline()
            for serialized_envelope in due_messages:
                pipeline.xadd(queue_name, {"data": serialized_envelope})
                pipeline.zrem(scheduled_key, serialized_envelope)
                moved += 1
            pipeline.execute()

        return moved

    def dead_letter(
        self,
        *,
        queue_name: str,
        message_id: str,
        envelope: JobEnvelope,
        reason: str,
        failure_code: str,
    ) -> None:
        self.redis.xadd(
            f"{queue_name}:dead-letter",
            {
                "message_id": message_id,
                "job_id": str(envelope.job_id),
                "job_type": envelope.job_type,
                "failure_code": failure_code,
                "reason": reason,
                "failed_at": datetime.now(UTC).isoformat(),
                "envelope": envelope.model_dump_json(),
            },
        )

    def claim_stale(self, *, min_idle_ms: int, count: int = 20) -> list[ReceivedMessage]:
        claimed_messages: list[ReceivedMessage] = []
        for queue_name in self.queue_names:
            try:
                response = self.redis.xautoclaim(
                    queue_name,
                    self.consumer_group,
                    self.consumer_name,
                    min_idle_ms=min_idle_ms,
                    start_id="0-0",
                    count=count,
                )
            except ResponseError:
                continue

            messages = response[1] if isinstance(response, (list, tuple)) and len(response) > 1 else []
            claimed_messages.extend(self._parse_messages([(queue_name, messages)]))
        return claimed_messages

    def _scheduled_key(self, queue_name: str) -> str:
        return f"{queue_name}:scheduled"

    def _parse_messages(self, response: Any) -> list[ReceivedMessage]:
        messages: list[ReceivedMessage] = []
        for queue_name, stream_messages in response:
            for message_id, fields in stream_messages:
                payload = fields.get("data")
                if payload is None:
                    continue
                messages.append(
                    ReceivedMessage(
                        queue_name=queue_name,
                        message_id=message_id,
                        envelope=JobEnvelope.model_validate_json(payload),
                    )
                )
        return messages
