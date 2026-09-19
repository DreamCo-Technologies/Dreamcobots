#!/usr/bin/env python3
"""Turn self-build failures into recovery incidents. Never fake green."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "reports" / "self-build.json"
OUT = ROOT / "reports" / "self-fix.json"

SAFE_REGENERATORS = {
    "website": ["python3", "tools/generate_master_directive_status.py"],
    "tools": ["python3", "tools/buddy_recovery_systems.py"],
    "reports": ["python3", "tools/buddy_recovery_systems.py"],
}


def run(cmd: list[str]) -> dict[str, object]:
    try:
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=120)
        return {
            "cmd": cmd,
            "code": result.returncode,
            "tail": ((result.stdout or "") + (result.stderr or ""))[-800:],
        }
    except Exception as exc:
        return {"cmd": cmd, "code": 1, "tail": str(exc)}


def main() -> int:
    if not BUILD.exists():
        subprocess.run(["python3", "tools/buddy_self_build.py"], cwd=ROOT, check=False)
    payload = json.loads(BUILD.read_text(encoding="utf-8")) if BUILD.exists() else {"parts": []}
    incidents = []
    actions = []
    for part in payload.get("parts", []):
        if part.get("money_sensitive"):
            incidents.append(
                {
                    "id": f"fix-{part['id']}",
                    "lane": "safety",
                    "state": "BLOCKED",
                    "title": f"{part['id']} is money-sensitive",
                    "next": "Human vault. Self-fix will not edit.",
                }
            )
            continue
        if part.get("status") == "absent":
            incidents.append(
                {
                    "id": f"fix-{part['id']}",
                    "lane": part.get("lane", "detect"),
                    "state": "DETECTED",
                    "title": f"{part['id']} is not in this checkout",
                    "next": "Full checkout on Actions will score this part. Absence is not a pass.",
                }
            )
            continue
        if part.get("status") != "failed":
            continue
        incidents.append(
            {
                "id": f"fix-{part['id']}",
                "lane": part.get("lane", "detect"),
                "state": "TRIAGED",
                "title": f"{part['id']} self-build failed",
                "errors": part.get("errors", [])[:6],
                "next": part.get("fix"),
            }
        )
        regen = SAFE_REGENERATORS.get(part["id"])
        if regen:
            actions.append({"part": part["id"], "result": run(regen)})

    report = {
        "schema": "dreamco.buddy_self_fix.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "truth": "Self-fix files incidents and may regenerate catalogs. It never force-merges main or enables live Stripe.",
        "incidents": incidents,
        "actions": actions,
        "auto_merge_main": False,
        "live_stripe": False,
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    site = ROOT / "website" / "data"
    if site.exists():
        (site / "self-fix.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"incidents": len(incidents), "actions": len(actions)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
