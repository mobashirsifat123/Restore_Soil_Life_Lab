# Bio Soil Platform

Bio Soil is a science-driven software platform for soil-health analysis, simulation workflows, and content-managed scientific storytelling. The repository is structured as a monorepo so the web application, API, worker runtime, simulation engine, and shared packages can evolve together with clear boundaries.

## What The Project Includes

- a public marketing website built in Next.js
- an authenticated product workspace for projects, samples, scenarios, runs, and admin tools
- a FastAPI backend for auth, business rules, persistence, and API contracts
- a worker service for asynchronous execution
- a pure Python simulation engine isolated from HTTP and storage concerns
- shared TypeScript packages for UI primitives, design tokens, and the generated API client

## Core Product Capabilities

- member authentication with session-based login, registration, password reset, and profile management
- project-scoped workflows for soil samples, scenarios, and simulation runs
- deterministic simulation execution with versioned inputs and artifacts
- admin-managed content for marketing pages, blog content, calculator content, and media assets
- AI-assisted chat and analysis surfaces integrated into the application

## Repository Structure

```text
bio_lab/
├── apps/
│   └── web/                  # Next.js web app for marketing + platform surfaces
├── services/
│   ├── api/                  # FastAPI application, migrations, schemas, repositories
│   ├── worker/               # Async worker runtime for jobs and reports
│   └── simulation-engine/    # Pure scientific compute package
├── packages/
│   ├── api-client/           # Generated TypeScript client for the API
│   ├── design-tokens/        # Shared theme tokens
│   └── ui/                   # Shared React UI primitives
├── infra/
│   └── docker/               # Local PostgreSQL + Redis stack
├── docs/                     # Architecture, domain, roadmap, and quality docs
└── scripts/                  # Bootstrap and local development helper scripts
```

## Architecture Overview

The system is intentionally split by runtime responsibility.

- `apps/web`
  Public-facing pages and authenticated product UI. The app uses the Next.js App Router and contains both marketing routes and logged-in platform routes in one codebase.
- `services/api`
  The source of truth for auth, authorization, validation, organization scoping, CRUD operations, run orchestration, and API documentation.
- `services/worker`
  The background execution layer for queued jobs, long-running tasks, and report generation.
- `services/simulation-engine`
  The scientific model runtime. This package stays independent from FastAPI, SQLAlchemy, Redis, and browser concerns so it remains deterministic and easy to test.
- `packages/*`
  Shared frontend contracts and primitives that reduce duplication across the web app.

High-level request path:

```text
Browser -> Next.js web app -> FastAPI API -> PostgreSQL / Redis / storage
                                         -> Worker -> Simulation engine
```

## Main Application Areas

### Marketing Surface

The public site includes brand and science-oriented pages such as:

- home
- about
- science
- case studies
- blog
- contact

These routes live in the web app and are optimized for editorial control and presentation quality.

### Product Surface

The authenticated application includes:

- dashboard
- projects
- soil sample creation and management
- scenario setup
- simulation run submission and run detail views
- settings
- admin pages for users, blog content, about-page content, calculator content, media, and chat tools

### API Domains

The backend is organized around these primary domains:

- auth
- projects
- soil samples
- scenarios
- runs
- admin
- CMS
- chat
- system

## Technology Stack

### Frontend

- Next.js 15
- React
- TypeScript
- Tailwind CSS

### Backend

- FastAPI
- Pydantic
- SQLAlchemy
- Alembic

### Data And Jobs

- PostgreSQL
- Redis

### Scientific Compute

- Python package in `services/simulation-engine`

### Monorepo Tooling

- `pnpm` workspaces
- `turbo`
- per-service Python environments managed through the repository scripts

## Local Development

### Prerequisites

- Node.js 22+
- `pnpm` 9+
- Python 3.12+
- PostgreSQL
- Redis if you want the queue-backed worker path

Docker is optional if you already have local PostgreSQL and Redis running.

### Environment Files

Create the local environment files if they do not already exist:

- `.env`
- `apps/web/.env.local`
- `services/api/.env`
- `services/worker/.env`

The repository includes matching example files for each environment.

### Bootstrap

Install dependencies and initialize local environments:

```bash
pnpm bootstrap
```

### Database Migration

Apply API migrations:

```bash
pnpm db:migrate
```

### Start The App

Start the default local stack:

```bash
pnpm dev
```

This runs:

- web app on `http://localhost:3000`
- API on `http://localhost:8000`

To include the worker:

```bash
pnpm dev:full
```

If you want the repository-managed Redis/PostgreSQL containers:

```bash
pnpm dev:stack
```

Stop them with:

```bash
pnpm dev:stack:down
```

## Important Local Runtime Notes

- `pnpm dev` starts only the web app and API.
- `pnpm dev:full` adds the worker.
- If `RUN_INLINE_FALLBACK_ENABLED=true`, simulation runs can complete without Redis or the worker.
- If you want the real queue-backed job path, run Redis and start the worker.

## Root Commands

```bash
pnpm bootstrap
pnpm dev
pnpm dev:full
pnpm dev:web
pnpm dev:api
pnpm dev:worker
pnpm db:migrate
pnpm build
pnpm typecheck
pnpm lint
pnpm test
pnpm preflight:prod
pnpm gen:api-client
```

## Service-Level Notes

### `apps/web`

Responsibilities:

- marketing pages
- authenticated product UX
- admin UI
- route-level integration with the API

Relevant structure:

- `src/app/(marketing)` for public pages
- `src/app/(platform)` for authenticated product pages
- `src/app/admin` for admin-facing tools
- `src/app/api/bio/[...path]` as the local API proxy layer

### `services/api`

Responsibilities:

- session auth and password reset
- authorization and role handling
- business validation and organization scoping
- database access
- job submission and status APIs
- admin and CMS endpoints

Relevant structure:

- `app/api/v1/routes/`
- `app/services/`
- `app/repositories/`
- `app/schemas/`
- `alembic/versions/`

### `services/worker`

Responsibilities:

- consume queued jobs
- execute asynchronous run handlers
- generate reports and artifacts
- publish status updates

### `services/simulation-engine`

Responsibilities:

- pure scientific calculations
- deterministic execution for fixed inputs
- CLI and in-process invocation paths

Primary entry points:

- `python -m soil_engine.cli run --input input.json --output output.json`
- library-level execution through the package API

## Authentication And Roles

The project includes:

- login
- registration
- session cookies
- password reset
- member profile management
- organization membership
- role-based admin access

Local behavior can differ from production in one important way: password reset may expose a development recovery code instead of delivering a real email, depending on configuration.

## Data Model Summary

Core entities include:

- organizations
- users
- organization memberships
- auth sessions
- projects
- soil samples
- soil sample versions
- simulation scenarios
- simulation runs
- run artifacts
- CMS pages and sections
- blog posts
- media assets
- chat-related tables

## Testing And Quality

The repository includes coverage across JavaScript and Python services.

- `pnpm lint`
  Runs ESLint and Ruff.
- `pnpm typecheck`
  Runs TypeScript checks across the workspace.
- `pnpm test`
  Runs frontend package tests if present and Python test suites for API, worker, and simulation engine.
- `pnpm preflight:prod`
  Runs the production preflight sequence before release.

## Deployment And Production Notes

Production safety assumptions include:

- `API_ENV=production`
- `API_DEBUG=false`
- `DEBUG_AUTH_ENABLED=false`
- `AUTH_SESSION_SECURE_COOKIE=true`
- `ALLOWED_ORIGINS` must not include `*`

Additional production requirements:

- set `API_BASE_URL` for the deployed web runtime
- configure storage credentials if using media uploads
- configure LLM provider keys for live AI/chat behavior
- run `pnpm preflight:prod` before release

## Documentation

For deeper detail, start with:

- [docs/architecture.md](/Users/mobashirsifat/Desktop/bio_lab%20/docs/architecture.md)
- [docs/frontend/frontend-architecture.md](/Users/mobashirsifat/Desktop/bio_lab%20/docs/frontend/frontend-architecture.md)
- [docs/api/fastapi-backend-mvp.md](/Users/mobashirsifat/Desktop/bio_lab%20/docs/api/fastapi-backend-mvp.md)
- [docs/domain/simulation-engine-architecture.md](/Users/mobashirsifat/Desktop/bio_lab%20/docs/domain/simulation-engine-architecture.md)
- [docs/implementation-roadmap.md](/Users/mobashirsifat/Desktop/bio_lab%20/docs/implementation-roadmap.md)

## Current Development Status

The repository already contains working scaffolding and implemented flows across:

- auth
- project/sample/scenario/run APIs
- admin and CMS surfaces
- worker runtime
- simulation engine package
- generated client and shared UI packages

The platform is structured to support a full workflow from account access through simulation result retrieval, with room for further hardening, richer content management, and more advanced scientific modeling.
