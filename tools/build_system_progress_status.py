#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config" / "system-progress-gauges.json"
GAPS = ROOT / "config" / "generated" / "engineering-gap-closure-plan.json"
GH = ROOT / "config" / "generated" / "github-platform-parity-benchmark.json"
REVENUE = ROOT / "config" / "generated" / "live-revenue-readiness.json"
MARKET = ROOT / "website" / "data" / "manufacturer-marketplace.json"
CERT = ROOT / "config" / "generated" / "full-system-operational-certification.json"
OUT = ROOT / "config" / "generated" / "system-progress-status.json"


def read_json(path: Path, fallback: dict) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else fallback


def main() -> int:
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    gaps = read_json(GAPS, {"gaps": []})
    gh = read_json(GH, {"status_counts": {}, "parity_complete": False})
    revenue = read_json(REVENUE, {"bot_count": 0, "live_enabled_count": 0, "eligible_pending_owner_count": 0})
    market = read_json(MARKET, {"status": "not_generated", "manufacturer_count": 0, "rfq_count": 0, "quote_count": 0, "opportunity_count": 0})
    cert = read_json(CERT, {"status": "not_run", "core_operational_certified": False, "fully_operational_and_connected_claim_allowed": False, "speed_summary": {}, "accuracy_summary": {}, "connection_summary": {}})

    stage_weights = {row["id"]: int(row["weight"]) for row in cfg["gap_stages"]}
    stage_order = [row["id"] for row in cfg["gap_stages"]]
    rows = []
    for gap in gaps.get("gaps", []):
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

    if cert.get("status") == "blocked":
        status = "red"
    elif cert.get("core_operational_certified") is True and cert.get("fully_operational_and_connected_claim_allowed") is True and not rows and gh.get("parity_complete") is True:
        status = "green"
    else:
        status = "yellow"

    payload = {
        "schema": "dreamco.system_progress_status.v3",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "system_build_status": status,
        "full_system_certification": {
            "status": cert.get("status", "not_run"),
            "core_operational_certified": cert.get("core_operational_certified", False),
            "fully_operational_and_connected_claim_allowed": cert.get("fully_operational_and_connected_claim_allowed", False),
            "speed": cert.get("speed_summary", {}),
            "accuracy": cert.get("accuracy_summary", {}),
            "connections": cert.get("connection_summary", {}),
            "release_blockers": cert.get("release_blockers", []),
        },
        "gap_count": len(rows),
        "average_gap_percent": round(sum(r["percent_complete"] for r in rows) / len(rows), 1) if rows else 100.0,
        "github_parity_status_counts": gh.get("status_counts", {}),
        "live_revenue": {
            "bots_checked": revenue.get("bot_count", 0),
            "live_enabled": revenue.get("live_enabled_count", 0),
            "eligible_pending_owner": revenue.get("eligible_pending_owner_count", 0),
        },
        "manufacturer_marketplace": {
            "status": market.get("status", "not_generated"),
            "verified_manufacturers": market.get("manufacturer_count", 0),
            "rfqs": market.get("rfq_count", 0),
            "quotes": market.get("quote_count", 0),
            "opportunities": market.get("opportunity_count", 0),
            "authorized_source_adapters_planned": len(market.get("source_adapters", [])),
            "sandbox_checks_planned": len(market.get("sandbox_requirements", [])),
        },
        "gauges": rows,
        "truth_boundary": cfg["truth_rule"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "status": status,
        "certification": payload["full_system_certification"]["status"],
        "gaps": len(rows),
        "average_gap_percent": payload["average_gap_percent"],
        "output": str(OUT.relative_to(ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
