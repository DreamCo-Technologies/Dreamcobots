#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STEPS = [
    [sys.executable, "-m", "unittest", "tests.test_full_system_operational_certification", "tests.test_trusted_code_delivery", "tests.test_change_impact_test_policy"],
    ["node", "--import", "tsx", "--test", "tests/server-health-runtime-policy.test.ts"],
    ["npm", "run", "buddy:connections"],
    [sys.executable, "tools/audit_runtime_connections.py"],
    [sys.executable, "tools/audit_all_bots_categories_and_agents.py"],
    [sys.executable, "tools/audit_trusted_code_delivery.py"],
    ["node", "--import", "tsx", "tools/run_universal_verification.ts", "--production"],
    [sys.executable, "tools/run_system_speed_accuracy_benchmarks.py"],
    [sys.executable, "tools/smoke_production_runtime.py"],
]


def run(command: list[str]) -> dict:
    print(f"\n[certify] {' '.join(command)}", flush=True)
    proc = subprocess.run(command, cwd=ROOT)
    return {"command": command, "exit_code": proc.returncode}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean-install", action="store_true", help="Run npm ci before certification.")
    args = parser.parse_args()

    results = []
    if args.clean_install:
        result = run(["npm", "ci"])
        results.append(result)
        if result["exit_code"] != 0:
            print(json.dumps({"ok": False, "failed": result}, indent=2))
            return result["exit_code"]

    for command in STEPS:
        results.append(run(command))

    # Always attempt to assemble a receipt from whatever evidence was generated.
    receipt = run([sys.executable, "tools/build_full_system_certification.py"])
    results.append(receipt)
    failed = [row for row in results if row["exit_code"] != 0]
    print(json.dumps({
        "ok": not failed,
        "steps": len(results),
        "failed_steps": failed,
        "receipt": "config/generated/full-system-operational-certification.json",
    }, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
