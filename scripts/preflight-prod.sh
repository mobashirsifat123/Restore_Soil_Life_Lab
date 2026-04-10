#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "Running production preflight checks..."
echo "1) Formatting"
pnpm format:check

echo "2) Lint"
pnpm lint

echo "3) Typecheck"
pnpm typecheck

echo "4) Tests"
pnpm test

echo "5) Production build"
pnpm build

echo "6) Critical E2E checks"
pnpm --filter @bio/web exec playwright test tests/e2e/links.spec.ts tests/e2e/chat-widget.spec.ts --reporter=line

echo "Production preflight completed successfully."
