from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from uuid import UUID

from fastapi import UploadFile

from app.core.errors import AppError
from app.db.chat_models import ChatAttachment, ChatConversation, ChatMessage
from app.domain.auth import AuthenticatedUser
from app.repositories.chat_repository import ChatRepository
from app.schemas.chat import (
    ChatAssistantPromptPack,
    ChatAssistantUpsert,
    ChatAttachmentResponse,
    ChatConversationCreate,
    ChatConversationDetail,
    ChatConversationListResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatSoilAnalysisInput,
    ChatSoilAnalysisResponse,
    ChatWidgetConfigResponse,
)
from app.services.chat.assistant_admin_service import AssistantAdminService
from app.services.chat.conversation_service import ConversationService
from app.services.chat.provider_service import ProviderService
from app.services.chat.tool_router_service import ToolRouterService

UPLOAD_ROOT = Path(__file__).resolve().parents[4] / "uploads" / "chat"


class AssistantService:
    def __init__(
        self,
        repository: ChatRepository,
        conversation_service: ConversationService,
        tool_router_service: ToolRouterService,
        provider_service: ProviderService,
        admin_service: AssistantAdminService,
    ) -> None:
        self.repository = repository
        self.conversation_service = conversation_service
        self.tool_router_service = tool_router_service
        self.provider_service = provider_service
        self.admin_service = admin_service

    def get_widget_config(self) -> ChatWidgetConfigResponse:
        assistant = self.repository.get_active_assistant()
        if assistant is None:
            self.admin_service.create_assistant(
                payload=ChatAssistantUpsert(
                    slug="biosilk-chat",
                    name="BioSilk Chat",
                    provider=self.provider_service.settings.default_chat_provider,
                    model=self.provider_service.settings.default_chat_model,
                    access_mode="guest_teaser",
                    enabled_tools=[
                        "knowledge_search",
                        "soil_analysis",
                        "soil_history",
                        "weather",
                        "market_prices",
                        "pest_diagnosis",
                    ],
                    supported_languages=["English"],
                    config={"showCitations": True, "showConfidence": True},
                    is_active=True,
                    prompt_pack=ChatAssistantPromptPack(
                        general_prompt="You are BioSilk Chat, a practical farm and soil assistant. Stay grounded in known sources and tool outputs.",
                        soil_prompt="When discussing soil, prioritize biological interpretation, explain uncertainty clearly, and give farmer-friendly next actions.",
                        pest_prompt="When diagnosing crop issues, never overclaim. Recommend field confirmation where confidence is low.",
                        market_prompt="Provide practical selling guidance and clearly state when live market feeds are not configured.",
                        weather_prompt="Translate weather into clear field actions related to soil protection, irrigation, and timing.",
                        member_prompt="When the member is signed in, connect advice to their saved soil analyses when available.",
                        fallback_rules={"guestTeaser": "Provide short helpful answers and invite sign-in for personalized analysis."},
                        refusal_rules={"safety": "Do not provide hazardous chemical advice without caution and uncertainty language."},
                    ),
                ),
            )
        else:
            self._sync_default_provider(assistant)
        return self.admin_service.serialize_widget(self.repository.get_widget_config())

    def list_conversations(
        self,
        *,
        current_user: AuthenticatedUser | None,
        guest_token: str | None,
    ) -> ChatConversationListResponse:
        return self.conversation_service.list_conversations(current_user=current_user, guest_token=guest_token)

    def create_conversation(
        self,
        *,
        payload: ChatConversationCreate,
        current_user: AuthenticatedUser | None,
        guest_token: str | None,
    ) -> ChatConversationDetail:
        if current_user is None and not guest_token:
            raise AppError(status_code=400, code="guest_token_required", message="Guest conversations require a guest token.")

        assistant = self.repository.get_active_assistant()
        conversation = ChatConversation(
            organization_id=current_user.organization_id if current_user else None,
            user_id=current_user.user_id if current_user else None,
            assistant_id=assistant.id if assistant else None,
            guest_token=guest_token if current_user is None else None,
            channel=payload.channel,
            title=payload.title or "BioSilk Chat",
            summary=None,
            metadata_json={"accessMode": "member" if current_user else "guest"},
        )
        conversation = self.repository.create_conversation(conversation)
        return self.conversation_service.get_conversation(
            conversation.id,
            current_user=current_user,
            guest_token=guest_token,
        )

    def get_conversation(
        self,
        *,
        conversation_id: UUID,
        current_user: AuthenticatedUser | None,
        guest_token: str | None,
    ) -> ChatConversationDetail:
        return self.conversation_service.get_conversation(
            conversation_id,
            current_user=current_user,
            guest_token=guest_token,
        )

    def upload_attachment(
        self,
        *,
        conversation_id: UUID,
        upload: UploadFile,
        current_user: AuthenticatedUser | None,
        guest_token: str | None,
    ) -> ChatAttachmentResponse:
        conversation = self.conversation_service.assert_access(
            conversation_id=conversation_id,
            current_user=current_user,
            guest_token=guest_token,
        )
        UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
        extension = Path(upload.filename or "").suffix
        target_path = UPLOAD_ROOT / f"{conversation.id}-{datetime.now(UTC).timestamp():.0f}{extension}"
        content = upload.file.read()
        with target_path.open("wb") as file_obj:
            file_obj.write(content)

        attachment = ChatAttachment(
            conversation_id=conversation.id,
            uploaded_by_user_id=current_user.user_id if current_user else None,
            guest_token=guest_token if current_user is None else None,
            attachment_type="image" if (upload.content_type or "").startswith("image/") else "file",
            filename=upload.filename or "attachment",
            mime_type=upload.content_type,
            byte_size=len(content),
            local_path=str(target_path),
            metadata_json={"originalFilename": upload.filename},
        )
        created = self.repository.create_attachment(attachment)
        return self.conversation_service.serialize_attachment(created)

    def send_message(
        self,
        *,
        conversation_id: UUID,
        payload: ChatMessageCreate,
        current_user: AuthenticatedUser | None,
        guest_token: str | None,
    ) -> ChatMessageResponse:
        conversation = self.conversation_service.assert_access(
            conversation_id=conversation_id,
            current_user=current_user,
            guest_token=guest_token,
        )
        assistant = self.repository.get_active_assistant()
        if assistant is None:
            self.get_widget_config()
            assistant = self.repository.get_active_assistant()
        if assistant is None:
            raise AppError(status_code=500, code="chat_assistant_missing", message="No active BioSilk Chat assistant is configured.")

        user_message = ChatMessage(
            conversation_id=conversation.id,
            role="user",
            content=payload.content,
            metadata_json={"toolHint": payload.tool_hint, "quickAction": payload.quick_action, **(payload.metadata or {})},
        )
        user_message = self.repository.create_message(user_message, update_conversation=conversation)
        if payload.attachment_ids:
            self.repository.link_attachments_to_message(payload.attachment_ids, user_message.id)

        attachment = None
        if payload.attachment_ids:
            attachment = self.repository.get_attachment(payload.attachment_ids[-1])

        started = perf_counter()
        tool_name = self.tool_router_service.detect_tool(
            payload.content,
            tool_hint=payload.tool_hint,
            quick_action=payload.quick_action,
            has_attachment=attachment is not None,
        )
        tool_result = self.tool_router_service.route(
            tool_name=tool_name,
            content=payload.content,
            current_user=current_user,
            conversation_id=conversation.id,
            message_id=user_message.id,
            attachment=attachment,
            metadata=payload.metadata,
        )
        duration_ms = int((perf_counter() - started) * 1000)

        prompt_versions = self.repository.get_prompt_versions(assistant.id)
        system_prompt = (
            prompt_versions.get(tool_name.replace("_prices", "").replace("_diagnosis", "").replace("_analysis", ""))
            or prompt_versions.get("general")
        )
        grounded_context = "\n".join(
            part
            for part in [
                tool_result.get("summary", ""),
                "\n".join(tool_result.get("recommendations", [])),
                "\n".join(citation.get("snippet", "") for citation in tool_result.get("citations", [])),
            ]
            if part
        )
        generated = self.provider_service.generate_reply(
            provider=assistant.provider,
            model=assistant.model,
            system_prompt=system_prompt.system_prompt if system_prompt else "",
            user_prompt=payload.content,
            grounded_context=grounded_context,
        )
        assistant_text = generated or self._fallback_assistant_reply(tool_result, current_user=current_user)

        assistant_message = ChatMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=assistant_text,
            structured_payload_json={k: v for k, v in tool_result.items() if k not in {"summary", "recommendations", "citations"}},
            citations_json=tool_result.get("citations", []),
            metadata_json={"toolName": tool_name, "recommendations": tool_result.get("recommendations", [])},
            latency_ms=duration_ms,
        )
        conversation.summary = assistant_text[:240]
        if conversation.title in {None, "", "BioSilk Chat"}:
            conversation.title = payload.content[:64]
        assistant_message = self.repository.create_message(assistant_message, update_conversation=conversation)
        return self.conversation_service.serialize_message(assistant_message)

    def run_soil_analysis(
        self,
        *,
        payload: ChatSoilAnalysisInput,
        current_user: AuthenticatedUser | None,
        guest_token: str | None,
    ) -> ChatSoilAnalysisResponse:
        result = self.tool_router_service.run_soil_analysis(
            inputs=payload.model_dump(by_alias=True),
            current_user=current_user,
            conversation_id=None,
            message_id=None,
        )
        return ChatSoilAnalysisResponse.model_validate(
            {
                "score": result.get("score", 0),
                "band": result.get("band", "Functional"),
                "summary": result.get("summary", ""),
                "formula_name": result.get("formulaName"),
                "recommendations": result.get("recommendations", []),
                "component_scores": result.get("componentScores", {}),
                "citations": result.get("citations", []),
            }
        )

    def _fallback_assistant_reply(self, tool_result: dict, current_user: AuthenticatedUser | None) -> str:
        opener = "BioSilk Chat here."
        if current_user is not None and current_user.full_name:
            opener = f"{current_user.full_name}, BioSilk Chat here."
        summary = tool_result.get("summary") or "I processed your request."
        recommendations = tool_result.get("recommendations") or []
        recommendations_text = "\n".join(f"- {item}" for item in recommendations[:3])
        if recommendations_text:
            return f"{opener} {summary}\n\nRecommended next steps:\n{recommendations_text}"
        return f"{opener} {summary}"

    def _sync_default_provider(self, assistant) -> None:
        settings = self.provider_service.settings
        if assistant.provider != "gemini" or assistant.model != settings.gemini_model:
            return
        if settings.gemini_api_key or not settings.deepseek_api_key:
            return

        assistant.provider = settings.default_chat_provider
        assistant.model = settings.default_chat_model
        self.repository.update_assistant(assistant)
