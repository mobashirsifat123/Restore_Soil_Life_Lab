from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.models import (
    FoodWebDefinition,
    ParameterSet,
    Project,
    SimulationScenario,
    SoilSample,
    SoilSampleVersion,
)
from app.domain.enums import ScenarioStatus


class ScenarioRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def project_exists(self, organization_id: UUID, project_id: UUID) -> bool:
        statement = select(Project.id).where(
            Project.organization_id == organization_id,
            Project.id == project_id,
            Project.deleted_at.is_(None),
        )
        return self.session.scalar(statement) is not None

    def resolve_soil_sample_references(
        self,
        organization_id: UUID,
        project_id: UUID,
        references: list[dict],
    ) -> list[dict]:
        if not references:
            return []

        soil_sample_ids = {reference["soil_sample_id"] for reference in references}
        statement = select(SoilSample).where(
            SoilSample.organization_id == organization_id,
            SoilSample.project_id == project_id,
            SoilSample.id.in_(soil_sample_ids),
            SoilSample.deleted_at.is_(None),
        )
        soil_samples = list(self.session.scalars(statement))
        soil_sample_map = {soil_sample.id: soil_sample for soil_sample in soil_samples}
        if len(soil_sample_map) != len(soil_sample_ids):
            raise LookupError("soil_sample_not_found")

        required_version_ids = {
            reference["soil_sample_version_id"]
            for reference in references
            if reference.get("soil_sample_version_id") is not None
        }
        required_version_ids.update(
            soil_sample.current_version_id
            for soil_sample in soil_samples
            if soil_sample.current_version_id is not None
        )
        version_statement = select(SoilSampleVersion).where(
            SoilSampleVersion.organization_id == organization_id,
            SoilSampleVersion.project_id == project_id,
            SoilSampleVersion.id.in_(required_version_ids),
        )
        versions = list(self.session.scalars(version_statement))
        version_map = {version.id: version for version in versions}

        normalized_references: list[dict] = []
        for reference in references:
            soil_sample = soil_sample_map[reference["soil_sample_id"]]
            version_id = reference.get("soil_sample_version_id") or soil_sample.current_version_id
            if version_id is None:
                raise LookupError("soil_sample_version_not_found")
            version = version_map.get(version_id)
            if version is None or version.soil_sample_id != soil_sample.id:
                raise LookupError("soil_sample_version_not_found")
            normalized_references.append(
                {
                    "soil_sample_id": soil_sample.id,
                    "soil_sample_version_id": version.id,
                    "role": reference.get("role"),
                    "weight": reference.get("weight"),
                    "metadata": reference.get("metadata") or {},
                }
            )

        return normalized_references

    def list_for_project(
        self,
        organization_id: UUID,
        project_id: UUID,
        *,
        limit: int,
        cursor: str | None,
    ):
        statement = (
            select(SimulationScenario)
            .where(
                SimulationScenario.organization_id == organization_id,
                SimulationScenario.project_id == project_id,
                SimulationScenario.deleted_at.is_(None),
            )
            .order_by(SimulationScenario.created_at.desc(), SimulationScenario.id.desc())
            .limit(limit)
        )
        return list(self.session.scalars(statement))

    def get_by_id(self, organization_id: UUID, scenario_id: UUID):
        statement = (
            select(SimulationScenario)
            .options(
                joinedload(SimulationScenario.food_web_definition),
                joinedload(SimulationScenario.parameter_set),
                joinedload(SimulationScenario.soil_sample_version),
            )
            .where(
                SimulationScenario.organization_id == organization_id,
                SimulationScenario.id == scenario_id,
                SimulationScenario.deleted_at.is_(None),
            )
        )
        return self.session.scalar(statement)

    def create(self, organization_id: UUID, project_id: UUID, created_by_user_id: UUID, payload):
        if not self.project_exists(organization_id, project_id):
            raise LookupError("project_not_found")

        food_web = FoodWebDefinition(
            organization_id=organization_id,
            project_id=project_id,
            stable_key=uuid4(),
            version=1,
            name=payload.food_web.name,
            description=payload.food_web.description,
            nodes_json=[
                node.model_dump(mode="json", by_alias=True) for node in payload.food_web.nodes
            ],
            links_json=[
                link.model_dump(mode="json", by_alias=True) for link in payload.food_web.links
            ],
            metadata_json=payload.food_web.metadata,
            created_by_user_id=created_by_user_id,
        )
        parameter_set = ParameterSet(
            organization_id=organization_id,
            project_id=project_id,
            stable_key=uuid4(),
            version=1,
            name=payload.parameter_set.name,
            description=payload.parameter_set.description,
            parameters_json=payload.parameter_set.parameters,
            metadata_json=payload.parameter_set.metadata,
            created_by_user_id=created_by_user_id,
        )
        self.session.add(food_web)
        self.session.add(parameter_set)
        self.session.flush()

        scenario = SimulationScenario(
            organization_id=organization_id,
            project_id=project_id,
            stable_key=uuid4(),
            version=1,
            name=payload.name,
            description=payload.description,
            soil_sample_id=payload.soil_sample_id,
            soil_sample_version_id=payload.soil_sample_version_id,
            food_web_definition_id=food_web.id,
            parameter_set_id=parameter_set.id,
            scenario_config_json=payload.scenario_config,
            created_by_user_id=created_by_user_id,
        )
        self.session.add(scenario)
        self.session.commit()
        self.session.refresh(scenario)
        return scenario

    def update(
        self,
        scenario: SimulationScenario,
        *,
        payload,
        updated_by_user_id: UUID,
        increment_version: bool,
    ):
        if payload.food_web is not None:
            next_food_web = FoodWebDefinition(
                organization_id=scenario.organization_id,
                project_id=scenario.project_id,
                stable_key=scenario.food_web_definition.stable_key,
                version=scenario.food_web_definition.version + 1,
                name=payload.food_web.name,
                description=payload.food_web.description,
                nodes_json=[
                    node.model_dump(mode="json", by_alias=True) for node in payload.food_web.nodes
                ],
                links_json=[
                    link.model_dump(mode="json", by_alias=True) for link in payload.food_web.links
                ],
                metadata_json=payload.food_web.metadata,
                created_by_user_id=updated_by_user_id,
            )
            self.session.add(next_food_web)
            self.session.flush()
            scenario.food_web_definition_id = next_food_web.id

        if payload.parameter_set is not None:
            next_parameter_set = ParameterSet(
                organization_id=scenario.organization_id,
                project_id=scenario.project_id,
                stable_key=scenario.parameter_set.stable_key,
                version=scenario.parameter_set.version + 1,
                name=payload.parameter_set.name,
                description=payload.parameter_set.description,
                parameters_json=payload.parameter_set.parameters,
                metadata_json=payload.parameter_set.metadata,
                created_by_user_id=updated_by_user_id,
            )
            self.session.add(next_parameter_set)
            self.session.flush()
            scenario.parameter_set_id = next_parameter_set.id

        if payload.name is not None:
            scenario.name = payload.name
        if "description" in payload.model_fields_set:
            scenario.description = payload.description
        if payload.status is not None:
            scenario.status = payload.status
        if payload.soil_sample_id is not None:
            scenario.soil_sample_id = payload.soil_sample_id
        if payload.soil_sample_version_id is not None:
            scenario.soil_sample_version_id = payload.soil_sample_version_id
        if payload.scenario_config is not None:
            scenario.scenario_config_json = payload.scenario_config

        if increment_version:
            scenario.version += 1

        scenario.updated_at = datetime.now(UTC)
        self.session.add(scenario)
        self.session.commit()
        self.session.refresh(scenario)
        return scenario

    def soft_delete(self, organization_id: UUID, scenario_id: UUID, deleted_by_user_id: UUID):
        scenario = self.get_by_id(organization_id, scenario_id)
        if scenario is None:
            return None

        deleted_at = datetime.now(UTC)
        scenario.status = ScenarioStatus.ARCHIVED
        scenario.deleted_at = deleted_at
        scenario.updated_at = deleted_at
        self.session.add(scenario)
        self.session.commit()
        self.session.refresh(scenario)
        return scenario
