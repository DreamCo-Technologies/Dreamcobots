#!/usr/bin/env python3
"""Generate the browser-safe Buddy Media Quality Lab catalog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "config" / "buddy-media-quality-lab.json"
OUTPUT = ROOT / "website" / "data" / "buddy-media-quality-lab.js"


def render() -> str:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    serialized = json.dumps(payload, indent=2, ensure_ascii=True, sort_keys=True)
    return f"window.BUDDY_MEDIA_QUALITY_LAB = {serialized};\n"


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
