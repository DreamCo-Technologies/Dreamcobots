#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config" / "buddy-self-repair-controller.json"
OUT = ROOT / ".buddy-local" / "state" / "last-self-repair.json"

GENERATORS = [
    [sys.executable, "tools/build_universal_human_ai_task_sandbox.py"],
    [sys.executable, "tools/build_full_potential_sandbox_catalog.py"],
    [sys.executable, "tools/build_bot_sandbox_curriculum.py"],
    [sys.executable, "tools/build_council_bot_career_paths.py"],
    [sys.executable, "tools/audit_bot_division_placement.py"],
    [sys.executable, "tools/build_resource_sandbox_matrix.py"],
    [sys.executable, "tools/dreamco_generator_factory.py", "registry"],
    [sys.executable, "tools/build_notes_to_code_backlog.py"],
    [sys.executable, "tools/build_github_platform_benchmark.py"],
]


def run(command: list[str]) -> dict:
    proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    return {
        "command": command,
        "exit_code": proc.returncode,
        "stdout_tail": proc.stdout[-4000:],
        "stderr_tail": proc.stderr[-4000:],
    }


def main() -> int:
    config = json.loads(CFG.read_text(encoding="utf-8"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    results = [run(command) for command in GENERATORS]
    failures = [row for row in results if row["exit_code"] != 0]
    verification = run([
        sys.executable,
        "-m",
        "unittest",
        "tests.test_full_potential_sandbox",
        "tests.test_universal_human_ai_task_sandbox",
        "tests.test_bot_sandbox_curriculum",
        "tests.test_offline_generator_universal_sandbox",
        "tests.test_platform_evolution",
    ])
    if verification["exit_code"] != 0:
        failures.append(verification)
    payload = {
        "schema": "dreamco.self_repair_run.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "automatic_repairs_attempted": [
            "universal_task_sandbox_drift",
            "generated_artifact_drift",
            "sandbox_curriculum_drift",
            "career_path_drift",
            "division_audit_drift",
            "resource_matrix_drift",
            "generator_registry_drift",
            "notes_to_code_backlog_drift",
            "github_platform_benchmark_drift",
        ],
        "results": results,
        "verification": verification,
        "ok": not failures,
        "builder_handoff_required": bool(failures),
        "builder_handoff": [{"command": row["command"], "exit_code": row["exit_code"], "stderr_tail": row.get("stderr_tail", "")} for row in failures],
        "completion_gate": config["repair_completion_gate"],
        "truth_boundary": config["truth_rule"],
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": payload["ok"], "builder_handoff_required": payload["builder_handoff_required"], "output": str(OUT.relative_to(ROOT))}, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
