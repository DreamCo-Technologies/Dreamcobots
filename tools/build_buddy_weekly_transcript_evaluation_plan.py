#!/usr/bin/env python3
"""Build a metadata-only weekly queue for rights-cleared Buddy transcripts."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from buddy.learning.transcript_evaluation_scheduler import (  # noqa: E402
    build_weekly_transcript_evaluation_plan,
    validate_weekly_transcript_evaluation_plan,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", default="config/generated/freecodecamp-youtube-catalog.json")
    parser.add_argument("--output", default="artifacts/buddy-dataset-hub/weekly-transcript-evaluation-plan.json")
    parser.add_argument("--week-start")
    args = parser.parse_args()

    catalog = json.loads(Path(args.catalog).read_text(encoding="utf-8"))
    plan = build_weekly_transcript_evaluation_plan(catalog, args.week_start)
    validate_weekly_transcript_evaluation_plan(plan)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "eligible_transcripts": plan["eligible_transcript_count"],
        "blocked_transcripts": plan["blocked_transcript_count"],
        "frequency": plan["frequency"],
        "status": plan["status"],
        "buddy_evaluation_executed": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
