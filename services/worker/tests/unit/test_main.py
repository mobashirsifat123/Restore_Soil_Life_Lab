from app.main import _is_optional_redis_startup_failure


class FakeRedisError(Exception):
    pass


def test_optional_redis_startup_failure_recognizes_redis_errors(monkeypatch) -> None:
    monkeypatch.setattr("app.main.RedisError", FakeRedisError)

    assert _is_optional_redis_startup_failure(FakeRedisError("redis down")) is True
    assert _is_optional_redis_startup_failure(RuntimeError("other")) is False
