#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config" / "system-progress-gauges.json"
GAPS = ROOT / "config" / "generated" / "engineering-gap-closure-plan.json"
GH = ROOT / "config" / "generated" / "github-platform-parity-benchmark.json"
OUT = ROOT / "config" / "generated" / "system-progress-status.json"


def main() -> int:
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    gaps = json.loads(GAPS.read_text(encoding="utf-8")) if GAPS.exists() else {"gaps": []}
    gh = json.loads(GH.read_text(encoding="utf-8")) if GH.exists() else {"status_counts": {}}
    stage_weights = {row["id"]: int(row["weight"]) for row in cfg["gap_stages"]}
    stage_order = [row["id"] for row in cfg["gap_stages"]]
    rows = []
    for gap in gaps.get("gaps", []):
        # Generated gap plans prove discovery/ownership/acceptance intent, but not implementation/test success.
        achieved = {"discovered", "deduplicated", "owner_assigned", "acceptance_defined"}
        percent = sum(stage_weights[s] for s in achieved)
        rows.append({
            "gap_id": gap["gap_id"],
            "category": gap.get("category"),
            "owner": gap.get("primary_owner"),
            "percent_complete": percent,
            "stage": "acceptance_defined",
            "blockers": ["implementation/runtime evidence still required"],
            "tests_passed": 0,
            "tests_required": len(gap.get("acceptance", [])),
            "security_status": "required",
            "rollback_status": "required",
            "runtime_evidence_status": "missing",
            "risk": "unknown_until_tested",
            "priority": "high" if gap.get("status") != "repository_evidence_present" else "continuous_improvement",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "required_stages": stage_order,
        })
    red = False
    yellow = bool(rows) or gh.get("parity_complete") is False
    status = "red" if red else ("yellow" if yellow else "green")
    payload = {
        "schema": "dreamco.system_progress_status.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "system_build_status": status,
        "gap_count": len(rows),
        "average_gap_percent": round(sum(r["percent_complete"] for r in rows) / len(rows), 1) if rows else 100.0,
        "github_parity_status_counts": gh.get("status_counts", {}),
        "gauges": rows,
        "truth_boundary": cfg["truth_rule"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "status": status, "gaps": len(rows), "average_gap_percent": payload["average_gap_percent"], "output": str(OUT.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
