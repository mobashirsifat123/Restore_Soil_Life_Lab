from __future__ import annotations

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.domain.enums import ArtifactType, ProjectStatus, RunStatus, ScenarioStatus

EMPTY_JSON = text("'{}'::jsonb")
EMPTY_ARRAY_JSON = text("'[]'::jsonb")


def enum_values(enum_cls: type) -> list[str]:
    return [member.value for member in enum_cls]


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Organization(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "organizations"
    __table_args__ = (
        Index(
            "uq_organizations_slug_active",
            "slug",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)

    users: Mapped[list["User"]] = relationship(back_populates="organization")
    memberships: Mapped[list["OrganizationMembership"]] = relationship(back_populates="organization")
    projects: Mapped[list["Project"]] = relationship(back_populates="organization")
    soil_samples: Mapped[list["SoilSample"]] = relationship(back_populates="organization")
    soil_sample_versions: Mapped[list["SoilSampleVersion"]] = relationship(
        back_populates="organization"
    )
    food_web_definitions: Mapped[list["FoodWebDefinition"]] = relationship(back_populates="organization")
    parameter_sets: Mapped[list["ParameterSet"]] = relationship(back_populates="organization")
    scenarios: Mapped[list["SimulationScenario"]] = relationship(back_populates="organization")
    runs: Mapped[list["SimulationRun"]] = relationship(back_populates="organization")
    artifacts: Mapped[list["RunArtifact"]] = relationship(back_populates="organization")
    auth_sessions: Mapped[list["AuthSession"]] = relationship(back_populates="organization")


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"
    __table_args__ = (
        Index(
            "uq_users_email_active",
            "email",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index("ix_users_organization_active", "organization_id", "is_active"),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    organization_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)

    organization: Mapped[Organization] = relationship(back_populates="users")
    memberships: Mapped[list["OrganizationMembership"]] = relationship(back_populates="user")
    auth_sessions: Mapped[list["AuthSession"]] = relationship(back_populates="user")


class OrganizationMembership(Base, TimestampMixin):
    __tablename__ = "organization_memberships"
    __table_args__ = (
        Index("uq_organization_memberships_user_org", "user_id", "organization_id", unique=True),
        Index("ix_organization_memberships_org_active", "organization_id", "is_active"),
        Index("ix_organization_memberships_user_active", "user_id", "is_active"),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    organization_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(100), nullable=False, default="org_member")
    permissions_json: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default=EMPTY_ARRAY_JSON,
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)

    organization: Mapped[Organization] = relationship(back_populates="memberships")
    user: Mapped[User] = relationship(back_populates="memberships")


class AuthSession(Base, TimestampMixin):
    __tablename__ = "auth_sessions"
    __table_args__ = (
        Index("uq_auth_sessions_token_hash", "token_hash", unique=True),
        Index("ix_auth_sessions_user_active", "user_id", "revoked_at"),
        Index("ix_auth_sessions_org_active", "organization_id", "revoked_at"),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)

    user: Mapped[User] = relationship(back_populates="auth_sessions")
    organization: Mapped[Organization] = relationship(back_populates="auth_sessions")


class Project(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "projects"
    __table_args__ = (
        Index(
            "uq_projects_org_slug_active",
            "organization_id",
            "slug",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    organization_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, name="project_status", values_callable=enum_values),
        nullable=False,
        default=ProjectStatus.ACTIVE,
        server_default=ProjectStatus.ACTIVE.value,
    )
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    created_by_user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    organization: Mapped[Organization] = relationship(back_populates="projects")
    soil_samples: Mapped[list["SoilSample"]] = relationship(back_populates="project")
    soil_sample_versions: Mapped[list["SoilSampleVersion"]] = relationship(
        back_populates="project"
    )
    food_web_definitions: Mapped[list["FoodWebDefinition"]] = relationship(back_populates="project")
    parameter_sets: Mapped[list["ParameterSet"]] = relationship(back_populates="project")
    scenarios: Mapped[list["SimulationScenario"]] = relationship(back_populates="project")
    runs: Mapped[list["SimulationRun"]] = relationship(back_populates="project")


class SoilSample(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "soil_samples"
    __table_args__ = (
        Index(
            "uq_soil_samples_project_code_active",
            "project_id",
            "sample_code",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    organization_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    sample_code: Mapped[str] = mapped_column(String(100), nullable=False)
    current_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    collected_on: Mapped[date | None] = mapped_column(Date(), nullable=True)
    location_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    measurements_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=EMPTY_JSON,
    )
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    created_by_user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    current_version_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("soil_sample_versions.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    organization: Mapped[Organization] = relationship(back_populates="soil_samples")
    project: Mapped[Project] = relationship(back_populates="soil_samples")
    scenarios: Mapped[list["SimulationScenario"]] = relationship(back_populates="soil_sample")
    versions: Mapped[list["SoilSampleVersion"]] = relationship(
        back_populates="soil_sample",
        foreign_keys="SoilSampleVersion.soil_sample_id",
        order_by="SoilSampleVersion.version",
    )
    current_version_row: Mapped["SoilSampleVersion | None"] = relationship(
        foreign_keys=[current_version_id],
        post_update=True,
    )


class SoilSampleVersion(Base):
    __tablename__ = "soil_sample_versions"
    __table_args__ = (
        Index("ix_soil_sample_versions_org_project", "organization_id", "project_id"),
        Index("ix_soil_sample_versions_soil_sample", "soil_sample_id"),
        Index("uq_soil_sample_versions_sample_version", "soil_sample_id", "version", unique=True),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    soil_sample_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("soil_samples.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    sample_code: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    collected_on: Mapped[date | None] = mapped_column(Date(), nullable=True)
    location_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    measurements_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=EMPTY_JSON,
    )
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    created_by_user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    soil_sample: Mapped[SoilSample] = relationship(
        back_populates="versions",
        foreign_keys=[soil_sample_id],
    )
    organization: Mapped[Organization] = relationship(back_populates="soil_sample_versions")
    project: Mapped[Project] = relationship(back_populates="soil_sample_versions")
    scenarios: Mapped[list["SimulationScenario"]] = relationship(back_populates="soil_sample_version")


class FoodWebDefinition(Base, TimestampMixin):
    __tablename__ = "food_web_definitions"
    __table_args__ = (
        Index("ix_food_web_definitions_org_project", "organization_id", "project_id"),
        Index("ix_food_web_definitions_stable_key", "stable_key"),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    organization_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    stable_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, default=uuid4)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    nodes_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default=EMPTY_ARRAY_JSON)
    links_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default=EMPTY_ARRAY_JSON)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    created_by_user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    organization: Mapped[Organization] = relationship(back_populates="food_web_definitions")
    project: Mapped[Project] = relationship(back_populates="food_web_definitions")
    scenarios: Mapped[list["SimulationScenario"]] = relationship(back_populates="food_web_definition")


class ParameterSet(Base, TimestampMixin):
    __tablename__ = "parameter_sets"
    __table_args__ = (
        Index("ix_parameter_sets_org_project", "organization_id", "project_id"),
        Index("ix_parameter_sets_stable_key", "stable_key"),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    organization_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    stable_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, default=uuid4)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    parameters_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    created_by_user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    organization: Mapped[Organization] = relationship(back_populates="parameter_sets")
    project: Mapped[Project] = relationship(back_populates="parameter_sets")
    scenarios: Mapped[list["SimulationScenario"]] = relationship(back_populates="parameter_set")


class SimulationScenario(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "simulation_scenarios"
    __table_args__ = (
        Index("ix_simulation_scenarios_org_project", "organization_id", "project_id"),
        Index("ix_simulation_scenarios_stable_key", "stable_key"),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    organization_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    stable_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, default=uuid4)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    status: Mapped[ScenarioStatus] = mapped_column(
        Enum(ScenarioStatus, name="scenario_status", values_callable=enum_values),
        nullable=False,
        default=ScenarioStatus.ACTIVE,
        server_default=ScenarioStatus.ACTIVE.value,
    )
    soil_sample_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("soil_samples.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    soil_sample_version_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("soil_sample_versions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    food_web_definition_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("food_web_definitions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    parameter_set_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("parameter_sets.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    scenario_config_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=EMPTY_JSON,
    )
    created_by_user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    organization: Mapped[Organization] = relationship(back_populates="scenarios")
    project: Mapped[Project] = relationship(back_populates="scenarios")
    soil_sample: Mapped[SoilSample] = relationship(back_populates="scenarios")
    soil_sample_version: Mapped[SoilSampleVersion] = relationship(back_populates="scenarios")
    food_web_definition: Mapped[FoodWebDefinition] = relationship(back_populates="scenarios")
    parameter_set: Mapped[ParameterSet] = relationship(back_populates="scenarios")
    runs: Mapped[list["SimulationRun"]] = relationship(back_populates="scenario")


class SimulationRun(Base, TimestampMixin):
    __tablename__ = "simulation_runs"
    __table_args__ = (
        Index("ix_simulation_runs_org_project", "organization_id", "project_id"),
        Index("ix_simulation_runs_org_status", "organization_id", "status"),
        Index(
            "uq_simulation_runs_idempotency_active",
            "organization_id",
            "scenario_id",
            "idempotency_key",
            unique=True,
            postgresql_where=text("idempotency_key IS NOT NULL"),
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    organization_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    scenario_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("simulation_scenarios.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[RunStatus] = mapped_column(
        Enum(RunStatus, name="run_status", values_callable=enum_values),
        nullable=False,
        default=RunStatus.QUEUED,
        server_default=RunStatus.QUEUED.value,
    )
    engine_name: Mapped[str] = mapped_column(String(100), nullable=False)
    engine_version: Mapped[str] = mapped_column(String(50), nullable=False)
    input_schema_version: Mapped[str] = mapped_column(String(50), nullable=False)
    input_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    result_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    execution_options_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=EMPTY_JSON,
    )
    input_snapshot_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    result_summary_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    queue_name: Mapped[str] = mapped_column(String(100), nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(100), nullable=True)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    worker_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    queued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    canceled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failure_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    failure_message: Mapped[str | None] = mapped_column(Text(), nullable=True)
    failure_details_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=EMPTY_JSON,
    )
    created_by_user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    organization: Mapped[Organization] = relationship(back_populates="runs")
    project: Mapped[Project] = relationship(back_populates="runs")
    scenario: Mapped[SimulationScenario] = relationship(back_populates="runs")
    artifacts: Mapped[list["RunArtifact"]] = relationship(back_populates="run")


class RunArtifact(Base):
    __tablename__ = "run_artifacts"
    __table_args__ = (Index("ix_run_artifacts_run", "run_id"),)

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    organization_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    run_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("simulation_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    artifact_type: Mapped[ArtifactType] = mapped_column(
        Enum(ArtifactType, name="artifact_type", values_callable=enum_values),
        nullable=False,
    )
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(1024), nullable=False)
    byte_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default=EMPTY_JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    organization: Mapped[Organization] = relationship(back_populates="artifacts")
    run: Mapped[SimulationRun] = relationship(back_populates="artifacts")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    __table_args__ = (
        Index("ix_password_reset_tokens_user_id", "user_id"),
        Index("ix_password_reset_tokens_expires_at", "expires_at"),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    code_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class UserActivityLog(Base):
    __tablename__ = "user_activity_logs"
    __table_args__ = (
        Index("ix_user_activity_logs_org_happened_at", "organization_id", "happened_at"),
        Index("ix_user_activity_logs_user_id", "user_id"),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    organization_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
    )
    user_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    user_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    activity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    activity_label: Mapped[str] = mapped_column(String(255), nullable=False)
    details: Mapped[str | None] = mapped_column(Text(), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=EMPTY_JSON,
    )
    happened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
