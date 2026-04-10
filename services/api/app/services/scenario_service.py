from __future__ import annotations

from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.core.errors import AppError
from app.domain.auth import AuthenticatedUser
from app.repositories.scenario_repository import ScenarioRepository
from app.schemas.common import DeleteResponse
from app.schemas.scenario import (
    ScenarioCreate,
    ScenarioDetail,
    ScenarioListResponse,
    ScenarioSoilSampleReference,
    ScenarioUpdate,
    build_stored_scenario_config,
)
from app.services.serializers import serialize_scenario


class ScenarioService:
    def __init__(self, repository: ScenarioRepository) -> None:
        self.repository = repository

    def _ensure_project_exists(self, *, organization_id: UUID, project_id: UUID) -> None:
        if not self.repository.project_exists(organization_id, project_id):
            raise AppError(status_code=404, code="project_not_found", message="Project not found.")

    def _resolve_soil_sample_references(
        self,
        *,
        organization_id: UUID,
        project_id: UUID,
        soil_sample_references: list[ScenarioSoilSampleReference],
    ) -> list[ScenarioSoilSampleReference]:
        try:
            resolved_references = self.repository.resolve_soil_sample_references(
                organization_id,
                project_id,
                [
                    reference.model_dump(mode="python", by_alias=False)
                    for reference in soil_sample_references
                ],
            )
        except LookupError as exc:
            code = str(exc)
            if code == "soil_sample_version_not_found":
                raise AppError(
                    status_code=404,
                    code="soil_sample_version_not_found",
                    message=(
                        "One or more selected soil sample versions were not found in this project."
                    ),
                ) from exc
            raise AppError(
                status_code=404,
                code="soil_sample_not_found",
                message="One or more selected soil samples were not found in this project.",
            ) from exc

        return [
            ScenarioSoilSampleReference.model_validate(reference)
            for reference in resolved_references
        ]

    def list_scenarios(
        self,
        *,
        current_user: AuthenticatedUser,
        project_id: UUID,
        limit: int,
        cursor: str | None,
    ) -> ScenarioListResponse:
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
        return ScenarioListResponse(
            items=[serialize_scenario(item) for item in items],
            next_cursor=None,
        )

    def create_scenario(
        self,
        *,
        current_user: AuthenticatedUser,
        project_id: UUID,
        payload: ScenarioCreate,
    ) -> ScenarioDetail:
        self._ensure_project_exists(
            organization_id=current_user.organization_id,
            project_id=project_id,
        )
        resolved_references = self._resolve_soil_sample_references(
            organization_id=current_user.organization_id,
            project_id=project_id,
            soil_sample_references=payload.soil_sample_references,
        )
        normalized_payload = payload.model_copy(
            update={
                "soil_sample_id": resolved_references[0].soil_sample_id,
                "soil_sample_version_id": resolved_references[0].soil_sample_version_id,
                "soil_sample_references": resolved_references,
                "scenario_config": build_stored_scenario_config(
                    scenario_config=payload.scenario_config,
                    soil_sample_references=resolved_references,
                    primary_soil_sample_id=resolved_references[0].soil_sample_id,
                    primary_soil_sample_version_id=resolved_references[0].soil_sample_version_id,
                ),
            }
        )

        try:
            scenario = self.repository.create(
                current_user.organization_id,
                project_id,
                current_user.user_id,
                normalized_payload,
            )
        except LookupError as exc:
            code = str(exc)
            if code == "soil_sample_not_found":
                raise AppError(
                    status_code=404,
                    code="soil_sample_not_found",
                    message="One or more selected soil samples were not found in this project.",
                ) from exc
            raise AppError(
                status_code=404,
                code="project_not_found",
                message="Project not found.",
            ) from exc
        except IntegrityError as exc:
            raise AppError(
                status_code=409,
                code="scenario_conflict",
                message=(
                    "Scenario creation failed because a related record conflicts "
                    "with existing data."
                ),
            ) from exc
        return serialize_scenario(scenario)

    def get_scenario(self, *, current_user: AuthenticatedUser, scenario_id: UUID) -> ScenarioDetail:
        scenario = self.repository.get_by_id(current_user.organization_id, scenario_id)
        if scenario is None:
            raise AppError(
                status_code=404,
                code="scenario_not_found",
                message="Scenario not found.",
            )
        return serialize_scenario(scenario)

    def update_scenario(
        self,
        *,
        current_user: AuthenticatedUser,
        scenario_id: UUID,
        payload: ScenarioUpdate,
    ) -> ScenarioDetail:
        scenario = self.repository.get_by_id(current_user.organization_id, scenario_id)
        if scenario is None:
            raise AppError(
                status_code=404,
                code="scenario_not_found",
                message="Scenario not found.",
            )

        normalized_payload, scientific_change = self._normalize_update_payload(
            payload,
            scenario=scenario,
        )

        try:
            scenario = self.repository.update(
                scenario,
                payload=normalized_payload,
                updated_by_user_id=current_user.user_id,
                increment_version=scientific_change,
            )
        except IntegrityError as exc:
            raise AppError(
                status_code=409,
                code="scenario_conflict",
                message=(
                    "Scenario update failed because a related record conflicts "
                    "with existing data."
                ),
            ) from exc
        return serialize_scenario(scenario)

    def _normalize_update_payload(
        self,
        payload: ScenarioUpdate,
        *,
        scenario,
    ) -> tuple[ScenarioUpdate, bool]:
        current_scenario = serialize_scenario(scenario)
        soil_sample_fields_changed = bool(
            {"soil_sample_id", "soil_sample_version_id", "soil_sample_references"}
            & payload.model_fields_set
        )
        scientific_change = soil_sample_fields_changed or any(
            field in payload.model_fields_set
            for field in ("food_web", "parameter_set", "scenario_config")
        )

        if soil_sample_fields_changed:
            references_to_resolve = payload.soil_sample_references or [
                ScenarioSoilSampleReference(
                    soil_sample_id=payload.soil_sample_id or current_scenario.soil_sample_id,
                    soil_sample_version_id=payload.soil_sample_version_id,
                    role="primary",
                )
            ]
            resolved_references = self._resolve_soil_sample_references(
                organization_id=scenario.organization_id,
                project_id=scenario.project_id,
                soil_sample_references=references_to_resolve,
            )
        else:
            resolved_references = current_scenario.soil_sample_references

        scenario_config_payload = None
        if payload.scenario_config is not None or soil_sample_fields_changed:
            scenario_config_payload = build_stored_scenario_config(
                scenario_config=payload.scenario_config or scenario.scenario_config_json,
                soil_sample_references=resolved_references,
                primary_soil_sample_id=resolved_references[0].soil_sample_id,
                primary_soil_sample_version_id=resolved_references[0].soil_sample_version_id,
            )

        normalized_payload = payload.model_copy(
            update={
                "soil_sample_id": (
                    resolved_references[0].soil_sample_id
                    if scientific_change
                    else payload.soil_sample_id
                ),
                "soil_sample_version_id": (
                    resolved_references[0].soil_sample_version_id
                    if scientific_change
                    else payload.soil_sample_version_id
                ),
                "soil_sample_references": (
                    resolved_references
                    if soil_sample_fields_changed
                    else payload.soil_sample_references
                ),
                "scenario_config": scenario_config_payload,
            }
        )
        return normalized_payload, scientific_change

    def delete_scenario(
        self,
        *,
        current_user: AuthenticatedUser,
        scenario_id: UUID,
    ) -> DeleteResponse:
        scenario = self.repository.soft_delete(
            current_user.organization_id,
            scenario_id,
            current_user.user_id,
        )
        if scenario is None:
            raise AppError(
                status_code=404,
                code="scenario_not_found",
                message="Scenario not found.",
            )
        return DeleteResponse(id=scenario.id, deleted_at=scenario.deleted_at)
