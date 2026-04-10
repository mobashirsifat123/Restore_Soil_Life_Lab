#!/usr/bin/env bash
set -euo pipefail

WEB_ROOT="apps/web"
CACHE_DIR="$WEB_ROOT/.next"

if [ -d "$CACHE_DIR" ]; then
  rm -rf "$CACHE_DIR"
fi

pnpm --filter @bio/web dev
