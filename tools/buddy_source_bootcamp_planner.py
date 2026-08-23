"""Build a cost-aware study/source queue for Buddy's 1000-source bootcamp.

This planner does not fetch the web and never treats source text as authority.
It ranks already-registered sources against capability gaps and emits jobs for
separate governed adapters/sandboxes to execute.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config" / "buddy-web-source-registry.json"
BOOTCAMP = ROOT / "config" / "buddy-1000-source-bootcamp.json"
OUT = ROOT / "artifacts" / "buddy-source-bootcamp"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def source_score(source: dict, gaps: list[str]) -> float:
    domains = {str(x).lower() for x in source.get("domains", [])}
    gap_terms = {x.lower() for x in gaps}
    fit = sum(1 for term in gap_terms if term in domains or any(term in d for d in domains))
    tier = source.get("tier", "community")
    authority = {"primary_authoritative": 1.0, "education": 0.85, "research": 0.85,
                 "open_web_archive": 0.55, "community": 0.45}.get(tier, 0.4)
    return round(authority + min(fit, 5) * 0.15, 4)


def main() -> None:
    registry = load_json(REGISTRY)
    bootcamp = load_json(BOOTCAMP)
    gaps = [x.strip() for x in os.getenv("BUDDY_CAPABILITY_GAPS", "software-engineering,ai,agents,security,cloud,data,web").split(",") if x.strip()]
    limit = int(os.getenv("BUDDY_SOURCE_QUEUE_SIZE", "25"))

    sources = registry.get("sources", [])
    ranked = sorted(
        (
            {
                "source_id": s.get("id"),
                "url": s.get("url"),
                "tier": s.get("tier"),
                "domains": s.get("domains", []),
                "score": source_score(s, gaps),
                "gaps": gaps,
                "action": "discover_verify_ingest_generate_original_tasks_sandbox_validate",
            }
            for s in sources
        ),
        key=lambda item: (-item["score"], item["source_id"] or ""),
    )[:limit]

    plan = {
        "schema": "dreamco.buddy.source_bootcamp_plan.v1",
        "target_source_count": bootcamp["source_policy"]["target_count"],
        "registered_source_count": len(sources),
        "capability_gaps": gaps,
        "queue_size": len(ranked),
        "cost_policy": bootcamp["cost_aware_scheduler"],
        "mastery_gate": bootcamp["mastery_gate"],
        "jobs": ranked,
        "next_expansion": "Fill remaining verified source slots by capability-gap demand; never create fake source records merely to reach 1000.",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "latest-plan.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(plan, indent=2))


if __name__ == "__main__":
    main()
