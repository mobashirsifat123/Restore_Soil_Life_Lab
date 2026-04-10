from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.auth import CurrentUser, require_admin_user
from app.api.dependencies.db import DatabaseSession
from app.repositories.admin_repository import AdminRepository
from app.repositories.cms_repository import CmsRepository
from app.schemas.cms import (
    BlogPostCreate,
    BlogPostDetail,
    BlogPostSummary,
    BlogPostUpdate,
    CalculatorFormulaCreate,
    CalculatorFormulaResponse,
    CmsPageFullResponse,
    CmsPageResponse,
    CmsPageUpdate,
    CmsSectionResponse,
    CmsSectionUpdate,
    MediaAssetCreate,
    MediaAssetResponse,
)

router = APIRouter(prefix="/cms", tags=["cms"])


def get_cms_repo(db: DatabaseSession) -> CmsRepository:
    return CmsRepository(db)


CmsRepoDep = Annotated[CmsRepository, Depends(get_cms_repo)]


# ─── CMS Pages ────────────────────────────────────────────────────────────────

@router.get(
    "/pages/{slug}",
    response_model=CmsPageFullResponse,
    operation_id="cms_getPage",
    summary="Get full page data (hero + all sections)",
)
def get_page(slug: str, repo: CmsRepoDep, db: DatabaseSession) -> CmsPageFullResponse:
    page = repo.get_page(slug)
    if page is None:
        raise HTTPException(status_code=404, detail=f"Page '{slug}' not found.")
    sections_list = repo.get_all_sections_for_page(slug)
    sections_dict = {s.section_key: s.content_json for s in sections_list}
    return CmsPageFullResponse(
        page=CmsPageResponse.model_validate(page),
        sections=sections_dict,
    )


@router.patch(
    "/pages/{slug}",
    response_model=CmsPageResponse,
    operation_id="cms_updatePage",
    summary="Update page hero content (admin only)",
    dependencies=[require_admin_user()],
)
def update_page(
    slug: str,
    payload: CmsPageUpdate,
    repo: CmsRepoDep,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> CmsPageResponse:
    page = repo.update_page(slug, payload, user_id=current_user.user_id)
    if page is None:
        raise HTTPException(status_code=404, detail=f"Page '{slug}' not found.")
    AdminRepository(db).create_activity_log(
        organization_id=current_user.organization_id,
        activity_type="admin_content_edit",
        activity_label="Edited page content",
        user_id=current_user.user_id,
        user_email=current_user.email,
        details=f"Updated page '{slug}'.",
    )
    db.commit()
    return CmsPageResponse.model_validate(page)


# ─── CMS Sections ─────────────────────────────────────────────────────────────

@router.get(
    "/sections/{page_slug}/{section_key}",
    response_model=CmsSectionResponse,
    operation_id="cms_getSection",
    summary="Get a single page section",
)
def get_section(page_slug: str, section_key: str, repo: CmsRepoDep) -> CmsSectionResponse:
    section = repo.get_section(page_slug, section_key)
    if section is None:
        raise HTTPException(status_code=404, detail=f"Section '{section_key}' not found on page '{page_slug}'.")
    return CmsSectionResponse.model_validate(section)


@router.patch(
    "/sections/{page_slug}/{section_key}",
    response_model=CmsSectionResponse,
    operation_id="cms_updateSection",
    summary="Update or create a page section (admin only)",
    dependencies=[require_admin_user()],
)
def update_section(
    page_slug: str,
    section_key: str,
    payload: CmsSectionUpdate,
    repo: CmsRepoDep,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> CmsSectionResponse:
    section = repo.upsert_section(page_slug, section_key, payload, user_id=current_user.user_id)
    AdminRepository(db).create_activity_log(
        organization_id=current_user.organization_id,
        activity_type="admin_content_edit",
        activity_label="Edited page section",
        user_id=current_user.user_id,
        user_email=current_user.email,
        details=f"Updated section '{section_key}' on '{page_slug}'.",
    )
    db.commit()
    return CmsSectionResponse.model_validate(section)


# ─── Blog Posts ────────────────────────────────────────────────────────────────

@router.get(
    "/blog",
    response_model=list[BlogPostSummary],
    operation_id="cms_listBlogPosts",
    summary="List all published blog posts",
)
def list_posts(repo: CmsRepoDep, category: str | None = None) -> list[BlogPostSummary]:
    posts = repo.list_posts(published_only=True, category=category)
    return [BlogPostSummary.model_validate(p) for p in posts]


@router.get(
    "/blog/all",
    response_model=list[BlogPostSummary],
    operation_id="cms_listAllBlogPosts",
    summary="List ALL blog posts including drafts (admin only)",
    dependencies=[require_admin_user()],
)
def list_all_posts(repo: CmsRepoDep, _: CurrentUser) -> list[BlogPostSummary]:
    posts = repo.list_posts(published_only=False)
    return [BlogPostSummary.model_validate(p) for p in posts]


@router.get(
    "/blog/featured",
    response_model=list[BlogPostSummary],
    operation_id="cms_listFeaturedPosts",
    summary="List featured blog posts for homepage",
)
def list_featured(repo: CmsRepoDep) -> list[BlogPostSummary]:
    posts = repo.list_featured_posts()
    return [BlogPostSummary.model_validate(p) for p in posts]


@router.get(
    "/blog/{slug}",
    response_model=BlogPostDetail,
    operation_id="cms_getBlogPost",
    summary="Get a single blog post by slug",
)
def get_post(slug: str, repo: CmsRepoDep) -> BlogPostDetail:
    post = repo.get_post_by_slug(slug)
    if post is None:
        raise HTTPException(status_code=404, detail="Blog post not found.")
    return BlogPostDetail.model_validate(post)


@router.get(
    "/blog/id/{post_id}",
    response_model=BlogPostDetail,
    operation_id="cms_getBlogPostById",
    summary="Get a single blog post by ID (admin use)",
    dependencies=[require_admin_user()],
)
def get_post_by_id(post_id: UUID, repo: CmsRepoDep, _: CurrentUser) -> BlogPostDetail:
    post = repo.get_post_by_id(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Blog post not found.")
    return BlogPostDetail.model_validate(post)


@router.post(
    "/blog",
    response_model=BlogPostDetail,
    status_code=status.HTTP_201_CREATED,
    operation_id="cms_createBlogPost",
    summary="Create a new blog post (admin only)",
    dependencies=[require_admin_user()],
)
def create_post(
    payload: BlogPostCreate,
    repo: CmsRepoDep,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> BlogPostDetail:
    post = repo.create_post(payload, user_id=current_user.user_id)
    AdminRepository(db).create_activity_log(
        organization_id=current_user.organization_id,
        activity_type="admin_content_edit",
        activity_label="Created blog post",
        user_id=current_user.user_id,
        user_email=current_user.email,
        details=post.title,
    )
    db.commit()
    return BlogPostDetail.model_validate(post)


@router.patch(
    "/blog/{post_id}",
    response_model=BlogPostDetail,
    operation_id="cms_updateBlogPost",
    summary="Update a blog post (admin only)",
    dependencies=[require_admin_user()],
)
def update_post(
    post_id: UUID,
    payload: BlogPostUpdate,
    repo: CmsRepoDep,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> BlogPostDetail:
    post = repo.update_post(post_id, payload, user_id=current_user.user_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Blog post not found.")
    AdminRepository(db).create_activity_log(
        organization_id=current_user.organization_id,
        activity_type="admin_content_edit",
        activity_label="Updated blog post",
        user_id=current_user.user_id,
        user_email=current_user.email,
        details=post.title,
    )
    db.commit()
    return BlogPostDetail.model_validate(post)


@router.delete(
    "/blog/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="cms_deleteBlogPost",
    summary="Delete a blog post (admin only)",
    dependencies=[require_admin_user()],
)
def delete_post(post_id: UUID, repo: CmsRepoDep, db: DatabaseSession, _: CurrentUser) -> None:
    post = repo.get_post_by_id(post_id)
    deleted = repo.delete_post(post_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Blog post not found.")
    if post is not None:
        AdminRepository(db).create_activity_log(
            organization_id=post.created_by_user_id and _.organization_id or _.organization_id,
            activity_type="admin_content_edit",
            activity_label="Deleted blog post",
            user_id=_.user_id,
            user_email=_.email,
            details=post.title,
        )
    db.commit()


# ─── Calculator Formulas ───────────────────────────────────────────────────────

@router.get(
    "/calculator/active",
    response_model=CalculatorFormulaResponse,
    operation_id="cms_getActiveFormula",
    summary="Get the active calculator formula",
)
def get_active_formula(repo: CmsRepoDep) -> CalculatorFormulaResponse:
    formula = repo.get_active_formula()
    if formula is None:
        raise HTTPException(status_code=404, detail="No active calculator formula found.")
    return CalculatorFormulaResponse.model_validate(formula)


@router.get(
    "/calculator",
    response_model=list[CalculatorFormulaResponse],
    operation_id="cms_listFormulas",
    summary="List all calculator formula versions (admin only)",
    dependencies=[require_admin_user()],
)
def list_formulas(repo: CmsRepoDep, _: CurrentUser) -> list[CalculatorFormulaResponse]:
    return [CalculatorFormulaResponse.model_validate(f) for f in repo.list_formulas()]


@router.post(
    "/calculator",
    response_model=CalculatorFormulaResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="cms_createFormula",
    summary="Save a new calculator formula version (admin only)",
    dependencies=[require_admin_user()],
)
def create_formula(
    payload: CalculatorFormulaCreate,
    repo: CmsRepoDep,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> CalculatorFormulaResponse:
    formula = repo.create_formula(payload, user_id=current_user.user_id)
    AdminRepository(db).create_activity_log(
        organization_id=current_user.organization_id,
        activity_type="formula_changed",
        activity_label="Created formula version",
        user_id=current_user.user_id,
        user_email=current_user.email,
        details=formula.name,
    )
    db.commit()
    return CalculatorFormulaResponse.model_validate(formula)


@router.patch(
    "/calculator/{formula_id}",
    response_model=CalculatorFormulaResponse,
    operation_id="cms_updateFormula",
    summary="Update a calculator formula (admin only)",
    dependencies=[require_admin_user()],
)
def update_formula(
    formula_id: UUID,
    payload: CalculatorFormulaCreate,
    repo: CmsRepoDep,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> CalculatorFormulaResponse:
    formula = repo.update_formula(formula_id, payload, user_id=current_user.user_id)
    if formula is None:
        raise HTTPException(status_code=404, detail="Formula not found.")
    AdminRepository(db).create_activity_log(
        organization_id=current_user.organization_id,
        activity_type="formula_changed",
        activity_label="Updated formula",
        user_id=current_user.user_id,
        user_email=current_user.email,
        details=formula.name,
    )
    db.commit()
    return CalculatorFormulaResponse.model_validate(formula)


@router.patch(
    "/calculator/{formula_id}/activate",
    response_model=CalculatorFormulaResponse,
    operation_id="cms_activateFormula",
    summary="Set a calculator formula as active (admin only)",
    dependencies=[require_admin_user()],
)
def activate_formula(
    formula_id: UUID,
    repo: CmsRepoDep,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> CalculatorFormulaResponse:
    formula = repo.activate_formula(formula_id, user_id=current_user.user_id)
    if formula is None:
        raise HTTPException(status_code=404, detail="Formula not found.")
    AdminRepository(db).create_activity_log(
        organization_id=current_user.organization_id,
        activity_type="formula_changed",
        activity_label="Activated formula",
        user_id=current_user.user_id,
        user_email=current_user.email,
        details=formula.name,
    )
    db.commit()
    return CalculatorFormulaResponse.model_validate(formula)


# ─── Media Assets ──────────────────────────────────────────────────────────────

@router.get(
    "/media",
    response_model=list[MediaAssetResponse],
    operation_id="cms_listMedia",
    summary="List all media assets",
)
def list_media(repo: CmsRepoDep) -> list[MediaAssetResponse]:
    return [MediaAssetResponse.model_validate(a) for a in repo.list_assets()]


@router.post(
    "/media",
    response_model=MediaAssetResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="cms_createMediaAsset",
    summary="Register a media asset (admin only)",
    dependencies=[require_admin_user()],
)
def create_media(
    payload: MediaAssetCreate,
    repo: CmsRepoDep,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> MediaAssetResponse:
    asset = repo.create_asset(payload, user_id=current_user.user_id)
    AdminRepository(db).create_activity_log(
        organization_id=current_user.organization_id,
        activity_type="media_upload",
        activity_label="Uploaded media",
        user_id=current_user.user_id,
        user_email=current_user.email,
        details=asset.filename,
    )
    db.commit()
    return MediaAssetResponse.model_validate(asset)


@router.delete(
    "/media/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="cms_deleteMediaAsset",
    summary="Delete a media asset (admin only)",
    dependencies=[require_admin_user()],
)
def delete_media(asset_id: UUID, repo: CmsRepoDep, db: DatabaseSession, _: CurrentUser) -> None:
    assets = repo.list_assets()
    asset = next((item for item in assets if item.id == asset_id), None)
    deleted = repo.delete_asset(asset_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Asset not found.")
    if asset is not None:
        AdminRepository(db).create_activity_log(
            organization_id=_.organization_id,
            activity_type="media_delete",
            activity_label="Deleted media",
            user_id=_.user_id,
            user_email=_.email,
            details=asset.filename,
        )
    db.commit()
