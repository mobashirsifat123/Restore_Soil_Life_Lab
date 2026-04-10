"""Create initial MVP tenant, project, scenario, run, and artifact schema.

Revision ID: 20260331_0001
Revises:
Create Date: 2026-03-31 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260331_0001"
down_revision = None
branch_labels = None
depends_on = None

DEBUG_ORGANIZATION_ID = "00000000-0000-7000-0000-000000000101"
DEBUG_USER_ID = "00000000-0000-7000-0000-000000000001"

project_status = sa.Enum("active", "archived", name="project_status")
scenario_status = sa.Enum("active", "archived", name="scenario_status")
run_status = sa.Enum(
    "draft",
    "queued",
    "running",
    "succeeded",
    "failed",
    "cancel_requested",
    "canceled",
    name="run_status",
)
artifact_type = sa.Enum(
    "result_json",
    "summary_json",
    "csv_export",
    "plot_image",
    "report_pdf",
    "log_bundle",
    "other",
    name="artifact_type",
)


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    project_status.create(op.get_bind(), checkfirst=True)
    scenario_status.create(op.get_bind(), checkfirst=True)
    run_status.create(op.get_bind(), checkfirst=True)
    artifact_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "uq_organizations_slug_active",
        "organizations",
        ["slug"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_users_organization_id", "users", ["organization_id"])
    op.create_index("ix_users_organization_active", "users", ["organization_id", "is_active"])
    op.create_index(
        "uq_users_email_active",
        "users",
        ["email"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.execute(
        sa.text(
            """
            INSERT INTO organizations (id, name, slug, description, is_active, metadata_json)
            VALUES (
                CAST(:organization_id AS UUID),
                :name,
                :slug,
                :description,
                true,
                '{}'::jsonb
            )
            """
        ).bindparams(
            organization_id=DEBUG_ORGANIZATION_ID,
            name="Local Development Organization",
            slug="local-dev-org",
            description="Bootstrap organization for local placeholder authentication.",
        )
    )
    op.execute(
        sa.text(
            """
            INSERT INTO users (id, organization_id, email, full_name, is_active, metadata_json)
            VALUES (
                CAST(:user_id AS UUID),
                CAST(:organization_id AS UUID),
                :email,
                :full_name,
                true,
                '{}'::jsonb
            )
            """
        ).bindparams(
            user_id=DEBUG_USER_ID,
            organization_id=DEBUG_ORGANIZATION_ID,
            email="scientist@example.com",
            full_name="Local Scientist",
        )
    )

    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", project_status, nullable=False, server_default="active"),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_projects_organization_id", "projects", ["organization_id"])
    op.create_index("ix_projects_created_by_user_id", "projects", ["created_by_user_id"])
    op.create_index(
        "uq_projects_org_slug_active",
        "projects",
        ["organization_id", "slug"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "soil_samples",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sample_code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("collected_on", sa.Date(), nullable=True),
        sa.Column("location_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("measurements_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_soil_samples_organization_id", "soil_samples", ["organization_id"])
    op.create_index("ix_soil_samples_project_id", "soil_samples", ["project_id"])
    op.create_index("ix_soil_samples_created_by_user_id", "soil_samples", ["created_by_user_id"])
    op.create_index(
        "uq_soil_samples_project_code_active",
        "soil_samples",
        ["project_id", "sample_code"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "food_web_definitions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("stable_key", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("nodes_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("links_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_food_web_definitions_organization_id", "food_web_definitions", ["organization_id"])
    op.create_index("ix_food_web_definitions_project_id", "food_web_definitions", ["project_id"])
    op.create_index("ix_food_web_definitions_created_by_user_id", "food_web_definitions", ["created_by_user_id"])
    op.create_index("ix_food_web_definitions_stable_key", "food_web_definitions", ["stable_key"])

    op.create_table(
        "parameter_sets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("stable_key", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("parameters_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_parameter_sets_organization_id", "parameter_sets", ["organization_id"])
    op.create_index("ix_parameter_sets_project_id", "parameter_sets", ["project_id"])
    op.create_index("ix_parameter_sets_created_by_user_id", "parameter_sets", ["created_by_user_id"])
    op.create_index("ix_parameter_sets_stable_key", "parameter_sets", ["stable_key"])

    op.create_table(
        "simulation_scenarios",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("stable_key", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", scenario_status, nullable=False, server_default="active"),
        sa.Column("soil_sample_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("food_web_definition_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("parameter_set_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scenario_config_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["soil_sample_id"], ["soil_samples.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["food_web_definition_id"], ["food_web_definitions.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["parameter_set_id"], ["parameter_sets.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_simulation_scenarios_organization_id", "simulation_scenarios", ["organization_id"])
    op.create_index("ix_simulation_scenarios_project_id", "simulation_scenarios", ["project_id"])
    op.create_index("ix_simulation_scenarios_soil_sample_id", "simulation_scenarios", ["soil_sample_id"])
    op.create_index("ix_simulation_scenarios_created_by_user_id", "simulation_scenarios", ["created_by_user_id"])
    op.create_index("ix_simulation_scenarios_stable_key", "simulation_scenarios", ["stable_key"])

    op.create_table(
        "simulation_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scenario_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", run_status, nullable=False, server_default="queued"),
        sa.Column("engine_name", sa.String(length=100), nullable=False),
        sa.Column("engine_version", sa.String(length=50), nullable=False),
        sa.Column("input_schema_version", sa.String(length=50), nullable=False),
        sa.Column("input_hash", sa.String(length=64), nullable=False),
        sa.Column("result_hash", sa.String(length=64), nullable=True),
        sa.Column("execution_options_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("input_snapshot_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("result_summary_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("queue_name", sa.String(length=100), nullable=False),
        sa.Column("idempotency_key", sa.String(length=100), nullable=True),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("worker_id", sa.String(length=100), nullable=True),
        sa.Column("queued_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("canceled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_code", sa.String(length=100), nullable=True),
        sa.Column("failure_message", sa.Text(), nullable=True),
        sa.Column("failure_details_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["scenario_id"], ["simulation_scenarios.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_simulation_runs_organization_id", "simulation_runs", ["organization_id"])
    op.create_index("ix_simulation_runs_project_id", "simulation_runs", ["project_id"])
    op.create_index("ix_simulation_runs_scenario_id", "simulation_runs", ["scenario_id"])
    op.create_index("ix_simulation_runs_created_by_user_id", "simulation_runs", ["created_by_user_id"])
    op.create_index("ix_simulation_runs_input_hash", "simulation_runs", ["input_hash"])
    op.create_index("ix_simulation_runs_org_status", "simulation_runs", ["organization_id", "status"])
    op.create_index(
        "uq_simulation_runs_idempotency_active",
        "simulation_runs",
        ["organization_id", "scenario_id", "idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )

    op.create_table(
        "run_artifacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("artifact_type", artifact_type, nullable=False),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("storage_key", sa.String(length=1024), nullable=False),
        sa.Column("byte_size", sa.Integer(), nullable=True),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["run_id"], ["simulation_runs.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_run_artifacts_organization_id", "run_artifacts", ["organization_id"])
    op.create_index("ix_run_artifacts_run", "run_artifacts", ["run_id"])


def downgrade() -> None:
    op.drop_index("ix_run_artifacts_run", table_name="run_artifacts")
    op.drop_index("ix_run_artifacts_organization_id", table_name="run_artifacts")
    op.drop_table("run_artifacts")

    op.drop_index("uq_simulation_runs_idempotency_active", table_name="simulation_runs")
    op.drop_index("ix_simulation_runs_org_status", table_name="simulation_runs")
    op.drop_index("ix_simulation_runs_input_hash", table_name="simulation_runs")
    op.drop_index("ix_simulation_runs_created_by_user_id", table_name="simulation_runs")
    op.drop_index("ix_simulation_runs_scenario_id", table_name="simulation_runs")
    op.drop_index("ix_simulation_runs_project_id", table_name="simulation_runs")
    op.drop_index("ix_simulation_runs_organization_id", table_name="simulation_runs")
    op.drop_table("simulation_runs")

    op.drop_index("ix_simulation_scenarios_stable_key", table_name="simulation_scenarios")
    op.drop_index("ix_simulation_scenarios_created_by_user_id", table_name="simulation_scenarios")
    op.drop_index("ix_simulation_scenarios_soil_sample_id", table_name="simulation_scenarios")
    op.drop_index("ix_simulation_scenarios_project_id", table_name="simulation_scenarios")
    op.drop_index("ix_simulation_scenarios_organization_id", table_name="simulation_scenarios")
    op.drop_table("simulation_scenarios")

    op.drop_index("ix_parameter_sets_stable_key", table_name="parameter_sets")
    op.drop_index("ix_parameter_sets_created_by_user_id", table_name="parameter_sets")
    op.drop_index("ix_parameter_sets_project_id", table_name="parameter_sets")
    op.drop_index("ix_parameter_sets_organization_id", table_name="parameter_sets")
    op.drop_table("parameter_sets")

    op.drop_index("ix_food_web_definitions_stable_key", table_name="food_web_definitions")
    op.drop_index("ix_food_web_definitions_created_by_user_id", table_name="food_web_definitions")
    op.drop_index("ix_food_web_definitions_project_id", table_name="food_web_definitions")
    op.drop_index("ix_food_web_definitions_organization_id", table_name="food_web_definitions")
    op.drop_table("food_web_definitions")

    op.drop_index("uq_soil_samples_project_code_active", table_name="soil_samples")
    op.drop_index("ix_soil_samples_created_by_user_id", table_name="soil_samples")
    op.drop_index("ix_soil_samples_project_id", table_name="soil_samples")
    op.drop_index("ix_soil_samples_organization_id", table_name="soil_samples")
    op.drop_table("soil_samples")

    op.drop_index("uq_projects_org_slug_active", table_name="projects")
    op.drop_index("ix_projects_created_by_user_id", table_name="projects")
    op.drop_index("ix_projects_organization_id", table_name="projects")
    op.drop_table("projects")

    op.drop_index("uq_users_email_active", table_name="users")
    op.drop_index("ix_users_organization_active", table_name="users")
    op.drop_index("ix_users_organization_id", table_name="users")
    op.drop_table("users")

    op.drop_index("uq_organizations_slug_active", table_name="organizations")
    op.drop_table("organizations")

    artifact_type.drop(op.get_bind(), checkfirst=True)
    run_status.drop(op.get_bind(), checkfirst=True)
    scenario_status.drop(op.get_bind(), checkfirst=True)
    project_status.drop(op.get_bind(), checkfirst=True)
