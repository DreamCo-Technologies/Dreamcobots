#!/usr/bin/env python3
"""Validate Buddy's canonical vibe-coding taxonomy contract."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = ROOT / "config" / "vibe-coding" / "capability-taxonomy.json"

REQUIRED_CATEGORIES = {
    "Games", "Software", "Websites", "Mobile Apps", "AI & Agents", "Education", "Video", "Movies & Film", "Advertising", "Social Media",
    "Writing & Publishing", "Design", "Hardware", "Electrical Engineering", "Manufacturing", "Robotics", "Smart Home / IoT", "Automotive",
    "Engineering", "Business", "Finance / FinTech", "E-Commerce", "Real Estate", "Healthcare Technology", "Science", "Environment",
    "Maps / Geography", "Travel", "Music", "Audio", "VR / AR / XR", "Simulation", "Aerospace / Space", "Cybersecurity", "Cloud / Infrastructure",
    "Developer Tools", "APIs / Platforms", "Data", "Analytics", "Productivity", "Government / Civic Tech", "Legal Technology", "Career / Workforce",
    "Local Business Systems", "Logistics", "Industrial Automation", "Virtual Worlds", "Creator Economy", "News / Media", "Physical Products",
}

REQUIRED_FAMILIES = {"CREATE", "OPERATE", "LEARN", "SHIP"}
REQUIRED_EVIDENCE = ["idea", "generated", "executed", "tested", "verified", "deployed", "real_world_validated"]
REQUIRED_BLUEPRINTS = {"game_company", "hardware_startup", "movie_studio", "education_company"}


def main() -> int:
    data = json.loads(TAXONOMY.read_text(encoding="utf-8"))
    categories = set(data.get("top_level_categories", []))
    missing = sorted(REQUIRED_CATEGORIES - categories)
    extra = sorted(categories - REQUIRED_CATEGORIES)
    if len(categories) != 50 or missing or extra:
        raise SystemExit(f"taxonomy categories invalid: count={len(categories)} missing={missing} extra={extra}")
    if set(data.get("category_families", {})) != REQUIRED_FAMILIES:
        raise SystemExit("taxonomy category families must be exactly CREATE/OPERATE/LEARN/SHIP")
    if data.get("evidence_lifecycle") != REQUIRED_EVIDENCE:
        raise SystemExit("evidence lifecycle does not match canonical contract")
    if set(data.get("cross_combine_engine", {}).get("example_blueprints", {})) != REQUIRED_BLUEPRINTS:
        raise SystemExit("cross-combine example blueprints are incomplete")
    contract = data.get("required_project_contract", {})
    for key in ("inputs", "planning", "outputs", "gates"):
        if not contract.get(key):
            raise SystemExit(f"project contract missing {key}")
    print(f"PASS: DreamCo vibe-coding taxonomy validated ({len(categories)} categories)")
    print("PASS: CREATE/OPERATE/LEARN/SHIP families present")
    print("PASS: IDEA→REAL-WORLD evidence lifecycle present")
    print("PASS: game, hardware, movie, and education cross-combine blueprints present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
