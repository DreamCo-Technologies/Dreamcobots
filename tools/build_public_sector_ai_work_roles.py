#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOV = json.loads((ROOT / "config" / "government-nonprofit-contract-readiness.json").read_text(encoding="utf-8"))
OUT = ROOT / "config" / "generated" / "public-sector-ai-work-roles.json"


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def main() -> int:
    roles = []
    for family in GOV["government_job_families"]:
        rid = f"ai-public-work:{slug(family)}"
        roles.append({
            "role_id": rid,
            "human_job_family": family,
            "role_name": f"Buddy {family.title()} Work Assistant",
            "status": "sandbox_only_until_evidence",
            "work_modes": ["research", "draft", "organize", "analyze", "quality_check", "workflow_assist", "human_handoff"],
            "prohibited_authority": GOV["high_risk_human_authority"],
            "required_benchmark": {
                "baseline": ["human_minutes", "error_rate", "rework_rate", "throughput", "cost_basis"],
                "assisted": ["human_minutes", "AI_compute_cost", "error_rate", "rework_rate", "throughput", "review_minutes"],
                "acceptance": ["correctness_not_worse", "security_privacy_pass", "human_authority_preserved", "measurable_time_or_cost_value"],
            },
            "savings_claim_rule": "No labor/time/cost saving claim until baseline and assisted workflow are measured on representative tasks.",
            "employment_rule": "A task-efficiency benchmark does not determine staffing, job elimination, hiring, firing, or workforce policy.",
        })
    payload = {
        "schema": "dreamco.public_sector_ai_work_roles.v1",
        "role_count": len(roles),
        "roles": roles,
        "goal": "Create AI-assisted work roles that can prove administrative productivity and service-quality improvements while preserving authorized human responsibility.",
        "truth_boundary": GOV["truth_rule"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "roles": len(roles), "output": str(OUT.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
