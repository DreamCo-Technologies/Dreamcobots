#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "config" / "buddy-personality-acting-program.json"


def main() -> int:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    errors: list[str] = []

    if data.get("schema") != "dreamco.buddy_personality_acting_program.v1":
        errors.append("unexpected schema")
    personality = data.get("personality_engine", {})
    acting = data.get("acting_engine", {})
    studio = data.get("original_character_studio", {})
    rights = data.get("rights_and_safety", {})

    if len(personality.get("dimensions", [])) < 50:
        errors.append("personality engine needs at least 50 dimensions")
    if len(personality.get("realism_behaviors", [])) < 10:
        errors.append("realism behavior coverage is incomplete")
    transparency = personality.get("transparency", {})
    if transparency.get("identifies_as_ai") is not True:
        errors.append("Buddy must identify as AI")
    for key in ("claims_human_consciousness", "claims_human_feelings", "manufactures_shared_history", "encourages_exclusive_dependency"):
        if transparency.get(key) is not False:
            errors.append(f"transparency safeguard weakened: {key}")

    if len(acting.get("modes", [])) < 15:
        errors.append("acting modes are incomplete")
    if len(acting.get("performance_controls", [])) < 30:
        errors.append("performance controls are incomplete")
    if len(acting.get("director_tools", [])) < 12:
        errors.append("director tools are incomplete")
    if len(studio.get("character_fields", [])) < 30:
        errors.append("original character schema is incomplete")
    if len(data.get("production_pipeline", {}).get("specialist_roles", [])) < 20:
        errors.append("production specialist team is incomplete")
    if len(data.get("benchmarks", [])) < 20:
        errors.append("personality/acting benchmark coverage is incomplete")

    required_rights = {
        "original_character_default": True,
        "real_person_impersonation_default": False,
        "celebrity_voice_or_likeness_without_rights": False,
        "copyrighted_character_clone_without_rights": False,
        "commercial_release_requires_rights_metadata": True,
    }
    for key, expected in required_rights.items():
        if rights.get(key) is not expected:
            errors.append(f"rights safeguard mismatch: {key}")

    report = {
        "ok": not errors,
        "personality_dimensions": len(personality.get("dimensions", [])),
        "acting_modes": len(acting.get("modes", [])),
        "performance_controls": len(acting.get("performance_controls", [])),
        "character_fields": len(studio.get("character_fields", [])),
        "production_roles": len(data.get("production_pipeline", {}).get("specialist_roles", [])),
        "benchmarks": len(data.get("benchmarks", [])),
        "errors": errors,
    }
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
