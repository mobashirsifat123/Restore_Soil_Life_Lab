from __future__ import annotations

import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from typing import Final
from urllib.parse import quote, urlsplit
from uuid import UUID

from fastapi import Request

from app.core.config import Settings
from app.core.errors import AppError
from app.domain.auth import AuthenticatedUser
from app.domain.permissions import Permissions
from app.repositories.auth_repository import AuthRepository
from app.schemas.auth import (
    AuthSessionListResponse,
    AuthSessionSummary,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    MemberPreferences,
    MemberProfileResponse,
    RegisterRequest,
    ResetPasswordRequest,
    SessionResponse,
    SessionUser,
    UpdateMemberProfileRequest,
)
from app.security.passwords import (
    generate_password_reset_token,
    generate_session_token,
    hash_password,
    hash_password_reset_token,
    hash_recovery_code,
    hash_session_token,
    verify_password,
)

ROLE_PERMISSION_MAP: Final[dict[str, set[str]]] = {
    "org_admin": {
        Permissions.PROJECT_READ,
        Permissions.PROJECT_WRITE,
        Permissions.SAMPLE_READ,
        Permissions.SAMPLE_WRITE,
        Permissions.SCENARIO_READ,
        Permissions.SCENARIO_WRITE,
        Permissions.RUN_READ,
        Permissions.RUN_SUBMIT,
        Permissions.REPORT_READ,
        Permissions.REPORT_WRITE,
    },
    "scientist": {
        Permissions.PROJECT_READ,
        Permissions.PROJECT_WRITE,
        Permissions.SAMPLE_READ,
        Permissions.SAMPLE_WRITE,
        Permissions.SCENARIO_READ,
        Permissions.SCENARIO_WRITE,
        Permissions.RUN_READ,
        Permissions.RUN_SUBMIT,
        Permissions.REPORT_READ,
    },
    "viewer": {
        Permissions.PROJECT_READ,
        Permissions.SAMPLE_READ,
        Permissions.SCENARIO_READ,
        Permissions.RUN_READ,
        Permissions.REPORT_READ,
    },
}


@dataclass(slots=True)
class AuthSessionResult:
    session: SessionResponse
    session_token: str


class AuthService:
    def __init__(self, repository: AuthRepository, settings: Settings) -> None:
        self.repository = repository
        self.settings = settings

    def login(
        self,
        *,
        payload: LoginRequest,
        user_agent: str | None,
        ip_address: str | None,
    ) -> AuthSessionResult:
        user = self.repository.get_user_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.password_hash):
            self.repository.create_activity_log(
                organization_id=user.organization_id if user is not None else None,
                activity_type="failed_login",
                activity_label="Failed sign in",
                user_id=user.id if user is not None else None,
                user_email=payload.email,
                details="Invalid email or password.",
            )
            raise AppError(
                status_code=401,
                code="invalid_credentials",
                message="Invalid email or password.",
            )

        membership = self._resolve_membership(
            user_id=user.id,
            requested_organization_id=payload.organization_id,
            default_organization_id=user.organization_id,
        )
        self.repository.update_user_last_login(user)

        session_token = generate_session_token()
        self.repository.create_session(
            user_id=user.id,
            organization_id=membership.organization_id,
            token_hash=hash_session_token(session_token),
            ttl_hours=self.settings.auth_session_ttl_hours,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        current_user = self._build_authenticated_user(
            user_id=user.id,
            organization_id=membership.organization_id,
            email=user.email,
            full_name=user.full_name,
            role=membership.role,
            membership_permissions=membership.permissions_json,
        )
        self.repository.create_activity_log(
            organization_id=membership.organization_id,
            activity_type="user_login",
            activity_label="Signed in",
            user_id=user.id,
            user_email=user.email,
            details="Authenticated session created.",
        )
        return AuthSessionResult(
            session=self.build_session(current_user),
            session_token=session_token,
        )

    def register(
        self,
        *,
        payload: RegisterRequest,
        user_agent: str | None,
        ip_address: str | None,
    ) -> AuthSessionResult:
        existing = self.repository.get_user_by_email(payload.email)
        if existing is not None:
            raise AppError(
                status_code=400,
                code="email_in_use",
                message="An account with this email already exists.",
            )
            
        org_name = payload.organization_name if payload.organization_name else f"{payload.name}'s Workspace"
        user, membership = self.repository.create_user_and_org(
            email=payload.email,
            password_hash=hash_password(payload.password),
            full_name=payload.name,
            org_name=org_name,
            role=self._initial_role_for_email(payload.email),
        )
        
        session_token = generate_session_token()
        self.repository.create_session(
            user_id=user.id,
            organization_id=membership.organization_id,
            token_hash=hash_session_token(session_token),
            ttl_hours=self.settings.auth_session_ttl_hours,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        
        current_user = self._build_authenticated_user(
            user_id=user.id,
            organization_id=membership.organization_id,
            email=user.email,
            full_name=user.full_name,
            role=membership.role,
            membership_permissions=membership.permissions_json,
        )
        self.repository.create_activity_log(
            organization_id=membership.organization_id,
            activity_type="user_signup",
            activity_label="Signed up",
            user_id=user.id,
            user_email=user.email,
            details=full_name if (full_name := payload.name.strip()) else "New account created.",
        )
        return AuthSessionResult(
            session=self.build_session(current_user),
            session_token=session_token,
        )

    def forgot_password(
        self,
        *,
        payload: ForgotPasswordRequest,
        user_agent: str | None,
        ip_address: str | None,
        frontend_origin: str | None = None,
        frontend_referer: str | None = None,
    ) -> ForgotPasswordResponse:
        # FRONTEND_URL (or a forwarded browser Origin) is required so reset links point at the web app.
        frontend_url = self._resolve_frontend_url(
            frontend_origin=frontend_origin,
            frontend_referer=frontend_referer,
        )
        if frontend_url is None:
            raise AppError(
                status_code=503,
                code="password_reset_not_configured",
                message="Password reset is not configured. Set FRONTEND_URL for reset links.",
            )

        # SMTP_* env vars are optional in local development, but production needs them to deliver reset emails.
        if not self.settings.password_reset_email_enabled and not (
            self.settings.is_development or self.settings.api_debug
        ):
            raise AppError(
                status_code=503,
                code="password_reset_not_configured",
                message="Password reset email delivery is not configured.",
            )

        user = self.repository.get_user_by_email(payload.email)
        if user is None:
            return ForgotPasswordResponse(
                message="If that account exists, a password reset link has been sent."
            )

        reset_token = generate_password_reset_token()
        reset_url = f"{frontend_url.rstrip('/')}/reset-password?token={quote(reset_token)}"
        self.repository.create_password_reset_token(
            user_id=user.id,
            # Stored as a hash so leaked database rows cannot be used to reset passwords.
            code_hash=hash_password_reset_token(reset_token),
            ttl_minutes=15,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        if self.settings.password_reset_email_enabled:
            self._send_password_reset_email(email=user.email, reset_url=reset_url)

        self.repository.create_activity_log(
            organization_id=user.organization_id,
            activity_type="password_reset_requested",
            activity_label="Requested password reset",
            user_id=user.id,
            user_email=user.email,
            details="Password reset link generated.",
        )
        return ForgotPasswordResponse(
            message="If that account exists, a password reset link has been sent.",
            development_reset_url=(
                reset_url if (self.settings.is_development or self.settings.api_debug) else None
            ),
        )

    def reset_password(self, *, payload: ResetPasswordRequest) -> None:
        bundle = None
        if payload.token:
            bundle = self.repository.get_valid_password_reset_token_by_hash(
                token_hash=hash_password_reset_token(payload.token),
            )
        elif payload.email and payload.code:
            bundle = self.repository.get_valid_password_reset_token(
                email=payload.email,
                code_hash=hash_recovery_code(payload.code),
            )

        if bundle is None:
            raise AppError(
                status_code=400,
                code="invalid_recovery_token",
                message="The password reset link or recovery code is invalid or expired.",
            )

        token, user = bundle
        self.repository.update_password_with_token(
            user=user,
            token=token,
            password_hash=hash_password(payload.new_password),
        )
        self.repository.create_activity_log(
            organization_id=user.organization_id,
            activity_type="password_reset_completed",
            activity_label="Reset password",
            user_id=user.id,
            user_email=user.email,
            details="Password updated successfully.",
        )

    def get_profile(self, current_user: AuthenticatedUser) -> MemberProfileResponse:
        user = self.repository.get_user_by_id(current_user.user_id)
        if user is None:
            raise AppError(status_code=404, code="user_not_found", message="User account not found.")
        return self._build_member_profile(user=user, roles=current_user.roles)

    def update_profile(
        self,
        *,
        current_user: AuthenticatedUser,
        payload: UpdateMemberProfileRequest,
    ) -> MemberProfileResponse:
        user = self.repository.get_user_by_id(current_user.user_id)
        if user is None:
            raise AppError(status_code=404, code="user_not_found", message="User account not found.")

        existing_metadata = dict(user.metadata_json or {})
        existing_preferences = dict(existing_metadata.get("preferences") or {})
        next_preferences = {
            "dashboardDensity": payload.dashboard_density or existing_preferences.get("dashboardDensity", "comfortable"),
            "notifyProductUpdates": payload.notify_product_updates
            if payload.notify_product_updates is not None
            else existing_preferences.get("notifyProductUpdates", True),
            "notifyResearchDigest": payload.notify_research_digest
            if payload.notify_research_digest is not None
            else existing_preferences.get("notifyResearchDigest", True),
            "notifySecurityAlerts": payload.notify_security_alerts
            if payload.notify_security_alerts is not None
            else existing_preferences.get("notifySecurityAlerts", True),
        }

        next_metadata = {
            **existing_metadata,
            "avatarUrl": self._normalize_optional_text(payload.avatar_url),
            "bio": self._normalize_optional_text(payload.bio),
            "jobTitle": self._normalize_optional_text(payload.job_title),
            "location": self._normalize_optional_text(payload.location),
            "phone": self._normalize_optional_text(payload.phone),
            "preferences": next_preferences,
        }
        user = self.repository.update_user_profile(
            user=user,
            full_name=self._normalize_optional_text(payload.full_name),
            metadata_json=next_metadata,
        )
        self.repository.create_activity_log(
            organization_id=current_user.organization_id,
            activity_type="profile_updated",
            activity_label="Updated profile",
            user_id=current_user.user_id,
            user_email=current_user.email,
            details="Member account details were updated.",
        )
        return self._build_member_profile(user=user, roles=current_user.roles)

    def change_password(
        self,
        *,
        current_user: AuthenticatedUser,
        payload: ChangePasswordRequest,
    ) -> None:
        user = self.repository.get_user_by_id(current_user.user_id)
        if user is None:
            raise AppError(status_code=404, code="user_not_found", message="User account not found.")
        if not user.password_hash or not verify_password(payload.current_password, user.password_hash):
            raise AppError(
                status_code=400,
                code="invalid_current_password",
                message="Current password is incorrect.",
            )
        if payload.current_password == payload.new_password:
            raise AppError(
                status_code=400,
                code="password_unchanged",
                message="Choose a new password that is different from the current one.",
            )
        self.repository.update_user_password(user=user, password_hash=hash_password(payload.new_password))
        self.repository.create_activity_log(
            organization_id=current_user.organization_id,
            activity_type="password_changed",
            activity_label="Changed password",
            user_id=current_user.user_id,
            user_email=current_user.email,
            details="Member password updated.",
        )

    def list_sessions(self, request: Request, current_user: AuthenticatedUser) -> AuthSessionListResponse:
        current_token_hash = self._current_token_hash(request)
        sessions = self.repository.list_sessions_for_user(current_user.user_id)
        return AuthSessionListResponse(
            items=[
                AuthSessionSummary(
                    id=session.id,
                    user_agent=session.user_agent,
                    ip_address=session.ip_address,
                    created_at=session.created_at.isoformat(),
                    last_used_at=session.last_used_at.isoformat() if session.last_used_at else None,
                    expires_at=session.expires_at.isoformat(),
                    is_current=bool(current_token_hash and session.token_hash == current_token_hash),
                )
                for session in sessions
            ]
        )

    def revoke_session_by_id(
        self,
        *,
        current_user: AuthenticatedUser,
        session_id: UUID,
        request: Request,
    ) -> None:
        auth_session = self.repository.get_session_by_id(user_id=current_user.user_id, session_id=session_id)
        if auth_session is None:
            raise AppError(status_code=404, code="session_not_found", message="Session not found.")
        current_token_hash = self._current_token_hash(request)
        if current_token_hash and auth_session.token_hash == current_token_hash:
            raise AppError(
                status_code=400,
                code="cannot_revoke_current_session",
                message="Use sign out to revoke the current session.",
            )
        self.repository.revoke_session_record(auth_session)

    def revoke_other_sessions(self, *, current_user: AuthenticatedUser, request: Request) -> None:
        self.repository.revoke_other_sessions(
            user_id=current_user.user_id,
            keep_token_hash=self._current_token_hash(request),
        )
        self.repository.create_activity_log(
            organization_id=current_user.organization_id,
            activity_type="revoked_other_sessions",
            activity_label="Signed out other sessions",
            user_id=current_user.user_id,
            user_email=current_user.email,
            details="All other active sessions were revoked.",
        )

    def authenticate_request(self, request: Request) -> AuthenticatedUser:
        session_token = self._extract_session_token(request)
        if session_token is None:
            raise AppError(
                status_code=401,
                code="auth_required",
                message="Authentication is required.",
            )

        bundle = self.repository.get_session_bundle(hash_session_token(session_token))
        if bundle is None:
            raise AppError(
                status_code=401,
                code="invalid_session",
                message="Your session is invalid or expired.",
            )

        auth_session, user, membership = bundle
        self.repository.touch_session(auth_session)
        return self._build_authenticated_user(
            user_id=user.id,
            organization_id=membership.organization_id,
            email=user.email,
            full_name=user.full_name,
            role=membership.role,
            membership_permissions=membership.permissions_json,
        )

    def logout(self, request: Request) -> None:
        session_token = self._extract_session_token(request)
        if session_token is None:
            return
        self.repository.revoke_session(hash_session_token(session_token))

    def build_session(self, current_user: AuthenticatedUser) -> SessionResponse:
        return SessionResponse(
            user=SessionUser(
                id=current_user.user_id,
                email=current_user.email,
                full_name=current_user.full_name,
                roles=current_user.roles,
                permissions=sorted(current_user.permissions),
            ),
            active_organization_id=current_user.organization_id,
        )

    def _resolve_membership(
        self,
        *,
        user_id: UUID,
        requested_organization_id: UUID | None,
        default_organization_id: UUID,
    ):
        if requested_organization_id is not None:
            membership = self.repository.get_active_membership(
                user_id=user_id,
                organization_id=requested_organization_id,
            )
            if membership is None:
                raise AppError(
                    status_code=403,
                    code="organization_access_denied",
                    message="You do not have access to the requested organization.",
                    details={"organizationId": str(requested_organization_id)},
                )
            return membership

        memberships = self.repository.list_active_memberships_for_user(user_id)
        if not memberships:
            raise AppError(
                status_code=403,
                code="organization_access_denied",
                message="You do not have an active organization membership.",
            )

        for membership in memberships:
            if membership.organization_id == default_organization_id:
                return membership
        return memberships[0]

    def _is_admin_email(self, email: str) -> bool:
        return email.strip().lower() in self.settings.admin_user_emails

    def _initial_role_for_email(self, email: str) -> str:
        return "org_admin" if self._is_admin_email(email) else "scientist"

    def _effective_role(self, *, email: str, role: str) -> str:
        if self._is_admin_email(email):
            return "org_admin"
        if role == "org_admin":
            return "scientist"
        return role

    def _extract_session_token(self, request: Request) -> str | None:
        authorization = request.headers.get("authorization")
        if authorization:
            scheme, _, credentials = authorization.partition(" ")
            if scheme.lower() == "bearer" and credentials.strip():
                return credentials.strip()

        session_token = request.cookies.get(self.settings.auth_session_cookie_name)
        if session_token:
            return session_token
        return None

    def _current_token_hash(self, request: Request) -> str | None:
        token = self._extract_session_token(request)
        if token is None:
            return None
        return hash_session_token(token)

    def _build_authenticated_user(
        self,
        *,
        user_id: UUID,
        organization_id: UUID,
        email: str,
        full_name: str | None,
        role: str,
        membership_permissions: list,
    ) -> AuthenticatedUser:
        effective_role = self._effective_role(email=email, role=role)
        permissions = set(ROLE_PERMISSION_MAP.get(effective_role, set()))
        permissions.update(str(permission) for permission in membership_permissions)
        return AuthenticatedUser(
            user_id=user_id,
            organization_id=organization_id,
            email=email,
            full_name=full_name,
            roles=[effective_role],
            permissions=permissions,
        )

    def _build_member_profile(self, *, user, roles: list[str]) -> MemberProfileResponse:
        metadata = dict(user.metadata_json or {})
        preferences = dict(metadata.get("preferences") or {})
        return MemberProfileResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            avatar_url=metadata.get("avatarUrl"),
            bio=metadata.get("bio"),
            job_title=metadata.get("jobTitle"),
            location=metadata.get("location"),
            phone=metadata.get("phone"),
            organization_name=user.organization.name if user.organization else None,
            roles=roles,
            preferences=MemberPreferences(
                dashboard_density=preferences.get("dashboardDensity", "comfortable"),
                notify_product_updates=preferences.get("notifyProductUpdates", True),
                notify_research_digest=preferences.get("notifyResearchDigest", True),
                notify_security_alerts=preferences.get("notifySecurityAlerts", True),
            ),
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat(),
        )

    def _normalize_optional_text(self, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    def _resolve_frontend_url(
        self,
        *,
        frontend_origin: str | None,
        frontend_referer: str | None,
    ) -> str | None:
        if self.settings.frontend_url:
            return self.settings.frontend_url.rstrip("/")
        if frontend_origin:
            return frontend_origin.rstrip("/")
        if frontend_referer:
            parts = urlsplit(frontend_referer)
            if parts.scheme and parts.netloc:
                return f"{parts.scheme}://{parts.netloc}"
        if self.settings.allowed_origins:
            return self.settings.allowed_origins[0].rstrip("/")
        return None

    def _send_password_reset_email(self, *, email: str, reset_url: str) -> None:
        if not self.settings.password_reset_email_enabled or not self.settings.smtp_host:
            return

        message = EmailMessage()
        message["Subject"] = "Reset your Bio Soil password"
        message["From"] = self.settings.smtp_from_email
        message["To"] = email
        message.set_content(
            "We received a request to reset your Bio Soil password.\n\n"
            f"Use this link to choose a new password:\n{reset_url}\n\n"
            "If you did not request this, you can safely ignore this email."
        )

        try:
            with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=20) as server:
                if self.settings.smtp_starttls:
                    server.starttls()
                if self.settings.smtp_username:
                    server.login(self.settings.smtp_username, self.settings.smtp_password or "")
                server.send_message(message)
        except OSError as exc:
            raise AppError(
                status_code=502,
                code="password_reset_delivery_failed",
                message="Could not send the password reset email.",
            ) from exc
