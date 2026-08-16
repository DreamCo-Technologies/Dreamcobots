#!/usr/bin/env bash
set -u
set -o pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

printf '\n=== DreamCo Local Command Center ===\n'
printf 'Repository: %s\n' "$ROOT"
printf 'Branch: %s\n\n' "$(git branch --show-current 2>/dev/null || echo unknown)"

run(){
  echo "\n>>> $*"
  "$@"
  rc=$?
  if [ "$rc" -ne 0 ]; then
    echo "[RECOVERABLE] command failed with exit $rc; continuing so one failure cannot stop the command center."
  fi
  return 0
}

run git fetch --all --prune
run git status --short --branch

if command -v python3 >/dev/null 2>&1; then
  if [ -f tools/check_bot_framework.py ]; then run python3 tools/check_bot_framework.py; fi
  if [ -f tools/bot_test_validator.py ]; then run python3 tools/bot_test_validator.py; fi
fi

if [ -f package.json ] && command -v npm >/dev/null 2>&1; then
  run npm test -- --runInBand
fi

if command -v git >/dev/null 2>&1; then
  echo "\n=== Next steps ==="
  echo "1. Review benchmark output."
  echo "2. Inspect failures rather than hiding them."
  echo "3. Make changes on a review branch."
  echo "4. Commit intentionally."
  echo "5. Push only after reviewing the diff."
fi

printf '\n=== Command Center finished; failures are recorded, not fatal. ===\n'
