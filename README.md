# Bio Soil Platform

Premium scientific SaaS monorepo for a high-trust bio soil company.

## Repository Layout

- `apps/web`
  - Next.js App Router application for marketing and product surfaces
- `services/api`
  - FastAPI API, validation, business rules, and persistence
- `services/worker`
  - background execution for simulations and reports
- `services/simulation-engine`
  - pure Python scientific engine, isolated from HTTP concerns
- `packages/api-client`
  - generated frontend API client surface
- `packages/ui`
  - shared React UI primitives
- `packages/design-tokens`
  - shared design tokens and theme values
- `infra/docker`
  - local PostgreSQL and Redis stack

Architecture details live in `docs/architecture.md`.

## Tooling Strategy

- `pnpm` workspaces manage JavaScript and TypeScript packages
- `turbo` coordinates JS builds and typechecks
- `uv` manages Python environments per service
- each Python service owns its own `pyproject.toml`
- there is intentionally no root Python package

This keeps:

- the FastAPI API isolated from worker runtime concerns
- the worker isolated from frontend dependencies
- the simulation engine isolated from FastAPI and HTTP packages

## Environment Files

Create local env files from the examples:

- `.env.example -> .env`
- `apps/web/.env.example -> apps/web/.env.local`
- `services/api/.env.example -> services/api/.env`
- `services/worker/.env.example -> services/worker/.env`

`pnpm bootstrap` creates missing local env files automatically.

## Quick Start

1. Install:
   - Node.js 22+
   - `pnpm`
   - Python 3.12+
   - `uv`
   - Docker
2. Bootstrap the repo:
   - `pnpm bootstrap`
3. Start local infrastructure:
   - `pnpm dev:stack`
4. Apply database migrations:
   - `pnpm db:migrate`
5. Start the application processes:
   - `pnpm dev`

For the current local setup, `pnpm dev` starts the web app and API only. This is the smooth default when using Supabase plus the API's inline run fallback. If you also have Redis running and want the queue-backed worker path, use `pnpm dev:full`.

## Root Commands

- `pnpm bootstrap`
  - installs JS dependencies, syncs Python service environments, and creates local env files
- `pnpm dev:stack`
  - starts PostgreSQL and Redis
- `pnpm dev`
  - runs web and API together for the default local workflow
- `pnpm dev:full`
  - runs web, API, and worker together when Redis is available
- `pnpm dev:web`
  - starts the Next.js app after clearing the local `.next` cache to avoid stale dev artifacts
- `pnpm build`
  - runs Turbo builds for the JS workspace
- `pnpm typecheck`
  - runs Turbo typechecks for the JS workspace
- `pnpm lint`
  - runs ESLint for JS/TS and Ruff for Python
- `pnpm format`
  - formats supported files with Prettier
- `pnpm test`
  - runs JS tests if present and Python test suites
- `pnpm gen:api-client`
  - regenerates the TypeScript API client
- `pnpm preflight:prod`
  - runs full production preflight (format, lint, typecheck, tests, build, critical E2E link/chat checks)

## Production Readiness

- Keep production runtime flags safe:
  - `API_ENV=production`
  - `API_DEBUG=false`
  - `DEBUG_AUTH_ENABLED=false`
  - `AUTH_SESSION_SECURE_COOKIE=true`
  - `ALLOWED_ORIGINS` must not include `*`
  - `WORKER_OPTIONAL_WHEN_REDIS_UNAVAILABLE=false` when `WORKER_ENV=production`
- Set `API_BASE_URL` for the deployed web runtime to the public API origin.
- For live chatbot LLM replies, set `DEEPSEEK_API_KEY` in `services/api/.env` and optionally tune `DEEPSEEK_MODEL` / `DEEPSEEK_BASE_URL`.
- Gemini envs remain optional for backward compatibility, but DeepSeek is now the default chat provider.
- Run `pnpm preflight:prod` before every release.

## Local Ports

- Web: `http://localhost:3000`
- API: `http://localhost:8000`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

## Local Dev Notes

- The default local path uses Supabase for PostgreSQL.
- If `RUN_INLINE_FALLBACK_ENABLED=true`, simulation runs can complete without Redis or the worker.
- If you want the real queue-backed worker flow, start Redis first and then use `pnpm dev:full`.

## First Thin Slice

The first milestone is:

1. create a project
2. add a soil sample
3. create a simulation scenario
4. submit a simulation run
5. let the worker process a placeholder engine run
6. open the results page and view metadata plus output
