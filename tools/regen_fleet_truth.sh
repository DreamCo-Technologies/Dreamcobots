#!/usr/bin/env bash
# Regenerate every fleet-truth artifact in dependency order (offline, no secrets).
#   FULL=1 tools/regen_fleet_truth.sh   # also re-run the slow folder tests
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tools/generate_bot_manifests.py
if [ "${FULL:-0}" = "1" ]; then
  python3 tools/fleet_runtime_audit.py
else
  python3 tools/fleet_runtime_audit.py --skip-folder-tests   # keeps the last full folder verdicts
fi
python3 tools/audit_actions_health.py > /dev/null
python3 tools/build_actions_prospectus.py
python3 tools/build_file_prospectus.py
python3 tools/audit_pages_features.py
python3 tools/build_actions_prospectus.py --check --check-buttons
python3 tools/build_file_prospectus.py --check
python3 tools/audit_pages_features.py --check --check-regressions
python3 -m buddy.fleet_runtime division-smoke --all > /dev/null
