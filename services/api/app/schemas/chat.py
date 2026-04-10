from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas.common import ApiModel, JsonDict


class ChatCitation(ApiModel):
    title: str
    source_type: str
    snippet: str | None = None
    source_url: str | None = None


class ChatAttachmentResponse(ApiModel):
    id: UUID
    attachment_type: str
    filename: str
    mime_type: str | None = None
    byte_size: int | None = None
    created_at: datetime


class ChatMessageResponse(ApiModel):
    id: UUID
    role: str
    content: str
    structured_payload: JsonDict = Field(default_factory=dict)
    citations: list[ChatCitation] = Field(default_factory=list)
    metadata: JsonDict = Field(default_factory=dict)
    latency_ms: int | None = None
    created_at: datetime


class ChatConversationSummary(ApiModel):
    id: UUID
    title: str | None = None
    channel: str
    status: str
    summary: str | None = None
    last_activity_at: datetime
    created_at: datetime


class ChatConversationDetail(ChatConversationSummary):
    messages: list[ChatMessageResponse] = Field(default_factory=list)
    attachments: list[ChatAttachmentResponse] = Field(default_factory=list)


class ChatConversationListResponse(ApiModel):
    items: list[ChatConversationSummary]


class ChatConversationCreate(ApiModel):
    title: str | None = Field(default=None, max_length=255)
    channel: str = Field(default="web", max_length=64)


class ChatMessageCreate(ApiModel):
    content: str = Field(min_length=1)
    tool_hint: str | None = Field(default=None, max_length=120)
    quick_action: str | None = Field(default=None, max_length=120)
    attachment_ids: list[UUID] = Field(default_factory=list)
    metadata: JsonDict = Field(default_factory=dict)


class ChatAssistantPromptPack(ApiModel):
    general_prompt: str = ""
    soil_prompt: str = ""
    pest_prompt: str = ""
    market_prompt: str = ""
    weather_prompt: str = ""
    member_prompt: str = ""
    fallback_rules: JsonDict = Field(default_factory=dict)
    refusal_rules: JsonDict = Field(default_factory=dict)


class ChatAssistantResponse(ApiModel):
    id: UUID
    slug: str
    name: str
    provider: str
    model: str
    access_mode: str
    enabled_tools: list[str] = Field(default_factory=list)
    supported_languages: list[str] = Field(default_factory=list)
    config: JsonDict = Field(default_factory=dict)
    is_active: bool
    prompt_pack: ChatAssistantPromptPack
    created_at: datetime
    updated_at: datetime


class ChatAssistantUpsert(ApiModel):
    slug: str = Field(min_length=1, max_length=120)
    name: str = Field(min_length=1, max_length=255)
    provider: str = Field(default="deepseek", max_length=64)
    model: str = Field(default="deepseek-chat", max_length=128)
    access_mode: str = Field(default="guest_teaser", max_length=64)
    enabled_tools: list[str] = Field(default_factory=list)
    supported_languages: list[str] = Field(default_factory=list)
    config: JsonDict = Field(default_factory=dict)
    is_active: bool = True
    prompt_pack: ChatAssistantPromptPack = Field(default_factory=ChatAssistantPromptPack)


class ChatWidgetGreeting(ApiModel):
    guest_title: str = "BioSilk Chat"
    guest_body: str = "Ask a basic farming question or sign in for deeper soil analysis."
    member_title: str = "Welcome back to BioSilk Chat"
    member_body: str = "Ask about your soil, upload a crop photo, or request weather and market guidance."


class ChatWidgetConfigResponse(ApiModel):
    id: UUID
    hero_cta_label: str
    hero_subtitle: str
    launcher_label: str
    guest_teaser_limit: int
    greeting: ChatWidgetGreeting
    quick_actions: list[dict] = Field(default_factory=list)
    theme: JsonDict = Field(default_factory=dict)


class ChatWidgetConfigUpdate(ApiModel):
    hero_cta_label: str | None = Field(default=None, max_length=255)
    hero_subtitle: str | None = None
    launcher_label: str | None = Field(default=None, max_length=255)
    guest_teaser_limit: int | None = Field(default=None, ge=1, le=20)
    greeting: ChatWidgetGreeting | None = None
    quick_actions: list[dict] | None = None
    theme: JsonDict | None = None


class ChatKnowledgeSourceResponse(ApiModel):
    id: UUID
    source_type: str
    title: str
    body_text: str | None = None
    source_url: str | None = None
    is_enabled: bool
    metadata: JsonDict = Field(default_factory=dict)
    reindexed_at: datetime | None = None
    created_at: datetime


class ChatKnowledgeSourceCreate(ApiModel):
    source_type: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=1, max_length=255)
    body_text: str | None = None
    source_url: str | None = None
    is_enabled: bool = True
    metadata: JsonDict = Field(default_factory=dict)


class ChatKnowledgeSourceListResponse(ApiModel):
    items: list[ChatKnowledgeSourceResponse]


class ChatReindexResponse(ApiModel):
    source_id: UUID
    chunk_count: int
    reindexed_at: datetime


class ChatToolStatus(ApiModel):
    tool_name: str
    status: str
    confidence: float | None = None
    detail: str | None = None


class ChatSoilAnalysisInput(ApiModel):
    ph: float
    organic_matter: float
    moisture: float
    temperature: float
    bacteria: float
    fungi: float
    protozoa: float = 0
    nematodes: float = 0
    compaction: float | None = None
    nitrate_n: float | None = None
    soil_texture: str | None = None
    production_system: str | None = None


class ChatSoilAnalysisResponse(ApiModel):
    score: float
    band: str
    summary: str
    formula_name: str | None = None
    recommendations: list[str] = Field(default_factory=list)
    component_scores: JsonDict = Field(default_factory=dict)
    citations: list[ChatCitation] = Field(default_factory=list)


class ChatAttachmentUpload(ApiModel):
    file_name: str
    mime_type: str | None = None
    byte_size: int | None = None
    attachment_type: str = "file"


class ChatAnalytics(ApiModel):
    conversation_count: int = 0
    message_count: int = 0
    low_confidence_count: int = 0
    failed_tool_runs: int = 0


class ChatAdminConfigResponse(ApiModel):
    widget: ChatWidgetConfigResponse
    active_assistant: ChatAssistantResponse | None = None
    analytics: ChatAnalytics
