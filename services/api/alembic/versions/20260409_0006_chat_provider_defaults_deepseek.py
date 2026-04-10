"""chat_provider_defaults_deepseek

Revision ID: 20260409_0006
Revises: 20260407_0005
Create Date: 2026-04-09 11:45:00.000000
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260409_0006"
down_revision = "20260407_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "chat_assistants",
        "provider",
        existing_type=sa.String(length=64),
        server_default="deepseek",
    )
    op.alter_column(
        "chat_assistants",
        "model",
        existing_type=sa.String(length=128),
        server_default="deepseek-chat",
    )


def downgrade() -> None:
    op.alter_column(
        "chat_assistants",
        "provider",
        existing_type=sa.String(length=64),
        server_default="gemini",
    )
    op.alter_column(
        "chat_assistants",
        "model",
        existing_type=sa.String(length=128),
        server_default="gemini-1.5-flash",
    )
