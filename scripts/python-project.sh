#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_ARG="${1:?project path is required}"
shift

PROJECT_DIR="${ROOT_DIR}/${PROJECT_ARG}"
VENV_DIR="${PROJECT_DIR}/.venv"
STAMP_FILE="${VENV_DIR}/.codex-installed"
LOCK_DIR="${PROJECT_DIR}/.venv-install.lock"

if [[ ! -d "${PROJECT_DIR}" ]]; then
  echo "Project directory not found: ${PROJECT_DIR}" >&2
  exit 1
fi

if [[ $# -eq 0 ]]; then
  echo "No command provided for ${PROJECT_ARG}" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required when uv is unavailable." >&2
  exit 1
fi

while ! mkdir "${LOCK_DIR}" 2>/dev/null; do
  sleep 1
done

cleanup_lock() {
  rmdir "${LOCK_DIR}" 2>/dev/null || true
}

trap cleanup_lock EXIT

needs_install=0

if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
  needs_install=1
elif ! "${VENV_DIR}/bin/python" -c "import sys" >/dev/null 2>&1; then
  needs_install=1
elif [[ ! -f "${STAMP_FILE}" || "${PROJECT_DIR}/pyproject.toml" -nt "${STAMP_FILE}" ]]; then
  needs_install=1
fi

if [[ "${needs_install}" -eq 1 ]]; then
  rm -rf "${VENV_DIR}"
  python3 -m venv "${VENV_DIR}"
  "${VENV_DIR}/bin/pip" install --upgrade pip setuptools wheel >/dev/null
  "${VENV_DIR}/bin/pip" install -e "${PROJECT_DIR}[dev]" >/dev/null
  touch "${STAMP_FILE}"
fi

cleanup_lock
trap - EXIT

cd "${PROJECT_DIR}"
PATH="${VENV_DIR}/bin:${PATH}" exec "$@"
