"""Add CMS tables: cms_pages, cms_sections, blog_posts, calculator_formulas, media_assets.

Revision ID: 20260406_0004
Revises: 20260401_0003
Create Date: 2026-04-06 00:00:00
"""

from __future__ import annotations

import json

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260406_0004"
down_revision = "20260401_0003"
branch_labels = None
depends_on = None

# ---------------------------------------------------------------------------
# Seed data — mirrors the current hardcoded page content exactly
# ---------------------------------------------------------------------------

HOME_PROBLEMS = [
    {"icon": "🌿", "title": "Diminishing Soil Fertility", "subtitle": "The Soil-ution",
     "body": "With a restored soil food web in place, plants can control nutrient cycling in their root zones, accessing minerals stored in organic matter and parent material. Plants get a constant flow of nutrients they control.",
     "link": "/science/nutrient-cycling"},
    {"icon": "🛡️", "title": "Diseases, Pests & Weeds", "subtitle": "Problem Solved",
     "body": "The soil food web provides natural protection against pests and diseases and also inhibits the growth of weeds — without chemical intervention.",
     "link": "/science"},
    {"icon": "📈", "title": "Declining Farm Profits", "subtitle": "How We Help",
     "body": "When the soil food web is restored, farmers no longer need chemicals. Reduced irrigation and plowing requirements also result in significant cost savings.",
     "link": "/science"},
    {"icon": "🌍", "title": "Climate Change", "subtitle": "Carbon Sequestration",
     "body": "Plants absorb carbon and invest ~40% into the soil to feed microorganisms. By regenerating the world's soils we could halt and reverse climate change within 15–20 years.",
     "link": "/science/carbon-sequestration"},
    {"icon": "🦋", "title": "Bird & Insect Decline", "subtitle": "Ecosystem Restoration",
     "body": "With the soil food web in place and natural farming practices, pesticides aren't required. The soil food web naturally protects plants, and the entire ecosystem flourishes.",
     "link": "/science"},
    {"icon": "⛰️", "title": "Soil Erosion", "subtitle": "Structure Formation",
     "body": "Soil food web microorganisms build soil structure that prevents erosion by wind and rain. Compaction layers break up, allowing water and plant roots to penetrate deeper.",
     "link": "/science"},
]

HOME_STATS = [
    {"number": "150%", "label": "Reported yield increase", "sub": "In the first growing season"},
    {"number": "100%", "label": "Reduction in pest damage", "sub": "Using natural food web protection"},
    {"number": "60%", "label": "Cut in fertilizer costs", "sub": "After soil biology restored"},
    {"number": "6", "label": "Continents with proven results", "sub": "Farmers transformed worldwide"},
]

HOME_TESTIMONIALS = [
    {"quote": "Our farm was in serious trouble, but after implementing the soil food web approach we increased our yield by 150% in a single season. We also cut fertilizer costs by at least 60%. We continue to monitor and move our soils to a much better place.", "author": "Hassan A.", "role": "Grain Farmer, Morocco"},
    {"quote": "I'm learning so much I never knew before — even after receiving a degree in Horticulture. Bio Soil explains everything so precisely. I'm excited to start this journey with the soil food web approach!", "author": "Meredith L.", "role": "Horticulturist, New Zealand"},
    {"quote": "It was one of the greatest courses I have ever taken. The potential of being able to help farmers transition to biology-first agriculture is incredibly exciting.", "author": "Thomas B.", "role": "Agricultural Consultant, Germany"},
    {"quote": "Great information. It has given me a new outlook for the future of farming. The soil health calculator alone saved me weeks of guesswork.", "author": "Sara M.", "role": "Regenerative Farmer, Oregon"},
    {"quote": "I've taken many professional certifications throughout my career and I do appreciate this format. Obviously the content is invaluable.", "author": "Akira T.", "role": "Soil Scientist, Japan"},
    {"quote": "I have greatly appreciated this approach. It has filled in gaps in my knowledge on how to heal depleted soil. Bio Soil's tools make it practical.", "author": "Camille R.", "role": "Permaculture Designer, France"},
]

HOME_CALCULATOR_SPOTLIGHT = {
    "kicker": "New Feature",
    "heading": "SilkSoil",
    "body": "Enter your soil measurements — pH, organic matter, temperature, moisture, microbial indicators — and receive a comprehensive Soil Health Score with actionable recommendations.",
    "features": [
        "Fungal-to-Bacterial ratio analysis",
        "Nutrient availability scoring",
        "Biological activity index",
        "Predictive yield improvement estimate",
        "Personalised restoration roadmap",
    ],
    "cta_text": "Open SilkSoil — Member Access",
    "cta_link": "/silksoil",
    "image_url": "/images/soil-hero-bg.png",
}

HOME_ABOUT_SECTION = {
    "kicker": "Our Approach",
    "heading": "The Bio Soil Approach to Soil Regeneration",
    "body1": "The complete soil food web can be found in virgin soils around the world. Once disrupted by chemical inputs, tillage, and monoculture, it must be deliberately and methodically restored.",
    "body2": "Using BioComplete™ soil amendments aligned with the soil food web science, most soils can be regenerated in the first growing season — with measurable, quantifiable results tracked through our analysis platform.",
    "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "video_image": "/images/soil-microorganism-microscope.png",
    "video_caption": "Soil food web under fluorescence microscopy",
}

HOME_PHOTO_FEATURE = {
    "left": {
        "image": "/images/soil-scientist-hands.png",
        "alt": "Scientist holding healthy soil showing living root and fungi networks",
        "kicker": "In the field",
        "heading": "Living soil you can see and feel",
        "caption": "Healthy soil teems with organisms visible to the naked eye — earthworms, fungi strands, and structured aggregates.",
    },
    "right": {
        "image": "/images/healthy-farm-field.png",
        "alt": "Healthy regenerative farm field at golden hour showing thriving crops",
        "kicker": "Results on six continents",
        "heading": "Measurable yield improvements",
        "caption": "Farmers report yield increases of up to 150% in the first season after restoring their soil food web.",
    },
}

ABOUT_TEAM = [
    {"name": "Dr. Lu Hongyan", "role": "Chief Soil Biologist", "bio": "PhD in Microbial Ecology. 20 years researching soil food web dynamics in agricultural and restoration contexts across 4 continents.", "emoji": "🔬"},
    {"name": "Marcus Chen", "role": "Head of Regenerative Agronomy", "bio": "Former conventional farmer turned regenerative advocate. Guided 200+ farm transitions across North America and Asia.", "emoji": "🔬"},
    {"name": "Dr. Amara Diallo", "role": "Soil Physics & Modelling", "bio": "Specialises in predictive soil formation modelling and building quantifiable metrics for biological restoration.", "emoji": "🔬"},
]

ABOUT_MILESTONES = [
    {"year": "2018", "text": "Bio Soil founded following a 3-year soil restoration study across degraded agricultural land."},
    {"year": "2020", "text": "First soil food web analysis platform launched, serving 500+ farms in the first year."},
    {"year": "2022", "text": "Expanded to 6 continents with 2,000+ certified consultants and lab technicians."},
    {"year": "2024", "text": "SilkSoil analysis system launched, integrating temperature and microbial indicators."},
    {"year": "2025", "text": "SilkSoil released — first free, scientifically validated soil scoring tool."},
    {"year": "2026", "text": "Bio Soil Foundation established as a nonprofit to carry forward regenerative soil science."},
]

ABOUT_STATS = [
    {"n": "6", "label": "Continents"},
    {"n": "2,400+", "label": "Certified Consultants"},
    {"n": "12,000+", "label": "Farms Transformed"},
    {"n": "150%", "label": "Avg. Yield Increase Reported"},
]

ABOUT_INTRO = {
    "kicker": "Who we are",
    "heading": "Science-led. Community-driven. Results-obsessed.",
    "paragraphs": [
        "Bio Soil was founded by soil biologists and former farmers who saw an urgent need to translate cutting-edge soil food web science into practical, accessible tools that real farmers could use.",
        "Our approach is built on four decades of soil biology research. Every feature — from our simulation platform to our free SilkSoil — is grounded in measurable, quantifiable outcomes.",
        "We train consultants, partner with labs, and build software tools that help any farmer — regardless of size or location — understand and restore the biology beneath their feet.",
    ],
    "image_url": "/images/soil-scientist-hands.png",
}

SCIENCE_FOOD_WEB_LEVELS = [
    {"level": 1, "name": "Primary Producers", "members": "Plants, Algae", "color": "#3a8c2f", "description": "Fix energy from sunlight, feed the web with root exudates"},
    {"level": 2, "name": "Primary Consumers", "members": "Bacteria, Fungi, Root Feeders", "color": "#5a7c2f", "description": "Break down organic matter, immobilise nutrients"},
    {"level": 3, "name": "Secondary Consumers", "members": "Protozoa, Nematodes, Microarthropods", "color": "#8aaa3a", "description": "Eat bacteria and fungi, release nutrients in plant-available forms"},
    {"level": 4, "name": "Tertiary Consumers", "members": "Predatory Nematodes, Mites, Spiders", "color": "#b9933d", "description": "Regulate lower trophic levels, prevent population imbalances"},
    {"level": 5, "name": "Higher-Order Predators", "members": "Earthworms, Centipedes, Beetles", "color": "#d4933d", "description": "Redistribute organic matter, aerate and structure soil"},
    {"level": 6, "name": "Apex Organisms", "members": "Mammals, Birds, Reptiles", "color": "#b97849", "description": "Long-range redistribution of nutrients and biology"},
]

SCIENCE_CONCEPTS = [
    {"id": "soil-food-web", "icon": "🕸️", "title": "The Soil Food Web", "subtitle": "Nature's Soil Operating System",
     "body": "The soil food web is the interconnected community of organisms living in soil — bacteria, fungi, protozoa, nematodes, arthropods, earthworms, and more. Each plays a specific role in nutrient cycling, soil structure, and plant health. When this web is intact, plants thrive without chemical inputs.",
     "detail": "A single tablespoon of healthy soil contains 1 billion bacteria, 120,000 fungi, and 25,000 protozoa — each essential."},
    {"id": "nutrient-cycling", "icon": "♻️", "title": "Nutrient Cycling", "subtitle": "Plants control their own nutrition",
     "body": "Plants exude sugars through their roots to attract bacteria and fungi. These microbes dissolve and immobilise nutrients. Protozoa and nematodes eat the bacteria and fungi, releasing nutrients directly in the root zone — in the exact form plants need, at the right time. No leaching. No waste.",
     "detail": "Restored nutrient cycling has been linked to yield increases of up to 150% in the first growing season."},
    {"id": "carbon-sequestration", "icon": "🌍", "title": "Carbon Sequestration", "subtitle": "Soil as the climate solution",
     "body": "Plants absorb CO₂ during photosynthesis and invest approximately 40% as root exudates to feed soil microorganisms. These organisms build stable organic compounds — humus and glomalin — that lock carbon into the soil for decades. Scientists estimate that restoring the world's soils could halt and reverse climate change within 15–20 years.",
     "detail": "Biological agriculture can sequester 2–5 tonnes of carbon per hectare per year — far exceeding industrial tree planting."},
    {"id": "suppress-pests-disease", "icon": "🛡️", "title": "Pest & Disease Suppression", "subtitle": "Built-in natural protection",
     "body": "A complete soil food web naturally suppresses pathogens and pests. Fungal networks produce antibiotic compounds. Bacterial films coat root surfaces, blocking pathogen attachment. Predatory nematodes control harmful pest populations. The result: crops grown in biologically active soil have far lower disease and pest pressure — without pesticides.",
     "detail": "Farmers report up to 100% reduction in pesticide use after restoring soil biology."},
    {"id": "weed-suppression", "icon": "🌾", "title": "Weed Suppression", "subtitle": "Biology outcompetes weeds",
     "body": "Weeds are indicators of disturbed or depleted soil. They colonise biological vacuums left by degraded growing conditions. When soil biology is restored, desirable plant communities competitive advantage increases dramatically. Biology — not herbicide — becomes the primary weed management system.",
     "detail": "Cover crop diversity + biological soil management can reduce weed pressure by 60–80%."},
    {"id": "structure-formation", "icon": "⛰️", "title": "Soil Structure Formation", "subtitle": "Building soil from within",
     "body": "Bacteria produce sticky polysaccharides that bind soil particles into aggregates. Fungal hyphae create a physical mesh that reinforces aggregate stability. Earthworms produce castings that dramatically improve water infiltration and aeration. This structured soil resists erosion, holds moisture, and supports deep root penetration.",
     "detail": "Biologically active soil holds 3× more water than compacted or chemically treated soil of the same texture."},
]

SCIENCE_STATS = [
    {"n": "1B+", "label": "Bacteria per teaspoon of soil"},
    {"n": "120,000", "label": "Fungal strands per teaspoon"},
    {"n": "40%", "label": "Of plant photosynthate invested in soil"},
    {"n": "15–20yr", "label": "Timeline to halt climate change via soil"},
]

BLOG_CATEGORIES = ["All", "Science", "Case Studies", "Updates", "Events", "Community"]

DEFAULT_FORMULA = {
    "version": "1.0",
    "name": "Soil Health Score v1",
    "description": "Weighted composite score from key soil health indicators.",
    "weights": {
        "ph": {"weight": 0.15, "optimal_min": 6.0, "optimal_max": 7.0, "description": "Soil pH — optimal range 6.0–7.0"},
        "organic_matter": {"weight": 0.20, "optimal_min": 3.0, "optimal_max": 8.0, "description": "Organic matter % — above 3% is healthy"},
        "microbial_activity": {"weight": 0.25, "optimal_min": 60, "optimal_max": 100, "description": "Microbial activity index (0–100)"},
        "fungal_bacterial_ratio": {"weight": 0.20, "optimal_min": 1.0, "optimal_max": 5.0, "description": "Fungal:Bacterial ratio — 1:1 to 5:1 is healthy"},
        "moisture": {"weight": 0.10, "optimal_min": 20, "optimal_max": 60, "description": "Soil moisture % — 20–60% is ideal"},
        "temperature": {"weight": 0.10, "optimal_min": 10, "optimal_max": 30, "description": "Soil temperature °C — 10–30°C is active range"},
    },
    "score_bands": [
        {"min": 0, "max": 39, "label": "Poor", "color": "#dc2626", "description": "Severely degraded. Immediate biological restoration needed."},
        {"min": 40, "max": 59, "label": "Fair", "color": "#d97706", "description": "Moderately degraded. Targeted interventions recommended."},
        {"min": 60, "max": 74, "label": "Good", "color": "#ca8a04", "description": "Developing biology. Continue restoration programme."},
        {"min": 75, "max": 89, "label": "Excellent", "color": "#16a34a", "description": "Biologically active. Maintain current approach."},
        {"min": 90, "max": 100, "label": "Exceptional", "color": "#059669", "description": "Peak soil food web health. Model farm."},
    ],
}

SEED_BLOG_POSTS = [
    {
        "slug": "mycorrhizal-fungi-nutrient-cycling",
        "category": "Science",
        "title": "How Mycorrhizal Fungi Networks Drive Nutrient Cycling",
        "excerpt": "Underground fungal highways transport nutrients between plants and microorganisms in ways that still astonish soil scientists today.",
        "body_markdown": "# How Mycorrhizal Fungi Networks Drive Nutrient Cycling\n\nUnderground fungal highways transport nutrients between plants and microorganisms in ways that still astonish soil scientists today.\n\nMycorrhizal fungi form symbiotic relationships with over 90% of land plants. In exchange for carbon-rich sugars from the plant, the fungi extend the plant's effective root system by orders of magnitude, accessing water and nutrients that roots alone could never reach.\n\n## The Wood Wide Web\n\nRecent research has revealed that mycorrhizal networks can connect multiple plants across large distances — creating what some scientists have termed the \"Wood Wide Web.\" Through this network, established trees can support seedlings, nutrients can be transferred between species, and even warning signals about pest attacks can be communicated.\n\n## Nutrient Cycling Mechanism\n\nThe fungi physically mine nutrients from soil minerals and organic matter using specialised enzymes. These nutrients are then transported through hyphal networks directly to plant roots — bypassing the need for chemical fertilisers entirely when the system is healthy.\n\n## Key Takeaway\n\nRestoring mycorrhizal networks is one of the most powerful and cost-effective interventions available to regenerative farmers. Avoid tillage, reduce chemical inputs, and establish diverse plant communities to support fungal networks.",
        "author": "Dr. Sarah Greenfield",
        "is_featured": True,
        "read_time_minutes": 6,
    },
    {
        "slug": "pakistani-farm-soil-restored",
        "category": "Case Studies",
        "title": "Pakistani Farm Soil Restored in One Season with Bio Approach",
        "excerpt": "Wild Soils UK and TrashIt demonstrate how the soil food web approach transformed degraded farmland in Pakistan, achieving a 120% yield increase.",
        "body_markdown": "# Pakistani Farm Soil Restored in One Season\n\nWild Soils UK and TrashIt demonstrate how the soil food web approach transformed degraded farmland in Pakistan, achieving a 120% yield increase.\n\n## The Challenge\n\nThe farm had been under intensive conventional cultivation for 15 years. Soil tests revealed:\n- pH: 8.2 (too alkaline)\n- Organic matter: 0.8% (severely depleted)\n- Microbial activity: near-zero\n- Heavy compaction layer at 15cm depth\n\n## The Intervention\n\nOver a single growing season, the team implemented:\n1. BioComplete soil amendments\n2. Cover crop interplanting\n3. Elimination of all synthetic inputs\n4. Minimal tillage protocol\n\n## Results After One Season\n\n- Yield increase: 120%\n- pH normalised to 6.8\n- Organic matter increased to 2.1%\n- Significant earthworm return observed\n- Pesticide costs: zero\n\nThis case demonstrates that dramatic improvements can happen within a single growing season when the biological approach is applied correctly.",
        "author": "Marcus Chen",
        "is_featured": True,
        "read_time_minutes": 8,
    },
    {
        "slug": "silksoil-microbiome-scoring",
        "category": "Updates",
        "title": "SilkSoil: New Microbiome Scoring Module Released",
        "excerpt": "Our latest calculator update adds fungal-to-bacterial ratio scoring and a predictive yield improvement estimate based on 5 years of field data.",
        "body_markdown": "# SilkSoil: New Microbiome Scoring Module\n\nWe're excited to announce a significant update to SilkSoil, our free soil health calculator.\n\n## What's New\n\n### Fungal:Bacterial Ratio Analysis\nThe new module analyses your estimated F:B ratio and scores it against optimal ranges for different crop types.\n\n### Predictive Yield Estimate\nBased on 5 years of field data from 2,400+ farms, the calculator can now estimate potential yield improvement after biological restoration.\n\n### Personalised Roadmap\nEvery score now comes with a personalised 3-step restoration roadmap tailored to your specific soil profile.\n\n## How to Access\n\nSimply log in to your Bio Soil account and navigate to SilkSoil. The new features are available to all members at no additional cost.",
        "author": "Bio Soil Team",
        "is_featured": True,
        "read_time_minutes": 4,
    },
    {
        "slug": "carbon-sequestration-biological-soil",
        "category": "Science",
        "title": "Carbon Sequestration Through Biological Soil Restoration",
        "excerpt": "New research confirms that restoring the soil food web can sequester carbon at rates that could meaningfully reverse atmospheric CO₂ levels.",
        "body_markdown": "# Carbon Sequestration Through Biological Soil Restoration\n\nNew research confirms that restoring the soil food web can sequester carbon at rates that could meaningfully reverse atmospheric CO₂ levels.\n\n## The Science of Soil Carbon\n\nWhen the soil food web is intact, plants invest approximately 40% of their photosynthate — the sugars produced from sunlight — into the soil as root exudates. These exudates feed bacteria and fungi, which in turn build complex organic compounds that lock carbon into the soil for decades or even centuries.\n\n## Key Carbon Compounds\n\n- **Humic acids**: Stable carbon compounds that persist in soil for thousands of years\n- **Glomalin**: A glycoprotein produced by mycorrhizal fungi that accounts for 15–20% of soil organic carbon\n- **Microbial biomass**: Living microorganisms that represent active carbon storage\n\n## Sequestration Rates\n\nResearch from our partner labs shows that restored soil food web systems can sequester 2–5 tonnes of carbon per hectare per year — far exceeding the rates achieved by tree planting initiatives.",
        "author": "Dr. Amara Diallo",
        "is_featured": False,
        "read_time_minutes": 9,
    },
    {
        "slug": "soil-food-web-webinar-series",
        "category": "Events",
        "title": "Free Webinar Series: A Living Legacy — The Science of the Soil Food Web",
        "excerpt": "Join us for a 6-part free webinar series exploring the foundational science behind the soil food web approach, from bacteria to food chains.",
        "body_markdown": "# Free Webinar Series: A Living Legacy\n\nJoin us for a 6-part free webinar series exploring the foundational science behind the soil food web approach.\n\n## Series Schedule\n\n1. **Session 1**: The Invisible World — Understanding Soil Bacteria\n2. **Session 2**: Fungal Networks — The Wood Wide Web\n3. **Session 3**: Protozoa & Nematodes — Nutrient Cycling Engines\n4. **Session 4**: Larger Organisms — Earthworms, Arthropods & More\n5. **Session 5**: How Plants Control Their Nutrition\n6. **Session 6**: Practical Restoration — From Diagnosis to Action\n\n## How to Register\n\nAll sessions are free and open to the public. Register via the Events page on our website.",
        "author": "Bio Soil Team",
        "is_featured": False,
        "read_time_minutes": 3,
    },
    {
        "slug": "500-new-consultants-q1-2026",
        "category": "Community",
        "title": "Bio Soil Welcomes 500 New Certified Consultants in Q1 2026",
        "excerpt": "Our community of certified soil consultants grew by 500 members this quarter, now spanning 48 countries on 6 continents.",
        "body_markdown": "# Bio Soil Welcomes 500 New Certified Consultants\n\nWe're thrilled to announce that our global community of certified soil consultants grew by 500 members in Q1 2026.\n\n## Community Milestones\n\n- **Total consultants**: 2,400+\n- **Countries represented**: 48\n- **Continents**: 6\n- **Farms advised in Q1**: 3,200+\n\n## What Certification Means\n\nOur certification programme covers the complete soil food web science, practical diagnosis methods, and use of our SilkSoil platform. Certified consultants are equipped to guide farmers through the full restoration journey.\n\n## Join the Community\n\nInterested in becoming a certified consultant? Our next cohort opens in June 2026.",
        "author": "Bio Soil Team",
        "is_featured": False,
        "read_time_minutes": 3,
    },
]


def upgrade() -> None:
    # CMS Pages table
    op.create_table(
        "cms_pages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("meta_description", sa.Text(), nullable=True),
        sa.Column("hero_kicker", sa.String(length=255), nullable=True),
        sa.Column("hero_heading", sa.Text(), nullable=True),
        sa.Column("hero_subheading", sa.Text(), nullable=True),
        sa.Column("hero_image_url", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("uq_cms_pages_slug", "cms_pages", ["slug"], unique=True)

    # CMS Sections table
    op.create_table(
        "cms_sections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("page_slug", sa.String(length=100), nullable=False),
        sa.Column("section_key", sa.String(length=100), nullable=False),
        sa.Column("content_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("uq_cms_sections_page_key", "cms_sections", ["page_slug", "section_key"], unique=True)
    op.create_index("ix_cms_sections_page_slug", "cms_sections", ["page_slug"])

    # Blog Posts table
    op.create_table(
        "blog_posts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("slug", sa.String(length=200), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("excerpt", sa.Text(), nullable=True),
        sa.Column("body_markdown", sa.Text(), nullable=True),
        sa.Column("cover_image_url", sa.Text(), nullable=True),
        sa.Column("author", sa.String(length=255), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("read_time_minutes", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("uq_blog_posts_slug", "blog_posts", ["slug"], unique=True)
    op.create_index("ix_blog_posts_published_at", "blog_posts", ["published_at"])
    op.create_index("ix_blog_posts_category", "blog_posts", ["category"])
    op.create_index("ix_blog_posts_is_featured", "blog_posts", ["is_featured"])

    # Calculator Formulas table
    op.create_table(
        "calculator_formulas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("formula_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("changelog", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_calculator_formulas_is_active", "calculator_formulas", ["is_active"])

    # Media Assets table
    op.create_table(
        "media_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("filename", sa.String(length=500), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("alt_text", sa.Text(), nullable=True),
        sa.Column("mime_type", sa.String(length=100), nullable=True),
        sa.Column("byte_size", sa.Integer(), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("uploaded_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["uploaded_by_user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_media_assets_uploaded_at", "media_assets", ["uploaded_at"])

    # ---- Seed data ----
    bind = op.get_bind()

    # Seed cms_pages
    pages = [
        ("home", "Bio Soil — Soil Food Web Science, Education & Tools",
         "Bio Soil brings together soil biology education, a free soil health calculator, and a scientific member platform so farmers, consultants, and ecologists can restore the soil food web.",
         "Soil Food Web Science · Education · Precision Tools",
         "Healthy soil starts with understanding the living community beneath your feet.",
         "Bio Soil brings together soil biology education, a free soil health calculator, and a scientific member platform so farmers, consultants, and ecologists can restore the soil food web and see measurable results.",
         "/images/soil-hero-bg.png"),
        ("about", "About Bio Soil",
         "Learn about Bio Soil's mission to restore the soil food web and empower farmers, consultants, and ecologists with science-backed tools.",
         "Our mission",
         "Restoring Earth's Living Soil, One Farm at a Time",
         "The complete soil food web exists in virgin soils around the world. Once disrupted by chemical agriculture, it must be deliberately restored. That's our life's work.",
         "/images/soil-scientist-hands.png"),
        ("science", "The Science — Bio Soil",
         "Understand how the soil food web works — nutrient cycling, carbon sequestration, pest suppression — and why restoring it transforms agriculture.",
         "Peer-reviewed science, practical results",
         "How the Soil Food Web Works",
         "Understanding the science behind the soil food web is the foundation of everything we do. Explore the key ecological mechanisms that govern soil health, nutrition, and productivity.",
         None),
        ("blog", "News, Science & Stories — Bio Soil",
         "Insights from our soil scientists, case studies from the field, and updates from the Bio Soil community around the world.",
         "From the field",
         "News, Science & Stories",
         "Insights from our soil scientists, case studies from the field, and updates from the Bio Soil community around the world.",
         None),
    ]

    for slug, title, meta_desc, kicker, heading, subheading, image_url in pages:
        bind.execute(sa.text("""
            INSERT INTO cms_pages (slug, title, meta_description, hero_kicker, hero_heading, hero_subheading, hero_image_url)
            VALUES (:slug, :title, :meta_desc, :kicker, :heading, :subheading, :image_url)
        """), {"slug": slug, "title": title, "meta_desc": meta_desc, "kicker": kicker,
               "heading": heading, "subheading": subheading, "image_url": image_url})

    # Seed cms_sections
    sections = [
        ("home", "problems", HOME_PROBLEMS),
        ("home", "stats", HOME_STATS),
        ("home", "testimonials", HOME_TESTIMONIALS),
        ("home", "calculator_spotlight", HOME_CALCULATOR_SPOTLIGHT),
        ("home", "about_section", HOME_ABOUT_SECTION),
        ("home", "photo_feature", HOME_PHOTO_FEATURE),
        ("about", "team", ABOUT_TEAM),
        ("about", "milestones", ABOUT_MILESTONES),
        ("about", "stats", ABOUT_STATS),
        ("about", "intro", ABOUT_INTRO),
        ("science", "food_web_levels", SCIENCE_FOOD_WEB_LEVELS),
        ("science", "concepts", SCIENCE_CONCEPTS),
        ("science", "stats", SCIENCE_STATS),
        ("blog", "categories", BLOG_CATEGORIES),
    ]

    for page_slug, section_key, content in sections:
        bind.execute(sa.text("""
            INSERT INTO cms_sections (page_slug, section_key, content_json)
            VALUES (:page_slug, :section_key, CAST(:content AS jsonb))
        """), {"page_slug": page_slug, "section_key": section_key,
               "content": json.dumps(content)})

    # Seed blog posts
    from datetime import datetime, timezone
    published_dates = [
        "2026-04-03", "2026-03-28", "2026-03-20", "2026-03-10", "2026-02-28", "2026-02-15"
    ]
    for i, post in enumerate(SEED_BLOG_POSTS):
        pub_date = datetime.fromisoformat(published_dates[i]).replace(tzinfo=timezone.utc)
        bind.execute(sa.text("""
            INSERT INTO blog_posts (slug, category, title, excerpt, body_markdown, author, published_at, is_featured, read_time_minutes)
            VALUES (:slug, :category, :title, :excerpt, :body_markdown, :author, :published_at, :is_featured, :read_time)
        """), {
            "slug": post["slug"],
            "category": post["category"],
            "title": post["title"],
            "excerpt": post["excerpt"],
            "body_markdown": post["body_markdown"],
            "author": post["author"],
            "published_at": pub_date,
            "is_featured": post["is_featured"],
            "read_time": post["read_time_minutes"],
        })

    # Seed calculator formula
    bind.execute(sa.text("""
        INSERT INTO calculator_formulas (name, is_active, formula_json, changelog)
        VALUES (:name, true, CAST(:formula AS jsonb), :changelog)
    """), {
        "name": "Soil Health Score v1",
        "formula": json.dumps(DEFAULT_FORMULA),
        "changelog": "Initial formula based on Bio Soil research data.",
    })


def downgrade() -> None:
    op.drop_index("ix_media_assets_uploaded_at", table_name="media_assets")
    op.drop_table("media_assets")

    op.drop_index("ix_calculator_formulas_is_active", table_name="calculator_formulas")
    op.drop_table("calculator_formulas")

    op.drop_index("ix_blog_posts_is_featured", table_name="blog_posts")
    op.drop_index("ix_blog_posts_category", table_name="blog_posts")
    op.drop_index("ix_blog_posts_published_at", table_name="blog_posts")
    op.drop_index("uq_blog_posts_slug", table_name="blog_posts")
    op.drop_table("blog_posts")

    op.drop_index("ix_cms_sections_page_slug", table_name="cms_sections")
    op.drop_index("uq_cms_sections_page_key", table_name="cms_sections")
    op.drop_table("cms_sections")

    op.drop_index("uq_cms_pages_slug", table_name="cms_pages")
    op.drop_table("cms_pages")
