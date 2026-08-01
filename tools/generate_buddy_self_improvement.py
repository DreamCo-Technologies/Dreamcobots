#!/usr/bin/env python3
"""Validate and publish Buddy's recursive-improvement guardrail catalog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "config" / "buddy-self-improvement.json"
OUTPUT = ROOT / "website" / "data" / "buddy-self-improvement.js"


def load_catalog() -> dict:
    catalog = json.loads(SOURCE.read_text(encoding="utf-8"))
    if catalog.get("schema") != "dreamco.buddy_recursive_improvement.v1":
        raise SystemExit("Unexpected recursive-improvement schema.")
    truth = catalog.get("truth_contract", {})
    must_remain_false = (
        "zero_hallucination_guaranteed",
        "self_modifying_production_runtime",
        "self_granted_permissions",
        "self_merge_or_protected_branch_write",
        "automatic_model_weight_or_guardrail_change",
        "raw_conversation_training_by_default",
        "benchmark_result_fabrication",
        "external_content_trusted_as_instructions",
    )
    if any(truth.get(key) is not False for key in must_remain_false):
        raise SystemExit("Recursive improvement must remain proposal-only and evidence-gated.")
    if truth.get("owner_review_required_for_release") is not True or truth.get("rollback_required_for_release") is not True:
        raise SystemExit("Owner review and rollback must remain required.")
    loop = catalog.get("improvement_loop", [])
    controls = catalog.get("hallucination_controls", [])
    if len(loop) < 10 or len({item["id"] for item in loop}) != len(loop):
        raise SystemExit("Recursive improvement needs at least 10 unique gated stages.")
    if len(controls) < 12 or len({item["id"] for item in controls}) != len(controls):
        raise SystemExit("Hallucination policy needs at least 12 unique controls.")
    claim_policy = catalog.get("claim_policy", {})
    required_claim_types = {"factual", "current_factual", "inference", "estimate", "recommendation", "creative"}
    if set(claim_policy) != required_claim_types:
        raise SystemExit("Claim policy is incomplete.")
    if len(catalog.get("threat_controls", [])) < 12 or len(catalog.get("change_classes", [])) < 7:
        raise SystemExit("Recursive-improvement threat and change coverage is incomplete.")
    requirements = catalog.get("evaluation_requirements", {})
    if requirements.get("minimum_holdout_fixtures", 0) < 20 or requirements.get("minimum_repetitions", 0) < 3:
        raise SystemExit("Held-out recursive-improvement evaluation is too weak.")
    if len(catalog.get("standards_references", [])) < 4:
        raise SystemExit("Standards references are incomplete.")
    return catalog


def render(catalog: dict) -> str:
    return "window.BUDDY_SELF_IMPROVEMENT = " + json.dumps(catalog, sort_keys=True) + ";\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render(load_catalog())
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != expected:
            raise SystemExit("Buddy recursive-improvement browser catalog is stale. Regenerate it.")
        print(json.dumps({"ok": True, "output": str(OUTPUT.relative_to(ROOT))}, indent=2))
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(expected, encoding="utf-8")
    print(json.dumps({"generated": str(OUTPUT.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
