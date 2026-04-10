from uuid import UUID

from fastapi import APIRouter, Depends, Path, status

from app.api.dependencies.auth import AuthenticatedUser, require_permission
from app.api.dependencies.services import get_run_service
from app.domain.permissions import Permissions
from app.schemas.run import (
    RunCreate,
    RunDetail,
    RunListResponse,
    RunResultsResponse,
    RunStatusResponse,
)
from app.services.run_service import RunService

router = APIRouter(prefix="/runs", tags=["runs"])


@router.get(
    "",
    response_model=RunListResponse,
    operation_id="runs_listSimulationRuns",
    summary="List simulation runs",
)
def list_runs(
    current_user: AuthenticatedUser = require_permission(Permissions.RUN_READ),
    run_service: RunService = Depends(get_run_service),
) -> RunListResponse:
    return run_service.list_runs(current_user=current_user)

@router.post(
    "",
    response_model=RunDetail,
    status_code=status.HTTP_202_ACCEPTED,
    operation_id="runs_createSimulationRun",
    summary="Submit a simulation run",
)
def create_run(
    payload: RunCreate,
    current_user: AuthenticatedUser = require_permission(Permissions.RUN_SUBMIT),
    run_service: RunService = Depends(get_run_service),
) -> RunDetail:
    return run_service.create_run(current_user=current_user, payload=payload)


@router.get(
    "/{run_id}",
    response_model=RunDetail,
    operation_id="runs_getSimulationRun",
    summary="Get simulation run details",
)
def get_run(
    run_id: UUID = Path(...),
    current_user: AuthenticatedUser = require_permission(Permissions.RUN_READ),
    run_service: RunService = Depends(get_run_service),
) -> RunDetail:
    return run_service.get_run(current_user=current_user, run_id=run_id)


@router.get(
    "/{run_id}/status",
    response_model=RunStatusResponse,
    operation_id="runs_getSimulationRunStatus",
    summary="Get simulation run status",
)
def get_run_status(
    run_id: UUID = Path(...),
    current_user: AuthenticatedUser = require_permission(Permissions.RUN_READ),
    run_service: RunService = Depends(get_run_service),
) -> RunStatusResponse:
    return run_service.get_run_status(current_user=current_user, run_id=run_id)


@router.get(
    "/{run_id}/results",
    response_model=RunResultsResponse,
    operation_id="runs_getSimulationRunResults",
    summary="Fetch simulation run results and artifacts",
)
def get_run_results(
    run_id: UUID = Path(...),
    current_user: AuthenticatedUser = require_permission(Permissions.RUN_READ),
    run_service: RunService = Depends(get_run_service),
) -> RunResultsResponse:
    return run_service.get_run_results(current_user=current_user, run_id=run_id)
