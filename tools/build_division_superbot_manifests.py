#!/usr/bin/env python3
"""Build one normalized manifest per Division Superbot.

The builder is intentionally loss-minimizing: source profiles are retained as
provenance and only normalized fields are synthesized. It never deletes source
files. Ambiguous ownership stays reviewable.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "superbot-consolidation-v1.json"
INVENTORY = ROOT / "config" / "generated" / "superbot-repository-inventory.json"
OUT = ROOT / "config" / "divisions"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def main() -> int:
    config = load_json(CONFIG)
    if not INVENTORY.exists():
        raise SystemExit("Missing inventory. Run tools/build_superbot_repository_inventory.py first.")
    inventory = load_json(INVENTORY)
    records = inventory.get("records", [])
    OUT.mkdir(parents=True, exist_ok=True)

    divisions = config.get("division_superbots", [])
    written = 0
    for division in divisions:
        division_name = division["division"]
        division_id = division["id"]
        cluster = division["cluster"]
        owned_files = [r for r in records if r.get("proposed_superbot") == cluster or r.get("division") == division_name]
        bot_profiles = [r["path"] for r in owned_files if r.get("is_bot_named")]
        manifest = {
            "schema": "dreamco.division_superbot.v1",
            "version": "1.0.0",
            "identity": {
                "id": division_id,
                "displayName": f"{division_name} Superbot",
                "division": division_name,
                "cluster": cluster,
            },
            "mission": f"Own, coordinate and continuously improve the capabilities assigned to {division_name} while preserving compatibility and governed execution.",
            "userJobs": [],
            "capabilities": [],
            "tools": [],
            "connectors": [],
            "policies": {
                "externalWritesDefault": "disabled",
                "approvalRequiredForHighImpact": True,
                "secretPolicy": "secrets-never-in-source",
            },
            "dependencies": [],
            "workflows": [],
            "benchmarks": [],
            "commercial": {"revenueModels": [], "outcomeMetrics": []},
            "migration": {
                "legacyProfiles": sorted(set(bot_profiles)),
                "legacyFiles": sorted(set(r["path"] for r in owned_files)),
                "aliases": [],
                "provenanceRequired": True,
            },
            "status": "cataloged",
            "notes": [
                "Generated from repository inventory; domain-specific mission, capabilities and evidence must be enriched before production certification.",
                "Do not delete source artifacts during manifest generation.",
            ],
        }
        (OUT / f"{slug(division_name)}.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        written += 1

    print(f"Generated {written} Division Superbot manifests in {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
