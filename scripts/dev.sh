#!/usr/bin/env bash
# Run the Flask dev server on port 4108 (override with PORT).
# Sets a fake SECRET_KEY for local development only. Never use it anywhere else.
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -x .venv/bin/flask ]; then
  echo "No .venv found. Run scripts/setup.sh first." >&2
  exit 1
fi

export SECRET_KEY="${SECRET_KEY:-dev-only-not-a-real-secret}"
export FLASK_DEBUG="${FLASK_DEBUG:-1}"

exec .venv/bin/flask --app app run --host 127.0.0.1 --port "${PORT:-4108}"
