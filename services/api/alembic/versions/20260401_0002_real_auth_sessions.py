"""Add organization memberships and real auth sessions.

Revision ID: 20260401_0002
Revises: 20260331_0001
Create Date: 2026-04-01 09:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260401_0002"
down_revision = "20260331_0001"
branch_labels = None
depends_on = None

DEBUG_USER_ID = "00000000-0000-7000-0000-000000000001"
LOCAL_SCIENTIST_PASSWORD_HASH = (
    "scrypt$16384$8$1$gIFQ_Goz1IX1Lk6vh55erA$RBWLynFo-NsigLl7EcM5yt8wAf01fWqDBIAIx12R6M0"
)
ALL_PERMISSIONS_JSON = """
[
  "projects:read",
  "projects:write",
  "soil_samples:read",
  "soil_samples:write",
  "scenarios:read",
  "scenarios:write",
  "runs:read",
  "runs:write",
  "reports:read",
  "reports:write"
]
"""


def upgrade() -> None:
    op.add_column("users", sa.Column("password_hash", sa.String(length=255), nullable=True))

    op.create_table(
        "organization_memberships",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(length=100), nullable=False, server_default="org_member"),
        sa.Column("permissions_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_organization_memberships_organization_id", "organization_memberships", ["organization_id"])
    op.create_index("ix_organization_memberships_user_id", "organization_memberships", ["user_id"])
    op.create_index(
        "uq_organization_memberships_user_org",
        "organization_memberships",
        ["user_id", "organization_id"],
        unique=True,
    )
    op.create_index(
        "ix_organization_memberships_org_active",
        "organization_memberships",
        ["organization_id", "is_active"],
    )
    op.create_index(
        "ix_organization_memberships_user_active",
        "organization_memberships",
        ["user_id", "is_active"],
    )

    op.create_table(
        "auth_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])
    op.create_index("ix_auth_sessions_organization_id", "auth_sessions", ["organization_id"])
    op.create_index("uq_auth_sessions_token_hash", "auth_sessions", ["token_hash"], unique=True)
    op.create_index("ix_auth_sessions_user_active", "auth_sessions", ["user_id", "revoked_at"])
    op.create_index("ix_auth_sessions_org_active", "auth_sessions", ["organization_id", "revoked_at"])

    op.execute(
        sa.text(
            """
            INSERT INTO organization_memberships (
                organization_id,
                user_id,
                role,
                permissions_json,
                is_default,
                is_active,
                metadata_json
            )
            SELECT
                users.organization_id,
                users.id,
                'org_admin',
                CAST(:permissions_json AS jsonb),
                true,
                users.is_active,
                '{}'::jsonb
            FROM users
            WHERE users.deleted_at IS NULL
            ON CONFLICT (user_id, organization_id) DO NOTHING
            """
        ).bindparams(permissions_json=ALL_PERMISSIONS_JSON)
    )
    op.execute(
        sa.text(
            """
            UPDATE users
            SET password_hash = :password_hash
            WHERE id = :user_id
            """
        ).bindparams(
            user_id=DEBUG_USER_ID,
            password_hash=LOCAL_SCIENTIST_PASSWORD_HASH,
        )
    )


def downgrade() -> None:
    op.drop_index("ix_auth_sessions_org_active", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_user_active", table_name="auth_sessions")
    op.drop_index("uq_auth_sessions_token_hash", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_organization_id", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_user_id", table_name="auth_sessions")
    op.drop_table("auth_sessions")

    op.drop_index("ix_organization_memberships_user_active", table_name="organization_memberships")
    op.drop_index("ix_organization_memberships_org_active", table_name="organization_memberships")
    op.drop_index("uq_organization_memberships_user_org", table_name="organization_memberships")
    op.drop_index("ix_organization_memberships_user_id", table_name="organization_memberships")
    op.drop_index("ix_organization_memberships_organization_id", table_name="organization_memberships")
    op.drop_table("organization_memberships")

    op.drop_column("users", "password_hash")
