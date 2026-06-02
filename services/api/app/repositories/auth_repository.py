from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.models import (
    AuthSession,
    Organization,
    OrganizationMembership,
    PasswordResetToken,
    User,
    UserActivityLog,
)


class AuthRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_user_by_email(self, email: str) -> User | None:
        statement = select(User).where(
            User.email == email,
            User.deleted_at.is_(None),
            User.is_active.is_(True),
        )
        return self.session.scalar(statement)

    def get_user_by_id(self, user_id: UUID) -> User | None:
        statement = select(User).where(
            User.id == user_id,
            User.deleted_at.is_(None),
            User.is_active.is_(True),
        )
        return self.session.scalar(statement)

    def create_user_and_org(
        self,
        *,
        email: str,
        password_hash: str,
        full_name: str,
        org_name: str,
        role: str = "scientist",
    ) -> tuple[User, OrganizationMembership]:
        import re
        import uuid
        
        slug_base = re.sub(r'[^a-z0-9]+', '-', org_name.lower()).strip('-')
        if not slug_base:
            slug_base = "org"
        slug = f"{slug_base}-{str(uuid.uuid4())[:8]}"

        org = Organization(name=org_name, slug=slug)
        self.session.add(org)
        
        user = User(
            email=email,
            full_name=full_name,
            password_hash=password_hash,
            organization=org
        )
        self.session.add(user)
        
        membership = OrganizationMembership(
            organization=org,
            user=user,
            role=role,
            is_default=True
        )
        self.session.add(membership)
        self.session.commit()
        self.session.refresh(user)
        self.session.refresh(membership)
        
        return user, membership

    def list_active_memberships_for_user(self, user_id: UUID) -> list[OrganizationMembership]:
        statement = (
            select(OrganizationMembership)
            .join(Organization, Organization.id == OrganizationMembership.organization_id)
            .where(
                OrganizationMembership.user_id == user_id,
                OrganizationMembership.is_active.is_(True),
                Organization.is_active.is_(True),
                Organization.deleted_at.is_(None),
            )
            .order_by(
                OrganizationMembership.is_default.desc(),
                OrganizationMembership.created_at.asc(),
            )
        )
        return list(self.session.scalars(statement))

    def get_active_membership(
        self,
        *,
        user_id: UUID,
        organization_id: UUID,
    ) -> OrganizationMembership | None:
        statement = (
            select(OrganizationMembership)
            .join(Organization, Organization.id == OrganizationMembership.organization_id)
            .where(
                OrganizationMembership.user_id == user_id,
                OrganizationMembership.organization_id == organization_id,
                OrganizationMembership.is_active.is_(True),
                Organization.is_active.is_(True),
                Organization.deleted_at.is_(None),
            )
        )
        return self.session.scalar(statement)

    def create_session(
        self,
        *,
        user_id: UUID,
        organization_id: UUID,
        token_hash: str,
        ttl_hours: int,
        user_agent: str | None,
        ip_address: str | None,
    ) -> AuthSession:
        now = datetime.now(UTC)
        auth_session = AuthSession(
            user_id=user_id,
            organization_id=organization_id,
            token_hash=token_hash,
            expires_at=now + timedelta(hours=ttl_hours),
            last_used_at=now,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self.session.add(auth_session)
        self.session.commit()
        self.session.refresh(auth_session)
        return auth_session

    def get_session_bundle(self, token_hash: str):
        statement = (
            select(AuthSession, User, OrganizationMembership)
            .join(User, User.id == AuthSession.user_id)
            .join(
                OrganizationMembership,
                and_(
                    OrganizationMembership.user_id == AuthSession.user_id,
                    OrganizationMembership.organization_id == AuthSession.organization_id,
                ),
            )
            .join(Organization, Organization.id == AuthSession.organization_id)
            .where(
                AuthSession.token_hash == token_hash,
                AuthSession.revoked_at.is_(None),
                AuthSession.expires_at > datetime.now(UTC),
                User.deleted_at.is_(None),
                User.is_active.is_(True),
                OrganizationMembership.is_active.is_(True),
                Organization.is_active.is_(True),
                Organization.deleted_at.is_(None),
            )
        )
        return self.session.execute(statement).first()

    def touch_session(self, auth_session: AuthSession) -> None:
        auth_session.last_used_at = datetime.now(UTC)
        self.session.add(auth_session)
        self.session.commit()

    def revoke_session(self, token_hash: str) -> None:
        statement = select(AuthSession).where(
            AuthSession.token_hash == token_hash,
            AuthSession.revoked_at.is_(None),
        )
        auth_session = self.session.scalar(statement)
        if auth_session is None:
            return

        now = datetime.now(UTC)
        auth_session.revoked_at = now
        auth_session.updated_at = now
        self.session.add(auth_session)
        self.session.commit()

    def update_user_last_login(self, user: User) -> None:
        user.last_login_at = datetime.now(UTC)
        self.session.add(user)
        self.session.commit()

    def update_user_profile(
        self,
        *,
        user: User,
        full_name: str | None,
        metadata_json: dict,
    ) -> User:
        user.full_name = full_name
        user.metadata_json = metadata_json
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def update_user_password(self, *, user: User, password_hash: str) -> User:
        user.password_hash = password_hash
        user.updated_at = datetime.now(UTC)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def list_sessions_for_user(self, user_id: UUID) -> list[AuthSession]:
        statement = (
            select(AuthSession)
            .where(
                AuthSession.user_id == user_id,
                AuthSession.revoked_at.is_(None),
            )
            .order_by(AuthSession.last_used_at.desc().nullslast(), AuthSession.created_at.desc())
        )
        return list(self.session.scalars(statement))

    def get_session_by_id(self, *, user_id: UUID, session_id: UUID) -> AuthSession | None:
        statement = select(AuthSession).where(
            AuthSession.id == session_id,
            AuthSession.user_id == user_id,
            AuthSession.revoked_at.is_(None),
        )
        return self.session.scalar(statement)

    def revoke_session_record(self, auth_session: AuthSession) -> None:
        now = datetime.now(UTC)
        auth_session.revoked_at = now
        auth_session.updated_at = now
        self.session.add(auth_session)
        self.session.commit()

    def revoke_other_sessions(self, *, user_id: UUID, keep_token_hash: str | None) -> None:
        statement = select(AuthSession).where(
            AuthSession.user_id == user_id,
            AuthSession.revoked_at.is_(None),
        )
        for auth_session in self.session.scalars(statement):
            if keep_token_hash and auth_session.token_hash == keep_token_hash:
                continue
            auth_session.revoked_at = datetime.now(UTC)
            auth_session.updated_at = datetime.now(UTC)
            self.session.add(auth_session)
        self.session.commit()

    def create_password_reset_token(
        self,
        *,
        user_id: UUID,
        code_hash: str,
        ttl_minutes: int,
        user_agent: str | None,
        ip_address: str | None,
    ) -> PasswordResetToken:
        now = datetime.now(UTC)
        self.session.execute(
            select(PasswordResetToken).where(PasswordResetToken.user_id == user_id)
        )
        self.session.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.used_at.is_(None),
        ).update({"used_at": now}, synchronize_session=False)
        token = PasswordResetToken(
            user_id=user_id,
            code_hash=code_hash,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=now + timedelta(minutes=ttl_minutes),
        )
        self.session.add(token)
        self.session.commit()
        self.session.refresh(token)
        return token

    def get_valid_password_reset_token(
        self,
        *,
        email: str,
        code_hash: str,
    ) -> tuple[PasswordResetToken, User] | None:
        statement = (
            select(PasswordResetToken, User)
            .join(User, User.id == PasswordResetToken.user_id)
            .where(
                User.email == email,
                User.deleted_at.is_(None),
                User.is_active.is_(True),
                PasswordResetToken.code_hash == code_hash,
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.expires_at > datetime.now(UTC),
            )
            .order_by(PasswordResetToken.created_at.desc())
        )
        return self.session.execute(statement).first()

    def get_valid_password_reset_token_by_hash(
        self,
        *,
        token_hash: str,
    ) -> tuple[PasswordResetToken, User] | None:
        statement = (
            select(PasswordResetToken, User)
            .join(User, User.id == PasswordResetToken.user_id)
            .where(
                User.deleted_at.is_(None),
                User.is_active.is_(True),
                PasswordResetToken.code_hash == token_hash,
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.expires_at > datetime.now(UTC),
            )
            .order_by(PasswordResetToken.created_at.desc())
        )
        return self.session.execute(statement).first()

    def update_password_with_token(
        self,
        *,
        user: User,
        token: PasswordResetToken,
        password_hash: str,
    ) -> None:
        now = datetime.now(UTC)
        user.password_hash = password_hash
        user.updated_at = now
        token.used_at = now
        self.session.add(user)
        self.session.add(token)
        self.session.commit()

    def create_activity_log(
        self,
        *,
        organization_id: UUID | None,
        activity_type: str,
        activity_label: str,
        user_id: UUID | None = None,
        user_email: str | None = None,
        details: str | None = None,
        metadata_json: dict | None = None,
    ) -> None:
        activity = UserActivityLog(
            organization_id=organization_id,
            user_id=user_id,
            user_email=user_email,
            activity_type=activity_type,
            activity_label=activity_label,
            details=details,
            metadata_json=metadata_json or {},
        )
        try:
            self.session.add(activity)
            self.session.commit()
        except SQLAlchemyError:
            # Activity logs are non-critical telemetry and should never block auth flows.
            self.session.rollback()
