#!/usr/bin/env bash
# Safe, reproducible repair pass for the failures found in the 2026-11-18 audit.
# Run from the repository root: bash tools/reconcile_repository_health.sh
set -Eeuo pipefail
cd "$(dirname "$0")/.."

echo "==> Install exact locked dependencies"
npm ci
python3 -m pip install --disable-pip-version-check pyyaml pytest openpyxl

echo "==> Apply non-breaking dependency security updates"
npm audit fix
npm audit --audit-level=high

echo "==> Regenerate repository and Pages source-of-truth artifacts"
FULL=1 bash tools/regen_fleet_truth.sh

echo "==> Run fleet and prospectus regression tests"
python3 -m pytest -q -p no:cacheprovider \
  tests/test_fleet_runtime_executor.py \
  tests/test_fleet_runtime_customize.py \
  tests/test_generate_bot_manifests.py \
  tests/test_fleet_runtime_audit.py \
  tests/test_check_website_links.py \
  tests/test_run_prospectus.py \
  tests/test_file_prospectus.py \
  tests/test_fleet_divisions.py \
  tests/test_pages_feature_audit.py \
  tests/test_build_queue.py

echo "==> Verify Actions and Pages contracts"
node --test tests/buddy-run-page.test.mjs tests/actions-page.test.mjs
python3 tools/build_actions_prospectus.py --check --check-buttons
python3 tools/build_file_prospectus.py --check
python3 tools/audit_pages_features.py --check --check-regressions
python3 tools/check_website_links.py --all

echo "==> Verify public site and production bundle"
npm run buddy:site:check
npm run build

echo "==> Repair pass complete. Review git diff, commit on a branch, and open a PR."
