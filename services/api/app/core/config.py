import json
from functools import lru_cache
from pathlib import Path
from uuid import UUID

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

SERVICE_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(SERVICE_ROOT / ".env", REPO_ROOT / ".env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        env_parse_none_str="",
    )

    api_name: str = Field(default="Bio Soil API", alias="API_NAME")
    api_version: str = Field(default="0.1.0", alias="API_VERSION")
    api_env: str = Field(default="development", alias="API_ENV")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_debug: bool = Field(default=True, alias="API_DEBUG")
    auth_session_cookie_name: str = Field(default="bio_session", alias="AUTH_SESSION_COOKIE_NAME")
    auth_session_ttl_hours: int = Field(default=168, alias="AUTH_SESSION_TTL_HOURS")
    auth_session_secure_cookie: bool = Field(default=False, alias="AUTH_SESSION_SECURE_COOKIE")
    admin_user_emails_raw: str = Field(default="", alias="ADMIN_USER_EMAILS")
    debug_auth_enabled: bool = Field(default=False, alias="DEBUG_AUTH_ENABLED")
    debug_auth_user_id: UUID = Field(
        default=UUID("00000000-0000-7000-0000-000000000001"),
        alias="DEBUG_AUTH_USER_ID",
    )
    debug_auth_organization_id: UUID = Field(
        default=UUID("00000000-0000-7000-0000-000000000101"),
        alias="DEBUG_AUTH_ORGANIZATION_ID",
    )
    debug_auth_user_email: str = Field(
        default="scientist@example.com",
        alias="DEBUG_AUTH_USER_EMAIL",
    )
    debug_auth_roles: list[str] = Field(default_factory=lambda: ["org_admin"], alias="DEBUG_AUTH_ROLES")
    debug_auth_permissions: list[str] = Field(
        default_factory=lambda: [
            "projects:read",
            "projects:write",
            "soil_samples:read",
            "soil_samples:write",
            "scenarios:read",
            "scenarios:write",
            "runs:read",
            "runs:write",
        ],
        alias="DEBUG_AUTH_PERMISSIONS",
    )
    database_url: str = Field(alias="DATABASE_URL")
    database_echo: bool = Field(default=False, alias="DATABASE_ECHO")
    redis_url: str = Field(alias="REDIS_URL")
    allowed_origins_raw: str = Field(default="", alias="ALLOWED_ORIGINS")
    deepseek_api_key: str | None = Field(default=None, alias="DEEPSEEK_API_KEY")
    deepseek_base_url: str = Field(default="https://api.deepseek.com", alias="DEEPSEEK_BASE_URL")
    deepseek_model: str = Field(default="deepseek-chat", alias="DEEPSEEK_MODEL")
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-1.5-flash", alias="GEMINI_MODEL")
    gemini_vision_model: str = Field(default="gemini-1.5-flash", alias="GEMINI_VISION_MODEL")
    simulation_queue_name: str = Field(default="jobs:simulation", alias="SIMULATION_QUEUE_NAME")
    simulation_engine_name: str = Field(default="soil-engine", alias="SIMULATION_ENGINE_NAME")
    simulation_engine_version: str = Field(default="0.1.0", alias="SIMULATION_ENGINE_VERSION")
    simulation_input_schema_version: str = Field(
        default="1.0.0",
        alias="SIMULATION_INPUT_SCHEMA_VERSION",
    )
    run_inline_fallback_enabled: bool = Field(
        default=False,
        alias="RUN_INLINE_FALLBACK_ENABLED",
    )
    otel_exporter_otlp_endpoint: str | None = Field(default=None, alias="OTEL_EXPORTER_OTLP_ENDPOINT")

    @property
    def is_development(self) -> bool:
        return self.api_env.lower() in {"development", "dev", "local"}

    @property
    def is_production(self) -> bool:
        return self.api_env.lower() in {"production", "prod"}

    @property
    def default_chat_provider(self) -> str:
        if self.deepseek_api_key:
            return "deepseek"
        if self.gemini_api_key:
            return "gemini"
        return "deepseek"

    @property
    def default_chat_model(self) -> str:
        if self.default_chat_provider == "gemini":
            return self.gemini_model
        return self.deepseek_model

    @field_validator("debug_auth_roles", "debug_auth_permissions", mode="before")
    @classmethod
    def parse_string_list(cls, value: object) -> list[str]:
        if value is None or value == "":
            return []
        if isinstance(value, list):
            return [str(item) for item in value]
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("["):
                return [str(item) for item in json.loads(stripped)]
            return [item.strip() for item in stripped.split(",") if item.strip()]
        raise TypeError("Expected a JSON array or comma-separated string.")

    @property
    def allowed_origins(self) -> list[str]:
        raw = self.allowed_origins_raw.strip()
        if not raw:
            return []
        # Strip surrounding quotes that .env files sometimes add
        raw = raw.strip("'\"")
        if raw.startswith("["):
            try:
                return [str(item) for item in json.loads(raw)]
            except json.JSONDecodeError:
                pass
        return [item.strip().strip("'\"" ) for item in raw.split(",") if item.strip()]

    @property
    def admin_user_emails(self) -> set[str]:
        raw = self.admin_user_emails_raw.strip()
        if not raw:
            return set()
        raw = raw.strip("'\"")
        if raw.startswith("["):
            try:
                return {str(item).strip().lower() for item in json.loads(raw) if str(item).strip()}
            except json.JSONDecodeError:
                pass
        return {item.strip().strip("'\"").lower() for item in raw.split(",") if item.strip()}

    @model_validator(mode="after")
    def validate_runtime_safety(self) -> "Settings":
        if not self.is_production:
            return self

        errors: list[str] = []

        if self.api_debug:
            errors.append("API_DEBUG must be false in production.")
        if self.debug_auth_enabled:
            errors.append("DEBUG_AUTH_ENABLED must be false in production.")
        if not self.auth_session_secure_cookie:
            errors.append("AUTH_SESSION_SECURE_COOKIE must be true in production.")
        if any(origin.strip() == "*" for origin in self.allowed_origins):
            errors.append("ALLOWED_ORIGINS cannot contain '*' in production.")

        if errors:
            raise ValueError(" ".join(errors))

        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
