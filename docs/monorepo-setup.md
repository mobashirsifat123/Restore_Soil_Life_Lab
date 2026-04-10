# Bio Soil Monorepo Setup

## Goal

This document defines the initial monorepo structure and setup plan for a production-grade scientific SaaS platform with:

- `apps/web` for the Next.js App Router application
- `services/api` for the FastAPI API
- `services/worker` for async job execution
- `services/simulation-engine` for the pure Python scientific engine
- `packages/api-client` for generated TypeScript API bindings
- `packages/ui` for shared UI components
- `packages/design-tokens` for brand tokens
- `packages/validation` for shared TypeScript validation models where useful
- `infra/docker`, `infra/monitoring`, and `infra/terraform` for runtime and deployment infrastructure
- `docs`, `scripts`, and `tests` for platform operations and quality

The structure below is optimized for clean boundaries, OpenAPI code generation, contract testing, end-to-end testing, future observability, and future enterprise features.

## Recommended Tooling

Use these from day one:

- Node workspace manager: `pnpm`
- Task runner and build orchestration: `turbo`
- Python package and environment manager: `uv`
- TypeScript linting: `eslint`
- TypeScript formatting: `prettier`
- Python linting and formatting: `ruff`
- Python tests: `pytest`
- End-to-end tests: `playwright`
- Contract testing: `pytest` for API contract checks and `vitest` or `playwright` smoke checks on the generated client
- Git hooks: `husky` plus `lint-staged`
- Release versioning: delay `changesets` until multiple packages are independently versioned

Why this stack:

- `pnpm` handles monorepo workspaces cleanly and efficiently
- `turbo` gives deterministic task pipelines and cacheable builds
- `uv` keeps Python setup fast and reproducible
- `ruff` reduces Python tooling sprawl by handling linting and formatting

## Final Folder Tree

```text
bio_lab/
├── .editorconfig
├── .gitignore
├── .nvmrc
├── .python-version
├── Makefile
├── package.json
├── pnpm-workspace.yaml
├── turbo.json
├── README.md
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── e2e.yml
│       └── deploy.yml
├── apps/
│   └── web/
│       ├── package.json
│       ├── next.config.ts
│       ├── postcss.config.js
│       ├── tailwind.config.ts
│       ├── tsconfig.json
│       ├── .env.example
│       ├── public/
│       │   ├── fonts/
│       │   ├── icons/
│       │   └── images/
│       └── src/
│           ├── app/
│           │   ├── (marketing)/
│           │   │   ├── page.tsx
│           │   │   ├── science/
│           │   │   ├── about/
│           │   │   ├── contact/
│           │   │   └── layout.tsx
│           │   ├── (platform)/
│           │   │   ├── dashboard/
│           │   │   ├── projects/
│           │   │   ├── runs/
│           │   │   ├── reports/
│           │   │   └── layout.tsx
│           │   ├── api/
│           │   │   └── auth/
│           │   ├── login/
│           │   ├── globals.css
│           │   └── layout.tsx
│           ├── components/
│           │   ├── layout/
│           │   ├── navigation/
│           │   └── primitives/
│           ├── features/
│           │   ├── auth/
│           │   ├── dashboard/
│           │   ├── projects/
│           │   ├── samples/
│           │   ├── food-webs/
│           │   ├── scenarios/
│           │   ├── runs/
│           │   ├── reports/
│           │   └── marketing/
│           ├── hooks/
│           ├── lib/
│           │   ├── api/
│           │   ├── auth/
│           │   ├── config/
│           │   ├── analytics/
│           │   └── observability/
│           ├── providers/
│           ├── styles/
│           ├── content/
│           ├── types/
│           └── tests/
│               ├── e2e/
│               ├── integration/
│               └── fixtures/
├── services/
│   ├── api/
│   │   ├── pyproject.toml
│   │   ├── alembic.ini
│   │   ├── .env.example
│   │   ├── alembic/
│   │   │   └── versions/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── api/
│   │   │   │   ├── dependencies/
│   │   │   │   └── v1/
│   │   │   │       ├── router.py
│   │   │   │       └── routes/
│   │   │   ├── core/
│   │   │   │   ├── config.py
│   │   │   │   ├── security.py
│   │   │   │   └── logging.py
│   │   │   ├── db/
│   │   │   │   ├── base.py
│   │   │   │   ├── session.py
│   │   │   │   └── models/
│   │   │   ├── domain/
│   │   │   ├── schemas/
│   │   │   ├── repositories/
│   │   │   ├── services/
│   │   │   ├── adapters/
│   │   │   │   ├── queue/
│   │   │   │   ├── storage/
│   │   │   │   └── auth/
│   │   │   ├── observability/
│   │   │   └── tasks/
│   │   └── tests/
│   │       ├── unit/
│   │       ├── integration/
│   │       ├── contract/
│   │       └── fixtures/
│   ├── worker/
│   │   ├── pyproject.toml
│   │   ├── .env.example
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── jobs/
│   │   │   ├── runners/
│   │   │   ├── services/
│   │   │   ├── adapters/
│   │   │   │   ├── queue/
│   │   │   │   ├── storage/
│   │   │   │   └── telemetry/
│   │   │   └── observability/
│   │   └── tests/
│   │       ├── unit/
│   │       ├── integration/
│   │       └── fixtures/
│   └── simulation-engine/
│       ├── pyproject.toml
│       ├── README.md
│       ├── soil_engine/
│       │   ├── __init__.py
│       │   ├── version.py
│       │   ├── common/
│       │   │   ├── models.py
│       │   │   ├── types.py
│       │   │   ├── exceptions.py
│       │   │   └── utils.py
│       │   ├── flux/
│       │   ├── mineralization/
│       │   ├── stability/
│       │   ├── dynamics/
│       │   ├── decomposition/
│       │   └── io/
│       ├── notebooks/
│       └── tests/
│           ├── unit/
│           ├── fixtures/
│           ├── regression/
│           └── benchmarks/
├── packages/
│   ├── api-client/
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── openapi.config.ts
│   │   ├── src/
│   │   │   ├── generated/
│   │   │   ├── client.ts
│   │   │   └── index.ts
│   │   └── scripts/
│   │       └── generate.ts
│   ├── ui/
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── utils/
│   │   │   └── index.ts
│   │   └── stories/
│   ├── design-tokens/
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── src/
│   │   │   ├── colors.ts
│   │   │   ├── spacing.ts
│   │   │   ├── typography.ts
│   │   │   ├── shadows.ts
│   │   │   └── index.ts
│   │   └── tokens/
│   ├── validation/
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── src/
│   │   │   ├── api/
│   │   │   ├── forms/
│   │   │   └── index.ts
│   ├── config-eslint/
│   │   ├── package.json
│   │   └── index.js
│   └── config-typescript/
│       ├── package.json
│       ├── base.json
│       └── nextjs.json
├── infra/
│   ├── docker/
│   │   ├── compose.dev.yml
│   │   ├── api.Dockerfile
│   │   ├── web.Dockerfile
│   │   ├── worker.Dockerfile
│   │   └── simulation-engine.Dockerfile
│   ├── monitoring/
│   │   ├── prometheus/
│   │   ├── grafana/
│   │   └── otel-collector/
│   └── terraform/
│       ├── modules/
│       │   ├── app-service/
│       │   ├── database/
│       │   ├── redis/
│       │   ├── object-storage/
│       │   ├── networking/
│       │   └── observability/
│       └── environments/
│           ├── dev/
│           ├── staging/
│           └── production/
├── docs/
│   ├── architecture.md
│   ├── implementation-roadmap.md
│   ├── monorepo-setup.md
│   ├── adr/
│   ├── api/
│   ├── domain/
│   ├── runbooks/
│   └── testing/
├── scripts/
│   ├── bootstrap.sh
│   ├── dev.sh
│   ├── generate-api-client.sh
│   ├── wait-for-services.sh
│   ├── seed-dev-data.py
│   └── verify-openapi-drift.sh
├── tests/
│   ├── contract/
│   ├── performance/
│   ├── smoke/
│   └── fixtures/
└── tooling/
    ├── eslint/
    ├── prettier/
    └── templates/
```

## Purpose Of Each Major Directory

### `apps/web`

Contains the single flagship web application. It serves:

- public marketing pages
- authenticated product routes
- route-level access boundaries
- page composition, product UX, and browser-specific concerns

This app should never contain scientific formulas or simulation execution logic.

### `services/api`

Contains the HTTP API and domain orchestration layer. It owns:

- request validation
- auth and authorization enforcement
- database transactions
- run creation and lifecycle transitions
- OpenAPI generation
- integration with queue, object storage, and auth providers

It should orchestrate simulation runs, not implement scientific formulas.

### `services/worker`

Contains the async runtime for:

- queued simulation execution
- report generation
- artifact creation
- retries, dead-letter handling, and operator diagnostics

It should import the simulation engine package but remain separate from the FastAPI app.

### `services/simulation-engine`

Contains pure Python scientific code only. It owns:

- mathematical models
- simulation input and output models
- numerical utilities
- fixture-based regression tests
- performance benchmarks

It must have no dependency on FastAPI, SQLAlchemy, request objects, or web frameworks.

### `packages/api-client`

Contains generated TypeScript bindings from the FastAPI OpenAPI spec. It should expose:

- typed request and response models
- API client factory
- thin wrappers for auth header injection if needed

Generated code lives under `src/generated`. Handwritten wrappers live outside that folder.

### `packages/ui`

Contains reusable presentational components and primitives shared by marketing and platform surfaces. Examples:

- buttons
- forms
- tables
- cards
- modals
- charts wrappers

No app-specific data fetching logic should live here.

### `packages/design-tokens`

Contains brand constants and theme primitives. Examples:

- colors
- typography scales
- spacing
- radii
- shadows
- motion tokens

This package should feed Tailwind, CSS variables, and UI components.

### `packages/validation`

Contains shared TypeScript-side validation helpers where they add value. Day-one uses:

- form schemas
- parsing helpers for URL params or query state
- frontend-safe domain constraints that mirror API constraints

Do not try to make TypeScript the source of truth for backend validation. Backend truth stays in Pydantic. This package exists to reduce duplicated UX validation, not to replace API validation.

### `infra/docker`

Contains local and container runtime definitions for development and CI.

### `infra/monitoring`

Contains baseline observability setup:

- local Prometheus and Grafana config
- OpenTelemetry collector config
- dashboards and alert rules later

### `infra/terraform`

Contains reusable infrastructure modules and per-environment composition.

### `docs`

Contains architecture decisions, API docs, domain definitions, runbooks, and testing guidance. Put ADRs in `docs/adr`.

### `scripts`

Contains repo automation scripts. Keep these simple and deterministic. Prefer scripts over hidden tribal knowledge.

### `tests`

Contains cross-cutting tests not owned by one service, such as:

- contract validation against generated clients
- smoke tests
- performance tests

## Starter Manifest Strategy

## Root `package.json`

The root package should be a workspace orchestrator, not an application package.

Responsibilities:

- workspace scripts
- dev orchestration
- lint/typecheck/test commands
- codegen commands
- shared dev dependencies for JS tooling only

Recommended root scripts:

```json
{
  "private": true,
  "packageManager": "pnpm@10",
  "scripts": {
    "dev": "turbo run dev --parallel",
    "dev:web": "pnpm --filter @bio/web dev",
    "dev:stack": "docker compose -f infra/docker/compose.dev.yml up -d",
    "lint": "turbo run lint",
    "typecheck": "turbo run typecheck",
    "test": "turbo run test",
    "test:e2e": "pnpm --filter @bio/web test:e2e",
    "gen:api-client": "pnpm --filter @bio/api-client generate",
    "build": "turbo run build",
    "clean": "turbo run clean"
  }
}
```

Do not put application runtime dependencies in the root package.

## `apps/web/package.json`

Owns:

- `next`
- `react`
- `react-dom`
- `tailwindcss`
- `@tanstack/react-query`
- auth SDKs
- browser analytics SDKs

It should depend on:

- `@bio/api-client`
- `@bio/ui`
- `@bio/design-tokens`
- `@bio/validation`

## `packages/ui/package.json`

Owns:

- React peer dependencies
- shared component library dependencies
- utility dependencies for UI only

Avoid putting Next.js-specific APIs here.

## `packages/api-client/package.json`

Owns:

- generated client tooling
- fetch client wrapper
- generated code output path

This package should be regenerated from OpenAPI, not hand-maintained.

## Python `pyproject.toml` strategy

Use one `pyproject.toml` per Python service or package:

- `services/api/pyproject.toml`
- `services/worker/pyproject.toml`
- `services/simulation-engine/pyproject.toml`

Each should define:

- project metadata
- Python version
- dependencies
- optional dev dependencies
- `ruff` config
- `pytest` config

Use path dependencies for local Python packages.

Example dependency relationship:

- `worker` depends on `simulation-engine`
- `api` does not depend on `simulation-engine` directly unless absolutely necessary for schema reuse

Keep service dependencies narrow:

- API: FastAPI, Pydantic, SQLAlchemy, Alembic, auth, queue and storage adapters
- Worker: queue runtime, storage, logging, telemetry, simulation-engine
- Simulation engine: numerical libraries only

## Shared Packages: Day One vs Later

### Create From Day One

- `packages/ui`
- `packages/design-tokens`
- `packages/api-client`
- `packages/config-eslint`
- `packages/config-typescript`

### Create From Day One Only If Needed Immediately

- `packages/validation`

Create it now if you know the web app will have non-trivial forms in the first two weeks. Otherwise add it once duplicated browser-side validation appears.

### Delay Until Later

- `packages/charts`
- `packages/auth`
- `packages/analytics`
- `packages/testing`

Only split these once multiple apps or packages genuinely share them.

## Dependency Strategy

### TypeScript

- app runtime dependencies live in the app or package that executes them
- shared code lives in `packages/*`
- `apps/web` consumes shared packages through workspace imports
- generated API bindings are the single typed source for frontend API calls

### Python

- `services/simulation-engine` is versionable and independently testable
- `services/worker` imports `simulation-engine`
- `services/api` talks to the worker and database, not directly to the scientific engine for heavy execution
- shared Python helpers should live in the owning package until duplication is real

### Cross-Language

- OpenAPI is the contract between FastAPI and TypeScript
- simulation request and response persistence format should be JSON-schema-compatible
- no direct TypeScript-to-Python shared code generation is required on day one beyond OpenAPI

## Coding Conventions

### Naming

- TypeScript packages use `@bio/*`
- Python packages use `bio_*` if multiple internal packages are added later
- database table names are plural snake_case
- API payloads use JSON camelCase externally and Python snake_case internally if using aliasing

### Imports

- use absolute imports within packages
- no deep imports into another package's private files
- only import from another package's public entrypoint
- generated client code should be imported via `@bio/api-client`

### Web App Structure

- put route handlers and page composition in `app/`
- put domain UI and hooks in `features/`
- put generic presentational parts in `components/`
- put framework wiring in `lib/`

### API Structure

- routes call services
- services coordinate repositories and adapters
- repositories handle persistence
- adapters wrap external systems
- domain rules should not live in routes

### Simulation Engine Structure

- each scientific capability gets its own module namespace
- shared numeric utilities live in `common/`
- reference fixtures and regression tests are mandatory for any algorithm promoted to production use

## Import Boundaries

Use these allowed directions:

- `apps/web` -> `packages/ui`, `packages/design-tokens`, `packages/api-client`, `packages/validation`
- `services/api` -> its own `app/*` modules only
- `services/worker` -> its own modules and `services/simulation-engine`
- `services/simulation-engine` -> its own package only

Do not allow these directions:

- `services/simulation-engine` -> `services/api`
- `services/simulation-engine` -> `services/worker`
- `packages/ui` -> `apps/web`
- `packages/api-client` -> `apps/web`
- `services/api` -> `apps/web`
- `apps/web` -> direct database access
- `apps/web` -> direct imports from Python services

## Do Not Violate These Boundaries

1. Never put scientific formulas in the Next.js app.
2. Never import FastAPI, SQLAlchemy, or request models into `services/simulation-engine`.
3. Never let route handlers own business logic that belongs in API services.
4. Never let the web app construct raw fetch calls once the generated API client exists.
5. Never deep-import from `packages/api-client/src/generated/*` directly in app code.
6. Never let the worker write results without updating run lifecycle state transactionally.
7. Never store artifact files without corresponding metadata rows in the database.
8. Never bypass organization scoping in repository queries.
9. Never share secrets via root `.env`; use service-level env files and deployment-managed secrets.
10. Never add a shared package until at least two consumers need it or the boundary is strategically important from day one.

## Environment Variable Strategy

Use service-local `.env.example` files and validate configuration at startup.

Rules:

- root `.env` should not exist
- each executable app or service gets its own `.env.example`
- browser-exposed values in Next.js must use `NEXT_PUBLIC_`
- Python services validate env vars with Pydantic settings
- TypeScript services validate env vars with a small config module and schema validation

Recommended service env groups:

### `apps/web`

- `NEXT_PUBLIC_APP_URL`
- `NEXT_PUBLIC_API_BASE_URL`
- `NEXT_PUBLIC_ENVIRONMENT`
- auth provider public keys
- analytics IDs later

### `services/api`

- `API_PORT`
- `DATABASE_URL`
- `REDIS_URL`
- `OBJECT_STORAGE_ENDPOINT`
- `OBJECT_STORAGE_BUCKET`
- `OBJECT_STORAGE_ACCESS_KEY`
- `OBJECT_STORAGE_SECRET_KEY`
- `AUTH_ISSUER_URL`
- `AUTH_AUDIENCE`
- `LOG_LEVEL`
- `OTEL_EXPORTER_OTLP_ENDPOINT`

### `services/worker`

- `WORKER_CONCURRENCY`
- `REDIS_URL`
- `DATABASE_URL`
- `OBJECT_STORAGE_*`
- `LOG_LEVEL`
- `OTEL_EXPORTER_OTLP_ENDPOINT`

### `services/simulation-engine`

Prefer keeping this package pure and parameter-driven. Avoid service-like env config unless benchmarks or optional model toggles require it.

## Local Development Workflow

Use this daily flow:

1. install Node and Python toolchains
2. install JS and Python dependencies
3. start local infrastructure with Docker Compose
4. apply database migrations
5. start API, worker, and web in parallel
6. regenerate API client after any API schema change
7. run contract and end-to-end tests before merging

Recommended developer loop:

1. `pnpm dev:stack`
2. `uv run --project services/api alembic upgrade head`
3. `pnpm dev:web`
4. `uv run --project services/api fastapi dev services/api/app/main.py`
5. `uv run --project services/worker python -m app.main`

If you want a one-command workflow, wrap the above in `scripts/dev.sh`.

## Bootstrap Commands

These are the initial bootstrap commands to implement once the repo scaffolding begins:

```bash
# Node toolchain
corepack enable
corepack prepare pnpm@latest --activate

# Python toolchain
curl -LsSf https://astral.sh/uv/install.sh | sh

# Workspace bootstrap
pnpm install
uv sync --project services/api
uv sync --project services/worker
uv sync --project services/simulation-engine

# Local infrastructure
docker compose -f infra/docker/compose.dev.yml up -d

# Database migration
uv run --project services/api alembic upgrade head

# API client generation
pnpm gen:api-client

# Start services
pnpm dev:web
uv run --project services/api fastapi dev services/api/app/main.py
uv run --project services/worker python -m app.main
```

If you want a friendlier onboarding path, wrap them with:

- `make bootstrap`
- `make dev`
- `make test`

## Setup Instructions

Use this order to stand up the repo:

1. add root workspace files
2. add JS shared config packages
3. scaffold `apps/web`
4. scaffold Python services with `pyproject.toml`
5. add Docker Compose for local infra
6. add API OpenAPI generation path
7. add `packages/api-client` codegen
8. add migrations and DB bootstrap
9. add worker runtime and queue wiring
10. add testing harnesses and CI

Concrete root files to create first:

- `package.json`
- `pnpm-workspace.yaml`
- `turbo.json`
- `Makefile`
- `.editorconfig`
- `.gitignore`
- `.nvmrc`
- `.python-version`

Concrete service files to create first:

- `apps/web/package.json`
- `apps/web/tsconfig.json`
- `apps/web/next.config.ts`
- `services/api/pyproject.toml`
- `services/api/app/main.py`
- `services/worker/pyproject.toml`
- `services/worker/app/main.py`
- `services/simulation-engine/pyproject.toml`
- `services/simulation-engine/soil_engine/__init__.py`
- `packages/api-client/package.json`
- `packages/ui/package.json`
- `packages/design-tokens/package.json`

## Contract Testing Strategy

Prepare for these from day one:

- API exports OpenAPI spec on every build
- `packages/api-client` regenerates from that spec
- CI checks for OpenAPI drift
- root `tests/contract` contains tests ensuring the generated client still works against the running API

Do not hand-maintain frontend request types once codegen exists.

## End-To-End Testing Strategy

Start with:

- Playwright in `apps/web/src/tests/e2e`
- one critical flow test for login -> create project -> submit run -> view results

Keep browser tests focused on a few critical flows. Push most logic verification into unit, integration, and contract tests.

## Future Enterprise Readiness

The structure above is intentionally ready for:

- SSO and enterprise auth adapters
- audit logging and support views
- multi-environment deployments
- object storage artifact retention
- observability pipelines with traces and dashboards
- org-scoped RBAC and support operations

Do not add the full enterprise surface area early. Keep the seams available, but implement only what the first pilot requires.
