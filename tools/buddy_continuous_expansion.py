#!/usr/bin/env python3
"""Generate additive DreamCo expansion proposals without deleting existing assets."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config" / "buddy_continuous_expansion.json"
LIBRARIES = ROOT / "data" / "library_specialists.seed.json"
BOT_DIR = ROOT / "App_bots"

INVENTED_SYSTEMS = [
    ("library-compatibility-bot", "Maps version compatibility and migration risks across libraries."),
    ("dependency-conflict-bot", "Finds conflicting dependency requirements and proposes isolated resolutions."),
    ("package-license-bot", "Tracks package licenses and flags incompatible usage plans."),
    ("api-drift-bot", "Detects API and documentation drift before upgrades break production."),
    ("international-registry-scout-bot", "Discovers relevant non-US and non-English package ecosystems and official registries."),
    ("company-capability-gap-bot", "Compares technology-company offerings with DreamCo capability coverage."),
    ("innovation-composer-bot", "Combines certified primitives from multiple specialists into testable new product ideas."),
    ("specialist-certification-bot", "Promotes specialist capabilities only when required evidence gates pass."),
    ("benchmark-evidence-bot", "Builds repeatable evidence packets for capability, cost, latency, and reliability comparisons."),
    ("ecosystem-translator-bot", "Maps equivalent tools and patterns between programming ecosystems."),
]


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def existing_bot_slugs() -> set[str]:
    slugs: set[str] = set()
    if not BOT_DIR.exists():
        return slugs
    for path in sorted(BOT_DIR.glob("*.json")):
        data = load_json(path, {})
        for bot in data.get("bots", []):
            slug = bot.get("slug")
            if isinstance(slug, str):
                slugs.add(slug)
    return slugs


def library_bot_proposals(records: list[dict[str, Any]]) -> list[dict[str, str]]:
    proposals = []
    for record in records:
        ecosystem = record.get("ecosystem", "unknown")
        package = record.get("package", "unknown")
        proposals.append({
            "id": f"library-specialist:{ecosystem}:{package}",
            "kind": "library_specialist",
            "name": f"{package} Specialist Bot",
            "source": f"{ecosystem}:{package}",
            "status": "proposed_until_certified",
        })
    return proposals


def build_expansion_plan() -> dict[str, Any]:
    policy = load_json(POLICY, {})
    libraries = load_json(LIBRARIES, [])
    slugs = existing_bot_slugs()
    invented = [
        {
            "id": slug,
            "kind": "invented_bot",
            "name": slug.replace("-", " ").title(),
            "description": description,
            "status": "already_exists" if slug in slugs else "proposed",
        }
        for slug, description in INVENTED_SYSTEMS
    ]
    return {
        "schema": "dreamco.buddy_expansion_plan.v1",
        "preserve_existing": bool(policy.get("preserve_existing", True)),
        "existing_bot_count_detected": len(slugs),
        "library_specialist_proposals": library_bot_proposals(libraries),
        "invented_system_proposals": invented,
        "rules": policy.get("rules", []),
    }


def main() -> int:
    plan = build_expansion_plan()
    print(json.dumps(plan, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
