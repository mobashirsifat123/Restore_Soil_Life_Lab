from __future__ import annotations

import pytest

from app.core.config import Settings


def _set_required_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REDIS_URL", "redis://cache.example.com:6379/0")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:pass@db.example.com:5432/postgres")
    monkeypatch.setenv("OBJECT_STORAGE_BUCKET", "bio-prod-artifacts")


def test_production_rejects_optional_worker_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_required_env(monkeypatch)
    monkeypatch.setenv("WORKER_ENV", "production")
    monkeypatch.setenv("WORKER_OPTIONAL_WHEN_REDIS_UNAVAILABLE", "true")

    with pytest.raises(ValueError):
        Settings()
