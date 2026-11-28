"""Connect cited research and verified benchmark results to learning jobs/points."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from buddy.learning.research_benchmark_bridge import (ResearchBridgeError,
    research_benchmark_failure_to_learning_jobs, research_item_to_benchmark_candidate)


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ResearchBridgeError("Input JSON must contain one object.")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    candidate = subs.add_parser("candidate", help="Turn one sourced discovery into a benchmark proposal")
    candidate.add_argument("input", type=Path)
    failure = subs.add_parser("failure", help="Turn one verified benchmark failure into diagnostic learning jobs")
    failure.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        value = load_json(args.input)
        if args.command == "candidate":
            result = research_item_to_benchmark_candidate(value)
        else:
            result = research_benchmark_failure_to_learning_jobs(value)
        json.dump(result, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    except (OSError, json.JSONDecodeError, ResearchBridgeError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
