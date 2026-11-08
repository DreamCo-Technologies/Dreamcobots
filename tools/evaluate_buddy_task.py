#!/usr/bin/env python3
"""Score a same-task Buddy, wrapper, and distilled-student evaluation record."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from buddy_os.benchmarks.task_evaluation import evaluate_task


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Versioned task-evaluation JSON input")
    parser.add_argument("--output", default="buddy-task-evaluation-result.json")
    parser.add_argument("--minimum-quality-score", type=float, default=75.0)
    args = parser.parse_args()

    record = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = evaluate_task(record, minimum_score=args.minimum_quality_score)
    output = Path(args.output)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "evaluation_id": result["evaluation_id"],
        "task_id": result["task_id"],
        "buddy_status": result["candidates"]["buddy"]["status"],
        "buddy_quality_score": result["candidates"]["buddy"]["quality_score"],
        "learning_score": result["candidates"]["buddy"]["learning_score"],
        "output": str(output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
