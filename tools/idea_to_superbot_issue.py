#!/usr/bin/env python3
"""Generate a governed idea intake record.

This tool deliberately prepares work; it does not merge code, deploy software,
or bypass approval gates.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "config" / "idea_queue"


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:80]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("idea")
    parser.add_argument("--division", default="unassigned")
    parser.add_argument("--value", default="")
    parser.add_argument("--risk", choices=["low", "medium", "high", "critical"], default="medium")
    args = parser.parse_args()

    now = datetime.now(timezone.utc).isoformat()
    record = {
        "schema": "dreamco.idea.v1",
        "id": f"idea-{slug(args.idea)}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "createdAt": now,
        "source": "human-approved-idea",
        "idea": args.idea,
        "targetDivision": args.division,
        "expectedOutcome": args.value,
        "risk": args.risk,
        "status": "triage",
        "relatedCapabilities": [],
        "evidence": [],
        "builderTasks": ["scout", "architect", "research", "implementation", "test", "security", "performance", "revenue", "release"],
        "approvalRequired": args.risk in {"high", "critical"},
    }
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{record['id']}.json"
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
