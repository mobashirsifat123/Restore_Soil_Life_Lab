from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

SERVICE_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(SERVICE_ROOT / ".env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    worker_name: str = Field(default="bio-worker", alias="WORKER_NAME")
    worker_id: str = Field(default="worker-dev-1", alias="WORKER_ID")
    worker_env: str = Field(default="development", alias="WORKER_ENV")
    redis_url: str = Field(alias="REDIS_URL")
    database_url: str = Field(alias="DATABASE_URL")
    simulation_queue_name: str = Field(default="jobs:simulation", alias="SIMULATION_QUEUE_NAME")
    decomposition_queue_name: str = Field(
        default="jobs:decomposition", alias="DECOMPOSITION_QUEUE_NAME"
    )
    report_queue_name: str = Field(default="jobs:report", alias="REPORT_QUEUE_NAME")
    worker_concurrency: int = Field(default=2, alias="WORKER_CONCURRENCY")
    heartbeat_interval_seconds: int = Field(default=15, alias="HEARTBEAT_INTERVAL_SECONDS")
    queue_block_timeout_seconds: int = Field(default=5, alias="QUEUE_BLOCK_TIMEOUT_SECONDS")
    job_lease_seconds: int = Field(default=120, alias="JOB_LEASE_SECONDS")
    simulation_timeout_seconds: int = Field(default=1800, alias="SIMULATION_TIMEOUT_SECONDS")
    decomposition_timeout_seconds: int = Field(
        default=3600, alias="DECOMPOSITION_TIMEOUT_SECONDS"
    )
    report_timeout_seconds: int = Field(default=600, alias="REPORT_TIMEOUT_SECONDS")
    max_simulation_attempts: int = Field(default=3, alias="MAX_SIMULATION_ATTEMPTS")
    max_decomposition_attempts: int = Field(default=3, alias="MAX_DECOMPOSITION_ATTEMPTS")
    max_report_attempts: int = Field(default=5, alias="MAX_REPORT_ATTEMPTS")
    object_storage_bucket: str = Field(alias="OBJECT_STORAGE_BUCKET")
    artifact_storage_root: str = Field(default=".data/artifacts", alias="ARTIFACT_STORAGE_ROOT")
    simulation_engine_command: str = Field(
        default="python3 -m soil_engine.cli",
        alias="SIMULATION_ENGINE_COMMAND",
    )
    simulation_engine_pythonpath: str = Field(
        default="services/simulation-engine",
        alias="SIMULATION_ENGINE_PYTHONPATH",
    )
    worker_optional_when_redis_unavailable: bool = Field(
        default=False,
        alias="WORKER_OPTIONAL_WHEN_REDIS_UNAVAILABLE",
    )

    @property
    def queue_names(self) -> list[str]:
        return [
            self.simulation_queue_name,
            self.decomposition_queue_name,
            self.report_queue_name,
        ]

    @property
    def is_production(self) -> bool:
        return self.worker_env.lower() in {"production", "prod"}

    @model_validator(mode="after")
    def validate_runtime_safety(self) -> "Settings":
        if not self.is_production:
            return self

        errors: list[str] = []
        if self.worker_optional_when_redis_unavailable:
            errors.append("WORKER_OPTIONAL_WHEN_REDIS_UNAVAILABLE must be false in production.")
        if self.worker_concurrency < 1:
            errors.append("WORKER_CONCURRENCY must be at least 1 in production.")

        if errors:
            raise ValueError(" ".join(errors))

        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
