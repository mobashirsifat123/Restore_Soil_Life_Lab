from __future__ import annotations

import json
from urllib import error, request

from app.core.config import Settings


class ProviderService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def generate_reply(
        self,
        *,
        provider: str | None = None,
        model: str | None = None,
        system_prompt: str,
        user_prompt: str,
        grounded_context: str,
    ) -> str | None:
        resolved = self._resolve_provider_config(provider=provider, model=model)
        if resolved is None:
            return None
        resolved_provider, resolved_model = resolved

        if resolved_provider == "gemini":
            return self._generate_gemini_reply(
                model=resolved_model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                grounded_context=grounded_context,
            )
        return self._generate_deepseek_reply(
            model=resolved_model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            grounded_context=grounded_context,
        )

    def _resolve_provider_config(self, *, provider: str | None, model: str | None) -> tuple[str, str] | None:
        requested_provider = (provider or self.settings.default_chat_provider).strip().lower()

        if requested_provider == "deepseek" and self.settings.deepseek_api_key:
            return ("deepseek", model or self.settings.deepseek_model)
        if requested_provider == "gemini" and self.settings.gemini_api_key:
            return ("gemini", model or self.settings.gemini_model)

        if self.settings.deepseek_api_key:
            return ("deepseek", self.settings.deepseek_model)
        if self.settings.gemini_api_key:
            return ("gemini", self.settings.gemini_model)
        return None

    def _generate_deepseek_reply(
        self,
        *,
        model: str,
        system_prompt: str,
        user_prompt: str,
        grounded_context: str,
    ) -> str | None:
        if not self.settings.deepseek_api_key:
            return None

        endpoint = f"{self.settings.deepseek_base_url.rstrip('/')}/chat/completions"
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt.strip()},
                {
                    "role": "user",
                    "content": "\n\n".join(
                        part
                        for part in [
                            f"Grounded context:\n{grounded_context.strip()}",
                            f"User request:\n{user_prompt.strip()}",
                        ]
                        if part and part.strip()
                    ),
                },
            ],
            "stream": False,
        }
        req = request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.settings.deepseek_api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=20) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (error.URLError, TimeoutError, json.JSONDecodeError):
            return None

        choices = body.get("choices") or []
        if not choices:
            return None
        message = choices[0].get("message") or {}
        return self._extract_text(message.get("content"))

    def _generate_gemini_reply(
        self,
        *,
        model: str,
        system_prompt: str,
        user_prompt: str,
        grounded_context: str,
    ) -> str | None:
        if not self.settings.gemini_api_key:
            return None

        endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={self.settings.gemini_api_key}"
        )
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": "\n\n".join(
                                part
                                for part in [
                                    system_prompt.strip(),
                                    f"Grounded context:\n{grounded_context.strip()}",
                                    f"User request:\n{user_prompt.strip()}",
                                ]
                                if part and part.strip()
                            )
                        }
                    ],
                }
            ]
        }
        req = request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=20) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (error.URLError, TimeoutError, json.JSONDecodeError):
            return None

        candidates = body.get("candidates") or []
        if not candidates:
            return None
        parts = candidates[0].get("content", {}).get("parts") or []
        texts = [part.get("text", "").strip() for part in parts if part.get("text")]
        return "\n\n".join(texts).strip() or None

    def _extract_text(self, content: object) -> str | None:
        if isinstance(content, str):
            text = content.strip()
            return text or None
        if isinstance(content, list):
            texts = [
                item.get("text", "").strip()
                for item in content
                if isinstance(item, dict) and item.get("type") == "text" and item.get("text")
            ]
            joined = "\n\n".join(texts).strip()
            return joined or None
        return None
