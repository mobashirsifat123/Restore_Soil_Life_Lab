# ruff: noqa: B008

from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.dependencies.auth import AuthenticatedUser, require_permission
from app.api.dependencies.services import get_scenario_service
from app.domain.permissions import Permissions
from app.schemas.common import DeleteResponse
from app.schemas.scenario import (
    ScenarioCreate,
    ScenarioDetail,
    ScenarioListResponse,
    ScenarioUpdate,
)
from app.services.scenario_service import ScenarioService

router = APIRouter(tags=["scenarios"])


@router.get(
    "/projects/{project_id}/scenarios",
    response_model=ScenarioListResponse,
    operation_id="scenarios_listScenarios",
    summary="List scenarios for a project",
)
def list_scenarios(
    project_id: UUID = Path(...),
    limit: int = Query(default=25, ge=1, le=100),
    cursor: str | None = Query(default=None),
    current_user: AuthenticatedUser = require_permission(Permissions.SCENARIO_READ),
    scenario_service: ScenarioService = Depends(get_scenario_service),
) -> ScenarioListResponse:
    return scenario_service.list_scenarios(
        current_user=current_user,
        project_id=project_id,
        limit=limit,
        cursor=cursor,
    )


@router.post(
    "/projects/{project_id}/scenarios",
    response_model=ScenarioDetail,
    status_code=status.HTTP_201_CREATED,
    operation_id="scenarios_createScenario",
    summary="Create a scenario version",
)
def create_scenario(
    payload: ScenarioCreate,
    project_id: UUID = Path(...),
    current_user: AuthenticatedUser = require_permission(Permissions.SCENARIO_WRITE),
    scenario_service: ScenarioService = Depends(get_scenario_service),
) -> ScenarioDetail:
    return scenario_service.create_scenario(
        current_user=current_user,
        project_id=project_id,
        payload=payload,
    )


@router.get(
    "/scenarios/{scenario_id}",
    response_model=ScenarioDetail,
    operation_id="scenarios_getScenario",
    summary="Get a scenario by id",
)
def get_scenario(
    scenario_id: UUID = Path(...),
    current_user: AuthenticatedUser = require_permission(Permissions.SCENARIO_READ),
    scenario_service: ScenarioService = Depends(get_scenario_service),
) -> ScenarioDetail:
    return scenario_service.get_scenario(current_user=current_user, scenario_id=scenario_id)


@router.patch(
    "/scenarios/{scenario_id}",
    response_model=ScenarioDetail,
    operation_id="scenarios_updateScenario",
    summary="Update a scenario",
)
def update_scenario(
    payload: ScenarioUpdate,
    scenario_id: UUID = Path(...),
    current_user: AuthenticatedUser = require_permission(Permissions.SCENARIO_WRITE),
    scenario_service: ScenarioService = Depends(get_scenario_service),
) -> ScenarioDetail:
    return scenario_service.update_scenario(
        current_user=current_user,
        scenario_id=scenario_id,
        payload=payload,
    )


@router.delete(
    "/scenarios/{scenario_id}",
    response_model=DeleteResponse,
    operation_id="scenarios_deleteScenario",
    summary="Soft-delete a scenario",
)
def delete_scenario(
    scenario_id: UUID = Path(...),
    current_user: AuthenticatedUser = require_permission(Permissions.SCENARIO_WRITE),
    scenario_service: ScenarioService = Depends(get_scenario_service),
) -> DeleteResponse:
    return scenario_service.delete_scenario(
        current_user=current_user,
        scenario_id=scenario_id,
    )
