"""Add immutable soil sample versions and pin scenarios to exact versions.

Revision ID: 20260401_0003
Revises: 20260401_0002
Create Date: 2026-04-01 14:00:00
"""

from __future__ import annotations

from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "20260401_0003"
down_revision = "20260401_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()

    op.create_table(
        "soil_sample_versions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("soil_sample_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("sample_code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("collected_on", sa.Date(), nullable=True),
        sa.Column(
            "location_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "measurements_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["soil_sample_id"], ["soil_samples.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index(
        "ix_soil_sample_versions_soil_sample_id",
        "soil_sample_versions",
        ["soil_sample_id"],
    )
    op.create_index(
        "ix_soil_sample_versions_organization_id",
        "soil_sample_versions",
        ["organization_id"],
    )
    op.create_index(
        "ix_soil_sample_versions_project_id",
        "soil_sample_versions",
        ["project_id"],
    )
    op.create_index(
        "ix_soil_sample_versions_org_project",
        "soil_sample_versions",
        ["organization_id", "project_id"],
    )
    op.create_index(
        "uq_soil_sample_versions_sample_version",
        "soil_sample_versions",
        ["soil_sample_id", "version"],
        unique=True,
    )

    op.add_column(
        "soil_samples",
        sa.Column("current_version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "soil_samples",
        sa.Column("current_version_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_soil_samples_current_version_id",
        "soil_samples",
        "soil_sample_versions",
        ["current_version_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_soil_samples_current_version_id", "soil_samples", ["current_version_id"])

    op.add_column(
        "simulation_scenarios",
        sa.Column("soil_sample_version_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_simulation_scenarios_soil_sample_version_id",
        "simulation_scenarios",
        "soil_sample_versions",
        ["soil_sample_version_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_simulation_scenarios_soil_sample_version_id",
        "simulation_scenarios",
        ["soil_sample_version_id"],
    )

    soil_sample_rows = bind.execute(
        sa.text(
            """
            SELECT
                id,
                organization_id,
                project_id,
                sample_code,
                name,
                description,
                collected_on,
                location_json,
                measurements_json,
                metadata_json,
                created_by_user_id,
                created_at,
                updated_at
            FROM soil_samples
            """
        )
    ).mappings()

    soil_sample_versions = sa.table(
        "soil_sample_versions",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("soil_sample_id", postgresql.UUID(as_uuid=True)),
        sa.column("organization_id", postgresql.UUID(as_uuid=True)),
        sa.column("project_id", postgresql.UUID(as_uuid=True)),
        sa.column("version", sa.Integer()),
        sa.column("sample_code", sa.String()),
        sa.column("name", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("collected_on", sa.Date()),
        sa.column("location_json", postgresql.JSONB(astext_type=sa.Text())),
        sa.column("measurements_json", postgresql.JSONB(astext_type=sa.Text())),
        sa.column("metadata_json", postgresql.JSONB(astext_type=sa.Text())),
        sa.column("created_by_user_id", postgresql.UUID(as_uuid=True)),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )

    version_rows: list[dict] = []
    version_by_sample_id: dict[str, dict[str, object]] = {}
    for row in soil_sample_rows:
        version_id = uuid4()
        version_rows.append(
            {
                "id": version_id,
                "soil_sample_id": row["id"],
                "organization_id": row["organization_id"],
                "project_id": row["project_id"],
                "version": 1,
                "sample_code": row["sample_code"],
                "name": row["name"],
                "description": row["description"],
                "collected_on": row["collected_on"],
                "location_json": row["location_json"],
                "measurements_json": row["measurements_json"],
                "metadata_json": row["metadata_json"],
                "created_by_user_id": row["created_by_user_id"],
                "created_at": row["updated_at"] or row["created_at"],
            }
        )
        version_by_sample_id[str(row["id"])] = {"id": version_id, "version": 1}

    if version_rows:
        op.bulk_insert(soil_sample_versions, version_rows)
        for soil_sample_id, version_info in version_by_sample_id.items():
            bind.execute(
                sa.text(
                    """
                    UPDATE soil_samples
                    SET current_version = :current_version,
                        current_version_id = :current_version_id
                    WHERE id = :soil_sample_id
                    """
                ),
                {
                    "current_version": version_info["version"],
                    "current_version_id": version_info["id"],
                    "soil_sample_id": soil_sample_id,
                },
            )

    update_scenario_statement = sa.text(
        """
        UPDATE simulation_scenarios
        SET soil_sample_version_id = :soil_sample_version_id,
            scenario_config_json = :scenario_config_json
        WHERE id = :scenario_id
        """
    ).bindparams(
        sa.bindparam(
            "scenario_config_json",
            type_=postgresql.JSONB(astext_type=sa.Text()),
        )
    )

    scenario_rows = bind.execute(
        sa.text(
            """
            SELECT id, soil_sample_id, scenario_config_json
            FROM simulation_scenarios
            """
        )
    ).mappings()

    for row in scenario_rows:
        primary_soil_sample_id = str(row["soil_sample_id"])
        primary_version = version_by_sample_id[primary_soil_sample_id]
        scenario_config = dict(row["scenario_config_json"] or {})
        raw_references = scenario_config.get("soilSampleReferences")
        if isinstance(raw_references, list) and raw_references:
            scenario_config["soilSampleReferences"] = [
                {
                    **reference,
                    "soilSampleVersionId": str(
                        version_by_sample_id[str(reference["soilSampleId"])]["id"]
                    ),
                }
                for reference in raw_references
            ]
        else:
            scenario_config["soilSampleReferences"] = [
                {
                    "soilSampleId": primary_soil_sample_id,
                    "soilSampleVersionId": str(primary_version["id"]),
                    "role": "primary",
                }
            ]

        scenario_config["primarySoilSampleId"] = primary_soil_sample_id
        scenario_config["primarySoilSampleVersionId"] = str(primary_version["id"])
        bind.execute(
            update_scenario_statement,
            {
                "scenario_id": row["id"],
                "soil_sample_version_id": primary_version["id"],
                "scenario_config_json": scenario_config,
            },
        )

    op.alter_column("simulation_scenarios", "soil_sample_version_id", nullable=False)


def downgrade() -> None:
    op.drop_index(
        "ix_simulation_scenarios_soil_sample_version_id",
        table_name="simulation_scenarios",
    )
    op.drop_constraint(
        "fk_simulation_scenarios_soil_sample_version_id",
        "simulation_scenarios",
        type_="foreignkey",
    )
    op.drop_column("simulation_scenarios", "soil_sample_version_id")

    op.drop_index("ix_soil_samples_current_version_id", table_name="soil_samples")
    op.drop_constraint(
        "fk_soil_samples_current_version_id",
        "soil_samples",
        type_="foreignkey",
    )
    op.drop_column("soil_samples", "current_version_id")
    op.drop_column("soil_samples", "current_version")

    op.drop_index("uq_soil_sample_versions_sample_version", table_name="soil_sample_versions")
    op.drop_index("ix_soil_sample_versions_org_project", table_name="soil_sample_versions")
    op.drop_index("ix_soil_sample_versions_project_id", table_name="soil_sample_versions")
    op.drop_index("ix_soil_sample_versions_organization_id", table_name="soil_sample_versions")
    op.drop_index("ix_soil_sample_versions_soil_sample_id", table_name="soil_sample_versions")
    op.drop_table("soil_sample_versions")
