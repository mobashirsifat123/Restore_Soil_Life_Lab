# Build Backlog

## Purpose

This document converts the current architecture, roadmap, thin-slice plan, quality strategy, and deployment blueprint into an implementation backlog.

Primary source documents:

- [architecture.md](/Users/mobashirsifat/Desktop/bio_lab/docs/architecture.md)
- [implementation-roadmap.md](/Users/mobashirsifat/Desktop/bio_lab/docs/implementation-roadmap.md)
- [first-thin-vertical-slice.md](/Users/mobashirsifat/Desktop/bio_lab/docs/slices/first-thin-vertical-slice.md)
- [quality-strategy.md](/Users/mobashirsifat/Desktop/bio_lab/docs/quality/quality-strategy.md)
- [deployment-architecture.md](/Users/mobashirsifat/Desktop/bio_lab/docs/deployment/deployment-architecture.md)

This backlog is optimized for:

- one builder working mostly sequentially
- two builders working in parallel with clear write boundaries

## Planning Rules

- keep heavy compute in `services/worker` and `services/simulation-engine`
- keep scientific logic out of FastAPI route handlers
- keep OpenAPI as the external contract source of truth
- treat reproducibility as part of the product, not a later hardening step
- prefer the first thin vertical slice over broad surface-area scaffolding

## Implementation Order

Build in this order:

1. Epic 0: Repo Foundation
2. Epic 1: Contracts And Core Data Model
3. Epic 2: API Thin Slice
4. Epic 3: Worker And Simulation Placeholder
5. Epic 4: Web Thin Slice
6. Epic 5: Quality, CI, And Observability
7. Epic 6: Scientific Function V1
8. Epic 7: Artifact Storage, Reports, And Deployment Hardening
9. Epic 8: Marketing And Post-MVP Expansion

## Must Be Sequential

- `E0` before all other epics
- contract freeze for scenario/run payloads before generated client work
- database migration before repository implementation
- run submission API before worker execution handler
- worker success path before run results page
- deterministic placeholder engine before full scientific implementations
- CI migration smoke test before production deployment work

## Can Be Parallelized

After `E0.1` and `E0.2` are done:

- web shell work can proceed in parallel with API route implementation
- design system primitives can proceed in parallel with feature forms
- worker queue adapter can proceed in parallel with frontend pages
- quality harnesses can proceed in parallel with thin-slice UI once endpoint shapes are stable

After `E1.2` contract freeze is done:

- generated API client work
- frontend form implementation
- worker payload implementation
- engine request/response fixture work

## Recommended Team Split

## Solo Builder

Work almost fully in implementation order. Only parallelize mentally by keeping tasks small and switching when blocked.

## Two-Person Team

Use these lanes:

- Builder A: backend, worker, database, CI, deployment
- Builder B: web app, shared UI, generated client, Playwright

Shared checkpoints:

- after contract freeze
- after thin-slice API routes are stable
- before E2E and release hardening

## Epic 0: Repo Foundation

### Feature E0.1: Root Workspace Bootstrap

Acceptance criteria:

- repo installs from documented commands
- `apps/web`, `services/api`, `services/worker`, and `services/simulation-engine` each have runnable manifests
- root scripts exist for local dev and migrations

Tasks:

- `T0.1` Add root workspace files: `package.json`, `pnpm-workspace.yaml`, `turbo.json`, `tsconfig.base.json`
  - depends on: none
  - parallelizable: no
- `T0.2` Add root environment and editor files: `.gitignore`, `.editorconfig`, `.nvmrc`, `.python-version`
  - depends on: none
  - parallelizable: yes with `T0.1`
- `T0.3` Add root developer commands: `Makefile`, README bootstrap section
  - depends on: `T0.1`
  - parallelizable: yes

### Feature E0.2: Local Infrastructure

Acceptance criteria:

- local PostgreSQL and Redis start with one command
- service `.env.example` files exist and match code expectations
- local artifact storage path is defined

Tasks:

- `T0.4` Add Docker Compose for Postgres and Redis under [infra/docker](/Users/mobashirsifat/Desktop/bio_lab/infra/docker)
  - depends on: `T0.1`
  - parallelizable: yes
- `T0.5` Add service-level `.env.example` files for web, API, and worker
  - depends on: `T0.1`
  - parallelizable: yes
- `T0.6` Add local artifact storage convention for worker and document it
  - depends on: `T0.4`
  - parallelizable: yes

### Feature E0.3: CI Skeleton

Acceptance criteria:

- lint, typecheck, and test jobs are defined
- migration smoke test job exists
- simulation engine tests can run in CI

Tasks:

- `T0.7` Add CI workflow for frontend typecheck/lint
  - depends on: `T0.1`
  - parallelizable: yes
- `T0.8` Add CI workflow for Python lint/tests and migration smoke
  - depends on: `T0.4`
  - parallelizable: yes
- `T0.9` Add CI workflow for simulation engine unit/regression tests
  - depends on: `T0.1`
  - parallelizable: yes

## Epic 1: Contracts And Core Data Model

### Feature E1.1: Thin-Slice Contract Freeze

Acceptance criteria:

- scenario creation request shape is fixed
- run request, run detail, run results, and provenance fields are fixed
- run lifecycle statuses are fixed and documented

Tasks:

- `T1.1` Freeze run lifecycle enum and transition rules
  - depends on: `T0.1`
  - parallelizable: no
- `T1.2` Freeze scenario create request with inline `food_web` and `parameter_set`
  - depends on: `T0.1`
  - parallelizable: no
- `T1.3` Freeze run result summary and provenance response shape
  - depends on: `T1.1`
  - parallelizable: yes

### Feature E1.2: Core Database Schema

Acceptance criteria:

- core thin-slice tables exist with org scoping
- run table stores snapshot, hashes, engine metadata, status, timestamps, and failure fields
- migration applies cleanly on an empty database

Tasks:

- `T1.4` Implement SQLAlchemy base models and shared mixins
  - depends on: `T0.1`
  - parallelizable: yes
- `T1.5` Add initial Alembic migration for `projects`, `soil_samples`, `food_web_definitions`, `parameter_sets`, `simulation_scenarios`, `simulation_runs`, and `run_artifacts`
  - depends on: `T1.1`, `T1.2`, `T1.4`
  - parallelizable: no
- `T1.6` Add migration smoke test script for CI
  - depends on: `T1.5`
  - parallelizable: yes

### Feature E1.3: OpenAPI And Generated Client

Acceptance criteria:

- API emits stable OpenAPI schema
- `packages/api-client` is generated from the schema, not hand-maintained
- frontend imports API types only from `packages/api-client`

Tasks:

- `T1.7` Ensure route `operation_id`s and response models are complete for thin-slice endpoints
  - depends on: `T1.2`
  - parallelizable: yes
- `T1.8` Add OpenAPI export command and schema artifact path
  - depends on: `T1.7`
  - parallelizable: yes
- `T1.9` Replace placeholder client generation with actual OpenAPI codegen in [packages/api-client](/Users/mobashirsifat/Desktop/bio_lab/packages/api-client)
  - depends on: `T1.8`
  - parallelizable: no

## Epic 2: API Thin Slice

### Feature E2.1: Auth And Organization Context

Acceptance criteria:

- debug auth/session endpoint returns consistent user and organization context
- permission dependencies can protect project, sample, scenario, and run routes
- organization scoping is enforced in repositories

Tasks:

- `T2.1` Implement debug auth/session endpoint and dependency wiring
  - depends on: `T0.1`
  - parallelizable: yes
- `T2.2` Add permission constants and route protection for thin-slice routes
  - depends on: `T2.1`
  - parallelizable: yes
- `T2.3` Add repository-level org scoping checks for project, sample, scenario, and run queries
  - depends on: `T1.5`
  - parallelizable: no

### Feature E2.2: Project And Soil Sample APIs

Acceptance criteria:

- projects can be created, read, listed, updated, and soft-deleted
- soil samples can be created, read, listed, updated, and soft-deleted
- API returns consistent error envelope on validation and not-found states

Tasks:

- `T2.4` Implement project repository methods
  - depends on: `T1.5`
  - parallelizable: yes
- `T2.5` Implement project service methods and route wiring
  - depends on: `T2.4`
  - parallelizable: no
- `T2.6` Implement soil sample repository methods
  - depends on: `T1.5`, `T2.3`
  - parallelizable: yes with `T2.4`
- `T2.7` Implement soil sample service methods and route wiring
  - depends on: `T2.6`
  - parallelizable: no

### Feature E2.3: Scenario APIs

Acceptance criteria:

- creating a scenario also creates one versioned food web definition and one parameter set
- scenario responses include version metadata and linked IDs
- scenario retrieval works with org and project scoping

Tasks:

- `T2.8` Implement scenario schema validation for inline food web and parameter set
  - depends on: `T1.2`
  - parallelizable: yes
- `T2.9` Implement scenario repository create/list/get/update methods
  - depends on: `T1.5`, `T2.3`, `T2.8`
  - parallelizable: no
- `T2.10` Implement scenario service methods and route wiring
  - depends on: `T2.9`
  - parallelizable: no

### Feature E2.4: Run Submission And Results APIs

Acceptance criteria:

- `POST /runs` persists the authoritative input snapshot and enqueues a job
- run detail and status endpoints return lifecycle timestamps and failure metadata
- run results endpoint returns summary plus artifact metadata

Tasks:

- `T2.11` Implement input snapshot builder and `input_hash` computation
  - depends on: `T1.2`, `T1.3`, `T2.9`
  - parallelizable: yes
- `T2.12` Implement run repository methods including idempotency lookup
  - depends on: `T1.5`, `T2.3`
  - parallelizable: yes
- `T2.13` Implement `POST /runs` service logic and queue publisher
  - depends on: `T2.11`, `T2.12`
  - parallelizable: no
- `T2.14` Implement `GET /runs/{id}`, `GET /runs/{id}/status`, and `GET /runs/{id}/results`
  - depends on: `T2.12`
  - parallelizable: yes with `T2.13`

## Epic 3: Worker And Simulation Placeholder

### Feature E3.1: Queue Runtime

Acceptance criteria:

- worker consumes jobs from Redis Streams
- messages can be acked, retried, and dead-lettered
- stale messages can be reclaimed

Tasks:

- `T3.1` Implement queue payload schema and envelope validation
  - depends on: `T1.3`
  - parallelizable: yes
- `T3.2` Implement Redis Streams adapter: ensure stream, reserve, ack
  - depends on: `T0.4`
  - parallelizable: yes
- `T3.3` Implement retry requeue and dead-letter behavior
  - depends on: `T3.2`
  - parallelizable: no
- `T3.4` Implement stale message reclaim logic
  - depends on: `T3.2`
  - parallelizable: yes

### Feature E3.2: Run Processing Flow

Acceptance criteria:

- worker transitions run `queued -> running -> terminal`
- worker loads authoritative input snapshot from PostgreSQL
- worker writes artifacts and updates run rows transactionally enough for MVP

Tasks:

- `T3.5` Implement DB-backed status store start/success/failure transitions
  - depends on: `T1.5`, `T2.13`
  - parallelizable: no
- `T3.6` Implement artifact writer adapter for local filesystem with stable keys
  - depends on: `T0.6`
  - parallelizable: yes
- `T3.7` Implement simulation execution service using subprocess CLI invocation
  - depends on: `T3.1`
  - parallelizable: yes
- `T3.8` Implement simulation run job handler
  - depends on: `T3.5`, `T3.6`, `T3.7`
  - parallelizable: no

### Feature E3.3: Placeholder Simulation Engine

Acceptance criteria:

- engine request and result models are stable
- deterministic placeholder outputs are returned
- result provenance includes engine version, parameter version, input hash, and result hash

Tasks:

- `T3.9` Finalize engine request and result Pydantic models
  - depends on: `T1.2`, `T1.3`
  - parallelizable: yes
- `T3.10` Implement deterministic placeholder module outputs for all requested module categories
  - depends on: `T3.9`
  - parallelizable: yes
- `T3.11` Implement and verify CLI entrypoint contract
  - depends on: `T3.9`
  - parallelizable: yes
- `T3.12` Add engine determinism and regression tests
  - depends on: `T3.10`, `T3.11`
  - parallelizable: yes

## Epic 4: Web Thin Slice

### Feature E4.1: App Shell And Shared UI

Acceptance criteria:

- marketing and platform route groups are separated
- app providers, design tokens, and core UI primitives are wired
- API access goes through the generated client and server-side proxy

Tasks:

- `T4.1` Implement root Next.js app config, Tailwind wiring, and providers
  - depends on: `T0.1`
  - parallelizable: yes
- `T4.2` Implement platform shell and marketing shell
  - depends on: `T4.1`
  - parallelizable: yes
- `T4.3` Implement shared UI primitives needed for forms and status views
  - depends on: `T4.1`
  - parallelizable: yes
- `T4.4` Implement same-origin API proxy with debug auth header bridge
  - depends on: `T2.1`
  - parallelizable: yes

### Feature E4.2: Project, Sample, And Scenario Flow

Acceptance criteria:

- user can create a project
- user can add a soil sample under a project
- user can create a scenario with inline food web and parameter set
- success states redirect to the next useful page

Tasks:

- `T4.5` Implement dashboard project listing page
  - depends on: `T2.5`, `T4.2`, `T4.4`
  - parallelizable: yes
- `T4.6` Implement project creation form and mutation flow
  - depends on: `T2.5`, `T4.3`, `T4.4`
  - parallelizable: yes
- `T4.7` Implement soil sample creation page and mutation flow
  - depends on: `T2.7`, `T4.3`, `T4.4`
  - parallelizable: yes
- `T4.8` Implement scenario creation page and mutation flow
  - depends on: `T2.10`, `T4.3`, `T4.4`
  - parallelizable: yes
- `T4.9` Implement project overview page showing samples, scenarios, and run action
  - depends on: `T4.5`, `T4.7`, `T4.8`
  - parallelizable: no

### Feature E4.3: Run Submission And Results UI

Acceptance criteria:

- user can submit a run from the project page
- run detail page polls status until terminal
- results page shows summary, provenance, input snapshot, and artifact references

Tasks:

- `T4.10` Implement run submission mutation from project overview
  - depends on: `T2.13`, `T4.9`
  - parallelizable: no
- `T4.11` Implement run detail page with status polling
  - depends on: `T2.14`, `T4.3`, `T4.4`
  - parallelizable: yes
- `T4.12` Implement results panels for summary, lifecycle metadata, and artifacts
  - depends on: `T4.11`, `T3.8`
  - parallelizable: no

## Epic 5: Quality, CI, And Observability

### Feature E5.1: Thin-Slice Test Harness

Acceptance criteria:

- API integration tests cover thin-slice CRUD and run retrieval
- worker tests cover success and failure paths
- one end-to-end browser test covers the thin slice

Tasks:

- `T5.1` Add API integration test fixtures for PostgreSQL-backed thin-slice routes
  - depends on: `T2.5`, `T2.7`, `T2.10`, `T2.14`
  - parallelizable: yes
- `T5.2` Add worker integration tests for queued->running->succeeded and failure paths
  - depends on: `T3.8`
  - parallelizable: yes
- `T5.3` Add Playwright test for create project -> create sample -> create scenario -> submit run -> view results
  - depends on: `T4.12`, `T3.8`
  - parallelizable: no
- `T5.4` Add engine fixture regression tests for hash stability and output shape
  - depends on: `T3.12`
  - parallelizable: yes

### Feature E5.2: Contract And CI Gates

Acceptance criteria:

- CI fails on schema/codegen drift
- migrations are validated in CI
- thin-slice PRs cannot merge without passing tests

Tasks:

- `T5.5` Add OpenAPI export and generated-client drift check
  - depends on: `T1.9`
  - parallelizable: yes
- `T5.6` Add migration smoke test job using PostgreSQL container
  - depends on: `T1.6`, `T0.8`
  - parallelizable: yes
- `T5.7` Add PR quality gates for lint, typecheck, unit, integration, and thin-slice E2E
  - depends on: `T5.1`, `T5.2`, `T5.3`, `T5.5`, `T5.6`
  - parallelizable: no

### Feature E5.3: Logs, Metrics, And Tracing

Acceptance criteria:

- API and worker logs include request ID and run ID
- failures are traceable from browser action to run record
- Sentry and OTEL stubs are wired for later environment rollout

Tasks:

- `T5.8` Add structured logging fields for API and worker
  - depends on: `T2.13`, `T3.8`
  - parallelizable: yes
- `T5.9` Add request ID and run ID propagation across API enqueue and worker processing
  - depends on: `T5.8`
  - parallelizable: no
- `T5.10` Add Sentry and OTEL configuration stubs in web, API, and worker
  - depends on: `T0.1`
  - parallelizable: yes

## Epic 6: Scientific Function V1

### Feature E6.1: Flux And Mineralization

Acceptance criteria:

- engine returns non-placeholder flux values for reference fixtures
- mineralization outputs are computed from the same canonical request contract
- expected tolerances are documented and testable

Tasks:

- `T6.1` Implement flux calculation module v1
  - depends on: `T3.9`
  - parallelizable: yes
- `T6.2` Implement mineralization analysis module v1
  - depends on: `T6.1`
  - parallelizable: no
- `T6.3` Add reference fixtures and tolerance-based tests for flux and mineralization
  - depends on: `T6.1`, `T6.2`
  - parallelizable: yes

### Feature E6.2: Stability, Dynamics, And Decomposition

Acceptance criteria:

- stability and `smin` outputs exist with fixture validation
- dynamics simulation returns expected time-series shape
- decomposition returns decomposition constant and expected metadata

Tasks:

- `T6.4` Implement stability and `smin` module v1
  - depends on: `T3.9`
  - parallelizable: yes
- `T6.5` Implement non-equilibrium dynamics module v1
  - depends on: `T3.9`
  - parallelizable: yes
- `T6.6` Implement decomposition module v1
  - depends on: `T3.9`
  - parallelizable: yes
- `T6.7` Add reference fixtures and tolerance-based tests for stability, dynamics, and decomposition
  - depends on: `T6.4`, `T6.5`, `T6.6`
  - parallelizable: yes

### Feature E6.3: Reproducibility Hardening

Acceptance criteria:

- same input and engine version produce same hashes
- rerun from stored snapshot reproduces the same result for deterministic fixtures
- scientific output changes require engine version bump and fixture updates

Tasks:

- `T6.8` Add rerun-from-snapshot verification test in worker or engine harness
  - depends on: `T3.8`, `T6.3`, `T6.7`
  - parallelizable: yes
- `T6.9` Add engine version bump policy and enforcement checklist
  - depends on: `T6.3`, `T6.7`
  - parallelizable: yes
- `T6.10` Add regression test coverage for result hash stability across deterministic fixtures
  - depends on: `T6.8`
  - parallelizable: yes

## Epic 7: Artifact Storage, Reports, And Deployment Hardening

### Feature E7.1: Production Artifact Storage

Acceptance criteria:

- artifact storage adapter supports local and object storage implementations
- artifact metadata in DB matches stored object metadata
- downloads can be safely exposed later through signed URLs

Tasks:

- `T7.1` Extract storage interface used by worker artifact writer
  - depends on: `T3.6`
  - parallelizable: yes
- `T7.2` Implement object storage adapter for S3-compatible backend
  - depends on: `T7.1`
  - parallelizable: yes
- `T7.3` Add artifact metadata verification tests
  - depends on: `T7.2`
  - parallelizable: yes

### Feature E7.2: Reports

Acceptance criteria:

- report job type exists
- one report template can be generated from a run
- reports are stored and referenceable through API

Tasks:

- `T7.4` Add report table and migration
  - depends on: `T1.5`
  - parallelizable: yes
- `T7.5` Implement report job payload and worker handler
  - depends on: `T7.4`, `T3.2`, `T3.5`
  - parallelizable: yes
- `T7.6` Implement first report template and artifact writer path
  - depends on: `T7.5`
  - parallelizable: no
- `T7.7` Add report API and minimal UI entry point
  - depends on: `T7.6`
  - parallelizable: yes

### Feature E7.3: Deployment And Environment Hardening

Acceptance criteria:

- Dockerfiles exist for web, API, and worker
- Terraform environment skeleton exists for dev/staging/production
- a dev or staging environment can deploy the thin slice

Tasks:

- `T7.8` Add Dockerfiles for web, API, and worker
  - depends on: `E4`, `E3`
  - parallelizable: yes
- `T7.9` Add Terraform module skeleton and environment roots under [infra/terraform](/Users/mobashirsifat/Desktop/bio_lab/infra/terraform)
  - depends on: `T0.1`
  - parallelizable: yes
- `T7.10` Add deploy pipeline for dev or staging environment
  - depends on: `T7.8`, `T7.9`, `T5.7`
  - parallelizable: no
- `T7.11` Add backup and restore runbook for PostgreSQL and artifacts
  - depends on: `T7.10`
  - parallelizable: yes

## Epic 8: Marketing And Post-MVP Expansion

### Feature E8.1: Premium Marketing Surface

Acceptance criteria:

- marketing pages use the same design system foundation without leaking platform complexity
- public pages are SEO-ready and fast
- route separation remains intact

Tasks:

- `T8.1` Implement marketing homepage and shared editorial sections
  - depends on: `T4.1`, `T4.2`, `T4.3`
  - parallelizable: yes
- `T8.2` Add science page, case study page, and contact page scaffolds
  - depends on: `T8.1`
  - parallelizable: yes
- `T8.3` Add Lighthouse and SEO checks for marketing routes
  - depends on: `T8.1`, `T8.2`
  - parallelizable: yes

### Feature E8.2: Enterprise And Analytical Expansion

Acceptance criteria:

- later features land without breaking the thin-slice foundations
- auth, reporting, and scenario comparison can be added on existing boundaries

Tasks:

- `T8.4` Add real auth provider integration plan and backlog
  - depends on: `E2`, `E4`
  - parallelizable: yes
- `T8.5` Add scenario comparison backlog and data model review
  - depends on: `E6`
  - parallelizable: yes
- `T8.6` Add enterprise features backlog for SSO, dashboards, and provisioning
  - depends on: `E7`
  - parallelizable: yes

## Solo Execution Path

If one person is building, execute in this exact order:

1. `T0.1` to `T0.6`
2. `T1.1` to `T1.6`
3. `T2.1` to `T2.14`
4. `T3.1` to `T3.12`
5. `T4.1` to `T4.12`
6. `T5.1` to `T5.10`
7. `T6.1` to `T6.10`
8. `T7.1` to `T7.11`
9. `T8.1` onward

## Two-Person Execution Path

Use this order:

1. Both: `T0.1` to `T0.6`
2. Builder A: `T1.1` to `T2.14`
3. Builder B: `T4.1` to `T4.8` after `T1.2` and `T2.1`
4. Builder A: `T3.1` to `T3.8`
5. Builder B: `T4.9` to `T4.12`
6. Both: `T5.1` to `T5.10`
7. Builder A: `T6.1` to `T7.11`
8. Builder B: `T8.1` onward and report UI work as available

## Immediate Next Backlog Cut

If the team is starting today, do these first ten tasks:

1. `T0.1` Root workspace bootstrap
2. `T0.4` Local Docker Compose infra
3. `T0.5` Service `.env.example` files
4. `T1.1` Run lifecycle freeze
5. `T1.2` Scenario and run contract freeze
6. `T1.4` SQLAlchemy base models
7. `T1.5` Initial migration
8. `T2.4` Project repository methods
9. `T2.5` Project service and route wiring
10. `T2.11` Input snapshot builder

Those ten tasks unlock the thinnest credible path to the first working run pipeline.
