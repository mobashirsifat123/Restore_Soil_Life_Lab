"""chat_tables

Revision ID: 20260407_0005
Revises: 20260406_0004
Create Date: 2026-04-07 13:30:05.954359
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260407_0005"
down_revision = "20260406_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. chat_widget_settings
    op.create_table(
        "chat_widget_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("hero_cta_label", sa.String(length=255), nullable=False, server_default="BioSilk Chat"),
        sa.Column("hero_subtitle", sa.Text(), nullable=False, server_default=sa.text("'Ask BioSilk Chat about soil health, weather, markets, and crop conditions.'")),
        sa.Column("launcher_label", sa.String(length=255), nullable=False, server_default="BioSilk Chat"),
        sa.Column("guest_teaser_limit", sa.Integer(), nullable=False, server_default="4"),
        sa.Column("greeting_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("quick_actions_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("theme_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"], ondelete="SET NULL"),
    )

    # 2. chat_assistants
    op.create_table(
        "chat_assistants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False, server_default="gemini"),
        sa.Column("model", sa.String(length=128), nullable=False, server_default="gemini-1.5-flash"),
        sa.Column("access_mode", sa.String(length=64), nullable=False, server_default="guest_teaser"),
        sa.Column("enabled_tools_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("supported_languages_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("active_prompt_version_id", postgresql.UUID(as_uuid=True), nullable=True), # FK added later
        sa.Column("config_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_chat_assistants_active", "chat_assistants", ["is_active"], unique=False)
    op.create_index("ix_chat_assistants_slug", "chat_assistants", ["slug"], unique=True)

    # 3. chat_prompt_versions
    op.create_table(
        "chat_prompt_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("assistant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scope", sa.String(length=64), nullable=False, server_default="general"),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("system_prompt", sa.Text(), nullable=False),
        sa.Column("tool_instructions_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("fallback_rules_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("refusal_rules_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["assistant_id"], ["chat_assistants.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_chat_prompt_versions_assistant_scope", "chat_prompt_versions", ["assistant_id", "scope"], unique=False)

    # Add circular FK to chat_assistants
    op.create_foreign_key(
        "fk_chat_assistants_active_prompt_version_id",
        "chat_assistants", "chat_prompt_versions",
        ["active_prompt_version_id"], ["id"],
        ondelete="SET NULL"
    )

    # 4. chat_conversations
    op.create_table(
        "chat_conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("assistant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("guest_token", sa.String(length=128), nullable=True),
        sa.Column("channel", sa.String(length=64), nullable=False, server_default="web"),
        sa.Column("status", sa.String(length=64), nullable=False, server_default="active"),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["assistant_id"], ["chat_assistants.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_chat_conversations_guest", "chat_conversations", ["guest_token", "last_activity_at"], unique=False)
    op.create_index("ix_chat_conversations_user", "chat_conversations", ["user_id", "last_activity_at"], unique=False)

    # 5. chat_messages
    op.create_table(
        "chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("structured_payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("citations_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("token_stats_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["conversation_id"], ["chat_conversations.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_chat_messages_conversation", "chat_messages", ["conversation_id", "created_at"], unique=False)

    # 6. chat_attachments
    op.create_table(
        "chat_attachments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("message_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("uploaded_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("guest_token", sa.String(length=128), nullable=True),
        sa.Column("attachment_type", sa.String(length=32), nullable=False, server_default="file"),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=120), nullable=True),
        sa.Column("byte_size", sa.Integer(), nullable=True),
        sa.Column("local_path", sa.Text(), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["conversation_id"], ["chat_conversations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["message_id"], ["chat_messages.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["uploaded_by_user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_chat_attachments_conversation", "chat_attachments", ["conversation_id", "created_at"], unique=False)

    # 7. chat_tool_runs
    op.create_table(
        "chat_tool_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("message_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("tool_name", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="succeeded"),
        sa.Column("input_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("output_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["conversation_id"], ["chat_conversations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["message_id"], ["chat_messages.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_chat_tool_runs_conversation", "chat_tool_runs", ["conversation_id", "created_at"], unique=False)
    op.create_index("ix_chat_tool_runs_tool_name", "chat_tool_runs", ["tool_name"], unique=False)

    # 8. chat_knowledge_sources
    op.create_table(
        "chat_knowledge_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("assistant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body_text", sa.Text(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("reindexed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["assistant_id"], ["chat_assistants.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_chat_knowledge_sources_enabled", "chat_knowledge_sources", ["is_enabled"], unique=False)

    # 9. chat_knowledge_chunks
    op.create_table(
        "chat_knowledge_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["source_id"], ["chat_knowledge_sources.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_chat_knowledge_chunks_source", "chat_knowledge_chunks", ["source_id", "chunk_index"], unique=False)

    # 10. chat_analysis_sessions
    op.create_table(
        "chat_analysis_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("formula_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("formula_name", sa.String(length=255), nullable=True),
        sa.Column("input_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("result_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["formula_id"], ["calculator_formulas.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_chat_analysis_sessions_user", "chat_analysis_sessions", ["user_id", "created_at"], unique=False)

    # 11. pest_diagnosis_cases
    op.create_table(
        "pest_diagnosis_cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("message_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("attachment_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("classifier_label", sa.String(length=255), nullable=True),
        sa.Column("classifier_confidence", sa.Float(), nullable=True),
        sa.Column("fallback_label", sa.String(length=255), nullable=True),
        sa.Column("fallback_confidence", sa.Float(), nullable=True),
        sa.Column("recommended_action", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="completed"),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["attachment_id"], ["chat_attachments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["conversation_id"], ["chat_conversations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["message_id"], ["chat_messages.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_pest_diagnosis_cases_created", "pest_diagnosis_cases", ["created_at"], unique=False)

    # 12. weather_cache
    op.create_table(
        "weather_cache",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("location_key", sa.String(length=255), nullable=False),
        sa.Column("normalized_location", sa.String(length=255), nullable=False),
        sa.Column("forecast_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("advisory_text", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_weather_cache_location_key", "weather_cache", ["location_key"], unique=True)

    # 13. market_price_cache
    op.create_table(
        "market_price_cache",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("lookup_key", sa.String(length=255), nullable=False),
        sa.Column("crop_name", sa.String(length=255), nullable=False),
        sa.Column("region", sa.String(length=255), nullable=False),
        sa.Column("market_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("advisory_text", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_market_price_cache_lookup_key", "market_price_cache", ["lookup_key"], unique=True)


def downgrade() -> None:
    # Drop tables in reverse order to respect foreign keys
    op.drop_index("ix_market_price_cache_lookup_key", table_name="market_price_cache")
    op.drop_table("market_price_cache")

    op.drop_index("ix_weather_cache_location_key", table_name="weather_cache")
    op.drop_table("weather_cache")

    op.drop_index("ix_pest_diagnosis_cases_created", table_name="pest_diagnosis_cases")
    op.drop_table("pest_diagnosis_cases")

    op.drop_index("ix_chat_analysis_sessions_user", table_name="chat_analysis_sessions")
    op.drop_table("chat_analysis_sessions")

    op.drop_index("ix_chat_knowledge_chunks_source", table_name="chat_knowledge_chunks")
    op.drop_table("chat_knowledge_chunks")

    op.drop_index("ix_chat_knowledge_sources_enabled", table_name="chat_knowledge_sources")
    op.drop_table("chat_knowledge_sources")

    op.drop_index("ix_chat_tool_runs_tool_name", table_name="chat_tool_runs")
    op.drop_index("ix_chat_tool_runs_conversation", table_name="chat_tool_runs")
    op.drop_table("chat_tool_runs")

    op.drop_index("ix_chat_attachments_conversation", table_name="chat_attachments")
    op.drop_table("chat_attachments")

    op.drop_index("ix_chat_messages_conversation", table_name="chat_messages")
    op.drop_table("chat_messages")

    op.drop_index("ix_chat_conversations_user", table_name="chat_conversations")
    op.drop_index("ix_chat_conversations_guest", table_name="chat_conversations")
    op.drop_table("chat_conversations")

    op.drop_constraint("fk_chat_assistants_active_prompt_version_id", "chat_assistants", type_="foreignkey")

    op.drop_index("ix_chat_prompt_versions_assistant_scope", table_name="chat_prompt_versions")
    op.drop_table("chat_prompt_versions")

    op.drop_index("ix_chat_assistants_slug", table_name="chat_assistants")
    op.drop_index("ix_chat_assistants_active", table_name="chat_assistants")
    op.drop_table("chat_assistants")

    op.drop_table("chat_widget_settings")
