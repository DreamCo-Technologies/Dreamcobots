#!/usr/bin/env python3
"""Static regression checks for the PR Recovery Engine contract."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/pr-recovery-engine.yml"
ENGINE = ROOT / "tools/pr_recovery_engine.py"


def main() -> int:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    engine = ENGINE.read_text(encoding="utf-8")
    assert 'cron: "17 3,15 * * *"' in workflow, "recovery must run twice daily"
    assert 'pull-requests: write' in workflow
    assert 'contents: write' in workflow
    assert "--limit \"${{ inputs.max_prs || '1000' }}\"" in workflow
    for required in (
        "never_force_resolve",
        "never_discard_conflicting_changes",
        "preserve_all_source_changes",
        "skip_exactly_present_heads",
        "blocked_conflict",
        "already_present",
        "replayable",
    ):
        assert required in engine, f"missing recovery contract: {required}"
    print(json.dumps({"status": "pass", "checks": 10}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
