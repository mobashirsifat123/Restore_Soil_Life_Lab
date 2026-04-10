from __future__ import annotations

import pytest

from app.core.config import Settings


def _set_required_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:pass@db.example.com:5432/postgres")
    monkeypatch.setenv("REDIS_URL", "redis://cache.example.com:6379/0")


def test_production_rejects_insecure_debug_flags(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_required_env(monkeypatch)
    monkeypatch.setenv("API_ENV", "production")
    monkeypatch.setenv("API_DEBUG", "true")
    monkeypatch.setenv("DEBUG_AUTH_ENABLED", "true")
    monkeypatch.setenv("AUTH_SESSION_SECURE_COOKIE", "false")

    with pytest.raises(ValueError):
        Settings()


def test_production_rejects_wildcard_origin(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_required_env(monkeypatch)
    monkeypatch.setenv("API_ENV", "production")
    monkeypatch.setenv("API_DEBUG", "false")
    monkeypatch.setenv("DEBUG_AUTH_ENABLED", "false")
    monkeypatch.setenv("AUTH_SESSION_SECURE_COOKIE", "true")
    monkeypatch.setenv("ALLOWED_ORIGINS", '["*"]')

    with pytest.raises(ValueError):
        Settings()


def test_default_chat_provider_prefers_deepseek(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_required_env(monkeypatch)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-test-key")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    settings = Settings()

    assert settings.default_chat_provider == "deepseek"
    assert settings.default_chat_model == "deepseek-chat"
