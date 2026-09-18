#!/usr/bin/env python3
"""Run landed update builders in one sandbox pipeline."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "config" / "generated" / "build-updates-now.json"
OUT_MD = ROOT / "reports" / "BUILD_UPDATES_NOW.md"

STEPS = [
    ("scan_bot_fleet", [sys.executable, "tools/scan_bot_fleet.py", "--worklist", "reports/AUTONOMOUS_WORKLIST.md"]),
    ("compile_md_bots", [sys.executable, "tools/compile_md_bots.py"]),
    ("build_dream_systems", [sys.executable, "tools/build_dream_systems.py", "--mode", "all"]),
    ("place_original_bots", [sys.executable, "tools/place_original_bots.py"]),
    ("register_grok_team", [sys.executable, "tools/register_grok_team.py"]),
    ("build_grok_bot_twins", [sys.executable, "tools/build_grok_bot_twins.py"]),
    ("route_grok_twins", [sys.executable, "tools/route_grok_twins.py", "--slug", "buddy-bot"]),
    ("prove_buddy_learning", [sys.executable, "tools/prove_buddy_learning.py"]),
]


def run_step(name: str, cmd: list[str]) -> dict:
    script = ROOT / Path(cmd[1])
    if not script.exists():
        return {"name": name, "ok": False, "exit_code": 127, "detail": f"missing {script.relative_to(ROOT)}"}
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=180, check=False)
    return {
        "name": name,
        "ok": result.returncode == 0,
        "exit_code": result.returncode,
        "stdout_tail": (result.stdout or "")[-1200:],
        "stderr_tail": (result.stderr or "")[-1200:],
    }


def main() -> int:
    results = [run_step(name, cmd) for name, cmd in STEPS]
    payload = {
        "schema": "dreamco.build_updates_now.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "passed": sum(item["ok"] for item in results),
        "failed": sum(not item["ok"] for item in results),
        "results": results,
        "truth_boundary": "Sandbox catalogs, routes, and learning proof. Not live money, outreach, or frontier-parity training.",
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = ["# Build Updates Now", "", f"- Passed: **{payload['passed']}/{len(results)}**", "", "| Step | OK | Exit |", "| --- | --- | --- |"]
    for item in results:
        lines.append(f"| `{item['name']}` | {item['ok']} | {item['exit_code']} |")
    lines += ["", payload["truth_boundary"]]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"ok": payload["failed"] == 0, "passed": payload["passed"], "failed": payload["failed"]}, indent=2))
    return 0 if payload["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
