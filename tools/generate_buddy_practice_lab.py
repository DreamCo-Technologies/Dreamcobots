#!/usr/bin/env python3
"""Generate the browser-safe Buddy practice catalog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "config" / "buddy-practice-lab.json"
OUTPUT = ROOT / "website" / "data" / "buddy-practice-lab.js"


def load_catalog() -> dict:
    catalog = json.loads(SOURCE.read_text(encoding="utf-8"))
    if catalog.get("schema") != "dreamco.buddy_practice_lab.v1":
        raise SystemExit("Unexpected Buddy practice catalog schema.")
    modes = catalog.get("modes", [])
    if len(modes) < 9 or len({mode["id"] for mode in modes}) != len(modes):
        raise SystemExit("Buddy practice needs nine unique modes.")
    if any(len(mode.get("questions", [])) < 6 or not mode.get("specialists") for mode in modes):
        raise SystemExit("Every practice mode needs specialists and at least six questions.")
    if len(catalog.get("hard_boundaries", [])) < 7:
        raise SystemExit("Buddy practice boundaries are incomplete.")
    return catalog


def render() -> str:
    payload = json.dumps(load_catalog(), indent=2, ensure_ascii=True, sort_keys=True)
    return f"window.BUDDY_PRACTICE_LAB = {payload};\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"Generated file is stale: {OUTPUT.relative_to(ROOT)}")
        print(f"Verified {OUTPUT.relative_to(ROOT)}")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"Generated {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
