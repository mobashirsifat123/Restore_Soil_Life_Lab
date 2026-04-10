"""about_page_founder_redesign

Revision ID: 20260409_0007
Revises: 20260409_0006
Create Date: 2026-04-09 14:10:00.000000
"""
from __future__ import annotations

import json

import sqlalchemy as sa
from alembic import op

revision = "20260409_0007"
down_revision = "20260409_0006"
branch_labels = None
depends_on = None

ABOUT_PAGE = {
    "title": "About Bio Soil",
    "meta_description": (
        "Learn how Bio Soil helps communities regenerate living soil through practical "
        "soil food web education, diagnostics, and field-ready guidance."
    ),
    "hero_kicker": "About",
    "hero_heading": (
        "Our mission is to help people and organizations regenerate the soils that "
        "sustain their communities."
    ),
    "hero_subheading": (
        "Bio Soil turns soil food web science into clear education, measurable diagnostics, "
        "and practical next steps for the people doing the work on the ground."
    ),
    "hero_image_url": "/images/soil-scientist-hands.png",
}

FOUNDER_SECTION = {
    "eyebrow": "Our Founder",
    "label": "Dr. Lu Hongyan",
    "name": "A soil scientist devoted to rebuilding living agricultural systems.",
    "image_url": "/images/soil-scientist-hands.png",
    "image_alt": "Scientist holding healthy living soil in both hands",
    "paragraph_one": (
        "For more than two decades, Bio Soil's scientific leadership has focused on turning "
        "complex soil biology into practical guidance that growers, consultants, and communities "
        "can actually apply in the field."
    ),
    "paragraph_two": (
        "Our work centers on the living relationships between plants, fungi, bacteria, protozoa, "
        "nematodes, and organic matter. When those relationships are restored, degraded land can "
        "begin functioning like healthy soil again."
    ),
    "paragraph_three": (
        "Everything we build, from education to diagnostics to software, is designed to help "
        "people understand that biology clearly and use it to regenerate the soils that sustain "
        "their region."
    ),
    "question_heading": "Have more questions?",
    "question_cta_label": "Connect With Us",
    "question_cta_link": "/contact",
}

FOUNDER_CREDENTIALS = [
    {"text": "B.A., Biology and Chemistry"},
    {"text": "M.S., Microbial Ecology"},
    {"text": "Ph.D., Soil Microbiology"},
]

OLD_ABOUT_PAGE = {
    "hero_kicker": "Our mission",
    "hero_heading": "Restoring Earth's Living Soil, One Farm at a Time",
    "hero_subheading": (
        "The complete soil food web exists in virgin soils around the world. Once disrupted "
        "by chemical agriculture, it must be deliberately restored. That's our life's work."
    ),
}


def _upsert_section(page_slug: str, section_key: str, content: object) -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            insert into cms_sections (page_slug, section_key, content_json)
            values (:page_slug, :section_key, cast(:content as jsonb))
            on conflict (page_slug, section_key) do update
            set content_json = excluded.content_json,
                updated_at = now()
            """
        ),
        {
            "page_slug": page_slug,
            "section_key": section_key,
            "content": json.dumps(content),
        },
    )


def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            update cms_pages
            set title = :title,
                meta_description = :meta_description,
                hero_kicker = :hero_kicker,
                hero_heading = :hero_heading,
                hero_subheading = :hero_subheading,
                hero_image_url = :hero_image_url,
                updated_at = now()
            where slug = 'about'
            """
        ),
        ABOUT_PAGE,
    )
    _upsert_section("about", "founder", FOUNDER_SECTION)
    _upsert_section("about", "founder_credentials", FOUNDER_CREDENTIALS)


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            update cms_pages
            set hero_kicker = :hero_kicker,
                hero_heading = :hero_heading,
                hero_subheading = :hero_subheading,
                updated_at = now()
            where slug = 'about'
            """
        ),
        OLD_ABOUT_PAGE,
    )
    bind.execute(
        sa.text(
            """
            delete from cms_sections
            where page_slug = 'about'
              and section_key in ('founder', 'founder_credentials')
            """
        )
    )
