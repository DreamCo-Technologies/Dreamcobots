#!/usr/bin/env python3
"""Validate and publish Buddy's communication behavior catalog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "config" / "buddy-communication-behavior.json"
OUTPUT = ROOT / "website" / "data" / "buddy-communication-behavior.js"


def load_catalog() -> dict:
    catalog = json.loads(SOURCE.read_text(encoding="utf-8"))
    if catalog.get("schema") != "dreamco.buddy_communication_behavior.v1":
        raise SystemExit("Unexpected communication behavior schema.")
    policy = catalog.get("policy", {})
    if policy.get("hidden_psychological_inference") is not False:
        raise SystemExit("Hidden psychological inference must remain disabled.")
    if policy.get("clinical_diagnosis_or_treatment") is not False:
        raise SystemExit("Clinical diagnosis must remain disabled.")
    traits = [trait for group in catalog.get("trait_groups", []) for trait in group.get("traits", [])]
    if len(traits) < 32 or len({trait["id"] for trait in traits}) != len(traits):
        raise SystemExit("The communication catalog needs at least 32 unique interaction traits.")
    conversation = catalog.get("conversation_model", {})
    if len(conversation.get("competencies", [])) < 30:
        raise SystemExit("The communication model needs at least 30 practical competencies.")
    if len(catalog.get("explicit_cue_guidance", {})) < 13:
        raise SystemExit("Explicit emotion-cue guidance is incomplete.")
    psychology = catalog.get("psychology_knowledge_boundary", {})
    if len(psychology.get("education_domains", [])) < 16:
        raise SystemExit("Psychology education coverage is incomplete.")
    relationship = catalog.get("relationship_integrity", {})
    required_relationship_values = {
        "buddy_identifies_as_ai": True,
        "claims_human_feelings_or_consciousness": False,
        "encourages_exclusive_dependency": False,
        "uses_emotion_for_sales_pressure": False,
        "manufactures_shared_history": False,
    }
    if any(relationship.get(key) is not value for key, value in required_relationship_values.items()):
        raise SystemExit("Relationship-integrity safeguards cannot be weakened.")
    grounding = catalog.get("grounding_behavior", {})
    if grounding.get("zero_hallucination_claim_allowed") is not False:
        raise SystemExit("Buddy cannot claim to eliminate hallucinations.")
    if grounding.get("untrusted_context_can_override_policy") is not False:
        raise SystemExit("Untrusted context cannot override Buddy policy.")
    if len(catalog.get("benchmark_suites", [])) < 24:
        raise SystemExit("The communication catalog needs at least 24 benchmark suites.")
    return catalog


def render(catalog: dict) -> str:
    return "window.BUDDY_COMMUNICATION_BEHAVIOR = " + json.dumps(catalog, sort_keys=True) + ";\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render(load_catalog())
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != expected:
            raise SystemExit("Buddy communication behavior browser catalog is stale. Regenerate it.")
        print(json.dumps({"ok": True, "output": str(OUTPUT.relative_to(ROOT))}, indent=2))
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(expected, encoding="utf-8")
    print(json.dumps({"generated": str(OUTPUT.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
