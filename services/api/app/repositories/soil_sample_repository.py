from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Project, SoilSample, SoilSampleVersion


class SoilSampleRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def project_exists(self, organization_id: UUID, project_id: UUID) -> bool:
        statement = select(Project.id).where(
            Project.organization_id == organization_id,
            Project.id == project_id,
            Project.deleted_at.is_(None),
        )
        return self.session.scalar(statement) is not None

    def sample_code_exists(
        self,
        organization_id: UUID,
        project_id: UUID,
        sample_code: str,
        *,
        exclude_soil_sample_id: UUID | None = None,
    ) -> bool:
        statement = select(SoilSample.id).where(
            SoilSample.organization_id == organization_id,
            SoilSample.project_id == project_id,
            SoilSample.sample_code == sample_code,
            SoilSample.deleted_at.is_(None),
        )
        if exclude_soil_sample_id is not None:
            statement = statement.where(SoilSample.id != exclude_soil_sample_id)
        return self.session.scalar(statement) is not None

    def list_for_project(
        self,
        organization_id: UUID,
        project_id: UUID,
        *,
        limit: int,
        cursor: str | None,
    ):
        statement = (
            select(SoilSample)
            .where(
                SoilSample.organization_id == organization_id,
                SoilSample.project_id == project_id,
                SoilSample.deleted_at.is_(None),
            )
            .order_by(SoilSample.created_at.desc(), SoilSample.id.desc())
            .limit(limit)
        )
        return list(self.session.scalars(statement))

    def get_by_id(self, organization_id: UUID, soil_sample_id: UUID):
        statement = select(SoilSample).where(
            SoilSample.organization_id == organization_id,
            SoilSample.id == soil_sample_id,
            SoilSample.deleted_at.is_(None),
        )
        return self.session.scalar(statement)

    def create(
        self,
        *,
        organization_id: UUID,
        project_id: UUID,
        created_by_user_id: UUID,
        payload,
    ) -> SoilSample:
        if not self.project_exists(organization_id, project_id):
            raise LookupError("project_not_found")

        soil_sample = SoilSample(
            organization_id=organization_id,
            project_id=project_id,
            sample_code=payload.sample_code,
            current_version=1,
            name=payload.name,
            description=payload.description,
            collected_on=payload.collected_on,
            location_json=payload.location,
            measurements_json=payload.measurements,
            metadata_json=payload.metadata,
            created_by_user_id=created_by_user_id,
        )
        self.session.add(soil_sample)
        self.session.flush()

        soil_sample_version = SoilSampleVersion(
            soil_sample_id=soil_sample.id,
            organization_id=organization_id,
            project_id=project_id,
            version=1,
            sample_code=payload.sample_code,
            name=payload.name,
            description=payload.description,
            collected_on=payload.collected_on,
            location_json=payload.location,
            measurements_json=payload.measurements,
            metadata_json=payload.metadata,
            created_by_user_id=created_by_user_id,
        )
        self.session.add(soil_sample_version)
        self.session.flush()
        soil_sample.current_version_id = soil_sample_version.id
        self.session.add(soil_sample)
        self.session.commit()
        self.session.refresh(soil_sample)
        return soil_sample

    def update(
        self,
        soil_sample: SoilSample,
        *,
        updates: dict,
        created_by_user_id: UUID,
    ) -> SoilSample:
        next_state = {
            "sample_code": soil_sample.sample_code,
            "name": soil_sample.name,
            "description": soil_sample.description,
            "collected_on": soil_sample.collected_on,
            "location_json": soil_sample.location_json,
            "measurements_json": soil_sample.measurements_json,
            "metadata_json": soil_sample.metadata_json,
        }
        next_state.update(updates)

        next_version_number = soil_sample.current_version + 1
        soil_sample_version = SoilSampleVersion(
            soil_sample_id=soil_sample.id,
            organization_id=soil_sample.organization_id,
            project_id=soil_sample.project_id,
            version=next_version_number,
            sample_code=next_state["sample_code"],
            name=next_state["name"],
            description=next_state["description"],
            collected_on=next_state["collected_on"],
            location_json=next_state["location_json"],
            measurements_json=next_state["measurements_json"],
            metadata_json=next_state["metadata_json"],
            created_by_user_id=created_by_user_id,
        )
        self.session.add(soil_sample_version)
        self.session.flush()

        for field, value in next_state.items():
            setattr(soil_sample, field, value)
        soil_sample.current_version = next_version_number
        soil_sample.current_version_id = soil_sample_version.id
        soil_sample.updated_at = datetime.now(UTC)
        self.session.add(soil_sample)
        self.session.commit()
        self.session.refresh(soil_sample)
        return soil_sample

    def soft_delete(self, organization_id: UUID, soil_sample_id: UUID, deleted_by_user_id: UUID):
        soil_sample = self.get_by_id(organization_id, soil_sample_id)
        if soil_sample is None:
            return None
        soil_sample.deleted_at = datetime.now(UTC)
        soil_sample.updated_at = datetime.now(UTC)
        self.session.add(soil_sample)
        self.session.commit()
        self.session.refresh(soil_sample)
        return soil_sample
