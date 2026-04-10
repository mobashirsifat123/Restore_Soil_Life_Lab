from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Header, UploadFile, status

from app.api.dependencies.auth import OptionalCurrentUser
from app.api.dependencies.services import get_assistant_service
from app.schemas.chat import (
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
from app.services.chat.assistant_service import AssistantService

router = APIRouter(prefix="/chat", tags=["chat"])
AssistantServiceDependency = Annotated[AssistantService, Depends(get_assistant_service)]
GuestTokenHeader = Annotated[str | None, Header(alias="X-Bio-Guest-Id")]


@router.get(
    "/widget-config",
    response_model=ChatWidgetConfigResponse,
    operation_id="chat_getWidgetConfig",
    summary="Get BioSilk Chat widget and hero configuration",
)
def get_widget_config(
    assistant_service: AssistantServiceDependency,
) -> ChatWidgetConfigResponse:
    return assistant_service.get_widget_config()


@router.get(
    "/conversations",
    response_model=ChatConversationListResponse,
    operation_id="chat_listConversations",
    summary="List current user's or guest's chat conversations",
)
def list_conversations(
    current_user: OptionalCurrentUser,
    assistant_service: AssistantServiceDependency,
    guest_token: GuestTokenHeader = None,
) -> ChatConversationListResponse:
    return assistant_service.list_conversations(current_user=current_user, guest_token=guest_token)


@router.post(
    "/conversations",
    response_model=ChatConversationDetail,
    status_code=status.HTTP_201_CREATED,
    operation_id="chat_createConversation",
    summary="Create a new BioSilk Chat conversation",
)
def create_conversation(
    payload: ChatConversationCreate,
    current_user: OptionalCurrentUser,
    assistant_service: AssistantServiceDependency,
    guest_token: GuestTokenHeader = None,
) -> ChatConversationDetail:
    return assistant_service.create_conversation(
        payload=payload,
        current_user=current_user,
        guest_token=guest_token,
    )


@router.get(
    "/conversations/{conversation_id}",
    response_model=ChatConversationDetail,
    operation_id="chat_getConversation",
    summary="Get a conversation with all messages and attachments",
)
def get_conversation(
    conversation_id: UUID,
    current_user: OptionalCurrentUser,
    assistant_service: AssistantServiceDependency,
    guest_token: GuestTokenHeader = None,
) -> ChatConversationDetail:
    return assistant_service.get_conversation(
        conversation_id=conversation_id,
        current_user=current_user,
        guest_token=guest_token,
    )


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=ChatMessageResponse,
    operation_id="chat_sendMessage",
    summary="Send a message to BioSilk Chat",
)
def send_message(
    conversation_id: UUID,
    payload: ChatMessageCreate,
    current_user: OptionalCurrentUser,
    assistant_service: AssistantServiceDependency,
    guest_token: GuestTokenHeader = None,
) -> ChatMessageResponse:
    return assistant_service.send_message(
        conversation_id=conversation_id,
        payload=payload,
        current_user=current_user,
        guest_token=guest_token,
    )


@router.post(
    "/conversations/{conversation_id}/attachments",
    response_model=ChatAttachmentResponse,
    operation_id="chat_uploadAttachment",
    summary="Upload an attachment for BioSilk Chat",
)
def upload_attachment(
    conversation_id: UUID,
    current_user: OptionalCurrentUser,
    assistant_service: AssistantServiceDependency,
    file: UploadFile = File(...),
    guest_token: GuestTokenHeader = None,
) -> ChatAttachmentResponse:
    return assistant_service.upload_attachment(
        conversation_id=conversation_id,
        upload=file,
        current_user=current_user,
        guest_token=guest_token,
    )


@router.post(
    "/tools/soil-analysis",
    response_model=ChatSoilAnalysisResponse,
    operation_id="chat_runSoilAnalysis",
    summary="Run the active SilkSoil formula as a chat tool",
)
def run_soil_analysis(
    payload: ChatSoilAnalysisInput,
    current_user: OptionalCurrentUser,
    assistant_service: AssistantServiceDependency,
    guest_token: GuestTokenHeader = None,
) -> ChatSoilAnalysisResponse:
    return assistant_service.run_soil_analysis(
        payload=payload,
        current_user=current_user,
        guest_token=guest_token,
    )
