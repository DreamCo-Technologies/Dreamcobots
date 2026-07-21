#!/usr/bin/env python3
"""Run Buddy's local evidence-scored innovation loop for one objective."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dreamco_platform.innovation import InnovationEngine, InnovationRequest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("objective")
    parser.add_argument("--audience", default="DreamCo user")
    parser.add_argument("--mode", choices=["balanced", "bold", "trusted", "lean"], default="balanced")
    parser.add_argument("--tag", action="append", default=[])
    parser.add_argument("--constraint", action="append", default=[])
    args = parser.parse_args()
    result = InnovationEngine().run(
        InnovationRequest(
            objective=args.objective,
            audience=args.audience,
            mode=args.mode,
            tags=tuple(args.tag),
            constraints=tuple(args.constraint),
        )
    )
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
