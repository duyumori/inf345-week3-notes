#!/usr/bin/env bash
# Run the test suite. Exit 0 only if every test passes.
# Prints one normalised line: "TESTS: <passed>/<total>".
set -euo pipefail

cd "$(dirname "$0")/.."
source scripts/_venv.sh

out=$(mktemp)
trap 'rm -f "$out"' EXIT

rc=0
"$PY" -m pytest -v -p no:cacheprovider tests >"$out" 2>&1 || rc=$?
cat "$out"

# pytest's last line looks like "== 1 failed, 6 passed in 0.12s ==".
summary=$(tail -n 1 "$out")
count() { echo "$summary" | grep -oE "[0-9]+ $1" | grep -oE '[0-9]+' || echo 0; }
passed=$(count passed)
total=$(( passed + $(count failed) + $(count 'errors?') ))

echo "TESTS: $passed/$total"

if [ "$rc" -ne 0 ] || [ "$total" -eq 0 ]; then
    exit 1
fi
