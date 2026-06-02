#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
API_PORT="${PLAYWRIGHT_TEST_API_PORT:-8100}"
WEB_PORT="${PLAYWRIGHT_TEST_WEB_PORT:-3100}"

cleanup() {
  if [[ -n "${api_pid:-}" ]]; then
    kill "$api_pid" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT INT TERM

node "$SCRIPT_DIR/mock-api-server.mjs" &
api_pid=$!

cd "$APP_ROOT"
API_BASE_URL="http://127.0.0.1:${API_PORT}" pnpm exec next dev --hostname 127.0.0.1 --port "$WEB_PORT"
