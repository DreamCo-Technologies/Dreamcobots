#!/usr/bin/env python3
"""Grok operator: run every owner system script that exists on this checkout."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "config" / "generated" / "grok-owner-systems.json"
REPORT = ROOT / "reports" / "GROK_OWNER_SYSTEMS.md"
FEEL = ROOT / "reports" / "BUDDY_FEEL.md"

JOBS = [
    "tools/scan_bot_fleet.py",
    "tools/compile_md_bots.py",
    "tools/build_dream_systems.py",
    "tools/place_original_bots.py",
    "tools/register_grok_team.py",
    "tools/build_grok_bot_twins.py",
    "tools/route_grok_twins.py",
    "tools/prove_buddy_learning.py",
    "tools/build_hf_capability_packs.py",
    "tools/build_hf_download_packages.py",
    "tools/buddy_scan_hubs.py",
    "tools/build_foundry_guides.py",
    "tools/plan_us_weights.py",
    "tools/run_weight_balancer.py",
    "tools/build_customer_model_plan.py",
    "tools/plan_pass_all_500.py",
]


def run_job(rel: str) -> dict:
    path = ROOT / rel
    if not path.exists():
        return {"job": rel, "state": "missing", "ok": True, "note": "not on this branch yet"}
    result = subprocess.run([sys.executable, rel], cwd=ROOT, capture_output=True, text=True, timeout=180, check=False)
    return {
        "job": rel,
        "state": "passed" if result.returncode == 0 else "failed",
        "ok": result.returncode == 0,
        "exit_code": result.returncode,
        "stdout_tail": (result.stdout or "")[-800:],
        "stderr_tail": (result.stderr or "")[-800:],
    }


def feel(results: list[dict]) -> dict:
    present = [row for row in results if row["state"] != "missing"]
    failed = [row for row in results if row["state"] == "failed"]
    missing = [row for row in results if row["state"] == "missing"]
    passed = [row for row in results if row["state"] == "passed"]
    score = 0.0
    if present:
        score = len(passed) / len(present)
    mood = "sharp" if score >= 0.85 and not failed else "working" if score >= 0.5 else "needs_care"
    return {
        "mood": mood,
        "score": score,
        "passed": len(passed),
        "failed": len(failed),
        "missing": len(missing),
        "note": "Buddy feels good when owner systems pass and missing tools are just unmerged, not hidden failures.",
    }


def main() -> int:
    results = [run_job(job) for job in JOBS]
    vibe = feel(results)
    payload = {
        "schema": "dreamco.grok_owner_systems.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "operator": "grok-actions-operator",
        "results": results,
        "feel": vibe,
        "truth": "Grok runs the owner systems that exist. Missing scripts are skipped, not faked green.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = ["# Grok Owner Systems", "", f"- Mood: **{vibe['mood']}**", f"- Passed: **{vibe['passed']}**", f"- Failed: **{vibe['failed']}**", f"- Missing: **{vibe['missing']}**", "", "| Job | State |", "| --- | --- |"]
    for row in results:
        lines.append(f"| `{row['job']}` | {row['state']} |")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    FEEL.write_text(
        "# Buddy Feel\n\n"
        f"Buddy feels **{vibe['mood']}** ({vibe['score']:.0%} of present systems passed).\n\n"
        f"{vibe['note']}\n\n"
        "Owner path: Actions → Grok Owner Systems → Run workflow.\n",
        encoding="utf-8",
    )
    print(json.dumps({"ok": vibe["failed"] == 0, "feel": vibe}, indent=2))
    return 0 if vibe["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
