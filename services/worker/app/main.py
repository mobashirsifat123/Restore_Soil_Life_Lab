import logging

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.runners.worker_runner import WorkerRunner

try:
    from redis.exceptions import RedisError
except ModuleNotFoundError:  # pragma: no cover - exercised only in stripped local test envs.
    RedisError = Exception  # type: ignore[misc,assignment]

logger = logging.getLogger(__name__)


def _is_optional_redis_startup_failure(exc: Exception) -> bool:
    return isinstance(exc, RedisError)


def main() -> None:
    settings = get_settings()
    configure_logging(
        worker_id=settings.worker_id,
        worker_name=settings.worker_name,
        worker_env=settings.worker_env,
    )
    logger.info("worker_bootstrap", extra={"queue_names": settings.queue_names})
    runner = WorkerRunner.from_settings(settings)
    try:
        runner.run_forever()
    except Exception as exc:  # noqa: BLE001
        if (
            settings.worker_optional_when_redis_unavailable
            and _is_optional_redis_startup_failure(exc)
        ):
            logger.warning(
                "worker_skipped_missing_redis",
                extra={
                    "redis_url": settings.redis_url,
                    "reason": str(exc),
                },
            )
            return
        raise


if __name__ == "__main__":
    main()
