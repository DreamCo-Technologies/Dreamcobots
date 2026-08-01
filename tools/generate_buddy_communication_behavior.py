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
    if len(catalog.get("benchmark_suites", [])) < 18:
        raise SystemExit("The communication catalog needs at least 18 benchmark suites.")
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
