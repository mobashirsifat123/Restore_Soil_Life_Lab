from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.models.cms import BlogPost, CalculatorFormula, CmsPage, CmsSection, MediaAsset
from app.schemas.cms import (
    BlogPostCreate,
    BlogPostUpdate,
    CalculatorFormulaCreate,
    CmsPageUpdate,
    CmsSectionUpdate,
    MediaAssetCreate,
)


class CmsRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    # ── CMS Pages ──────────────────────────────────────────────────────────

    def get_page(self, slug: str) -> CmsPage | None:
        return self.session.scalar(
            sa.select(CmsPage).where(CmsPage.slug == slug)
        )

    def get_all_sections_for_page(self, slug: str) -> list[CmsSection]:
        return list(
            self.session.scalars(
                sa.select(CmsSection).where(CmsSection.page_slug == slug)
            ).all()
        )

    def update_page(self, slug: str, payload: CmsPageUpdate, user_id: UUID | None = None) -> CmsPage | None:
        page = self.get_page(slug)
        if page is None:
            return None
        data = payload.model_dump(exclude_none=True)
        for k, v in data.items():
            setattr(page, k, v)
        page.updated_at = datetime.now(tz=UTC)
        page.updated_by_user_id = user_id
        self.session.flush()
        return page

    # ── CMS Sections ───────────────────────────────────────────────────────

    def get_section(self, page_slug: str, section_key: str) -> CmsSection | None:
        return self.session.scalar(
            sa.select(CmsSection).where(
                CmsSection.page_slug == page_slug,
                CmsSection.section_key == section_key,
            )
        )

    def upsert_section(
        self, page_slug: str, section_key: str, payload: CmsSectionUpdate, user_id: UUID | None = None
    ) -> CmsSection:
        section = self.get_section(page_slug, section_key)
        if section is None:
            section = CmsSection(page_slug=page_slug, section_key=section_key)
            self.session.add(section)
        section.content_json = payload.content_json
        section.updated_at = datetime.now(tz=UTC)
        section.updated_by_user_id = user_id
        self.session.flush()
        return section

    # ── Blog Posts ─────────────────────────────────────────────────────────

    def list_posts(self, *, published_only: bool = True, category: str | None = None) -> list[BlogPost]:
        stmt = sa.select(BlogPost)
        if published_only:
            stmt = stmt.where(BlogPost.published_at.isnot(None))
        if category and category.lower() != "all":
            stmt = stmt.where(BlogPost.category == category)
        stmt = stmt.order_by(BlogPost.published_at.desc().nullslast())
        return list(self.session.scalars(stmt).all())

    def list_featured_posts(self) -> list[BlogPost]:
        return list(
            self.session.scalars(
                sa.select(BlogPost)
                .where(BlogPost.is_featured == True, BlogPost.published_at.isnot(None))  # noqa: E712
                .order_by(BlogPost.published_at.desc())
                .limit(3)
            ).all()
        )

    def get_post_by_slug(self, slug: str) -> BlogPost | None:
        return self.session.scalar(sa.select(BlogPost).where(BlogPost.slug == slug))

    def get_post_by_id(self, post_id: UUID) -> BlogPost | None:
        return self.session.scalar(sa.select(BlogPost).where(BlogPost.id == post_id))

    def create_post(self, payload: BlogPostCreate, user_id: UUID | None = None) -> BlogPost:
        now = datetime.now(tz=UTC)
        post = BlogPost(
            slug=payload.slug,
            category=payload.category,
            title=payload.title,
            excerpt=payload.excerpt,
            body_markdown=payload.body_markdown,
            cover_image_url=payload.cover_image_url,
            author=payload.author,
            is_featured=payload.is_featured,
            read_time_minutes=payload.read_time_minutes,
            published_at=now if payload.publish else None,
            created_by_user_id=user_id,
        )
        self.session.add(post)
        self.session.flush()
        return post

    def update_post(self, post_id: UUID, payload: BlogPostUpdate, user_id: UUID | None = None) -> BlogPost | None:
        post = self.get_post_by_id(post_id)
        if post is None:
            return None
        data = payload.model_dump(exclude_none=True, exclude={"publish"})
        for k, v in data.items():
            setattr(post, k, v)
        now = datetime.now(tz=UTC)
        if payload.publish is True and post.published_at is None:
            post.published_at = now
        elif payload.publish is False:
            post.published_at = None
        post.updated_at = now
        self.session.flush()
        return post

    def delete_post(self, post_id: UUID) -> bool:
        post = self.get_post_by_id(post_id)
        if post is None:
            return False
        self.session.delete(post)
        self.session.flush()
        return True

    # ── Calculator Formulas ────────────────────────────────────────────────

    def get_active_formula(self) -> CalculatorFormula | None:
        return self.session.scalar(
            sa.select(CalculatorFormula).where(CalculatorFormula.is_active == True)  # noqa: E712
        )

    def list_formulas(self) -> list[CalculatorFormula]:
        return list(
            self.session.scalars(
                sa.select(CalculatorFormula).order_by(CalculatorFormula.created_at.desc())
            ).all()
        )

    def create_formula(self, payload: CalculatorFormulaCreate, user_id: UUID | None = None) -> CalculatorFormula:
        formula = CalculatorFormula(
            name=payload.name,
            formula_json=payload.formula_json,
            changelog=payload.changelog,
            is_active=False,
            updated_by_user_id=user_id,
        )
        self.session.add(formula)
        self.session.flush()
        return formula

    def activate_formula(self, formula_id: UUID, user_id: UUID | None = None) -> CalculatorFormula | None:
        formula = self.session.scalar(
            sa.select(CalculatorFormula).where(CalculatorFormula.id == formula_id)
        )
        if formula is None:
            return None
        # Deactivate all others
        self.session.execute(
            sa.update(CalculatorFormula)
            .where(CalculatorFormula.id != formula_id)
            .values(is_active=False)
        )
        formula.is_active = True
        formula.updated_at = datetime.now(tz=UTC)
        formula.updated_by_user_id = user_id
        self.session.flush()
        return formula

    def update_formula(self, formula_id: UUID, payload: CalculatorFormulaCreate, user_id: UUID | None = None) -> CalculatorFormula | None:
        formula = self.session.scalar(
            sa.select(CalculatorFormula).where(CalculatorFormula.id == formula_id)
        )
        if formula is None:
            return None
        formula.name = payload.name
        formula.formula_json = payload.formula_json
        formula.changelog = payload.changelog
        formula.updated_at = datetime.now(tz=UTC)
        formula.updated_by_user_id = user_id
        self.session.flush()
        return formula

    # ── Media Assets ───────────────────────────────────────────────────────

    def list_assets(self) -> list[MediaAsset]:
        return list(
            self.session.scalars(
                sa.select(MediaAsset).order_by(MediaAsset.uploaded_at.desc())
            ).all()
        )

    def create_asset(self, payload: MediaAssetCreate, user_id: UUID | None = None) -> MediaAsset:
        asset = MediaAsset(
            filename=payload.filename,
            url=payload.url,
            alt_text=payload.alt_text,
            mime_type=payload.mime_type,
            byte_size=payload.byte_size,
            uploaded_by_user_id=user_id,
        )
        self.session.add(asset)
        self.session.flush()
        return asset

    def delete_asset(self, asset_id: UUID) -> bool:
        asset = self.session.scalar(sa.select(MediaAsset).where(MediaAsset.id == asset_id))
        if asset is None:
            return False
        self.session.delete(asset)
        self.session.flush()
        return True
