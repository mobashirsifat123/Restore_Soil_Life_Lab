from app.api.dependencies.db import DatabaseSession
from app.core.config import get_settings
from app.repositories.admin_repository import AdminRepository
from app.repositories.auth_repository import AuthRepository
from app.repositories.chat_repository import ChatRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.run_repository import RunRepository
from app.repositories.scenario_repository import ScenarioRepository
from app.repositories.soil_sample_repository import SoilSampleRepository
from app.services.admin_service import AdminService
from app.services.auth_service import AuthService
from app.services.chat.assistant_admin_service import AssistantAdminService
from app.services.chat.assistant_service import AssistantService
from app.services.chat.conversation_service import ConversationService
from app.services.chat.knowledge_base_service import KnowledgeBaseService
from app.services.chat.pest_diagnosis_service import PestDiagnosisService
from app.services.chat.provider_service import ProviderService
from app.services.chat.soil_chat_grounding_service import SoilChatGroundingService
from app.services.chat.tool_router_service import ToolRouterService
from app.services.project_service import ProjectService
from app.services.run_service import RunService
from app.services.scenario_service import ScenarioService
from app.services.soil_sample_service import SoilSampleService


def get_admin_service(session: DatabaseSession) -> AdminService:
    return AdminService(AdminRepository(session))


def get_auth_service(session: DatabaseSession) -> AuthService:
    return AuthService(AuthRepository(session), get_settings())


def get_assistant_admin_service(session: DatabaseSession) -> AssistantAdminService:
    repository = ChatRepository(session)
    knowledge_base_service = KnowledgeBaseService(repository)
    return AssistantAdminService(repository, knowledge_base_service)


def get_assistant_service(session: DatabaseSession) -> AssistantService:
    settings = get_settings()
    repository = ChatRepository(session)
    conversation_service = ConversationService(repository)
    knowledge_base_service = KnowledgeBaseService(repository)
    tool_router_service = ToolRouterService(
        repository,
        knowledge_base_service,
        PestDiagnosisService(repository, settings),
        SoilChatGroundingService(repository),
    )
    admin_service = AssistantAdminService(repository, knowledge_base_service)
    provider_service = ProviderService(settings)
    return AssistantService(
        repository,
        conversation_service,
        tool_router_service,
        provider_service,
        admin_service,
    )


def get_project_service(session: DatabaseSession) -> ProjectService:
    return ProjectService(ProjectRepository(session))


def get_soil_sample_service(session: DatabaseSession) -> SoilSampleService:
    return SoilSampleService(SoilSampleRepository(session))


def get_scenario_service(session: DatabaseSession) -> ScenarioService:
    return ScenarioService(ScenarioRepository(session))


def get_run_service(session: DatabaseSession) -> RunService:
    from app.jobs.publisher import JobPublisher
    from app.repositories.cms_repository import CmsRepository

    settings = get_settings()
    publisher = JobPublisher(redis_url=settings.redis_url)
    return RunService(RunRepository(session), publisher, CmsRepository(session))
