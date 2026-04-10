from __future__ import annotations

import json
from types import SimpleNamespace
from urllib import request

from app.services.chat.provider_service import ProviderService


class _FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def _settings(**overrides: object) -> SimpleNamespace:
    values = {
        "deepseek_api_key": None,
        "deepseek_base_url": "https://api.deepseek.com",
        "deepseek_model": "deepseek-chat",
        "gemini_api_key": None,
        "gemini_model": "gemini-1.5-flash",
        "default_chat_provider": "deepseek",
        "default_chat_model": "deepseek-chat",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_generate_reply_uses_deepseek_chat_completions(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(req: request.Request, timeout: int) -> _FakeResponse:
        captured["url"] = req.full_url
        captured["headers"] = {key.lower(): value for key, value in req.header_items()}
        captured["body"] = json.loads(req.data.decode("utf-8"))
        captured["timeout"] = timeout
        return _FakeResponse({"choices": [{"message": {"content": "DeepSeek says hello"}}]})

    monkeypatch.setattr(request, "urlopen", fake_urlopen)

    service = ProviderService(_settings(deepseek_api_key="deepseek-test-key"))
    reply = service.generate_reply(
        provider="deepseek",
        model="deepseek-chat",
        system_prompt="You are a farming assistant.",
        user_prompt="How is my soil?",
        grounded_context="Organic matter is moderate.",
    )

    assert reply == "DeepSeek says hello"
    assert captured["url"] == "https://api.deepseek.com/chat/completions"
    assert captured["timeout"] == 20
    assert captured["headers"]["authorization"] == "Bearer deepseek-test-key"
    assert captured["body"] == {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a farming assistant."},
            {
                "role": "user",
                "content": "Grounded context:\nOrganic matter is moderate.\n\nUser request:\nHow is my soil?",
            },
        ],
        "stream": False,
    }


def test_generate_reply_falls_back_to_deepseek_for_legacy_gemini_assistant(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(req: request.Request, timeout: int) -> _FakeResponse:
        captured["url"] = req.full_url
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return _FakeResponse({"choices": [{"message": {"content": "Fallback provider reply"}}]})

    monkeypatch.setattr(request, "urlopen", fake_urlopen)

    service = ProviderService(_settings(deepseek_api_key="deepseek-test-key"))
    reply = service.generate_reply(
        provider="gemini",
        model="gemini-1.5-flash",
        system_prompt="System prompt",
        user_prompt="User prompt",
        grounded_context="Grounded context",
    )

    assert reply == "Fallback provider reply"
    assert captured["url"] == "https://api.deepseek.com/chat/completions"
    assert captured["body"]["model"] == "deepseek-chat"


def test_generate_reply_returns_none_without_any_provider_keys() -> None:
    service = ProviderService(_settings())

    reply = service.generate_reply(
        provider="deepseek",
        model="deepseek-chat",
        system_prompt="System prompt",
        user_prompt="User prompt",
        grounded_context="Grounded context",
    )

    assert reply is None
