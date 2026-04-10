# Initial Domain Model And Relational Schema

## Goals

This schema is optimized for:

- clarity of ownership and tenant scoping
- reproducible and auditable simulation runs
- fast implementation for MVP
- enough structure for future enterprise and client-facing dashboards
- clean separation between business entities and scientific payloads

This is intentionally not a fully generalized scientific data platform. It is the minimum strong model that supports the product roadmap without boxing us in.

## Core Design Decisions

1. every tenant-owned row carries `organization_id`
2. runs are append-only operational records and should not be hard-deleted
3. food web definitions, parameter sets, and scenarios are versioned as immutable rows
4. scientific structures live in `jsonb`; operational metadata lives in normalized columns
5. every run stores a full `input_snapshot` so the result is reproducible even if source records later change
6. RBAC is organization-scoped from day one
7. soft delete is used for user-facing content, not for run history

## ERD-Style Explanation

- One `organization` has many `organization_memberships`.
- One `user` can belong to many `organizations` through `organization_memberships`.
- One `organization_membership` can have one or more `roles`.
- One `role` has many `permissions` through `role_permissions`.
- One `organization` has many `projects`.
- One `project` has many `soil_samples`.
- One `project` has many versioned `food_web_definitions`.
- One `project` has many versioned `parameter_sets`.
- One `project` has many versioned `simulation_scenarios`.
- One `simulation_scenario` references exactly one `soil_sample`, one `food_web_definition`, and one `parameter_set`.
- One `simulation_scenario` has many `simulation_runs`.
- One `simulation_run` has many `run_artifacts`.
- One `report` belongs to one `project` and may optionally be tied to one primary `simulation_run`.

Text ERD:

```text
organizations
  ├── organization_memberships ── users
  │     └── organization_membership_roles ── roles ── role_permissions ── permissions
  └── projects
        ├── soil_samples
        ├── food_web_definitions
        ├── parameter_sets
        ├── simulation_scenarios
        │     └── simulation_runs
        │           └── run_artifacts
        └── reports
```

## Required For MVP vs Later

### Required For MVP

- `organizations`
- `users`
- `organization_memberships`
- `roles`
- `permissions`
- `role_permissions`
- `organization_membership_roles`
- `projects`
- `soil_samples`
- `food_web_definitions`
- `parameter_sets`
- `simulation_scenarios`
- `simulation_runs`
- `run_artifacts`

### Can Wait Until Slightly Later

- `reports`

Reason:

The first usable product can ship with downloadable run artifacts and a run detail page before introducing a first-class report workflow. If simple PDF or CSV exports become important early, add `reports` in the second or third migration wave.

## Normalized Tables vs JSONB Snapshots

### Normalize These

- tenant hierarchy and access control
- top-level business entities and ownership
- statuses
- timestamps
- foreign key relationships
- version numbers
- artifact storage references
- engine name and engine version
- user attribution such as `created_by_user_id` and `submitted_by_user_id`

### Store As JSONB

- `soil_samples.measurements_json`
- `soil_samples.location_json`
- `food_web_definitions.structure_json`
- `parameter_sets.parameters_json`
- `simulation_scenarios.scenario_config_json`
- `simulation_runs.input_snapshot_json`
- `simulation_runs.result_summary_json`
- `simulation_runs.failure_details_json`
- `run_artifacts.metadata_json`
- `reports.input_snapshot_json`
- `reports.summary_json`

### Why

The scientific payloads will evolve faster than the operational model. Normalizing nodes, edges, trophic coefficients, and every numeric parameter too early would slow delivery and make change management harder. We only normalize what the product must query and enforce relationally.

## Status Enums

### `membership_status`

- `invited`
- `active`
- `suspended`
- `revoked`

### `project_status`

- `active`
- `archived`

### `run_status`

- `draft`
- `queued`
- `running`
- `succeeded`
- `failed`
- `cancel_requested`
- `canceled`

### `artifact_type`

- `result_json`
- `summary_json`
- `csv_export`
- `plot_image`
- `report_pdf`
- `log_bundle`
- `other`

### `report_status`

- `draft`
- `queued`
- `rendering`
- `succeeded`
- `failed`
- `canceled`

## Audit Metadata Strategy

### On Mutable User-Facing Tables

Include:

- `created_at`
- `updated_at`
- `created_by_user_id`
- `updated_by_user_id`
- `deleted_at`
- `deleted_by_user_id`

Use this on:

- `organizations`
- `projects`
- `soil_samples`
- `reports`

### On Immutable Versioned Tables

Include:

- `created_at`
- `created_by_user_id`

Use this on:

- `food_web_definitions`
- `parameter_sets`
- `simulation_scenarios`

Do not update these rows in place after creation, except possibly for harmless metadata such as `description` if the team decides that is acceptable. Prefer immutability.

### On Operational Tables

Include:

- `created_at`
- `updated_at`
- lifecycle timestamps such as `queued_at`, `started_at`, `completed_at`, `canceled_at`
- event actor fields like `submitted_by_user_id` or `requested_by_user_id`

Use this on:

- `simulation_runs`
- `run_artifacts`
- `reports`

## Soft Delete Strategy

### Use Soft Delete

Use `deleted_at` and `deleted_by_user_id` on:

- `organizations`
- `projects`
- `soil_samples`
- `reports`

### Do Not Soft Delete

Do not soft delete by default:

- `simulation_runs`
- `run_artifacts`
- RBAC join tables used for audit history

Why:

Run history is part of the scientific record. Hiding a run is acceptable with archival flags later, but deleting it undermines auditability.

### Versioned Tables

For `food_web_definitions`, `parameter_sets`, and `simulation_scenarios`, prefer immutable rows with optional `is_archived` if visibility control is needed later. Avoid soft delete as the primary mechanism.

## Table Definitions

## 1. `organizations`

Purpose:

- tenant root

Columns:

- `id uuid primary key`
- `name varchar(255) not null`
- `slug varchar(100) not null`
- `status varchar(32) not null default 'active'`
- `settings_json jsonb not null default '{}'::jsonb`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`
- `created_by_user_id uuid null references users(id)`
- `updated_by_user_id uuid null references users(id)`
- `deleted_at timestamptz null`
- `deleted_by_user_id uuid null references users(id)`

Constraints and indexes:

- unique index on `slug` where `deleted_at is null`
- index on `(status, created_at desc)`

Notes:

- keep `settings_json` flexible for branding, feature flags, and future client dashboard toggles

## 2. `users`

Purpose:

- global identity record

Columns:

- `id uuid primary key`
- `email varchar(320) not null`
- `full_name varchar(255) null`
- `auth_provider varchar(64) not null`
- `auth_subject varchar(255) not null`
- `avatar_url text null`
- `is_active boolean not null default true`
- `last_login_at timestamptz null`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`

Constraints and indexes:

- unique index on `email`
- unique index on `(auth_provider, auth_subject)`
- index on `(is_active, last_login_at desc)`

Notes:

- store email normalized to lowercase in application code

## 3. `organization_memberships`

Purpose:

- join users to organizations

Columns:

- `id uuid primary key`
- `organization_id uuid not null references organizations(id)`
- `user_id uuid not null references users(id)`
- `status membership_status not null default 'invited'`
- `invited_by_user_id uuid null references users(id)`
- `joined_at timestamptz null`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`

Constraints and indexes:

- unique index on `(organization_id, user_id)`
- index on `(user_id, status)`
- index on `(organization_id, status)`

## 4. `roles`

Purpose:

- RBAC roles; supports global system roles now and tenant-defined roles later

Columns:

- `id uuid primary key`
- `organization_id uuid null references organizations(id)`
- `slug varchar(64) not null`
- `name varchar(100) not null`
- `description text null`
- `is_system boolean not null default false`
- `created_at timestamptz not null default now()`

Constraints and indexes:

- unique partial index on `(slug)` where `organization_id is null`
- unique partial index on `(organization_id, slug)` where `organization_id is not null`

Seed roles for MVP:

- `org_admin`
- `scientist`
- `viewer`

## 5. `permissions`

Purpose:

- atomic capabilities for roles

Columns:

- `id uuid primary key`
- `key varchar(100) not null`
- `description text null`
- `created_at timestamptz not null default now()`

Constraints and indexes:

- unique index on `key`

Seed examples:

- `project.read`
- `project.write`
- `sample.read`
- `sample.write`
- `scenario.read`
- `scenario.write`
- `run.submit`
- `run.read`
- `report.read`
- `report.write`

## 6. `role_permissions`

Purpose:

- map roles to permissions

Columns:

- `role_id uuid not null references roles(id)`
- `permission_id uuid not null references permissions(id)`
- `created_at timestamptz not null default now()`

Constraints and indexes:

- primary key on `(role_id, permission_id)`
- index on `permission_id`

## 7. `organization_membership_roles`

Purpose:

- assign one or more roles to a membership

Columns:

- `membership_id uuid not null references organization_memberships(id)`
- `role_id uuid not null references roles(id)`
- `created_at timestamptz not null default now()`

Constraints and indexes:

- primary key on `(membership_id, role_id)`
- index on `role_id`

Tradeoff:

This is slightly more flexible than a single `role_slug` column on memberships. It avoids a migration when multiple roles or tenant-defined roles appear.

## 8. `projects`

Purpose:

- top-level workspace for scientific work inside an organization

Columns:

- `id uuid primary key`
- `organization_id uuid not null references organizations(id)`
- `name varchar(255) not null`
- `slug varchar(100) not null`
- `description text null`
- `status project_status not null default 'active'`
- `metadata_json jsonb not null default '{}'::jsonb`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`
- `created_by_user_id uuid null references users(id)`
- `updated_by_user_id uuid null references users(id)`
- `deleted_at timestamptz null`
- `deleted_by_user_id uuid null references users(id)`

Constraints and indexes:

- unique partial index on `(organization_id, slug)` where `deleted_at is null`
- index on `(organization_id, status, created_at desc)`

## 9. `soil_samples`

Purpose:

- a collected or imported soil sample associated with a project

Columns:

- `id uuid primary key`
- `organization_id uuid not null references organizations(id)`
- `project_id uuid not null references projects(id)`
- `sample_code varchar(100) not null`
- `name varchar(255) null`
- `description text null`
- `collected_on date null`
- `location_json jsonb not null default '{}'::jsonb`
- `measurements_json jsonb not null default '{}'::jsonb`
- `metadata_json jsonb not null default '{}'::jsonb`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`
- `created_by_user_id uuid null references users(id)`
- `updated_by_user_id uuid null references users(id)`
- `deleted_at timestamptz null`
- `deleted_by_user_id uuid null references users(id)`

Constraints and indexes:

- unique partial index on `(project_id, sample_code)` where `deleted_at is null`
- index on `(organization_id, project_id, created_at desc)`

Tradeoff:

`measurements_json` stays flexible because the exact lab fields may evolve. Reproducibility comes from the run snapshot, not from a fully versioned soil sample model.

## 10. `food_web_definitions`

Purpose:

- immutable versioned scientific structure describing the food web

Columns:

- `id uuid primary key`
- `organization_id uuid not null references organizations(id)`
- `project_id uuid not null references projects(id)`
- `stable_key uuid not null`
- `version integer not null`
- `name varchar(255) not null`
- `description text null`
- `structure_json jsonb not null`
- `content_hash char(64) not null`
- `created_at timestamptz not null default now()`
- `created_by_user_id uuid null references users(id)`

Constraints and indexes:

- unique index on `(project_id, stable_key, version)`
- index on `(project_id, stable_key, version desc)`
- index on `(project_id, content_hash)`

Notes:

- `structure_json` should include nodes, edges, trophic links, and any graph-level metadata
- rows are immutable; new edits create a new version row

## 11. `parameter_sets`

Purpose:

- immutable versioned model parameters

Columns:

- `id uuid primary key`
- `organization_id uuid not null references organizations(id)`
- `project_id uuid not null references projects(id)`
- `stable_key uuid not null`
- `version integer not null`
- `name varchar(255) not null`
- `description text null`
- `parameters_json jsonb not null`
- `content_hash char(64) not null`
- `created_at timestamptz not null default now()`
- `created_by_user_id uuid null references users(id)`

Constraints and indexes:

- unique index on `(project_id, stable_key, version)`
- index on `(project_id, stable_key, version desc)`
- index on `(project_id, content_hash)`

## 12. `simulation_scenarios`

Purpose:

- immutable versioned scenario referencing one sample, one food web definition, and one parameter set

Columns:

- `id uuid primary key`
- `organization_id uuid not null references organizations(id)`
- `project_id uuid not null references projects(id)`
- `stable_key uuid not null`
- `version integer not null`
- `name varchar(255) not null`
- `description text null`
- `soil_sample_id uuid not null references soil_samples(id)`
- `food_web_definition_id uuid not null references food_web_definitions(id)`
- `parameter_set_id uuid not null references parameter_sets(id)`
- `scenario_config_json jsonb not null`
- `content_hash char(64) not null`
- `created_at timestamptz not null default now()`
- `created_by_user_id uuid null references users(id)`

Constraints and indexes:

- unique index on `(project_id, stable_key, version)`
- index on `(project_id, stable_key, version desc)`
- index on `(soil_sample_id)`
- index on `(food_web_definition_id)`
- index on `(parameter_set_id)`

## 13. `simulation_runs`

Purpose:

- append-only execution record for a scenario run

Columns:

- `id uuid primary key`
- `organization_id uuid not null references organizations(id)`
- `project_id uuid not null references projects(id)`
- `scenario_id uuid not null references simulation_scenarios(id)`
- `soil_sample_id uuid not null references soil_samples(id)`
- `food_web_definition_id uuid not null references food_web_definitions(id)`
- `parameter_set_id uuid not null references parameter_sets(id)`
- `status run_status not null default 'draft'`
- `submitted_by_user_id uuid null references users(id)`
- `engine_name varchar(100) not null`
- `engine_version varchar(64) not null`
- `engine_build_sha varchar(64) null`
- `input_schema_version varchar(32) not null`
- `idempotency_key varchar(100) null`
- `queue_job_id varchar(255) null`
- `input_hash char(64) not null`
- `result_hash char(64) null`
- `input_snapshot_json jsonb not null`
- `result_summary_json jsonb null`
- `run_metadata_json jsonb not null default '{}'::jsonb`
- `failure_code varchar(64) null`
- `failure_message text null`
- `failure_details_json jsonb null`
- `queued_at timestamptz null`
- `started_at timestamptz null`
- `completed_at timestamptz null`
- `canceled_at timestamptz null`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`

Constraints and indexes:

- unique partial index on `(project_id, idempotency_key)` where `idempotency_key is not null`
- index on `(organization_id, created_at desc)`
- index on `(project_id, created_at desc)`
- index on `(scenario_id, created_at desc)`
- index on `(status, created_at desc)`
- index on `(submitted_by_user_id, created_at desc)`

Why duplicate source IDs here:

- easier filtering and debugging
- safer tenant-scoped querying
- cheaper joins for dashboards
- better audit visibility

This duplication is intentional.

## 14. `run_artifacts`

Purpose:

- object storage references for run outputs and exports

Columns:

- `id uuid primary key`
- `organization_id uuid not null references organizations(id)`
- `project_id uuid not null references projects(id)`
- `simulation_run_id uuid not null references simulation_runs(id)`
- `artifact_type artifact_type not null`
- `label varchar(255) not null`
- `storage_provider varchar(32) not null`
- `storage_bucket varchar(255) not null`
- `storage_key varchar(1024) not null`
- `content_type varchar(255) not null`
- `byte_size bigint null`
- `checksum_sha256 char(64) null`
- `metadata_json jsonb not null default '{}'::jsonb`
- `created_at timestamptz not null default now()`
- `created_by_user_id uuid null references users(id)`

Constraints and indexes:

- unique index on `(storage_provider, storage_bucket, storage_key)`
- index on `(simulation_run_id, artifact_type, created_at desc)`
- index on `(organization_id, created_at desc)`

## 15. `reports`

Purpose:

- report generation requests and report outputs

Columns:

- `id uuid primary key`
- `organization_id uuid not null references organizations(id)`
- `project_id uuid not null references projects(id)`
- `primary_simulation_run_id uuid null references simulation_runs(id)`
- `title varchar(255) not null`
- `report_type varchar(64) not null`
- `status report_status not null default 'draft'`
- `template_key varchar(100) not null`
- `template_version varchar(32) not null`
- `input_snapshot_json jsonb not null`
- `summary_json jsonb null`
- `storage_provider varchar(32) null`
- `storage_bucket varchar(255) null`
- `storage_key varchar(1024) null`
- `content_type varchar(255) null`
- `byte_size bigint null`
- `checksum_sha256 char(64) null`
- `failure_message text null`
- `failure_details_json jsonb null`
- `requested_by_user_id uuid null references users(id)`
- `requested_at timestamptz null`
- `started_at timestamptz null`
- `completed_at timestamptz null`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`
- `deleted_at timestamptz null`
- `deleted_by_user_id uuid null references users(id)`

Constraints and indexes:

- index on `(organization_id, created_at desc)`
- index on `(project_id, created_at desc)`
- index on `(primary_simulation_run_id)`
- index on `(status, created_at desc)`

Tradeoff:

This model supports one primary run per report. If multi-run comparative reports become common, add `report_runs` later instead of forcing it in now.

## Recommended SQL Features

- use `uuid` primary keys generated in the application layer, ideally UUIDv7 for index locality
- use `jsonb`
- use `timestamptz`
- avoid `gin` indexes on large JSON fields until actual query patterns justify them

## Suggested SQL Enum Definitions

```sql
create type membership_status as enum ('invited', 'active', 'suspended', 'revoked');
create type project_status as enum ('active', 'archived');
create type run_status as enum ('draft', 'queued', 'running', 'succeeded', 'failed', 'cancel_requested', 'canceled');
create type artifact_type as enum ('result_json', 'summary_json', 'csv_export', 'plot_image', 'report_pdf', 'log_bundle', 'other');
create type report_status as enum ('draft', 'queued', 'rendering', 'succeeded', 'failed', 'canceled');
```

## Tradeoffs And Rationale

### Why Versioned Definitions But Not Versioned Projects

Projects are organizational containers. Food web definitions, parameter sets, and scenarios directly affect scientific outputs and should be immutable version rows. Project metadata does not need that level of rigor.

### Why Keep Soil Samples Mutable

For MVP, run snapshots provide reproducibility without the cost of building a full sample revision system. If lab corrections become common and highly regulated, add `soil_sample_revisions` later.

### Why Duplicate `organization_id` And `project_id`

Strict normalization would let us infer them through joins. We intentionally denormalize them onto tenant-owned tables because:

- authorization queries become simpler and safer
- dashboards and reporting queries become cheaper
- support tooling becomes easier to build

### Why JSONB For Scientific Payloads

The graph structure and parameter payloads will change faster than the operational system. JSONB gives us flexibility while keeping relational integrity for ownership, status, and history.

### Why A Flexible RBAC Schema Early

Using `roles`, `permissions`, and join tables costs little now and avoids painful refactors when enterprise clients need custom roles or internal support roles.

## Recommended Alembic Migration Order

1. enable required extensions and create enums
2. create `users`
3. create `organizations`
4. create `organization_memberships`
5. create `roles`
6. create `permissions`
7. create `role_permissions`
8. create `organization_membership_roles`
9. create `projects`
10. create `soil_samples`
11. create `food_web_definitions`
12. create `parameter_sets`
13. create `simulation_scenarios`
14. create `simulation_runs`
15. create `run_artifacts`
16. create `reports`
17. seed system roles and permissions

If you want smaller, easier-to-review migrations, combine them into these migration groups:

- group A: identities and organizations
- group B: RBAC
- group C: projects and samples
- group D: versioned scientific definitions
- group E: runs and artifacts
- group F: reports and seeds

## SQLAlchemy Model Skeletons

These are outlines, not fully implemented files.

```python
from __future__ import annotations

import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )


class MembershipStatus(str, enum.Enum):
    INVITED = "invited"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"


class ProjectStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class RunStatus(str, enum.Enum):
    DRAFT = "draft"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCEL_REQUESTED = "cancel_requested"
    CANCELED = "canceled"


class ReportStatus(str, enum.Enum):
    DRAFT = "draft"
    QUEUED = "queued"
    RENDERING = "rendering"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"


class ArtifactType(str, enum.Enum):
    RESULT_JSON = "result_json"
    SUMMARY_JSON = "summary_json"
    CSV_EXPORT = "csv_export"
    PLOT_IMAGE = "plot_image"
    REPORT_PDF = "report_pdf"
    LOG_BUNDLE = "log_bundle"
    OTHER = "other"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    full_name: Mapped[str | None] = mapped_column(String(255))
    auth_provider: Mapped[str] = mapped_column(String(64), nullable=False)
    auth_subject: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    memberships: Mapped[list["OrganizationMembership"]] = relationship(back_populates="user")


class Organization(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    settings_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    memberships: Mapped[list["OrganizationMembership"]] = relationship(back_populates="organization")
    projects: Mapped[list["Project"]] = relationship(back_populates="organization")


class OrganizationMembership(Base, TimestampMixin):
    __tablename__ = "organization_memberships"
    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_membership_org_user"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status: Mapped[MembershipStatus] = mapped_column(Enum(MembershipStatus), nullable=False, default=MembershipStatus.INVITED)
    invited_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    joined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    organization: Mapped["Organization"] = relationship(back_populates="memberships")
    user: Mapped["User"] = relationship(back_populates="memberships")


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Project(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "projects"
    __table_args__ = (
        Index("ix_projects_org_status_created", "organization_id", "status", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), nullable=False, default=ProjectStatus.ACTIVE)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    organization: Mapped["Organization"] = relationship(back_populates="projects")


class SoilSample(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "soil_samples"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    sample_code: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    collected_on: Mapped[date | None] = mapped_column(Date)
    location_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    measurements_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)


class FoodWebDefinition(Base):
    __tablename__ = "food_web_definitions"
    __table_args__ = (
        UniqueConstraint("project_id", "stable_key", "version", name="uq_food_web_project_stable_version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    stable_key: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    structure_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))


class ParameterSet(Base):
    __tablename__ = "parameter_sets"
    __table_args__ = (
        UniqueConstraint("project_id", "stable_key", "version", name="uq_parameter_set_project_stable_version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    stable_key: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    parameters_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))


class SimulationScenario(Base):
    __tablename__ = "simulation_scenarios"
    __table_args__ = (
        UniqueConstraint("project_id", "stable_key", "version", name="uq_scenario_project_stable_version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    stable_key: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    soil_sample_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("soil_samples.id"), nullable=False)
    food_web_definition_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("food_web_definitions.id"), nullable=False)
    parameter_set_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parameter_sets.id"), nullable=False)
    scenario_config_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))


class SimulationRun(Base, TimestampMixin):
    __tablename__ = "simulation_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    scenario_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("simulation_scenarios.id"), nullable=False)
    soil_sample_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("soil_samples.id"), nullable=False)
    food_web_definition_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("food_web_definitions.id"), nullable=False)
    parameter_set_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parameter_sets.id"), nullable=False)
    status: Mapped[RunStatus] = mapped_column(Enum(RunStatus), nullable=False, default=RunStatus.DRAFT)
    submitted_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    engine_name: Mapped[str] = mapped_column(String(100), nullable=False)
    engine_version: Mapped[str] = mapped_column(String(64), nullable=False)
    engine_build_sha: Mapped[str | None] = mapped_column(String(64))
    input_schema_version: Mapped[str] = mapped_column(String(32), nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(100))
    queue_job_id: Mapped[str | None] = mapped_column(String(255))
    input_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    result_hash: Mapped[str | None] = mapped_column(String(64))
    input_snapshot_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    result_summary_json: Mapped[dict | None] = mapped_column(JSONB)
    run_metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    failure_code: Mapped[str | None] = mapped_column(String(64))
    failure_message: Mapped[str | None] = mapped_column(Text)
    failure_details_json: Mapped[dict | None] = mapped_column(JSONB)
    queued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    canceled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    artifacts: Mapped[list["RunArtifact"]] = relationship(back_populates="simulation_run")


class RunArtifact(Base):
    __tablename__ = "run_artifacts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    simulation_run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("simulation_runs.id"), nullable=False)
    artifact_type: Mapped[ArtifactType] = mapped_column(Enum(ArtifactType), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_provider: Mapped[str] = mapped_column(String(32), nullable=False)
    storage_bucket: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(1024), nullable=False)
    content_type: Mapped[str] = mapped_column(String(255), nullable=False)
    byte_size: Mapped[int | None] = mapped_column()
    checksum_sha256: Mapped[str | None] = mapped_column(String(64))
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    simulation_run: Mapped["SimulationRun"] = relationship(back_populates="artifacts")


class Report(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    primary_simulation_run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("simulation_runs.id")
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    report_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[ReportStatus] = mapped_column(Enum(ReportStatus), nullable=False, default=ReportStatus.DRAFT)
    template_key: Mapped[str] = mapped_column(String(100), nullable=False)
    template_version: Mapped[str] = mapped_column(String(32), nullable=False)
    input_snapshot_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    summary_json: Mapped[dict | None] = mapped_column(JSONB)
    storage_provider: Mapped[str | None] = mapped_column(String(32))
    storage_bucket: Mapped[str | None] = mapped_column(String(255))
    storage_key: Mapped[str | None] = mapped_column(String(1024))
    content_type: Mapped[str | None] = mapped_column(String(255))
    byte_size: Mapped[int | None] = mapped_column()
    checksum_sha256: Mapped[str | None] = mapped_column(String(64))
    failure_message: Mapped[str | None] = mapped_column(Text)
    failure_details_json: Mapped[dict | None] = mapped_column(JSONB)
    requested_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
```

## Implementation Notes

### Repository-Level Guardrail

Every query for tenant-owned rows should filter on `organization_id`. Do not rely on inherited joins alone for authorization.

### Run Submission Guardrail

When creating a `simulation_run`, copy a canonicalized snapshot of:

- scenario row
- soil sample inputs needed for computation
- food web structure
- parameter set values
- runtime config
- engine metadata

That snapshot is the source of truth for reproducing the run.

### Hashing Guardrail

Compute hashes over canonical JSON serialization, not arbitrary Python dict ordering.
