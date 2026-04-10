from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.jobs.payloads import JobEnvelope, JobPriority, JobType, SimulationRunPayload
from app.queue.redis_streams import RedisStreamsQueue


class FakePipeline:
    def __init__(self, redis_client) -> None:
        self.redis_client = redis_client
        self.operations = []

    def xadd(self, stream_name, fields):
        self.operations.append(("xadd", stream_name, fields))
        return self

    def zrem(self, key, member):
        self.operations.append(("zrem", key, member))
        return self

    def execute(self):
        for operation in self.operations:
            name = operation[0]
            if name == "xadd":
                _, stream_name, fields = operation
                self.redis_client.xadd(stream_name, fields)
            elif name == "zrem":
                _, key, member = operation
                self.redis_client.zrem(key, member)
        self.operations.clear()


class FakeRedis:
    def __init__(self) -> None:
        self.zsets: dict[str, dict[str, float]] = {}
        self.streams: dict[str, list[dict[str, str]]] = {}

    def zadd(self, key, mapping):
        bucket = self.zsets.setdefault(key, {})
        for member, score in mapping.items():
            bucket[member] = score

    def zrangebyscore(self, key, min, max, start=0, num=None):
        bucket = self.zsets.get(key, {})
        items = [member for member, score in sorted(bucket.items(), key=lambda item: item[1]) if score <= float(max)]
        if num is None:
            return items[start:]
        return items[start : start + num]

    def zrem(self, key, member):
        bucket = self.zsets.setdefault(key, {})
        bucket.pop(member, None)

    def xadd(self, stream_name, fields):
        self.streams.setdefault(stream_name, []).append(fields)

    def pipeline(self):
        return FakePipeline(self)


def build_envelope() -> JobEnvelope:
    payload = SimulationRunPayload(
        organization_id=uuid4(),
        project_id=uuid4(),
        initiated_by_user_id=uuid4(),
        run_id=uuid4(),
        scenario_id=uuid4(),
        engine_name="soil-engine",
        engine_version="0.1.0",
        input_schema_version="1.0.0",
        input_hash="abc123",
    )
    return JobEnvelope(
        job_id=uuid4(),
        job_type=JobType.SIMULATION_RUN,
        queue_name="jobs:simulation",
        priority=JobPriority.NORMAL,
        enqueued_at=datetime.now(UTC),
        payload=payload,
    )


def test_requeue_with_backoff_increments_attempt_and_schedules_message():
    fake_redis = FakeRedis()
    envelope = build_envelope()
    queue = RedisStreamsQueue(
        redis_url="redis://localhost:6379/0",
        queue_names=["jobs:simulation"],
        consumer_group="bio-worker",
        consumer_name="worker-1",
        redis_client=fake_redis,
    )

    queue.requeue_with_backoff(envelope=envelope, delay_seconds=30)

    scheduled_items = fake_redis.zsets["jobs:simulation:scheduled"]
    assert len(scheduled_items) == 1
    serialized_envelope = next(iter(scheduled_items.keys()))
    scheduled_envelope = JobEnvelope.model_validate_json(serialized_envelope)
    assert scheduled_envelope.payload.attempt == 2
    assert scheduled_envelope.available_at is not None


def test_drain_scheduled_moves_due_messages_back_to_stream():
    fake_redis = FakeRedis()
    envelope = build_envelope().model_copy(
        update={"available_at": datetime.now(UTC) - timedelta(seconds=1)}
    )
    queue = RedisStreamsQueue(
        redis_url="redis://localhost:6379/0",
        queue_names=["jobs:simulation"],
        consumer_group="bio-worker",
        consumer_name="worker-1",
        redis_client=fake_redis,
    )
    fake_redis.zadd(
        "jobs:simulation:scheduled",
        {envelope.model_dump_json(): envelope.available_at.timestamp()},
    )

    moved = queue.drain_scheduled(max_count=10)

    assert moved == 1
    assert fake_redis.streams["jobs:simulation"][0]["data"] == envelope.model_dump_json()
    assert fake_redis.zsets["jobs:simulation:scheduled"] == {}
