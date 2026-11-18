#!/usr/bin/env python3
"""Generate the Wikipedia discovery map for every registered goal and benchmark."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from buddy.learning.wikipedia_learning_bridge import build_default_target_map


OUTPUT = ROOT / "website" / "data" / "wikipedia-learning-target-map.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true", help="Fail if generated map is stale")
    args = parser.parse_args()
    encoded = json.dumps(build_default_target_map(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != encoded:
            print(f"Generated Wikipedia learning map is stale: {args.output}", file=sys.stderr)
            return 1
        print(f"Wikipedia learning map current: {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(encoded, encoding="utf-8")
    print(f"Generated Wikipedia learning map: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
