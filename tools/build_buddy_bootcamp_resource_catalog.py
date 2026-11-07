#!/usr/bin/env python3
"""Build/check the categorized user-selectable Buddy Bootcamp resource catalog."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from buddy.learning.bootcamp_resource_catalog import build_default_catalog

OUTPUT = ROOT / "website/data/buddy-bootcamp-resource-catalog.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(build_default_catalog(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != encoded:
            print(f"Bootcamp resource catalog is stale: {args.output}", file=sys.stderr)
            return 1
        print(f"Bootcamp resource catalog current: {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(encoded, encoding="utf-8")
    payload = json.loads(encoded)
    print(json.dumps({"output": str(args.output), "resources": payload["resource_count"],
                      "categories": payload["category_count"], "rea_included": True}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
