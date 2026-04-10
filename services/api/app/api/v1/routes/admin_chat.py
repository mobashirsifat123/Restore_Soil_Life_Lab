from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.dependencies.auth import CurrentUser, require_admin_user
from app.api.dependencies.services import get_assistant_admin_service
from app.schemas.chat import (
    ChatAdminConfigResponse,
    ChatAssistantResponse,
    ChatAssistantUpsert,
    ChatKnowledgeSourceCreate,
    ChatKnowledgeSourceListResponse,
    ChatKnowledgeSourceResponse,
    ChatReindexResponse,
    ChatWidgetConfigResponse,
    ChatWidgetConfigUpdate,
)
from app.services.chat.assistant_admin_service import AssistantAdminService

router = APIRouter(prefix="/admin/chat", tags=["admin-chat"])
AdminChatServiceDependency = Annotated[AssistantAdminService, Depends(get_assistant_admin_service)]


@router.get(
    "/config",
    response_model=ChatAdminConfigResponse,
    operation_id="adminChat_getConfig",
    summary="Get BioSilk Chat admin configuration",
    dependencies=[require_admin_user()],
)
def get_config(
    current_user: CurrentUser,
    assistant_admin_service: AdminChatServiceDependency,
) -> ChatAdminConfigResponse:
    return assistant_admin_service.get_admin_config(current_user=current_user)


@router.patch(
    "/config",
    response_model=ChatWidgetConfigResponse,
    operation_id="adminChat_updateConfig",
    summary="Update BioSilk Chat widget configuration",
    dependencies=[require_admin_user()],
)
def update_config(
    payload: ChatWidgetConfigUpdate,
    current_user: CurrentUser,
    assistant_admin_service: AdminChatServiceDependency,
) -> ChatWidgetConfigResponse:
    return assistant_admin_service.update_widget_config(current_user=current_user, payload=payload)


@router.get(
    "/assistants",
    response_model=list[ChatAssistantResponse],
    operation_id="adminChat_listAssistants",
    summary="List BioSilk Chat assistants",
    dependencies=[require_admin_user()],
)
def list_assistants(
    _: CurrentUser,
    assistant_admin_service: AdminChatServiceDependency,
) -> list[ChatAssistantResponse]:
    return assistant_admin_service.list_assistants()


@router.post(
    "/assistants",
    response_model=ChatAssistantResponse,
    operation_id="adminChat_createAssistant",
    summary="Create a BioSilk Chat assistant",
    dependencies=[require_admin_user()],
)
def create_assistant(
    payload: ChatAssistantUpsert,
    _: CurrentUser,
    assistant_admin_service: AdminChatServiceDependency,
) -> ChatAssistantResponse:
    return assistant_admin_service.create_assistant(payload=payload)


@router.patch(
    "/assistants/{assistant_id}",
    response_model=ChatAssistantResponse,
    operation_id="adminChat_updateAssistant",
    summary="Update a BioSilk Chat assistant",
    dependencies=[require_admin_user()],
)
def update_assistant(
    assistant_id: UUID,
    payload: ChatAssistantUpsert,
    _: CurrentUser,
    assistant_admin_service: AdminChatServiceDependency,
) -> ChatAssistantResponse:
    return assistant_admin_service.update_assistant(assistant_id=assistant_id, payload=payload)


@router.get(
    "/sources",
    response_model=ChatKnowledgeSourceListResponse,
    operation_id="adminChat_listSources",
    summary="List BioSilk Chat knowledge sources",
    dependencies=[require_admin_user()],
)
def list_sources(
    _: CurrentUser,
    assistant_admin_service: AdminChatServiceDependency,
) -> ChatKnowledgeSourceListResponse:
    return assistant_admin_service.list_sources()


@router.post(
    "/sources",
    response_model=ChatKnowledgeSourceResponse,
    operation_id="adminChat_createSource",
    summary="Create a BioSilk Chat knowledge source",
    dependencies=[require_admin_user()],
)
def create_source(
    payload: ChatKnowledgeSourceCreate,
    current_user: CurrentUser,
    assistant_admin_service: AdminChatServiceDependency,
) -> ChatKnowledgeSourceResponse:
    return assistant_admin_service.create_source(current_user=current_user, payload=payload)


@router.post(
    "/sources/{source_id}/reindex",
    response_model=ChatReindexResponse,
    operation_id="adminChat_reindexSource",
    summary="Reindex a BioSilk Chat knowledge source",
    dependencies=[require_admin_user()],
)
def reindex_source(
    source_id: UUID,
    _: CurrentUser,
    assistant_admin_service: AdminChatServiceDependency,
) -> ChatReindexResponse:
    return assistant_admin_service.reindex_source(source_id=source_id)
