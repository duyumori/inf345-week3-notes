#!/usr/bin/env bash
# Start the notes service. The port comes from $PORT, default 8080.
set -euo pipefail

cd "$(dirname "$0")/.."
source scripts/_venv.sh

exec "$PY" -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8080}"
