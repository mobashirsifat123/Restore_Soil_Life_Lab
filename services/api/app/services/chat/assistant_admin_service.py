from __future__ import annotations

from uuid import UUID

from app.core.errors import AppError
from app.db.chat_models import ChatAssistant, ChatKnowledgeSource, ChatPromptVersion
from app.domain.auth import AuthenticatedUser
from app.repositories.chat_repository import ChatRepository
from app.schemas.chat import (
    ChatAdminConfigResponse,
    ChatAnalytics,
    ChatAssistantPromptPack,
    ChatAssistantResponse,
    ChatAssistantUpsert,
    ChatKnowledgeSourceCreate,
    ChatKnowledgeSourceListResponse,
    ChatKnowledgeSourceResponse,
    ChatReindexResponse,
    ChatWidgetConfigResponse,
    ChatWidgetConfigUpdate,
)
from app.services.chat.knowledge_base_service import KnowledgeBaseService


class AssistantAdminService:
    def __init__(self, repository: ChatRepository, knowledge_base_service: KnowledgeBaseService) -> None:
        self.repository = repository
        self.knowledge_base_service = knowledge_base_service

    def get_admin_config(self, *, current_user: AuthenticatedUser) -> ChatAdminConfigResponse:
        self.knowledge_base_service.sync_system_sources()
        widget = self.serialize_widget(self.repository.get_widget_config())
        assistant = self.repository.get_active_assistant()
        analytics = ChatAnalytics.model_validate(self.repository.analytics())
        return ChatAdminConfigResponse(
            widget=widget,
            active_assistant=self.serialize_assistant(assistant) if assistant else None,
            analytics=analytics,
        )

    def update_widget_config(
        self,
        *,
        current_user: AuthenticatedUser,
        payload: ChatWidgetConfigUpdate,
    ) -> ChatWidgetConfigResponse:
        config = self.repository.get_widget_config()
        updates = payload.model_dump(exclude_none=True)
        if "greeting" in updates:
            config.greeting_json = payload.greeting.model_dump(by_alias=True) if payload.greeting else {}
            updates.pop("greeting", None)
        if "quick_actions" in updates:
            config.quick_actions_json = payload.quick_actions or []
            updates.pop("quick_actions", None)
        if "theme" in updates:
            config.theme_json = payload.theme or {}
            updates.pop("theme", None)
        for key, value in updates.items():
            setattr(config, key, value)
        config.updated_by_user_id = current_user.user_id
        return self.serialize_widget(self.repository.update_widget_config(config))

    def list_assistants(self) -> list[ChatAssistantResponse]:
        return [self.serialize_assistant(item) for item in self.repository.list_assistants()]

    def create_assistant(self, *, payload: ChatAssistantUpsert) -> ChatAssistantResponse:
        assistant = ChatAssistant(
            slug=payload.slug,
            name=payload.name,
            provider=payload.provider,
            model=payload.model,
            access_mode=payload.access_mode,
            enabled_tools_json=payload.enabled_tools,
            supported_languages_json=payload.supported_languages,
            config_json=payload.config,
            is_active=payload.is_active,
        )
        assistant = self.repository.create_assistant(assistant)
        self._replace_prompt_pack(assistant.id, payload.prompt_pack)
        assistant = self.repository.get_assistant(assistant.id)
        if assistant is None:
            raise AppError(status_code=500, code="chat_assistant_missing", message="Assistant could not be loaded.")
        return self.serialize_assistant(assistant)

    def update_assistant(self, *, assistant_id: UUID, payload: ChatAssistantUpsert) -> ChatAssistantResponse:
        assistant = self.repository.get_assistant(assistant_id)
        if assistant is None:
            raise AppError(status_code=404, code="chat_assistant_not_found", message="Assistant not found.")
        assistant.slug = payload.slug
        assistant.name = payload.name
        assistant.provider = payload.provider
        assistant.model = payload.model
        assistant.access_mode = payload.access_mode
        assistant.enabled_tools_json = payload.enabled_tools
        assistant.supported_languages_json = payload.supported_languages
        assistant.config_json = payload.config
        assistant.is_active = payload.is_active
        assistant = self.repository.update_assistant(assistant)
        self._replace_prompt_pack(assistant.id, payload.prompt_pack)
        assistant = self.repository.get_assistant(assistant.id)
        if assistant is None:
            raise AppError(status_code=500, code="chat_assistant_missing", message="Assistant could not be loaded.")
        return self.serialize_assistant(assistant)

    def list_sources(self) -> ChatKnowledgeSourceListResponse:
        self.knowledge_base_service.sync_system_sources()
        items = self.repository.list_sources()
        return ChatKnowledgeSourceListResponse(items=[self.serialize_source(item) for item in items])

    def create_source(
        self,
        *,
        current_user: AuthenticatedUser,
        payload: ChatKnowledgeSourceCreate,
    ) -> ChatKnowledgeSourceResponse:
        source = ChatKnowledgeSource(
            source_type=payload.source_type,
            title=payload.title,
            body_text=payload.body_text,
            source_url=payload.source_url,
            is_enabled=payload.is_enabled,
            metadata_json=payload.metadata,
            created_by_user_id=current_user.user_id,
        )
        return self.serialize_source(self.repository.create_source(source))

    def reindex_source(self, *, source_id: UUID) -> ChatReindexResponse:
        self.knowledge_base_service.sync_system_sources()
        source, count = self.knowledge_base_service.reindex_source(source_id)
        return ChatReindexResponse(
            source_id=source.id,
            chunk_count=count,
            reindexed_at=source.reindexed_at,
        )

    def _replace_prompt_pack(self, assistant_id: UUID, prompt_pack: ChatAssistantPromptPack) -> None:
        self.repository.deactivate_prompt_versions(assistant_id)
        prompt_versions = [
            ChatPromptVersion(
                assistant_id=assistant_id,
                scope=scope,
                label=f"{scope.replace('_', ' ').title()} Prompt",
                system_prompt=text,
                tool_instructions_json={},
                fallback_rules_json=prompt_pack.fallback_rules,
                refusal_rules_json=prompt_pack.refusal_rules,
                is_active=True,
            )
            for scope, text in {
                "general": prompt_pack.general_prompt,
                "soil": prompt_pack.soil_prompt,
                "pest": prompt_pack.pest_prompt,
                "market": prompt_pack.market_prompt,
                "weather": prompt_pack.weather_prompt,
                "member": prompt_pack.member_prompt,
            }.items()
            if text.strip()
        ]
        if not prompt_versions:
            prompt_versions.append(
                ChatPromptVersion(
                    assistant_id=assistant_id,
                    scope="general",
                    label="General Prompt",
                    system_prompt="You are BioSilk Chat, a practical farm and soil assistant. Stay grounded in tool results and known sources.",
                    tool_instructions_json={},
                    fallback_rules_json=prompt_pack.fallback_rules,
                    refusal_rules_json=prompt_pack.refusal_rules,
                    is_active=True,
                )
            )
        created = self.repository.create_prompt_versions(prompt_versions)
        assistant = self.repository.get_assistant(assistant_id)
        if assistant is not None:
            assistant.active_prompt_version_id = created[0].id
            self.repository.update_assistant(assistant)

    def serialize_assistant(self, assistant: ChatAssistant | None) -> ChatAssistantResponse:
        if assistant is None:
            raise AppError(status_code=404, code="chat_assistant_not_found", message="Assistant not found.")
        prompt_versions = self.repository.get_prompt_versions(assistant.id)
        prompt_pack = ChatAssistantPromptPack(
            general_prompt=prompt_versions.get("general").system_prompt if prompt_versions.get("general") else "",
            soil_prompt=prompt_versions.get("soil").system_prompt if prompt_versions.get("soil") else "",
            pest_prompt=prompt_versions.get("pest").system_prompt if prompt_versions.get("pest") else "",
            market_prompt=prompt_versions.get("market").system_prompt if prompt_versions.get("market") else "",
            weather_prompt=prompt_versions.get("weather").system_prompt if prompt_versions.get("weather") else "",
            member_prompt=prompt_versions.get("member").system_prompt if prompt_versions.get("member") else "",
            fallback_rules=prompt_versions.get("general").fallback_rules_json if prompt_versions.get("general") else {},
            refusal_rules=prompt_versions.get("general").refusal_rules_json if prompt_versions.get("general") else {},
        )
        return ChatAssistantResponse.model_validate(
            {
                "id": assistant.id,
                "slug": assistant.slug,
                "name": assistant.name,
                "provider": assistant.provider,
                "model": assistant.model,
                "access_mode": assistant.access_mode,
                "enabled_tools": assistant.enabled_tools_json or [],
                "supported_languages": assistant.supported_languages_json or [],
                "config": assistant.config_json or {},
                "is_active": assistant.is_active,
                "prompt_pack": prompt_pack,
                "created_at": assistant.created_at,
                "updated_at": assistant.updated_at,
            }
        )

    @staticmethod
    def serialize_widget(config) -> ChatWidgetConfigResponse:
        return ChatWidgetConfigResponse.model_validate(
            {
                "id": config.id,
                "hero_cta_label": config.hero_cta_label,
                "hero_subtitle": config.hero_subtitle,
                "launcher_label": config.launcher_label,
                "guest_teaser_limit": config.guest_teaser_limit,
                "greeting": config.greeting_json or {},
                "quick_actions": config.quick_actions_json or [],
                "theme": config.theme_json or {},
            }
        )

    @staticmethod
    def serialize_source(source: ChatKnowledgeSource) -> ChatKnowledgeSourceResponse:
        return ChatKnowledgeSourceResponse.model_validate(
            {
                "id": source.id,
                "source_type": source.source_type,
                "title": source.title,
                "body_text": source.body_text,
                "source_url": source.source_url,
                "is_enabled": source.is_enabled,
                "metadata": source.metadata_json or {},
                "reindexed_at": source.reindexed_at,
                "created_at": source.created_at,
            }
        )
