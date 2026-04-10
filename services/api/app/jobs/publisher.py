from __future__ import annotations

from redis import Redis

from app.jobs.contracts import JobEnvelope


class JobPublisher:
    def __init__(self, *, redis_url: str) -> None:
        self.redis = Redis.from_url(redis_url, decode_responses=True)

    def publish(self, envelope: JobEnvelope) -> None:
        self.redis.xadd(envelope.queue_name, {"data": envelope.model_dump_json()})
