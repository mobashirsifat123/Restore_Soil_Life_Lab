from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.dependencies.auth import AuthenticatedUser, require_permission
from app.api.dependencies.services import get_project_service
from app.domain.permissions import Permissions
from app.schemas.common import DeleteResponse
from app.schemas.project import ProjectCreate, ProjectDetail, ProjectListResponse, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get(
    "",
    response_model=ProjectListResponse,
    operation_id="projects_listProjects",
    summary="List projects in the current organization",
)
def list_projects(
    limit: int = Query(default=25, ge=1, le=100),
    cursor: str | None = Query(default=None),
    current_user: AuthenticatedUser = require_permission(Permissions.PROJECT_READ),
    project_service: ProjectService = Depends(get_project_service),
) -> ProjectListResponse:
    return project_service.list_projects(current_user=current_user, limit=limit, cursor=cursor)


@router.post(
    "",
    response_model=ProjectDetail,
    status_code=status.HTTP_201_CREATED,
    operation_id="projects_createProject",
    summary="Create a project",
)
def create_project(
    payload: ProjectCreate,
    current_user: AuthenticatedUser = require_permission(Permissions.PROJECT_WRITE),
    project_service: ProjectService = Depends(get_project_service),
) -> ProjectDetail:
    return project_service.create_project(current_user=current_user, payload=payload)


@router.get(
    "/{project_id}",
    response_model=ProjectDetail,
    operation_id="projects_getProject",
    summary="Get a project by id",
)
def get_project(
    project_id: UUID = Path(...),
    current_user: AuthenticatedUser = require_permission(Permissions.PROJECT_READ),
    project_service: ProjectService = Depends(get_project_service),
) -> ProjectDetail:
    return project_service.get_project(current_user=current_user, project_id=project_id)


@router.patch(
    "/{project_id}",
    response_model=ProjectDetail,
    operation_id="projects_updateProject",
    summary="Update project metadata",
)
def update_project(
    payload: ProjectUpdate,
    project_id: UUID = Path(...),
    current_user: AuthenticatedUser = require_permission(Permissions.PROJECT_WRITE),
    project_service: ProjectService = Depends(get_project_service),
) -> ProjectDetail:
    return project_service.update_project(
        current_user=current_user,
        project_id=project_id,
        payload=payload,
    )


@router.delete(
    "/{project_id}",
    response_model=DeleteResponse,
    operation_id="projects_deleteProject",
    summary="Soft-delete a project",
)
def delete_project(
    project_id: UUID = Path(...),
    current_user: AuthenticatedUser = require_permission(Permissions.PROJECT_WRITE),
    project_service: ProjectService = Depends(get_project_service),
) -> DeleteResponse:
    return project_service.delete_project(current_user=current_user, project_id=project_id)
