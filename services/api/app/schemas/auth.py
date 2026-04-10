from __future__ import annotations

from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.common import ApiModel


class LoginRequest(ApiModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=255)
    organization_id: UUID | None = None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class RegisterRequest(ApiModel):
    name: str = Field(min_length=1, max_length=255)
    organization_name: str | None = Field(None, max_length=255)
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=255)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class ForgotPasswordRequest(ApiModel):
    email: str = Field(min_length=3, max_length=320)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class ForgotPasswordResponse(ApiModel):
    message: str
    development_code: str | None = None


class ResetPasswordRequest(ApiModel):
    email: str = Field(min_length=3, max_length=320)
    code: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=8, max_length=255)

    @field_validator("email")
    @classmethod
    def normalize_reset_email(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return value.strip()


class SessionUser(ApiModel):
    id: UUID
    email: str
    full_name: str | None = None
    roles: list[str]
    permissions: list[str]


class SessionResponse(ApiModel):
    user: SessionUser
    active_organization_id: UUID


class MemberPreferences(ApiModel):
    dashboard_density: str = "comfortable"
    notify_product_updates: bool = True
    notify_research_digest: bool = True
    notify_security_alerts: bool = True


class MemberProfileResponse(ApiModel):
    id: UUID
    email: str
    full_name: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    job_title: str | None = None
    location: str | None = None
    phone: str | None = None
    organization_name: str | None = None
    roles: list[str]
    preferences: MemberPreferences
    created_at: str
    updated_at: str


class UpdateMemberProfileRequest(ApiModel):
    full_name: str | None = Field(default=None, max_length=255)
    avatar_url: str | None = Field(default=None, max_length=2048)
    bio: str | None = Field(default=None, max_length=1200)
    job_title: str | None = Field(default=None, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    dashboard_density: str | None = Field(default=None, max_length=50)
    notify_product_updates: bool | None = None
    notify_research_digest: bool | None = None
    notify_security_alerts: bool | None = None


class ChangePasswordRequest(ApiModel):
    current_password: str = Field(min_length=8, max_length=255)
    new_password: str = Field(min_length=8, max_length=255)


class AuthSessionSummary(ApiModel):
    id: UUID
    user_agent: str | None = None
    ip_address: str | None = None
    created_at: str
    last_used_at: str | None = None
    expires_at: str
    is_current: bool = False


class AuthSessionListResponse(ApiModel):
    items: list[AuthSessionSummary]
