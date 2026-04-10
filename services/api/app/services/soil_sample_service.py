from __future__ import annotations

from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.core.errors import AppError
from app.domain.auth import AuthenticatedUser
from app.repositories.soil_sample_repository import SoilSampleRepository
from app.schemas.common import DeleteResponse
from app.schemas.soil_sample import (
    SoilSampleCreate,
    SoilSampleDetail,
    SoilSampleListResponse,
    SoilSampleUpdate,
    scientific_model_dump,
)
from app.services.serializers import serialize_soil_sample


class SoilSampleService:
    def __init__(self, repository: SoilSampleRepository) -> None:
        self.repository = repository

    def _ensure_project_exists(self, *, organization_id: UUID, project_id: UUID) -> None:
        if not self.repository.project_exists(organization_id, project_id):
            raise AppError(status_code=404, code="project_not_found", message="Project not found.")

    def list_soil_samples(
        self,
        *,
        current_user: AuthenticatedUser,
        project_id: UUID,
        limit: int,
        cursor: str | None,
    ) -> SoilSampleListResponse:
        self._ensure_project_exists(
            organization_id=current_user.organization_id,
            project_id=project_id,
        )
        items = self.repository.list_for_project(
            current_user.organization_id,
            project_id,
            limit=limit,
            cursor=cursor,
        )
        return SoilSampleListResponse(
            items=[serialize_soil_sample(item) for item in items],
            next_cursor=None,
        )

    def create_soil_sample(
        self,
        *,
        current_user: AuthenticatedUser,
        project_id: UUID,
        payload: SoilSampleCreate,
    ) -> SoilSampleDetail:
        self._ensure_project_exists(
            organization_id=current_user.organization_id,
            project_id=project_id,
        )
        if self.repository.sample_code_exists(
            current_user.organization_id,
            project_id,
            payload.sample_code,
        ):
            raise AppError(
                status_code=409,
                code="soil_sample_conflict",
                message="A soil sample with the same code already exists for this project.",
            )

        try:
            soil_sample = self.repository.create(
                organization_id=current_user.organization_id,
                project_id=project_id,
                created_by_user_id=current_user.user_id,
                payload=payload.model_copy(
                    update={
                        "location": scientific_model_dump(payload.location),
                        "measurements": scientific_model_dump(payload.measurements),
                    }
                ),
            )
        except LookupError as exc:
            raise AppError(
                status_code=404,
                code="project_not_found",
                message="Project not found.",
            ) from exc
        except IntegrityError as exc:
            raise AppError(
                status_code=409,
                code="soil_sample_conflict",
                message="A soil sample with the same code already exists for this project.",
            ) from exc
        return serialize_soil_sample(soil_sample)

    def get_soil_sample(
        self,
        *,
        current_user: AuthenticatedUser,
        soil_sample_id: UUID,
    ) -> SoilSampleDetail:
        soil_sample = self.repository.get_by_id(current_user.organization_id, soil_sample_id)
        if soil_sample is None:
            raise AppError(
                status_code=404,
                code="soil_sample_not_found",
                message="Soil sample not found.",
            )
        return serialize_soil_sample(soil_sample)

    def update_soil_sample(
        self,
        *,
        current_user: AuthenticatedUser,
        soil_sample_id: UUID,
        payload: SoilSampleUpdate,
    ) -> SoilSampleDetail:
        soil_sample = self.repository.get_by_id(current_user.organization_id, soil_sample_id)
        if soil_sample is None:
            raise AppError(
                status_code=404,
                code="soil_sample_not_found",
                message="Soil sample not found.",
            )

        updates: dict[str, object] = {}
        if "sample_code" in payload.model_fields_set:
            if payload.sample_code is None:
                raise AppError(
                    status_code=422,
                    code="validation_error",
                    message="Request validation failed.",
                    details={"field": "sampleCode"},
                )
            if self.repository.sample_code_exists(
                current_user.organization_id,
                soil_sample.project_id,
                payload.sample_code,
                exclude_soil_sample_id=soil_sample.id,
            ):
                raise AppError(
                    status_code=409,
                    code="soil_sample_conflict",
                    message="A soil sample with the same code already exists for this project.",
                )
            updates["sample_code"] = payload.sample_code
        if "name" in payload.model_fields_set:
            updates["name"] = payload.name
        if "description" in payload.model_fields_set:
            updates["description"] = payload.description
        if "collected_on" in payload.model_fields_set:
            updates["collected_on"] = payload.collected_on
        if "location" in payload.model_fields_set:
            updates["location_json"] = scientific_model_dump(payload.location)
        if "measurements" in payload.model_fields_set:
            updates["measurements_json"] = scientific_model_dump(payload.measurements)
        if "metadata" in payload.model_fields_set:
            updates["metadata_json"] = payload.metadata or {}

        if not updates:
            return serialize_soil_sample(soil_sample)

        try:
            soil_sample = self.repository.update(
                soil_sample,
                updates=updates,
                created_by_user_id=current_user.user_id,
            )
        except IntegrityError as exc:
            raise AppError(
                status_code=409,
                code="soil_sample_conflict",
                message="Soil sample update would violate a uniqueness constraint.",
            ) from exc
        return serialize_soil_sample(soil_sample)

    def delete_soil_sample(
        self,
        *,
        current_user: AuthenticatedUser,
        soil_sample_id: UUID,
    ) -> DeleteResponse:
        soil_sample = self.repository.soft_delete(
            current_user.organization_id,
            soil_sample_id,
            current_user.user_id,
        )
        if soil_sample is None:
            raise AppError(
                status_code=404,
                code="soil_sample_not_found",
                message="Soil sample not found.",
            )
        return DeleteResponse(id=soil_sample.id, deleted_at=soil_sample.deleted_at)
