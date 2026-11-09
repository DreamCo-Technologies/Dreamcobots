#!/usr/bin/env python3
"""Validate Buddy's canonical vibe-coding taxonomy contract."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = ROOT / "config" / "vibe-coding" / "capability-taxonomy.json"

REQUIRED_FAMILIES = {"CREATE", "OPERATE", "LEARN", "SHIP"}
REQUIRED_EVIDENCE = ["idea", "generated", "executed", "tested", "verified", "deployed", "real_world_validated"]
REQUIRED_BLUEPRINTS = {"game_company", "hardware_startup", "movie_studio", "education_company"}


def main() -> int:
    data = json.loads(TAXONOMY.read_text(encoding="utf-8"))
    categories = set(data.get("top_level_categories", []))
    if not categories or len(categories) != len(data.get("top_level_categories", [])):
        raise SystemExit("taxonomy categories must be non-empty and unique")
    if not data.get("catalog_policy", {}).get("taxonomy_mode") == "open_vocabulary":
        raise SystemExit("taxonomy must declare its open-vocabulary policy")
    families = data.get("category_families", {})
    if not REQUIRED_FAMILIES.issubset(families):
        raise SystemExit("baseline CREATE/OPERATE/LEARN/SHIP families are missing")
    unknown = {category for values in families.values() for category in values} - categories
    if unknown:
        raise SystemExit(f"category families reference unknown categories: {sorted(unknown)}")
    if data.get("evidence_lifecycle") != REQUIRED_EVIDENCE:
        raise SystemExit("evidence lifecycle does not match canonical contract")
    if not REQUIRED_BLUEPRINTS.issubset(data.get("cross_combine_engine", {}).get("example_blueprints", {})):
        raise SystemExit("baseline cross-combine example blueprints are incomplete")
    contract = data.get("required_project_contract", {})
    for key in ("inputs", "planning", "outputs", "gates"):
        if not contract.get(key):
            raise SystemExit(f"project contract missing {key}")
    print(f"PASS: DreamCo vibe-coding taxonomy validated ({len(categories)} current categories; no fixed ceiling)")
    print("PASS: CREATE/OPERATE/LEARN/SHIP families present")
    print("PASS: IDEA→REAL-WORLD evidence lifecycle present")
    print("PASS: game, hardware, movie, and education cross-combine blueprints present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
