#!/usr/bin/env bash
# Sourced by run.sh and test.sh: create .venv and install dependencies once.
# Reinstalls only when the requirements files change.
set -euo pipefail

venv=".venv"
stamp="$venv/.requirements"
wanted=$(cat requirements.txt requirements-dev.txt)

if [ ! -x "$venv/bin/python" ]; then
    python3 -m venv "$venv"
fi
if [ ! -f "$stamp" ] || [ "$(cat "$stamp")" != "$wanted" ]; then
    "$venv/bin/python" -m pip install --quiet --disable-pip-version-check \
        -r requirements-dev.txt >&2
    printf '%s' "$wanted" > "$stamp"
fi
PY="$venv/bin/python"
