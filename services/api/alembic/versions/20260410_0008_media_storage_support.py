"""Add Supabase Storage metadata fields to media assets.

Revision ID: 20260410_0008
Revises: 20260409_0007
Create Date: 2026-04-10 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260410_0008"
down_revision = "20260409_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("media_assets", sa.Column("storage_bucket", sa.String(length=255), nullable=True))
    op.add_column("media_assets", sa.Column("storage_key", sa.String(length=1024), nullable=True))


def downgrade() -> None:
    op.drop_column("media_assets", "storage_key")
    op.drop_column("media_assets", "storage_bucket")
