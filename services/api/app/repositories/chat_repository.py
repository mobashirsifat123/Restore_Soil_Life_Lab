from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import delete, desc, func, or_, select
from sqlalchemy.orm import Session

from app.db.chat_models import (
    ChatAnalysisSession,
    ChatAssistant,
    ChatAttachment,
    ChatConversation,
    ChatKnowledgeChunk,
    ChatKnowledgeSource,
    ChatMessage,
    ChatPromptVersion,
    ChatToolRun,
    ChatWidgetSetting,
    MarketPriceCache,
    PestDiagnosisCase,
    WeatherCache,
)


class ChatRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_widget_config(self) -> ChatWidgetSetting:
        config = self.session.scalar(
            select(ChatWidgetSetting).order_by(ChatWidgetSetting.updated_at.desc())
        )
        if config is not None:
            return config

        config = ChatWidgetSetting(
            greeting_json={
                "guestTitle": "BioSilk Chat",
                "guestBody": "Ask basic farming questions or sign in for deeper soil guidance.",
                "memberTitle": "BioSilk Chat is ready",
                "memberBody": "Use BioSilk Chat for soil analysis, weather, market guidance, and crop questions.",
            },
            quick_actions_json=[
                {"id": "soil_analysis", "label": "Analyze my soil", "guestEnabled": False},
                {"id": "soil_history", "label": "Explain my last result", "guestEnabled": False},
                {"id": "pest_diagnosis", "label": "Upload crop photo", "guestEnabled": True},
                {"id": "weather", "label": "Weather advice", "guestEnabled": True},
                {"id": "market_prices", "label": "Market prices", "guestEnabled": True},
            ],
            theme_json={
                "accent": "#76c2a4",
                "panel": "#ffffff",
                "heroBadge": "BioSilk Chat",
            },
        )
        self.session.add(config)
        self.session.commit()
        self.session.refresh(config)
        return config

    def update_widget_config(self, config: ChatWidgetSetting) -> ChatWidgetSetting:
        config.updated_at = datetime.now(UTC)
        self.session.add(config)
        self.session.commit()
        self.session.refresh(config)
        return config

    def list_assistants(self) -> list[ChatAssistant]:
        return list(self.session.scalars(select(ChatAssistant).order_by(desc(ChatAssistant.updated_at))).all())

    def get_assistant(self, assistant_id: UUID) -> ChatAssistant | None:
        return self.session.get(ChatAssistant, assistant_id)

    def get_active_assistant(self) -> ChatAssistant | None:
        return self.session.scalar(select(ChatAssistant).where(ChatAssistant.is_active.is_(True)).order_by(desc(ChatAssistant.updated_at)))

    def create_assistant(self, assistant: ChatAssistant) -> ChatAssistant:
        if assistant.is_active:
            self.session.query(ChatAssistant).update({ChatAssistant.is_active: False})
        self.session.add(assistant)
        self.session.commit()
        self.session.refresh(assistant)
        return assistant

    def update_assistant(self, assistant: ChatAssistant) -> ChatAssistant:
        if assistant.is_active:
            self.session.query(ChatAssistant).filter(ChatAssistant.id != assistant.id).update({ChatAssistant.is_active: False})
        assistant.updated_at = datetime.now(UTC)
        self.session.add(assistant)
        self.session.commit()
        self.session.refresh(assistant)
        return assistant

    def deactivate_prompt_versions(self, assistant_id: UUID) -> None:
        self.session.query(ChatPromptVersion).filter(ChatPromptVersion.assistant_id == assistant_id).update({ChatPromptVersion.is_active: False})
        self.session.flush()

    def create_prompt_versions(self, prompt_versions: list[ChatPromptVersion]) -> list[ChatPromptVersion]:
        self.session.add_all(prompt_versions)
        self.session.flush()
        return prompt_versions

    def list_prompt_versions(self, assistant_id: UUID) -> list[ChatPromptVersion]:
        return list(
            self.session.scalars(
                select(ChatPromptVersion)
                .where(ChatPromptVersion.assistant_id == assistant_id)
                .order_by(ChatPromptVersion.scope.asc(), desc(ChatPromptVersion.updated_at))
            ).all()
        )

    def get_prompt_versions(self, assistant_id: UUID) -> dict[str, ChatPromptVersion]:
        items = self.list_prompt_versions(assistant_id)
        latest: dict[str, ChatPromptVersion] = {}
        for item in items:
            latest.setdefault(item.scope, item)
        return latest

    def list_sources(self) -> list[ChatKnowledgeSource]:
        return list(self.session.scalars(select(ChatKnowledgeSource).order_by(desc(ChatKnowledgeSource.updated_at))).all())

    def create_source(self, source: ChatKnowledgeSource) -> ChatKnowledgeSource:
        self.session.add(source)
        self.session.commit()
        self.session.refresh(source)
        return source

    def get_source(self, source_id: UUID) -> ChatKnowledgeSource | None:
        return self.session.get(ChatKnowledgeSource, source_id)

    def update_source(self, source: ChatKnowledgeSource) -> ChatKnowledgeSource:
        source.updated_at = datetime.now(UTC)
        self.session.add(source)
        self.session.commit()
        self.session.refresh(source)
        return source

    def replace_source_chunks(self, source_id: UUID, chunks: list[ChatKnowledgeChunk]) -> int:
        self.session.execute(delete(ChatKnowledgeChunk).where(ChatKnowledgeChunk.source_id == source_id))
        if chunks:
            self.session.add_all(chunks)
        source = self.get_source(source_id)
        if source is not None:
            source.reindexed_at = datetime.now(UTC)
            source.updated_at = datetime.now(UTC)
            self.session.add(source)
        self.session.commit()
        return len(chunks)

    def search_chunks(self, query_text: str, limit: int = 5) -> list[tuple[ChatKnowledgeChunk, ChatKnowledgeSource]]:
        tokens = [token.lower() for token in query_text.split() if len(token) > 2][:6]
        stmt = (
            select(ChatKnowledgeChunk, ChatKnowledgeSource)
            .join(ChatKnowledgeSource, ChatKnowledgeSource.id == ChatKnowledgeChunk.source_id)
            .where(ChatKnowledgeSource.is_enabled.is_(True))
        )
        if tokens:
            stmt = stmt.where(
                or_(*[func.lower(ChatKnowledgeChunk.content).contains(token) for token in tokens])
            )
        stmt = stmt.order_by(desc(ChatKnowledgeSource.reindexed_at), ChatKnowledgeChunk.chunk_index.asc()).limit(limit)
        return list(self.session.execute(stmt).all())

    def create_conversation(self, conversation: ChatConversation) -> ChatConversation:
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    def list_conversations(
        self,
        *,
        user_id: UUID | None,
        guest_token: str | None,
        limit: int = 20,
    ) -> list[ChatConversation]:
        stmt = select(ChatConversation).order_by(desc(ChatConversation.last_activity_at)).limit(limit)
        if user_id is not None:
            stmt = stmt.where(ChatConversation.user_id == user_id)
        elif guest_token:
            stmt = stmt.where(ChatConversation.guest_token == guest_token)
        else:
            return []
        return list(self.session.scalars(stmt).all())

    def get_conversation(
        self,
        conversation_id: UUID,
        *,
        user_id: UUID | None,
        guest_token: str | None,
    ) -> ChatConversation | None:
        stmt = select(ChatConversation).where(ChatConversation.id == conversation_id)
        if user_id is not None:
            stmt = stmt.where(ChatConversation.user_id == user_id)
        elif guest_token:
            stmt = stmt.where(ChatConversation.guest_token == guest_token)
        else:
            return None
        return self.session.scalar(stmt)

    def update_conversation(self, conversation: ChatConversation) -> ChatConversation:
        conversation.updated_at = datetime.now(UTC)
        conversation.last_activity_at = datetime.now(UTC)
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    def list_messages(self, conversation_id: UUID) -> list[ChatMessage]:
        return list(
            self.session.scalars(
                select(ChatMessage).where(ChatMessage.conversation_id == conversation_id).order_by(ChatMessage.created_at.asc())
            ).all()
        )

    def create_message(self, message: ChatMessage, *, update_conversation: ChatConversation | None = None) -> ChatMessage:
        self.session.add(message)
        if update_conversation is not None:
            update_conversation.updated_at = datetime.now(UTC)
            update_conversation.last_activity_at = datetime.now(UTC)
            self.session.add(update_conversation)
        self.session.commit()
        self.session.refresh(message)
        return message

    def list_attachments(self, conversation_id: UUID) -> list[ChatAttachment]:
        return list(
            self.session.scalars(
                select(ChatAttachment)
                .where(ChatAttachment.conversation_id == conversation_id)
                .order_by(ChatAttachment.created_at.asc())
            ).all()
        )

    def create_attachment(self, attachment: ChatAttachment) -> ChatAttachment:
        self.session.add(attachment)
        self.session.commit()
        self.session.refresh(attachment)
        return attachment

    def get_attachment(self, attachment_id: UUID) -> ChatAttachment | None:
        return self.session.get(ChatAttachment, attachment_id)

    def link_attachments_to_message(self, attachment_ids: list[UUID], message_id: UUID) -> None:
        if not attachment_ids:
            return
        self.session.query(ChatAttachment).filter(ChatAttachment.id.in_(attachment_ids)).update(
            {ChatAttachment.message_id: message_id},
            synchronize_session=False,
        )
        self.session.commit()

    def create_tool_run(self, tool_run: ChatToolRun) -> ChatToolRun:
        self.session.add(tool_run)
        self.session.commit()
        self.session.refresh(tool_run)
        return tool_run

    def save_analysis_session(self, item: ChatAnalysisSession) -> ChatAnalysisSession:
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def get_latest_analysis_session(self, user_id: UUID) -> ChatAnalysisSession | None:
        return self.session.scalar(
            select(ChatAnalysisSession)
            .where(ChatAnalysisSession.user_id == user_id)
            .order_by(desc(ChatAnalysisSession.created_at))
        )

    def create_pest_case(self, item: PestDiagnosisCase) -> PestDiagnosisCase:
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def get_weather_cache(self, location_key: str) -> WeatherCache | None:
        return self.session.scalar(select(WeatherCache).where(WeatherCache.location_key == location_key))

    def upsert_weather_cache(self, item: WeatherCache) -> WeatherCache:
        existing = self.get_weather_cache(item.location_key)
        if existing is not None:
            existing.normalized_location = item.normalized_location
            existing.forecast_json = item.forecast_json
            existing.advisory_text = item.advisory_text
            existing.expires_at = item.expires_at
            existing.updated_at = datetime.now(UTC)
            self.session.add(existing)
            self.session.commit()
            self.session.refresh(existing)
            return existing
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def get_market_cache(self, lookup_key: str) -> MarketPriceCache | None:
        return self.session.scalar(select(MarketPriceCache).where(MarketPriceCache.lookup_key == lookup_key))

    def upsert_market_cache(self, item: MarketPriceCache) -> MarketPriceCache:
        existing = self.get_market_cache(item.lookup_key)
        if existing is not None:
            existing.crop_name = item.crop_name
            existing.region = item.region
            existing.market_json = item.market_json
            existing.advisory_text = item.advisory_text
            existing.expires_at = item.expires_at
            existing.updated_at = datetime.now(UTC)
            self.session.add(existing)
            self.session.commit()
            self.session.refresh(existing)
            return existing
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def analytics(self) -> dict[str, int]:
        conversation_count = self.session.scalar(select(func.count()).select_from(ChatConversation)) or 0
        message_count = self.session.scalar(select(func.count()).select_from(ChatMessage)) or 0
        low_confidence_count = self.session.scalar(
            select(func.count()).select_from(ChatToolRun).where(ChatToolRun.confidence.is_not(None), ChatToolRun.confidence < 0.5)
        ) or 0
        failed_tool_runs = self.session.scalar(
            select(func.count()).select_from(ChatToolRun).where(ChatToolRun.status == "failed")
        ) or 0
        return {
            "conversation_count": int(conversation_count),
            "message_count": int(message_count),
            "low_confidence_count": int(low_confidence_count),
            "failed_tool_runs": int(failed_tool_runs),
        }
