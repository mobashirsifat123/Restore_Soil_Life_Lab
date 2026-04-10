from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ---------- CMS Pages ----------


class CmsPageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    title: str
    meta_description: str | None
    hero_kicker: str | None
    hero_heading: str | None
    hero_subheading: str | None
    hero_image_url: str | None
    updated_at: datetime


class CmsPageUpdate(BaseModel):
    title: str | None = None
    meta_description: str | None = None
    hero_kicker: str | None = None
    hero_heading: str | None = None
    hero_subheading: str | None = None
    hero_image_url: str | None = None


# ---------- CMS Sections ----------


class CmsSectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    page_slug: str
    section_key: str
    content_json: Any
    updated_at: datetime


class CmsSectionUpdate(BaseModel):
    content_json: Any


# ---------- Full Page Data (page + all sections) ----------


class CmsPageFullResponse(BaseModel):
    page: CmsPageResponse
    sections: dict[str, Any]


# ---------- Blog Posts ----------


class BlogPostSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    category: str
    title: str
    excerpt: str | None
    cover_image_url: str | None
    author: str | None
    published_at: datetime | None
    is_featured: bool
    read_time_minutes: int | None
    created_at: datetime
    updated_at: datetime


class BlogPostDetail(BlogPostSummary):
    body_markdown: str | None


class BlogPostCreate(BaseModel):
    slug: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=500)
    excerpt: str | None = None
    body_markdown: str | None = None
    cover_image_url: str | None = None
    author: str | None = None
    is_featured: bool = False
    read_time_minutes: int | None = None
    publish: bool = False  # If true, set published_at = now()


class BlogPostUpdate(BaseModel):
    slug: str | None = None
    category: str | None = None
    title: str | None = None
    excerpt: str | None = None
    body_markdown: str | None = None
    cover_image_url: str | None = None
    author: str | None = None
    is_featured: bool | None = None
    read_time_minutes: int | None = None
    publish: bool | None = None  # true=publish, false=unpublish


# ---------- Calculator Formulas ----------


class CalculatorFormulaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    is_active: bool
    formula_json: Any
    changelog: str | None
    created_at: datetime
    updated_at: datetime


class CalculatorFormulaCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    formula_json: Any
    changelog: str | None = None


# ---------- Media Assets ----------


class MediaAssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    url: str
    alt_text: str | None
    mime_type: str | None
    byte_size: int | None
    uploaded_at: datetime


class MediaAssetCreate(BaseModel):
    filename: str
    url: str
    alt_text: str | None = None
    mime_type: str | None = None
    byte_size: int | None = None
