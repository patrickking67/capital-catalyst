#!/usr/bin/env bash
# The one check command: lint, format check and tests.
# Usage: scripts/check.sh   (uses .venv if present, else the active Python)
set -euo pipefail

cd "$(dirname "$0")/.."

if [ -x .venv/bin/python ]; then
  PY=.venv/bin/python
else
  PY=python3
fi

echo "== ruff check"
"$PY" -m ruff check .
echo "== ruff format --check"
"$PY" -m ruff format --check .
echo "== pytest"
"$PY" -m pytest
