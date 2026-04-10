from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime


class WorkerContextFilter(logging.Filter):
    def __init__(self, *, worker_id: str, worker_name: str, worker_env: str) -> None:
        super().__init__()
        self.worker_id = worker_id
        self.worker_name = worker_name
        self.worker_env = worker_env

    def filter(self, record: logging.LogRecord) -> bool:
        record.worker_id = self.worker_id
        record.worker_name = self.worker_name
        record.worker_env = self.worker_env
        return True


class JsonLogFormatter(logging.Formatter):
    structured_fields = (
        "worker_id",
        "worker_name",
        "worker_env",
        "job_id",
        "job_type",
        "queue_names",
        "queue_name",
        "message_id",
        "run_id",
        "attempt",
        "message_count",
        "report_id",
    )

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for field in self.structured_fields:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=True)


def configure_logging(*, worker_id: str, worker_name: str, worker_env: str) -> None:
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonLogFormatter())
    handler.addFilter(
        WorkerContextFilter(
            worker_id=worker_id,
            worker_name=worker_name,
            worker_env=worker_env,
        )
    )

    root_logger.addHandler(handler)
