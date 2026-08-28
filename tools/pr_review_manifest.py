#!/usr/bin/env python3
"""Generate a deterministic PR-review manifest from GitHub API JSON.

This tool deliberately reports unknown states instead of inventing CI, runtime,
security, or benchmark results. It is safe to run locally or in Actions.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

STATES = {"verified", "implemented_unverified", "partial", "planned", "blocked", "not_applicable"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr-json", required=True)
    parser.add_argument("--output", default="artifacts/pr-review/manifest.json")
    args = parser.parse_args()

    source = json.loads(Path(args.pr_json).read_text(encoding="utf-8"))
    manifest = {
        "schema": "dreamco.pr_review_manifest.v1",
        "pr": source.get("number"),
        "title": source.get("title"),
        "mergeability": source.get("mergeable") or "unknown",
        "merge_state": source.get("mergeStateStatus") or "unknown",
        "checks": {
            "ci": "unknown",
            "security": "unknown",
            "benchmarks": "unknown",
            "regression": "unknown",
            "deployment": "unknown",
        },
        "decision": "blocked_until_evidence",
        "truth_rule": "unknown is never green",
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
