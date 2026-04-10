from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.dependencies.auth import AuthenticatedUser, require_permission
from app.api.dependencies.services import get_soil_sample_service
from app.domain.permissions import Permissions
from app.schemas.common import DeleteResponse
from app.schemas.soil_sample import (
    SoilSampleCreate,
    SoilSampleDetail,
    SoilSampleListResponse,
    SoilSampleUpdate,
)
from app.services.soil_sample_service import SoilSampleService

router = APIRouter(tags=["soil-samples"])


@router.get(
    "/projects/{project_id}/soil-samples",
    response_model=SoilSampleListResponse,
    operation_id="soilSamples_listSoilSamples",
    summary="List soil samples for a project",
)
def list_soil_samples(
    project_id: UUID = Path(...),
    limit: int = Query(default=25, ge=1, le=100),
    cursor: str | None = Query(default=None),
    current_user: AuthenticatedUser = require_permission(Permissions.SAMPLE_READ),
    soil_sample_service: SoilSampleService = Depends(get_soil_sample_service),
) -> SoilSampleListResponse:
    return soil_sample_service.list_soil_samples(
        current_user=current_user,
        project_id=project_id,
        limit=limit,
        cursor=cursor,
    )


@router.post(
    "/projects/{project_id}/soil-samples",
    response_model=SoilSampleDetail,
    status_code=status.HTTP_201_CREATED,
    operation_id="soilSamples_createSoilSample",
    summary="Create a soil sample",
)
def create_soil_sample(
    payload: SoilSampleCreate,
    project_id: UUID = Path(...),
    current_user: AuthenticatedUser = require_permission(Permissions.SAMPLE_WRITE),
    soil_sample_service: SoilSampleService = Depends(get_soil_sample_service),
) -> SoilSampleDetail:
    return soil_sample_service.create_soil_sample(
        current_user=current_user,
        project_id=project_id,
        payload=payload,
    )


@router.get(
    "/soil-samples/{soil_sample_id}",
    response_model=SoilSampleDetail,
    operation_id="soilSamples_getSoilSample",
    summary="Get a soil sample by id",
)
def get_soil_sample(
    soil_sample_id: UUID = Path(...),
    current_user: AuthenticatedUser = require_permission(Permissions.SAMPLE_READ),
    soil_sample_service: SoilSampleService = Depends(get_soil_sample_service),
) -> SoilSampleDetail:
    return soil_sample_service.get_soil_sample(
        current_user=current_user,
        soil_sample_id=soil_sample_id,
    )


@router.patch(
    "/soil-samples/{soil_sample_id}",
    response_model=SoilSampleDetail,
    operation_id="soilSamples_updateSoilSample",
    summary="Update a soil sample",
)
def update_soil_sample(
    payload: SoilSampleUpdate,
    soil_sample_id: UUID = Path(...),
    current_user: AuthenticatedUser = require_permission(Permissions.SAMPLE_WRITE),
    soil_sample_service: SoilSampleService = Depends(get_soil_sample_service),
) -> SoilSampleDetail:
    return soil_sample_service.update_soil_sample(
        current_user=current_user,
        soil_sample_id=soil_sample_id,
        payload=payload,
    )


@router.delete(
    "/soil-samples/{soil_sample_id}",
    response_model=DeleteResponse,
    operation_id="soilSamples_deleteSoilSample",
    summary="Soft-delete a soil sample",
)
def delete_soil_sample(
    soil_sample_id: UUID = Path(...),
    current_user: AuthenticatedUser = require_permission(Permissions.SAMPLE_WRITE),
    soil_sample_service: SoilSampleService = Depends(get_soil_sample_service),
) -> DeleteResponse:
    return soil_sample_service.delete_soil_sample(
        current_user=current_user,
        soil_sample_id=soil_sample_id,
    )
