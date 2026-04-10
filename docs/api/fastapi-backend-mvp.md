# FastAPI Backend Architecture And MVP Endpoint Plan

## Purpose

This document defines the initial FastAPI backend architecture for the Bio Soil platform and aligns it with the repository scaffold in `services/api`.

It covers:

1. route grouping and versioning
2. service and repository layering
3. Pydantic schema conventions
4. initial MVP endpoint set
5. run lifecycle and state transitions
6. error handling conventions
7. auth and RBAC integration
8. OpenAPI practices for frontend code generation
9. test strategy
10. starter module layout

## Architecture Overview

The FastAPI service should own:

- authentication and authorization enforcement
- request validation
- business rules for projects, samples, scenarios, runs, and reports
- database transaction boundaries
- queue submission for async runs
- result retrieval and artifact metadata access
- audit metadata and operational diagnostics
- OpenAPI generation for the frontend client

It should not own:

- heavy scientific computation
- long-running run execution
- direct browser UI concerns

That work belongs to the worker and simulation engine.

## Layering

Use this request path:

```text
route -> dependency injection -> service -> repository/adapters -> database/queue/storage
```

### Route Layer

Responsibilities:

- parse request bodies and path/query params
- enforce auth dependencies
- select the service method
- declare response models and status codes

Routes should not contain:

- SQLAlchemy queries
- orchestration logic
- run lifecycle rules

### Service Layer

Responsibilities:

- business validation
- organization scoping rules
- cross-entity checks
- run submission orchestration
- audit field handling
- mapping repository results into API responses

Examples:

- verify a project belongs to the current organization
- verify a scenario references resources in the same project
- generate run snapshots and idempotency keys
- enforce valid run status transitions

### Repository Layer

Responsibilities:

- SQLAlchemy queries
- row loading and persistence
- pagination queries
- organization-scoped filtering
- transaction-safe updates

Rules:

- repositories never raise `HTTPException`
- repositories return domain records or `None`
- services translate missing or invalid states into `AppError`

### Adapter Layer

Adapters are not fully scaffolded yet, but the API should eventually isolate:

- queue access
- object storage access
- auth provider access
- observability emitters

## Route Grouping And Versioning Strategy

### Versioning

Use URI versioning:

- `/api/v1/...`

Rules:

- all public frontend-facing endpoints live under `/api/v1`
- breaking changes require `/api/v2`
- additive fields are allowed within `v1`
- operation IDs must remain stable once frontend codegen depends on them

### Route Groups

MVP groups:

- `auth`
- `projects`
- `soil-samples`
- `scenarios`
- `runs`

Near-term group:

- `reports`

Current scaffold:

- [main.py](/Users/mobashirsifat/Desktop/bio_lab/services/api/app/main.py)
- [router.py](/Users/mobashirsifat/Desktop/bio_lab/services/api/app/api/v1/router.py)
- [auth.py](/Users/mobashirsifat/Desktop/bio_lab/services/api/app/api/v1/routes/auth.py)
- [projects.py](/Users/mobashirsifat/Desktop/bio_lab/services/api/app/api/v1/routes/projects.py)
- [soil_samples.py](/Users/mobashirsifat/Desktop/bio_lab/services/api/app/api/v1/routes/soil_samples.py)
- [scenarios.py](/Users/mobashirsifat/Desktop/bio_lab/services/api/app/api/v1/routes/scenarios.py)
- [runs.py](/Users/mobashirsifat/Desktop/bio_lab/services/api/app/api/v1/routes/runs.py)

## File Structure For `services/api`

```text
services/api/
├── pyproject.toml
├── .env.example
└── app/
    ├── main.py
    ├── api/
    │   ├── dependencies/
    │   │   ├── auth.py
    │   │   ├── db.py
    │   │   └── services.py
    │   └── v1/
    │       ├── router.py
    │       └── routes/
    │           ├── auth.py
    │           ├── projects.py
    │           ├── soil_samples.py
    │           ├── scenarios.py
    │           └── runs.py
    ├── core/
    │   ├── config.py
    │   ├── errors.py
    │   └── logging.py
    ├── db/
    │   └── session.py
    ├── domain/
    │   ├── enums.py
    │   ├── permissions.py
    │   └── run_lifecycle.py
    ├── repositories/
    │   ├── project_repository.py
    │   ├── soil_sample_repository.py
    │   ├── scenario_repository.py
    │   └── run_repository.py
    ├── schemas/
    │   ├── common.py
    │   ├── error.py
    │   ├── auth.py
    │   ├── project.py
    │   ├── soil_sample.py
    │   ├── scenario.py
    │   └── run.py
    └── services/
        ├── auth_service.py
        ├── project_service.py
        ├── soil_sample_service.py
        ├── scenario_service.py
        └── run_service.py
```

## Pydantic Schema Design

### External Naming

Use camelCase in the external API.

Reason:

- friendlier generated TypeScript
- consistent with frontend conventions

Implementation:

- [common.py](/Users/mobashirsifat/Desktop/bio_lab/services/api/app/schemas/common.py) defines `ApiModel` with an alias generator

### Schema Categories

For each resource, define:

- `Create` request schema
- `Update` request schema where mutation is allowed
- `Detail` response schema
- `ListResponse` schema

Current examples:

- [project.py](/Users/mobashirsifat/Desktop/bio_lab/services/api/app/schemas/project.py)
- [soil_sample.py](/Users/mobashirsifat/Desktop/bio_lab/services/api/app/schemas/soil_sample.py)
- [scenario.py](/Users/mobashirsifat/Desktop/bio_lab/services/api/app/schemas/scenario.py)
- [run.py](/Users/mobashirsifat/Desktop/bio_lab/services/api/app/schemas/run.py)

### Validation Rules

Put syntactic validation in Pydantic:

- field length
- required fields
- basic enum constraints
- shape of request JSON

Put business validation in services:

- same-organization checks
- project ownership checks
- immutable versioning rules
- run transition rules
- idempotency behavior

## Initial MVP Endpoint Set

### Auth

- `GET /api/v1/auth/session`

Purpose:

- returns the caller identity, active organization, roles, and permissions
- useful for app bootstrapping and layout gating

### Projects

- `GET /api/v1/projects`
- `POST /api/v1/projects`
- `GET /api/v1/projects/{projectId}`
- `PATCH /api/v1/projects/{projectId}`
- `DELETE /api/v1/projects/{projectId}`

### Soil Samples

- `GET /api/v1/projects/{projectId}/soil-samples`
- `POST /api/v1/projects/{projectId}/soil-samples`
- `GET /api/v1/soil-samples/{soilSampleId}`
- `PATCH /api/v1/soil-samples/{soilSampleId}`
- `DELETE /api/v1/soil-samples/{soilSampleId}`

### Scenarios

- `GET /api/v1/projects/{projectId}/scenarios`
- `POST /api/v1/projects/{projectId}/scenarios`
- `GET /api/v1/scenarios/{scenarioId}`
- `PATCH /api/v1/scenarios/{scenarioId}`

Important:

The `PATCH` route is for metadata only in MVP. Scientific content updates should create a new version later instead of mutating the original scenario record in place.

### Runs

- `POST /api/v1/runs`
- `GET /api/v1/runs/{runId}`
- `GET /api/v1/runs/{runId}/status`
- `GET /api/v1/runs/{runId}/results`

### Reports

Not scaffolded yet in code, but the next wave should add:

- `GET /api/v1/projects/{projectId}/reports`
- `POST /api/v1/reports`
- `GET /api/v1/reports/{reportId}`
- `GET /api/v1/reports/{reportId}/download`

## Example Endpoint Conventions

### Create A Run

Request:

```json
{
  "scenarioId": "0195f3e4-4a86-7d13-bb2a-d5428b76f7f0",
  "idempotencyKey": "proj-123-scenario-4-run-1",
  "executionOptions": {
    "priority": "normal"
  }
}
```

Response:

- `202 Accepted`

Body:

```json
{
  "id": "0195f3e4-4b9c-7f76-ae9d-c0df2b238f4a",
  "organizationId": "0195f3e4-4a86-7d13-bb2a-d5428b76f010",
  "projectId": "0195f3e4-4a86-7d13-bb2a-d5428b76f020",
  "scenarioId": "0195f3e4-4a86-7d13-bb2a-d5428b76f7f0",
  "status": "queued",
  "engineName": "soil-engine",
  "engineVersion": "0.1.0",
  "inputSchemaVersion": "1.0",
  "inputHash": "abc123...",
  "createdAt": "2026-03-31T12:00:00Z",
  "updatedAt": "2026-03-31T12:00:00Z"
}
```

### Get Run Status

Response:

```json
{
  "id": "0195f3e4-4b9c-7f76-ae9d-c0df2b238f4a",
  "status": "running",
  "queuedAt": "2026-03-31T12:00:00Z",
  "startedAt": "2026-03-31T12:00:05Z",
  "completedAt": null,
  "canceledAt": null,
  "failureCode": null,
  "failureMessage": null
}
```

## Run Lifecycle And State Machine

Current enum:

- `draft`
- `queued`
- `running`
- `succeeded`
- `failed`
- `cancel_requested`
- `canceled`

Current transition table is scaffolded in:

- [run_lifecycle.py](/Users/mobashirsifat/Desktop/bio_lab/services/api/app/domain/run_lifecycle.py)

Allowed transitions:

```text
draft -> queued, canceled
queued -> running, failed, cancel_requested, canceled
running -> succeeded, failed, cancel_requested, canceled
cancel_requested -> canceled, failed
succeeded -> terminal
failed -> terminal
canceled -> terminal
```

Rules:

- only the API may create a run record
- only the worker should move a run from `queued` to `running` or terminal states
- terminal runs should not transition again
- every transition should update the matching lifecycle timestamp

## Error Model Conventions

Use one envelope everywhere:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed.",
    "details": {},
    "issues": [
      {
        "field": "body.name",
        "message": "String should have at least 3 characters",
        "type": "string_too_short"
      }
    ]
  },
  "requestId": "..."
}
```

Implementation:

- [errors.py](/Users/mobashirsifat/Desktop/bio_lab/services/api/app/core/errors.py)
- [error.py](/Users/mobashirsifat/Desktop/bio_lab/services/api/app/schemas/error.py)

Rules:

- services raise `AppError`
- routes never raise raw `HTTPException` for business cases
- validation errors are translated centrally
- every response should carry `x-request-id`

Suggested codes:

- `auth_required`
- `permission_denied`
- `resource_not_found`
- `validation_error`
- `run_state_conflict`
- `idempotency_conflict`
- `internal_server_error`

## Auth And RBAC Integration Points

Current placeholder:

- [auth.py](/Users/mobashirsifat/Desktop/bio_lab/services/api/app/api/dependencies/auth.py)

What it does now:

- reads dev headers such as `x-user-id`, `x-organization-id`, `x-roles`, and `x-permissions`
- provides `get_current_user`
- provides `require_permission(permission)`

What to replace later:

- JWT/session validation against the chosen auth provider
- organization membership lookup
- role resolution from the database
- permission expansion from roles

Recommended integration shape:

1. auth adapter validates token
2. dependency resolves user and active organization membership
3. role/permission loader materializes effective permissions
4. `require_permission` enforces route-level access
5. services still perform organization-scoped entity checks

Important:

Route permission checks are necessary but not sufficient. Services and repositories still need organization-scoped filtering.

## OpenAPI Design Recommendations

Use these rules so code generation stays clean:

1. set explicit `operation_id` on every route
2. use stable route tags
3. always declare `response_model`
4. avoid ambiguous unions in response bodies
5. use explicit request and response schemas instead of anonymous dicts
6. prefer separate list response types over generic wrappers if codegen gets noisy
7. keep field names stable once generated clients ship
8. expose enums explicitly
9. include request examples for complex scientific payloads later
10. keep nullable fields explicit

Current examples:

- [projects.py](/Users/mobashirsifat/Desktop/bio_lab/services/api/app/api/v1/routes/projects.py)
- [runs.py](/Users/mobashirsifat/Desktop/bio_lab/services/api/app/api/v1/routes/runs.py)

Frontend codegen implications:

- generated TypeScript should come from `/openapi.json`
- app code should consume only the generated client package
- avoid hand-written duplicate request types in the frontend

## Dependency Injection Conventions

Use three dependency layers:

### Infrastructure Dependencies

- DB session
- queue clients later
- storage clients later

### Caller Context Dependencies

- current user
- required permission
- request ID

### Service Constructor Dependencies

- `get_project_service`
- `get_soil_sample_service`
- `get_scenario_service`
- `get_run_service`

Current implementation:

- [db.py](/Users/mobashirsifat/Desktop/bio_lab/services/api/app/api/dependencies/db.py)
- [services.py](/Users/mobashirsifat/Desktop/bio_lab/services/api/app/api/dependencies/services.py)

Rule:

Construct services in DI helpers, not inside route functions.

## Validation Conventions

### Pydantic

Use Pydantic for:

- body shape
- field length
- type coercion
- enum constraints

### Service Validation

Use services for:

- ownership checks
- state machine checks
- idempotency checks
- cross-resource consistency
- run reproducibility rules

### Repository Validation

Repositories should only guarantee:

- correct query shape
- correct organization scoping
- correct persistence mechanics

## Starter Code Skeletons In Repo

Key files now present:

- [pyproject.toml](/Users/mobashirsifat/Desktop/bio_lab/services/api/pyproject.toml)
- [main.py](/Users/mobashirsifat/Desktop/bio_lab/services/api/app/main.py)
- [config.py](/Users/mobashirsifat/Desktop/bio_lab/services/api/app/core/config.py)
- [errors.py](/Users/mobashirsifat/Desktop/bio_lab/services/api/app/core/errors.py)
- [auth.py](/Users/mobashirsifat/Desktop/bio_lab/services/api/app/api/dependencies/auth.py)
- [project_service.py](/Users/mobashirsifat/Desktop/bio_lab/services/api/app/services/project_service.py)
- [project_repository.py](/Users/mobashirsifat/Desktop/bio_lab/services/api/app/repositories/project_repository.py)
- [project.py](/Users/mobashirsifat/Desktop/bio_lab/services/api/app/schemas/project.py)

Important note:

Most service and repository methods are still explicit skeletons that return `501 not implemented` via `AppError`. That is intentional. The structure is now in place; the next step is wiring models, repositories, and actual business logic.

## Test Strategy

### Unit Tests

Target:

- service methods
- state transition helpers
- schema validation edge cases

Mock:

- repositories
- queue adapters
- storage adapters

### Repository Integration Tests

Target:

- SQLAlchemy queries
- organization scoping
- pagination behavior
- soft delete filtering

Use:

- ephemeral Postgres test database

### API Integration Tests

Target:

- route contracts
- status codes
- auth dependency behavior
- error envelope shape

Use:

- FastAPI `TestClient`
- seeded organization and membership fixtures

### Contract Tests

Target:

- OpenAPI stability
- generated TypeScript client compatibility

Rules:

- fail CI if the committed generated client is out of sync with OpenAPI
- add one smoke test using the generated client against a live test API

### End-To-End Tests

Target:

- login/session bootstrap
- create project
- create sample
- create scenario
- submit run
- poll run status
- open results page

Browser tests belong in the web app, but they depend on these API contracts staying stable.

## What To Implement Next

Build in this order:

1. SQLAlchemy models from the domain spec
2. Alembic base migration
3. repository implementations for projects, soil samples, scenarios, and runs
4. queue adapter for run submission
5. service-layer business rules
6. report routes after run artifacts are real

The highest-priority real endpoint is:

- `POST /api/v1/runs`

Reason:

It forces the API to prove auth, project/scenario ownership, input snapshot generation, audit metadata capture, and async orchestration.
