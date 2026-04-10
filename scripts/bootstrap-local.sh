#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

copy_if_missing() {
  local source_path="$1"
  local target_path="$2"

  if [[ ! -f "${ROOT_DIR}/${target_path}" ]]; then
    cp "${ROOT_DIR}/${source_path}" "${ROOT_DIR}/${target_path}"
    echo "created ${target_path}"
  fi
}

copy_if_missing ".env.example" ".env"
copy_if_missing "apps/web/.env.example" "apps/web/.env.local"
copy_if_missing "services/api/.env.example" "services/api/.env"
copy_if_missing "services/worker/.env.example" "services/worker/.env"

corepack enable
pnpm install
bash "${ROOT_DIR}/scripts/python-project.sh" services/api python -c "print('api ready')"
bash "${ROOT_DIR}/scripts/python-project.sh" services/worker python -c "print('worker ready')"
bash "${ROOT_DIR}/scripts/python-project.sh" services/simulation-engine python -c "print('simulation engine ready')"

echo "Bootstrap complete."
echo "Next steps:"
echo "  1. pnpm dev:stack"
echo "  2. pnpm db:migrate"
echo "  3. pnpm dev"
