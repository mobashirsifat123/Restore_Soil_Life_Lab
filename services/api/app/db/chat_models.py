from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

EMPTY_JSON = text("'{}'::jsonb")
EMPTY_ARRAY_JSON = text("'[]'::jsonb")


class ChatAssistant(Base):
    __tablename__ = "chat_assistants"
    __table_args__ = (
        Index("ix_chat_assistants_active", "is_active"),
        Index("ix_chat_assistants_slug", "slug", unique=True),
    )

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    slug: Mapped[str] = mapped_column(String(120), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(64), nullable=False, default="deepseek", server_default="deepseek")
    model: Mapped[str] = mapped_column(String(128), nullable=False, default="deepseek-chat", server_default="deepseek-chat")
    access_mode: Mapped[str] = mapped_column(String(64), nullable=False, default="guest_teaser", server_default="guest_teaser")
    enabled_tools_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default=EMPTY_ARRAY_JSON)
    supported_languages_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default=EMPTY_ARRAY_JSON)
    active_prompt_version_id: Mapped[str | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("chat_prompt_versions.id", ondelete="SET NULL"), nullable=True)
    config_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class ChatWidgetSetting(Base):
    __tablename__ = "chat_widget_settings"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    hero_cta_label: Mapped[str] = mapped_column(String(255), nullable=False, default="BioSilk Chat", server_default="BioSilk Chat")
    hero_subtitle: Mapped[str] = mapped_column(Text, nullable=False, default="Ask BioSilk Chat about soil health, weather, markets, and crop conditions.", server_default=text("'Ask BioSilk Chat about soil health, weather, markets, and crop conditions.'"))
    launcher_label: Mapped[str] = mapped_column(String(255), nullable=False, default="BioSilk Chat", server_default="BioSilk Chat")
    guest_teaser_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=4, server_default="4")
    greeting_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    quick_actions_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default=EMPTY_ARRAY_JSON)
    theme_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_by_user_id: Mapped[str | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)


class ChatPromptVersion(Base):
    __tablename__ = "chat_prompt_versions"
    __table_args__ = (
        Index("ix_chat_prompt_versions_assistant_scope", "assistant_id", "scope"),
    )

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    assistant_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("chat_assistants.id", ondelete="CASCADE"), nullable=False)
    scope: Mapped[str] = mapped_column(String(64), nullable=False, default="general", server_default="general")
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    tool_instructions_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    fallback_rules_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    refusal_rules_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class ChatConversation(Base):
    __tablename__ = "chat_conversations"
    __table_args__ = (
        Index("ix_chat_conversations_user", "user_id", "last_activity_at"),
        Index("ix_chat_conversations_guest", "guest_token", "last_activity_at"),
    )

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    organization_id: Mapped[str | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    user_id: Mapped[str | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assistant_id: Mapped[str | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("chat_assistants.id", ondelete="SET NULL"), nullable=True)
    guest_token: Mapped[str | None] = mapped_column(String(128), nullable=True)
    channel: Mapped[str] = mapped_column(String(64), nullable=False, default="web", server_default="web")
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="active", server_default="active")
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    __table_args__ = (
        Index("ix_chat_messages_conversation", "conversation_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    conversation_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("chat_conversations.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    structured_payload_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    citations_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default=EMPTY_ARRAY_JSON)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    token_stats_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class ChatAttachment(Base):
    __tablename__ = "chat_attachments"
    __table_args__ = (
        Index("ix_chat_attachments_conversation", "conversation_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    conversation_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("chat_conversations.id", ondelete="CASCADE"), nullable=False)
    message_id: Mapped[str | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("chat_messages.id", ondelete="SET NULL"), nullable=True)
    uploaded_by_user_id: Mapped[str | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    guest_token: Mapped[str | None] = mapped_column(String(128), nullable=True)
    attachment_type: Mapped[str] = mapped_column(String(32), nullable=False, default="file", server_default="file")
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    byte_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    local_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class ChatToolRun(Base):
    __tablename__ = "chat_tool_runs"
    __table_args__ = (
        Index("ix_chat_tool_runs_conversation", "conversation_id", "created_at"),
        Index("ix_chat_tool_runs_tool_name", "tool_name"),
    )

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    conversation_id: Mapped[str | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("chat_conversations.id", ondelete="SET NULL"), nullable=True)
    message_id: Mapped[str | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("chat_messages.id", ondelete="SET NULL"), nullable=True)
    tool_name: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="succeeded", server_default="succeeded")
    input_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    output_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class ChatKnowledgeSource(Base):
    __tablename__ = "chat_knowledge_sources"
    __table_args__ = (
        Index("ix_chat_knowledge_sources_enabled", "is_enabled"),
    )

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    assistant_id: Mapped[str | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("chat_assistants.id", ondelete="SET NULL"), nullable=True)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("true"))
    reindexed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    created_by_user_id: Mapped[str | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class ChatKnowledgeChunk(Base):
    __tablename__ = "chat_knowledge_chunks"
    __table_args__ = (
        Index("ix_chat_knowledge_chunks_source", "source_id", "chunk_index"),
    )

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    source_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("chat_knowledge_sources.id", ondelete="CASCADE"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class ChatAnalysisSession(Base):
    __tablename__ = "chat_analysis_sessions"
    __table_args__ = (
        Index("ix_chat_analysis_sessions_user", "user_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    organization_id: Mapped[str | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    user_id: Mapped[str | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    formula_id: Mapped[str | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("calculator_formulas.id", ondelete="SET NULL"), nullable=True)
    formula_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    input_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    result_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class PestDiagnosisCase(Base):
    __tablename__ = "pest_diagnosis_cases"
    __table_args__ = (
        Index("ix_pest_diagnosis_cases_created", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    conversation_id: Mapped[str | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("chat_conversations.id", ondelete="SET NULL"), nullable=True)
    message_id: Mapped[str | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("chat_messages.id", ondelete="SET NULL"), nullable=True)
    attachment_id: Mapped[str | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("chat_attachments.id", ondelete="SET NULL"), nullable=True)
    classifier_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    classifier_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    fallback_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fallback_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    recommended_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="completed", server_default="completed")
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class WeatherCache(Base):
    __tablename__ = "weather_cache"
    __table_args__ = (
        Index("ix_weather_cache_location_key", "location_key", unique=True),
    )

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    location_key: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_location: Mapped[str] = mapped_column(String(255), nullable=False)
    forecast_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    advisory_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class MarketPriceCache(Base):
    __tablename__ = "market_price_cache"
    __table_args__ = (
        Index("ix_market_price_cache_lookup_key", "lookup_key", unique=True),
    )

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    lookup_key: Mapped[str] = mapped_column(String(255), nullable=False)
    crop_name: Mapped[str] = mapped_column(String(255), nullable=False)
    region: Mapped[str] = mapped_column(String(255), nullable=False)
    market_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    advisory_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
