"""Bounded research/evaluation runner for Buddy's continuous gap loop.

This runner intentionally does not modify production code, grant permissions,
or execute instructions obtained from the web. It creates checkpoints for the
existing learning/evaluation pipeline to consume.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / os.getenv("BUDDY_GAP_CONFIG", "config/buddy-24h-gap-closure-bot.json")
OUT = ROOT / "artifacts" / "buddy-gap-closure"


def main() -> None:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    max_sources = int(os.getenv("BUDDY_MAX_SOURCES", "250"))
    max_workers = int(os.getenv("BUDDY_MAX_WORKERS", "20"))
    sandbox_only = os.getenv("BUDDY_SANDBOX_ONLY", "true").lower() == "true"

    checkpoint = {
        "schema": "dreamco.buddy_gap_checkpoint.v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "bot_id": config["bot_id"],
        "mode": "sandbox_only" if sandbox_only else "blocked",
        "max_sources": max_sources,
        "max_parallel_workers": max_workers,
        "source_discovery": "delegated_to_governed_source_adapters",
        "evaluation": "delegated_to_frontier_evaluation_harness",
        "production_changes": "disabled",
        "web_content_is_untrusted": True,
        "next_steps": [
            "load capability-gap inventory",
            "select highest-value open gaps",
            "discover permitted sources",
            "create isolated learning jobs",
            "run baseline and post-learning tests",
            "record evidence and measurable gain",
            "requeue unresolved gaps",
        ],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "latest-checkpoint.json").write_text(
        json.dumps(checkpoint, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(checkpoint, indent=2))


if __name__ == "__main__":
    main()
