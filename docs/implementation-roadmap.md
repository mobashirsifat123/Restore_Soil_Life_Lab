# Bio Soil Platform Implementation Roadmap

## Document Purpose

This roadmap is the execution plan for building the first production-capable version of the Bio Soil scientific SaaS platform.

It is written to answer:

1. recommended build order
2. milestone breakdown by phase
3. what to build first vs later
4. the first thin vertical slice
5. main technical risks and mitigations
6. team sequencing for 1 to 3 developers
7. deliverables for Week 1, Week 2, Week 3, and Month 2
8. MVP vs post-MVP scope
9. exact repo setup priorities
10. acceptance criteria by phase

## Execution Assumptions

These assumptions must be made explicit before development starts:

- the scientific formulas and expected outputs for the five core functions are either already defined or can be frozen quickly
- at least one reference dataset with expected outputs will be available for validation
- the initial user model can be simple: one organization, invited members, and three roles
- the first release does not require billing, SSO, or full CMS workflows
- object storage can be abstracted behind one provider interface

If the scientific formulas are still moving, insert a short pre-Phase-0 scientific specification sprint. Do not start building rich UX before the scientific contracts are stable enough to test.

## Recommended Build Order

Build in this order:

1. repository and local development foundation
2. deployment skeleton, observability primitives, and CI
3. authentication and RBAC skeleton
4. core database schema for organizations, projects, samples, scenarios, and runs
5. API contract and generated TypeScript client
6. worker pipeline and run lifecycle model
7. thin vertical slice from UI to API to worker to result page
8. simulation engine package with deterministic placeholder output
9. scientific function implementations with fixture-based validation
10. artifact storage, report generation, and production hardening
11. premium marketing pages and content workflow expansion
12. post-MVP features such as comparison tools, sensitivity analysis, and richer admin tooling

Why this order:

- it proves the hardest architectural path first
- it avoids blocking frontend progress on unfinished science
- it forces run versioning, auditability, and async orchestration into the foundation instead of bolting them on later

## What To Build First vs Delay

### Build First

- monorepo tooling and local infra
- Next.js app shell with route separation for marketing and platform
- FastAPI app shell with health checks and OpenAPI output
- worker service with job lifecycle states
- PostgreSQL schema for the minimum viable domain
- organization membership and three-role RBAC: `org_admin`, `scientist`, `viewer`
- simulation run submission, status polling, and persisted outputs
- deterministic placeholder simulation engine with a real input/output contract
- object storage integration for run artifacts
- structured logging, request IDs, run IDs, and error reporting
- contract tests and one end-to-end test for the thin slice

### Delay Until Later

- visual food web graph editor
- live collaboration and comments
- custom report builder UI
- multi-scenario comparison dashboards
- advanced decomposition exploration tooling
- Monte Carlo or sensitivity analysis
- billing, quotas, and subscriptions
- SSO and enterprise provisioning
- headless CMS integration
- websockets and live streaming updates
- granular admin analytics dashboards

Rule:

Use forms, validated JSON, or CSV import before building a graphical editor. Use polling before websockets. Use one report template before building configurable reporting.

## Thin Vertical Slice To Implement First

This is the first feature slice that proves the platform architecture.

### User Story

A signed-in scientist can:

- create a project
- create one soil sample under that project
- define a simple food web and parameter set
- create one simulation scenario
- submit a simulation run
- watch the run move from `queued` to `running` to `succeeded`
- open the results page and see outputs plus audit metadata

### Scope of the Thin Slice

Frontend pages:

- `/login`
- `/(platform)/projects`
- `/(platform)/projects/new`
- `/(platform)/projects/[projectId]`
- `/(platform)/projects/[projectId]/samples/new`
- `/(platform)/projects/[projectId]/scenarios/new`
- `/(platform)/runs/[runId]`

Minimum API endpoints:

- `POST /v1/projects`
- `GET /v1/projects/:id`
- `POST /v1/soil-samples`
- `POST /v1/food-webs`
- `POST /v1/parameter-sets`
- `POST /v1/scenarios`
- `POST /v1/runs`
- `GET /v1/runs/:id`
- `GET /v1/runs/:id/artifacts`

Minimum database tables:

- `organizations`
- `users`
- `organization_memberships`
- `projects`
- `soil_samples`
- `food_webs`
- `parameter_sets`
- `simulation_scenarios`
- `simulation_runs`
- `run_artifacts`

Run lifecycle states:

- `draft`
- `queued`
- `running`
- `succeeded`
- `failed`
- `canceled`

What the worker does in the thin slice:

- receives a run job
- loads the scenario snapshot
- calls the simulation engine package
- stores structured output JSON
- writes one artifact to object storage
- updates run status and timestamps

What the simulation engine does in the thin slice:

- accepts the final run input schema
- returns deterministic placeholder output with the real result shape
- exposes `engine_version`
- writes no HTTP-specific code

Why this slice comes first:

- it proves auth, CRUD, async orchestration, auditability, object storage, and UI integration in one pass
- it exposes contract and data model mistakes early
- it keeps the scientific package isolated from the web stack from day one

## Milestone Breakdown By Phase

## Phase 0: Foundation And Scientific Contract Freeze

Target duration:

- Week 1

Goals:

- make the repo runnable
- establish local developer workflow
- freeze the first simulation input and output contracts
- put CI, logging, and environment management in place

Implementation tasks:

- bootstrap `apps/web`, `services/api`, `services/worker`, and `services/simulation-engine`
- choose root toolchain: `pnpm`, `turbo`, `uv`, `ruff`, `pytest`, `eslint`, `prettier`
- add Docker Compose for PostgreSQL, Redis, and local object storage
- add `.env.example` files for each service
- add health endpoints for API and worker
- define the first OpenAPI skeleton
- define the first simulation engine Python interface
- agree on run lifecycle status model
- create the initial database migration for core tables
- define role model and authorization policy boundaries
- add CI pipeline for lint, typecheck, unit tests, and migration validation

Acceptance criteria:

- a clean machine can bootstrap the repo using documented commands
- `apps/web`, `services/api`, `services/worker`, and `services/simulation-engine` all start locally
- Docker Compose starts PostgreSQL, Redis, and object storage without manual steps
- CI runs on pull requests
- the first database migration applies successfully
- OpenAPI spec is generated by the API service
- the simulation engine interface is documented and importable from the worker
- a short ADR exists for auth, queue, and artifact storage choices

## Phase 1: Thin Vertical Slice

Target duration:

- Week 2

Goals:

- prove the end-to-end run pipeline with real persistence and async execution

Implementation tasks:

- build minimal login and organization context
- add project, soil sample, food web, parameter set, and scenario creation APIs
- generate the TypeScript API client from OpenAPI
- build the project and scenario creation UI
- add `POST /runs` and `GET /runs/:id`
- implement worker queue consumption
- persist run input snapshot and engine version
- store one result artifact in object storage
- build the run detail page with status polling
- add one end-to-end test for submit-run-view-results

Acceptance criteria:

- a scientist can complete the thin-slice user story without admin intervention
- a submitted run moves through `queued`, `running`, and `succeeded`
- every run stores `input_snapshot`, `engine_version`, `submitted_by`, `submitted_at`, `started_at`, and `completed_at`
- the results page renders the returned result payload
- rerunning the same deterministic placeholder scenario produces the same stored result payload
- one end-to-end test passes in CI for the full slice

## Phase 2: Scientific Function V1 And Auditability Hardening

Target duration:

- Week 3 through Week 6

Goals:

- replace placeholder outputs with scientifically meaningful implementations
- make results reproducible and testable
- harden failure handling and observability

Implementation tasks:

- implement the five scientific modules in `services/simulation-engine`
- add reference fixtures and expected tolerance-based outputs
- version parameter sets and snapshot them into runs
- add retry-safe worker logic and idempotent job handling
- add structured run logs and trace correlation
- save raw output JSON and rendered summary artifact
- add failure reason capture and operator-visible diagnostics
- add contract tests between API and generated TypeScript client
- add API pagination and filtering for projects, scenarios, and runs
- add role enforcement across org-scoped resources

Acceptance criteria:

- all five scientific modules return outputs for at least one supported scenario shape
- golden tests pass against reference datasets within defined tolerances
- the worker can safely retry a failed job without duplicating final artifacts
- a failed run surfaces a human-readable failure reason
- all project, scenario, and run data is organization-scoped
- audit metadata can reconstruct how a run was produced

## Phase 3: MVP Beta Hardening

Target duration:

- Week 7 through Month 2

Goals:

- make the product usable by real pilot users
- ship the first premium public site and production-ready product shell

Implementation tasks:

- build polished marketing home page, science page, and lead capture path
- finish authenticated dashboard and run history views
- add a simple report export flow
- add saved results browsing and artifact downloads
- add admin-only internal support views for run inspection
- add baseline rate limiting and abuse protection
- add backups, migration rollback procedure, and operational runbooks
- add staging deployment and production deployment pipeline
- add error alerting and a small service dashboard
- run performance pass on public pages and core API endpoints

Acceptance criteria:

- pilot users can sign in, create projects, run simulations, and review results without developer assistance
- public marketing pages meet performance and SEO quality bar
- role-based access control works for viewer, scientist, and org admin paths
- staging and production deployments are automated
- on-call diagnostics can identify failed jobs and missing artifacts
- the team has a documented release checklist and rollback checklist

## Phase 4: Post-MVP Expansion

Target duration:

- after Month 2

Goals:

- increase scientific depth, collaboration, and enterprise readiness

Implementation candidates:

- graphical food web editor
- scenario comparison
- decomposition exploration tools
- batch job execution
- billing and quota management
- SSO and enterprise access controls
- richer report templates
- content team CMS
- advanced admin analytics

Acceptance criteria:

- each feature is tied to user demand, not technical curiosity
- no post-MVP feature regresses run reproducibility or org isolation

## Suggested Team Sequencing

## If 1 Developer

Sequence:

1. Phase 0 repo and infra
2. API schema and migrations
3. worker pipeline
4. thin-slice UI
5. simulation engine placeholder
6. science implementation
7. marketing polish

Operating rule:

Do not split focus across premium marketing polish and scientific depth in the same week. Prove the run pipeline first.

## If 2 Developers

Developer 1 owns:

- API
- database
- worker
- deployment
- RBAC
- observability

Developer 2 owns:

- Next.js app
- design system
- product shell
- thin-slice UI
- marketing shell
- generated client integration

Shared milestones:

- agree on OpenAPI changes daily
- ship the thin vertical slice by the end of Week 2
- start scientific engine implementation together only after the thin slice works end to end

## If 3 Developers

Developer 1 owns platform backend:

- FastAPI
- PostgreSQL schema
- queue orchestration
- RBAC
- observability

Developer 2 owns frontend:

- route groups
- dashboard
- scenario setup flows
- results UI
- design tokens
- marketing experience

Developer 3 owns science:

- simulation engine package
- reference fixtures
- performance profiling
- result validation
- report payload structures

Shared rule:

The science owner should not be pulled into general CRUD or UI work during the first three weeks. Protect that focus.

## Week-By-Week Deliverables

## Week 1 Deliverables

- root repo tooling committed
- local Docker stack for PostgreSQL, Redis, and object storage
- bootstrapped Next.js, FastAPI, worker, and simulation-engine packages
- base CI pipeline
- auth and RBAC decision documented
- initial Alembic migration for core entities
- initial OpenAPI skeleton
- initial design token package
- logging and request correlation strategy documented
- developer setup instructions working on a clean machine

## Week 2 Deliverables

- login flow and org context
- core CRUD for project, soil sample, food web, parameter set, and scenario
- generated TypeScript API client wired into web app
- `POST /runs` and `GET /runs/:id`
- worker consuming jobs from Redis
- deterministic placeholder simulation output
- run details page with status polling
- first end-to-end test covering submit-run-view-results

## Week 3 Deliverables

- first real scientific implementation in the engine package
- versioned parameter set snapshots in run records
- object storage artifact upload and download
- run retry and failure handling
- contract tests for client and API
- org-scoped authorization checks
- basic dashboard showing recent runs
- first polished public landing page shell

## Month 2 Deliverables

- all five core scientific functions implemented for at least one supported model shape
- validated fixture suite with tolerance-based assertions
- project, scenario, and run history screens production-usable
- simple report export available
- staging and production deployment pipeline
- alerting, dashboards, and operational runbooks
- viewer, scientist, and org admin roles enforced
- public marketing site ready for external traffic
- pilot-ready MVP released to a small user cohort

## Definition Of MVP

MVP includes:

- premium public website shell
- authentication and organization scoping
- projects, soil samples, food webs, parameter sets, and scenarios
- async simulation submission and run tracking
- the five core scientific functions in version 1 form
- persisted run history with audit metadata
- downloadable artifacts and one simple report/export path
- three baseline roles: viewer, scientist, org admin
- staging and production deployment with basic monitoring

MVP does not include:

- advanced graph editing
- scenario comparison dashboards
- team collaboration features
- billing
- enterprise SSO
- configurable report builder
- advanced CMS workflows

## Definition Of Post-MVP

Post-MVP starts when:

- pilot users can complete the end-to-end simulation workflow without developer help
- scientific outputs are validated against reference fixtures
- the platform has basic operational reliability in staging and production

Post-MVP priorities:

- richer modeling UX
- collaboration and review workflows
- enterprise controls
- advanced analysis tooling
- content operations tooling

## Exact Repo Setup Priorities

Implement these in order:

1. root metadata
2. local infra
3. shared developer commands
4. base apps and services
5. linting and formatting
6. test runners
7. CI
8. OpenAPI generation and client generation
9. database migrations and seeds
10. observability bootstrap

Concrete repo items to add first:

- root `package.json`
- `pnpm-workspace.yaml`
- `turbo.json`
- `.gitignore`
- `.editorconfig`
- `.nvmrc`
- `.python-version`
- root `Makefile` or `justfile`
- service-level `.env.example` files
- `infra/docker/compose.dev.yml`
- `apps/web/package.json`
- `services/api/pyproject.toml`
- `services/worker/pyproject.toml`
- `services/simulation-engine/pyproject.toml`
- `packages/config-eslint/*`
- `packages/config-typescript/*`
- `scripts/generate-api-client.sh` or equivalent package script
- GitHub Actions workflow for lint, test, typecheck, and build

Root command priorities:

- `dev:web`
- `dev:api`
- `dev:worker`
- `dev:stack`
- `lint`
- `typecheck`
- `test`
- `test:e2e`
- `gen:api-client`
- `db:migrate`
- `db:seed`

## Main Technical Risks And Mitigations

| Risk                                   | Why it matters                                                 | Mitigation                                                                                             |
| -------------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Scientific formulas are underspecified | Engineering can build the wrong system quickly                 | Freeze input/output contracts early and require reference fixtures before Phase 2                      |
| Reproducibility drift                  | Scientific trust collapses if reruns change unexpectedly       | Snapshot inputs, parameter versions, engine version, dependency versions, and timestamps for every run |
| Async job duplication                  | Retries can create duplicate artifacts and inconsistent states | Use idempotency keys, terminal-state guards, and artifact naming by run ID                             |
| API and frontend contract drift        | Polyglot monorepo can still diverge                            | Generate the TypeScript client from OpenAPI in CI and block drift                                      |
| RBAC holes across organizations        | Multi-tenant leaks are existential risk                        | Scope every query by organization and add authorization tests at API layer                             |
| Overbuilding the editor too early      | UI complexity can bury the core science                        | Start with forms and import flows before graph visualization                                           |
| Weak observability in async systems    | Background failures become invisible                           | Attach request ID, job ID, and run ID to logs and traces across services                               |
| Local dev setup becomes painful        | Team loses speed immediately                                   | Standardize one-command bootstrapping and a documented Docker-based stack                              |
| Artifact storage inconsistency         | Reports and outputs can be lost or orphaned                    | Store artifact metadata in DB and treat object storage writes as part of run finalization              |

## Phase Acceptance Checklist Summary

Use this as the release gate checklist at the end of each phase.

### Phase 0 Must Be True

- repo starts locally from documentation
- CI passes
- migrations work
- OpenAPI spec exists
- simulation engine interface exists
- queue and artifact storage choices are locked

### Phase 1 Must Be True

- end-to-end thin slice works
- run lifecycle is visible in UI
- audit metadata is stored on every run
- object storage round-trip works
- one end-to-end test passes in CI

### Phase 2 Must Be True

- all five science modules have first working implementations
- reference fixture tests pass
- retry handling is idempotent
- org-scoped authorization is enforced
- failures are diagnosable without reading raw infrastructure logs

### Phase 3 Must Be True

- pilot users can use the system unaided
- marketing site is publicly presentable
- production deployment is automated
- role enforcement is validated
- dashboards and alerts exist for core services

## Immediate Next Actions

Start with these exact steps:

1. create repo bootstrap files and local Docker stack
2. scaffold `apps/web`, `services/api`, `services/worker`, and `services/simulation-engine`
3. define the first simulation input schema, result schema, and run status model
4. create the initial Alembic migration for organizations through simulation runs
5. implement the thin-slice `POST /runs` to worker to `GET /runs/:id` flow before any advanced UI work
