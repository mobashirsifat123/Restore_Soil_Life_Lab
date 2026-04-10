SHELL := /bin/bash

.PHONY: bootstrap dev stack-up stack-down dev-web dev-api dev-worker db-migrate build typecheck lint format test

bootstrap:
	bash ./scripts/bootstrap-local.sh

stack-up:
	docker compose -f infra/docker/compose.dev.yml up -d

stack-down:
	docker compose -f infra/docker/compose.dev.yml down

dev-worker:
	bash ./scripts/python-project.sh services/worker python -m app.main

dev-web:
	pnpm --filter @bio/web dev

dev-api:
	bash ./scripts/python-project.sh services/api uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev:
	pnpm dev

db-migrate:
	bash ./scripts/python-project.sh services/api alembic -c alembic.ini upgrade head

build:
	pnpm build

typecheck:
	pnpm typecheck

lint:
	pnpm lint

format:
	pnpm format

test:
	pnpm test
