# First Thin Vertical Slice Blueprint

## Goal

Deliver the first end-to-end product slice:

1. create project
2. add soil sample
3. create simulation scenario
4. submit simulation run
5. background worker processes placeholder simulation
6. run status updates from `queued` to `running` to terminal
7. results page shows run metadata, provenance, and placeholder output

This slice is intentionally narrow. It proves the system architecture, not the full scientific product surface.

## User Story

A signed-in scientist can:

- create a project
- add a soil sample to that project
- create a baseline scenario by supplying:
  - scenario metadata
  - a simple food web definition
  - a parameter set
- submit a run for that scenario
- open the run page and see live status updates
- view result summary, provenance, and artifact references after completion

## Product Scope Decisions

### Included In This Slice

- authenticated platform routes only
- one organization context
- one role with write access, using the existing debug auth placeholder for local development
- form-based data entry
- polling for run status
- mock or local-file artifact storage adapter
- deterministic placeholder simulation engine output

### Deliberately Excluded

- public marketing pages
- visual graph editor
- scenario comparison
- report generation UI
- websockets
- billing
- multi-org switching UI

## Architectural Shortcut For This Slice

To keep the user flow to four steps, the scenario creation request will accept the food web and parameter set inline.

Backend behavior:

- the API will create:
  - one versioned `food_web_definition`
  - one versioned `parameter_set`
  - one versioned `simulation_scenario`
- the frontend treats this as one “Create Scenario” step

Why:

- preserves the domain model
- reduces UI complexity
- avoids blocking the first slice on separate food web and parameter set management pages

Later, these can be split into explicit first-class CRUD surfaces without changing the run pipeline.

## End-To-End Component Map

```text
Next.js page/forms
  -> generated TS API client
  -> FastAPI endpoints
  -> PostgreSQL tables
  -> Redis job enqueue
  -> worker consumes job
  -> simulation-engine placeholder run
  -> mock artifact store writes result JSON
  -> worker updates run + artifact rows
  -> FastAPI returns status/results
  -> Next.js run page polls and renders output
```

## Components Required

## Frontend

- auth/session bootstrap
- project creation page
- soil sample creation page
- scenario creation page with embedded food web and parameter set form blocks
- run detail page with polling
- shared form components
- mutation hooks and loading/error state handling
- generated API client wiring

## Backend API

- debug auth/session endpoint
- project CRUD
- soil sample CRUD
- scenario creation and retrieval
- run submission
- run detail
- run status
- run results
- OpenAPI schema generation

## Database

- organizations
- users
- organization_memberships
- roles
- permissions
- role_permissions
- organization_membership_roles
- projects
- soil_samples
- food_web_definitions
- parameter_sets
- simulation_scenarios
- simulation_runs
- run_artifacts

## Worker

- Redis queue consumer
- run state lease acquisition
- simulation subprocess execution
- result artifact write
- retry and failure handling

## Simulation Engine

- deterministic request validation
- placeholder scientific calculations
- JSON result output with provenance

## Storage

For this slice, use a mock artifact store adapter:

- `storage_provider = "mock"`
- `storage_bucket = "local-dev"`
- `storage_key = "runs/{run_id}/result.json"`

Implementation options:

- local filesystem under `/tmp/bio_lab_artifacts`
- repo-local dev storage directory under `infra/docker/volumes/artifacts`

Use the same storage adapter contract that production object storage will use later.

## Backend Responsibilities By Layer

## API

- validate organization access
- create project, sample, and scenario records
- build run input snapshot from stored entities
- compute `input_hash`
- create `simulation_runs` row
- enqueue Redis job
- expose stable OpenAPI contract

## Worker

- consume simulation job
- load authoritative run snapshot from DB
- move run status to `running`
- call the simulation engine CLI or in-process `run()`
- write result artifact
- update `simulation_runs` and `run_artifacts`
- handle retryable and terminal failures

## Simulation Engine

- validate scientific request shape
- compute deterministic placeholder outputs
- return provenance and stable result hashes

## Frontend Responsibilities

## Pages

### `/login`

Purpose:

- local/dev auth entry point or redirect stub

State:

- if debug auth is enabled, auto-continue into platform

### `/(platform)/projects/new`

Purpose:

- create a project

Fields:

- `name`
- `slug` optional
- `description`

Success:

- redirect to `/projects/{projectId}`

### `/(platform)/projects/[projectId]`

Purpose:

- show project summary
- show latest sample and scenario if present
- show “Add Soil Sample” and “Create Scenario” actions

Sections:

- project header
- recent soil samples
- recent scenarios
- recent runs

### `/(platform)/projects/[projectId]/samples/new`

Purpose:

- create a soil sample

Fields:

- `sampleCode`
- `name`
- `description`
- `collectedOn`
- `location` JSON textarea or structured small fields
- `measurements` JSON textarea or structured key-value fields

Success:

- redirect back to project page

### `/(platform)/projects/[projectId]/scenarios/new`

Purpose:

- create scenario plus embedded food web and parameter set

Sections:

- scenario metadata
- soil sample selector
- food web definition JSON or small structured editor
- parameter set JSON or key-value fields

Minimum fields:

- `scenario.name`
- `scenario.description`
- `soilSampleId`
- `foodWeb.name`
- `foodWeb.nodes[]`
- `foodWeb.links[]`
- `parameterSet.name`
- `parameterSet.parameters`
- `scenario.configuration`

Success:

- redirect to scenario detail or back to project page with a “Run Scenario” call to action

### `/(platform)/runs/[runId]`

Purpose:

- show run lifecycle state
- poll status every 2 to 3 seconds until terminal
- show result summary and provenance
- show artifact list

Sections:

- status badge and timestamps
- provenance metadata
- summary metrics
- module result blocks
- artifacts

## Frontend Components

Required components:

- `ProjectForm`
- `SoilSampleForm`
- `ScenarioForm`
- `FoodWebEditorLite`
- `ParameterSetEditorLite`
- `RunStatusBadge`
- `RunTimeline`
- `RunResultsPanel`
- `AsyncStatePanel`

## Frontend Loading, Error, And Success States

### Project Create

- loading: disable submit, show inline spinner
- error: inline field errors plus top-level form error
- success: redirect to project page

### Soil Sample Create

- loading: disable submit
- error: validation errors near fields
- success: toast plus redirect

### Scenario Create

- loading: disable submit
- error: field-level plus JSON parsing error block if using JSON inputs
- success: redirect to project page or new scenario page

### Run Submit

- loading: button shows “Submitting run...”
- error: toast or callout with retry action
- success: redirect immediately to `/runs/{runId}`

### Run Detail

- `queued`: show pending state and submitted timestamp
- `running`: show active spinner and started timestamp
- `succeeded`: render result panels
- `failed`: render failure code/message and diagnostic artifact links

## Backend Endpoints For This Slice

Use `/api/v1`.

## Auth

- `GET /api/v1/auth/session`

## Projects

- `POST /api/v1/projects`
- `GET /api/v1/projects/{projectId}`
- `GET /api/v1/projects`

## Soil Samples

- `POST /api/v1/projects/{projectId}/soil-samples`
- `GET /api/v1/projects/{projectId}/soil-samples`
- `GET /api/v1/soil-samples/{soilSampleId}`

## Scenarios

- `POST /api/v1/projects/{projectId}/scenarios`
- `GET /api/v1/projects/{projectId}/scenarios`
- `GET /api/v1/scenarios/{scenarioId}`

## Runs

- `POST /api/v1/runs`
- `GET /api/v1/runs/{runId}`
- `GET /api/v1/runs/{runId}/status`
- `GET /api/v1/runs/{runId}/results`

## API Schema Design For This Slice

## `POST /api/v1/projects`

Request:

```json
{
  "name": "Spring Trial",
  "slug": "spring-trial",
  "description": "Baseline soil food web analysis for pilot site.",
  "metadata": {}
}
```

Response `201`:

```json
{
  "id": "00000000-0000-7000-0000-000000000201",
  "organizationId": "00000000-0000-7000-0000-000000000101",
  "name": "Spring Trial",
  "slug": "spring-trial",
  "description": "Baseline soil food web analysis for pilot site.",
  "status": "active",
  "metadata": {},
  "createdAt": "2026-03-31T10:00:00Z",
  "updatedAt": "2026-03-31T10:00:00Z"
}
```

## `POST /api/v1/projects/{projectId}/soil-samples`

Request:

```json
{
  "sampleCode": "SPR-001",
  "name": "North Plot Sample",
  "description": "Composite sample from north plot.",
  "collectedOn": "2026-03-31",
  "location": {
    "field": "North Plot",
    "latitude": 23.129,
    "longitude": 113.264
  },
  "measurements": {
    "ph": 6.5,
    "moisture": 0.31,
    "organicMatter": 4.2
  },
  "metadata": {}
}
```

Response `201`:

```json
{
  "id": "00000000-0000-7000-0000-000000000301",
  "organizationId": "00000000-0000-7000-0000-000000000101",
  "projectId": "00000000-0000-7000-0000-000000000201",
  "sampleCode": "SPR-001",
  "name": "North Plot Sample",
  "description": "Composite sample from north plot.",
  "collectedOn": "2026-03-31",
  "location": {
    "field": "North Plot",
    "latitude": 23.129,
    "longitude": 113.264
  },
  "measurements": {
    "ph": 6.5,
    "moisture": 0.31,
    "organicMatter": 4.2
  },
  "metadata": {},
  "createdAt": "2026-03-31T10:05:00Z",
  "updatedAt": "2026-03-31T10:05:00Z"
}
```

## `POST /api/v1/projects/{projectId}/scenarios`

Thin-slice request shape:

```json
{
  "scenario": {
    "name": "Baseline Scenario",
    "description": "Initial placeholder run for the north plot.",
    "soilSampleId": "00000000-0000-7000-0000-000000000301",
    "configuration": {
      "timeHorizonDays": 30,
      "timeSteps": 5,
      "decompositionDays": 21
    }
  },
  "foodWeb": {
    "name": "Baseline Food Web",
    "nodes": [
      {
        "key": "detritus",
        "label": "Detritus",
        "trophicGroup": "detritus",
        "biomassCarbon": 14.0,
        "biomassNitrogen": 3.0,
        "isDetritus": true
      },
      {
        "key": "fungi",
        "label": "Fungi",
        "trophicGroup": "fungus",
        "biomassCarbon": 5.0,
        "biomassNitrogen": 1.2
      }
    ],
    "links": [
      {
        "source": "detritus",
        "target": "fungi",
        "weight": 0.7
      }
    ]
  },
  "parameterSet": {
    "name": "Baseline Parameters",
    "parameters": {
      "dynamicDecayFactor": 0.018,
      "decompositionConstant": 0.024,
      "initialDetritusCarbon": 14.0
    }
  }
}
```

Response `201`:

```json
{
  "id": "00000000-0000-7000-0000-000000000401",
  "organizationId": "00000000-0000-7000-0000-000000000101",
  "projectId": "00000000-0000-7000-0000-000000000201",
  "stableKey": "00000000-0000-7000-0000-000000000402",
  "version": 1,
  "name": "Baseline Scenario",
  "description": "Initial placeholder run for the north plot.",
  "soilSampleId": "00000000-0000-7000-0000-000000000301",
  "foodWebDefinitionId": "00000000-0000-7000-0000-000000000403",
  "parameterSetId": "00000000-0000-7000-0000-000000000404",
  "scenarioConfig": {
    "timeHorizonDays": 30,
    "timeSteps": 5,
    "decompositionDays": 21
  },
  "createdAt": "2026-03-31T10:10:00Z"
}
```

## `POST /api/v1/runs`

Request:

```json
{
  "scenarioId": "00000000-0000-7000-0000-000000000401",
  "idempotencyKey": "spring-trial-baseline-run-1",
  "executionOptions": {
    "priority": "normal"
  }
}
```

Response `202`:

```json
{
  "id": "00000000-0000-7000-0000-000000000501",
  "organizationId": "00000000-0000-7000-0000-000000000101",
  "projectId": "00000000-0000-7000-0000-000000000201",
  "scenarioId": "00000000-0000-7000-0000-000000000401",
  "status": "queued",
  "engineName": "soil-engine",
  "engineVersion": "0.1.0",
  "inputSchemaVersion": "1.0.0",
  "inputHash": "abc123...",
  "resultHash": null,
  "queuedAt": "2026-03-31T10:15:00Z",
  "startedAt": null,
  "completedAt": null,
  "canceledAt": null,
  "failureCode": null,
  "failureMessage": null,
  "createdAt": "2026-03-31T10:15:00Z",
  "updatedAt": "2026-03-31T10:15:00Z"
}
```

## `GET /api/v1/runs/{runId}/status`

Response while running:

```json
{
  "id": "00000000-0000-7000-0000-000000000501",
  "status": "running",
  "queuedAt": "2026-03-31T10:15:00Z",
  "startedAt": "2026-03-31T10:15:02Z",
  "completedAt": null,
  "canceledAt": null,
  "failureCode": null,
  "failureMessage": null
}
```

## `GET /api/v1/runs/{runId}/results`

Response on success:

```json
{
  "id": "00000000-0000-7000-0000-000000000501",
  "status": "succeeded",
  "engineName": "soil-engine",
  "engineVersion": "0.1.0",
  "inputSnapshot": {
    "inputSchemaVersion": "1.0.0",
    "foodWeb": {
      "nodes": [],
      "links": []
    },
    "soilSample": {},
    "parameterSet": {},
    "scenario": {},
    "execution": {
      "deterministic": true,
      "randomSeed": 0
    }
  },
  "resultSummary": {
    "provenance": {
      "engineName": "soil-engine",
      "engineVersion": "0.1.0",
      "inputSchemaVersion": "1.0.0",
      "parameterSetVersion": 1,
      "deterministic": true,
      "randomSeed": 0,
      "inputHash": "abc123...",
      "resultHash": "def456...",
      "placeholder": true
    },
    "summary": {
      "nodeCount": 2,
      "linkCount": 1,
      "requestedModules": ["flux", "mineralization", "stability", "dynamics", "decomposition"],
      "warnings": []
    },
    "flux": {
      "totalCarbonFlux": 0.098
    },
    "mineralization": {
      "totalCarbonMineralization": 0.098
    },
    "stability": {
      "stable": true,
      "smin": 0.475
    },
    "dynamics": {
      "stepCount": 5
    },
    "decomposition": {
      "decompositionConstant": 0.024
    }
  },
  "artifacts": [
    {
      "id": "00000000-0000-7000-0000-000000000601",
      "artifactType": "result_json",
      "label": "Full Result JSON",
      "contentType": "application/json",
      "storageKey": "runs/00000000-0000-7000-0000-000000000501/result.json",
      "byteSize": 4096,
      "checksumSha256": "fedcba...",
      "metadata": {
        "storageProvider": "mock"
      },
      "createdAt": "2026-03-31T10:15:07Z"
    }
  ]
}
```

## Backend Schemas Needed

## API Request Schemas

- `ProjectCreate`
- `SoilSampleCreate`
- `ScenarioCreateThinSlice`
- `FoodWebCreateInline`
- `ParameterSetCreateInline`
- `RunCreate`

## API Response Schemas

- `ProjectDetail`
- `SoilSampleDetail`
- `ScenarioDetail`
- `RunDetail`
- `RunStatusResponse`
- `RunResultsResponse`
- `RunArtifact`

## Database Tables Required

## Core Tenant/Auth

- `organizations`
- `users`
- `organization_memberships`
- `roles`
- `permissions`
- `role_permissions`
- `organization_membership_roles`

## Slice Business Tables

- `projects`
- `soil_samples`
- `food_web_definitions`
- `parameter_sets`
- `simulation_scenarios`
- `simulation_runs`
- `run_artifacts`

## Slice-Critical Columns

### `simulation_runs`

Required columns:

- `id`
- `organization_id`
- `project_id`
- `scenario_id`
- `soil_sample_id`
- `food_web_definition_id`
- `parameter_set_id`
- `status`
- `submitted_by_user_id`
- `engine_name`
- `engine_version`
- `input_schema_version`
- `idempotency_key`
- `input_hash`
- `result_hash`
- `input_snapshot_json`
- `result_summary_json`
- `failure_code`
- `failure_message`
- `failure_details_json`
- `queued_at`
- `started_at`
- `completed_at`
- `created_at`
- `updated_at`

### `run_artifacts`

Required columns:

- `id`
- `organization_id`
- `project_id`
- `simulation_run_id`
- `artifact_type`
- `label`
- `storage_provider`
- `storage_bucket`
- `storage_key`
- `content_type`
- `byte_size`
- `checksum_sha256`
- `metadata_json`
- `created_at`

## Worker Job Payload And Flow

## Queue Payload

Use the existing `simulation.run.execute` job type.

Example envelope:

```json
{
  "jobId": "00000000-0000-7000-0000-000000000701",
  "jobType": "simulation.run.execute",
  "schemaVersion": "1.0",
  "queueName": "jobs:simulation",
  "priority": "normal",
  "enqueuedAt": "2026-03-31T10:15:00Z",
  "payload": {
    "jobType": "simulation.run.execute",
    "organizationId": "00000000-0000-7000-0000-000000000101",
    "projectId": "00000000-0000-7000-0000-000000000201",
    "initiatedByUserId": "00000000-0000-7000-0000-000000000001",
    "runId": "00000000-0000-7000-0000-000000000501",
    "scenarioId": "00000000-0000-7000-0000-000000000401",
    "engineName": "soil-engine",
    "engineVersion": "0.1.0",
    "inputSchemaVersion": "1.0.0",
    "attempt": 1,
    "maxAttempts": 3,
    "timeoutSeconds": 1800,
    "idempotencyKey": "spring-trial-baseline-run-1",
    "inputHash": "abc123...",
    "executionOptions": {
      "priority": "normal"
    }
  }
}
```

## Worker Processing Flow

1. reserve job from Redis
2. fetch `simulation_runs` row by `run_id`
3. if run is terminal, ack and exit
4. transition `queued -> running`, set `started_at`
5. load authoritative `input_snapshot_json`
6. write snapshot to temp file
7. execute `python -m soil_engine.cli run --input ... --output ...`
8. read result JSON from temp output file
9. write artifact to mock storage
10. insert `run_artifacts` row
11. update `simulation_runs.result_summary_json`, `result_hash`, `status = succeeded`, `completed_at`
12. ack queue message

On failure:

- retry transient failures up to max attempts
- mark `failed` with `failure_code` and `failure_message` for terminal failures

## Simulation Engine Placeholder Behavior For This Slice

Use the current placeholder engine behavior:

- deterministic output
- fixed execution order:
  - flux
  - mineralization
  - stability
  - dynamics
  - decomposition
- output includes:
  - provenance
  - summary
  - placeholder module outputs
  - diagnostics

The engine must:

- read pure input snapshot JSON
- emit stable JSON output
- include `engineVersion`, `inputHash`, `resultHash`, and `placeholder = true`

## Result Rendering On Frontend

The results page should render:

- `status`
- `queuedAt`, `startedAt`, `completedAt`
- `engineName`, `engineVersion`, `inputSchemaVersion`
- `inputHash`, `resultHash`
- summary card with node count, link count, requested modules
- result cards:
  - flux
  - mineralization
  - stability
  - dynamics
  - decomposition
- artifact list

## Loading, Error, And Success States

## API-Level Conventions

- all errors use the standard error envelope
- validation errors return `422`
- missing resources return `404`
- forbidden access returns `403`
- run conflicts return `409`

## Web-Level States

### General

- show inline form validation
- show mutation pending state per button
- preserve entered values on failure

### Results Polling

- start polling immediately after redirect to run page
- poll every `2s`
- stop polling on terminal state
- if polling fails temporarily, show non-blocking warning and continue retrying

### Empty States

- project page with no samples: show “Add Soil Sample”
- project page with no scenarios: show “Create Scenario”
- run page before results: show status timeline

## Test Coverage Needed

## Backend Unit Tests

- project service create/get
- soil sample service create/get
- scenario create service:
  - creates food web definition
  - creates parameter set
  - creates scenario
- run service:
  - builds input snapshot
  - computes input hash
  - creates queued run
- run lifecycle transitions

## Repository Integration Tests

- organization scoping on all queries
- unique slug/sample code/idempotency constraints
- scenario references valid sample/food web/parameter set
- run artifact insert and run update

## Worker Tests

- payload parsing
- job consumes and marks `running`
- successful execution marks `succeeded`
- retryable failure schedules retry
- terminal failure marks `failed`
- terminal run is not reprocessed

## Simulation Engine Tests

- placeholder engine returns all module outputs
- identical input gives identical `input_hash` and `result_hash`
- fixture-based regression test for stable output

## Frontend Unit/Integration Tests

- project form submit and redirect
- soil sample form validation
- scenario form serializes nested food web and parameter set
- run page polls until terminal
- result cards render placeholder output correctly

## End-To-End Test

Critical flow:

1. login/session bootstrap
2. create project
3. add soil sample
4. create scenario
5. submit run
6. wait for `succeeded`
7. open results and assert provenance plus module output visible

## Acceptance Criteria

The slice is complete only when all of the following are true:

1. a user can complete the flow without manual database edits
2. project, sample, scenario, and run records are persisted in PostgreSQL
3. the run row stores:
   - `input_snapshot_json`
   - `input_hash`
   - `engine_version`
   - `submitted_by_user_id`
   - `queued_at`
   - `started_at`
   - `completed_at`
4. the worker executes the placeholder engine outside the API request path
5. the run status transitions visibly in the UI
6. the results page renders both metadata and scientific output
7. one artifact record exists for a successful run
8. rerunning the same scenario with the same snapshot yields the same engine `result_hash`
9. one end-to-end test passes in CI for this flow

## Step-By-Step Implementation Plan

## Phase 1: Data And Contracts

1. add Alembic migration for the slice tables and indexes
2. implement SQLAlchemy models for project, sample, food web, parameter set, scenario, run, artifact
3. finalize Pydantic schemas for:
   - project
   - soil sample
   - thin-slice scenario create
   - run create
   - run results
4. expose OpenAPI and generate the TypeScript client

## Phase 2: Backend API

1. implement project repository and service
2. implement soil sample repository and service
3. implement scenario repository and service with embedded food web and parameter set creation
4. implement run repository and service
5. implement run snapshot builder
6. implement queue publisher adapter for simulation jobs

## Phase 3: Worker And Engine

1. implement Redis queue adapter
2. implement status store
3. implement mock artifact storage adapter
4. implement worker simulation handler
5. wire worker to call the simulation engine CLI
6. persist result summary and artifact metadata

## Phase 4: Frontend

1. scaffold authenticated platform layout
2. add session bootstrap
3. add project creation page
4. add soil sample creation page
5. add scenario creation page
6. add run submission action
7. add run detail page with polling
8. render result summary cards

## Phase 5: Tests And Hardening

1. add backend unit and integration tests
2. add worker integration tests
3. add engine regression tests
4. add one Playwright end-to-end test
5. verify determinism on repeated run submission

## Recommended Implementation Order

Use this exact order:

1. database models and migration
2. scenario create contract, because it defines the scientific input boundary
3. run create service and input snapshot generation
4. simulation engine placeholder verification
5. worker consumption and run finalization
6. results endpoint
7. generated TypeScript client
8. frontend project/sample/scenario forms
9. frontend run page polling and result rendering
10. end-to-end test

## Ownership Split

### Backend

- schemas
- services
- repositories
- queue publish
- run snapshot creation

### Worker

- queue consume
- execution supervision
- status transitions
- artifact metadata persistence

### Simulation Engine

- deterministic placeholder output
- provenance
- result hashing

### Frontend

- forms
- mutations
- polling
- result rendering
- loading and error states
