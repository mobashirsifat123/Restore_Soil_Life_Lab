from __future__ import annotations

from uuid import UUID

from app.core.errors import AppError
from app.db.chat_models import ChatAttachment, ChatConversation, ChatMessage
from app.domain.auth import AuthenticatedUser
from app.repositories.chat_repository import ChatRepository
from app.schemas.chat import (
    ChatAttachmentResponse,
    ChatConversationDetail,
    ChatConversationListResponse,
    ChatConversationSummary,
    ChatMessageResponse,
)


class ConversationService:
    def __init__(self, repository: ChatRepository) -> None:
        self.repository = repository

    def list_conversations(
        self,
        *,
        current_user: AuthenticatedUser | None,
        guest_token: str | None,
    ) -> ChatConversationListResponse:
        items = self.repository.list_conversations(
            user_id=current_user.user_id if current_user else None,
            guest_token=guest_token,
        )
        return ChatConversationListResponse(items=[self.serialize_summary(item) for item in items])

    def get_conversation(
        self,
        conversation_id: UUID,
        *,
        current_user: AuthenticatedUser | None,
        guest_token: str | None,
    ) -> ChatConversationDetail:
        conversation = self.repository.get_conversation(
            conversation_id,
            user_id=current_user.user_id if current_user else None,
            guest_token=guest_token,
        )
        if conversation is None:
            raise AppError(status_code=404, code="chat_conversation_not_found", message="Conversation not found.")
        messages = self.repository.list_messages(conversation.id)
        attachments = self.repository.list_attachments(conversation.id)
        return ChatConversationDetail(
            **self.serialize_summary(conversation).model_dump(),
            messages=[self.serialize_message(item) for item in messages],
            attachments=[self.serialize_attachment(item) for item in attachments],
        )

    def assert_access(
        self,
        *,
        conversation_id: UUID,
        current_user: AuthenticatedUser | None,
        guest_token: str | None,
    ) -> ChatConversation:
        conversation = self.repository.get_conversation(
            conversation_id,
            user_id=current_user.user_id if current_user else None,
            guest_token=guest_token,
        )
        if conversation is None:
            raise AppError(status_code=404, code="chat_conversation_not_found", message="Conversation not found.")
        return conversation

    @staticmethod
    def serialize_summary(conversation: ChatConversation) -> ChatConversationSummary:
        return ChatConversationSummary.model_validate(
            {
                "id": conversation.id,
                "title": conversation.title,
                "channel": conversation.channel,
                "status": conversation.status,
                "summary": conversation.summary,
                "last_activity_at": conversation.last_activity_at,
                "created_at": conversation.created_at,
            }
        )

    @staticmethod
    def serialize_message(message: ChatMessage) -> ChatMessageResponse:
        return ChatMessageResponse.model_validate(
            {
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "structured_payload": message.structured_payload_json or {},
                "citations": message.citations_json or [],
                "metadata": message.metadata_json or {},
                "latency_ms": message.latency_ms,
                "created_at": message.created_at,
            }
        )

    @staticmethod
    def serialize_attachment(attachment: ChatAttachment) -> ChatAttachmentResponse:
        return ChatAttachmentResponse.model_validate(
            {
                "id": attachment.id,
                "attachment_type": attachment.attachment_type,
                "filename": attachment.filename,
                "mime_type": attachment.mime_type,
                "byte_size": attachment.byte_size,
                "created_at": attachment.created_at,
            }
        )
