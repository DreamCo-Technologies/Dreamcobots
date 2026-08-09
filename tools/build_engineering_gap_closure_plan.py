#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEAM = ROOT / "config" / "engineering-gap-closure-team.json"
GH = ROOT / "config" / "generated" / "github-platform-parity-benchmark.json"
OUT = ROOT / "config" / "generated" / "engineering-gap-closure-plan.json"

CATEGORY_LANES = {
    "core_git": "platform_builder",
    "collaboration": "platform_builder",
    "automation": "ci_reliability_builder",
    "delivery": "deployment_builder",
    "developer_experience": "developer_experience_builder",
    "security_supply_chain": "security_builder",
    "governance": "chief_architect",
    "extensibility": "platform_builder",
    "ai_development": "agent_runtime_builder",
    "operations": "observability_builder",
    "community_open_source": "open_source_builder",
}


def main() -> int:
    team = json.loads(TEAM.read_text(encoding="utf-8"))
    if not GH.exists():
        raise SystemExit("Run tools/build_github_platform_benchmark.py first")
    gh = json.loads(GH.read_text(encoding="utf-8"))
    gaps = []
    owner_counts = defaultdict(int)
    max_lanes = int(team["parallel_policy"]["maximum_parallel_lanes"])

    candidates = [row for row in gh["capabilities"] if row.get("status") != "repository_evidence_present"]
    for index, row in enumerate(candidates):
        owner = CATEGORY_LANES.get(row.get("category"), "chief_architect")
        owner_counts[owner] += 1
        gaps.append({
            "gap_id": f"github-{row['id']}",
            "source": "github_platform_parity",
            "capability": row["id"],
            "category": row.get("category"),
            "status": row.get("status"),
            "primary_owner": owner,
            "parallel_slot": (index % max_lanes) + 1,
            "acceptance": row["gap_builder_plan"]["acceptance"],
            "next_step": row["gap_builder_plan"]["next_step"],
            "required_reviewers": ["security_builder", "sandbox_qa_builder", "release_reviewer"],
            "completion_gate": team["completion_gate"],
        })

    payload = {
        "schema": "dreamco.engineering_gap_closure_plan.v1",
        "gap_count": len(gaps),
        "parallel_slots": min(max_lanes, max(1, len(gaps))),
        "owner_load": dict(sorted(owner_counts.items())),
        "gaps": gaps,
        "parallel_policy": team["parallel_policy"],
        "truth_boundary": team["truth_rule"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "gaps": len(gaps), "parallel_slots": payload["parallel_slots"], "owner_load": payload["owner_load"], "output": str(OUT.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
