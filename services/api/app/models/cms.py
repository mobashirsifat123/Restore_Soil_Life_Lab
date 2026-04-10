from __future__ import annotations

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class CmsPage(Base):
    __tablename__ = "cms_pages"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"))
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    meta_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    hero_kicker: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hero_heading: Mapped[str | None] = mapped_column(Text, nullable=True)
    hero_subheading: Mapped[str | None] = mapped_column(Text, nullable=True)
    hero_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=sa.func.now())
    updated_by_user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)


class CmsSection(Base):
    __tablename__ = "cms_sections"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"))
    page_slug: Mapped[str] = mapped_column(String(100), nullable=False)
    section_key: Mapped[str] = mapped_column(String(100), nullable=False)
    content_json: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=sa.text("'{}'::jsonb"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=sa.func.now())
    updated_by_user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)


class BlogPost(Base):
    __tablename__ = "blog_posts"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"))
    slug: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=sa.text("false"))
    read_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=sa.func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=sa.func.now())
    created_by_user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)


class CalculatorFormula(Base):
    __tablename__ = "calculator_formulas"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=sa.text("false"))
    formula_json: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=sa.text("'{}'::jsonb"))
    changelog: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=sa.func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=sa.func.now())
    updated_by_user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)


class MediaAsset(Base):
    __tablename__ = "media_assets"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"))
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    alt_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    byte_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=sa.func.now())
    uploaded_by_user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
