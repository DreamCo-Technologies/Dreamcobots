#!/usr/bin/env python3
"""Collect bounded, read-only Keep Green evidence for scheduled diagnostics.

Never equate absent, stale, or malformed GitHub data with a passing gate.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import subprocess

REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def parse_time(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.astimezone(timezone.utc) if parsed.tzinfo else None


def observations(payload: object, *, now: datetime, max_age_hours: int) -> list[dict]:
    """Return at most one verified completed observation or a visible unknown."""
    if not isinstance(payload, dict) or not isinstance(payload.get("workflow_runs"), list):
        raise ValueError("GitHub workflow run response lacks workflow_runs array")
    if now.tzinfo is None or max_age_hours < 1 or max_age_hours > 24:
        raise ValueError("bounded, timezone-aware observation window required")
    cutoff = now.astimezone(timezone.utc) - timedelta(hours=max_age_hours)
    eligible = []
    for run in payload["workflow_runs"]:
        if not isinstance(run, dict):
            continue
        if run.get("name") != "Keep Green" or run.get("status") != "completed" or run.get("head_branch") != "main":
            continue
        completed_at = parse_time(run.get("updated_at"))
        if completed_at is None or not cutoff <= completed_at <= now.astimezone(timezone.utc):
            continue
        conclusion = run.get("conclusion")
        if conclusion not in {"success", "failure", "cancelled", "timed_out", "action_required", "stale", "skipped", "neutral"}:
            continue
        run_id = run.get("id")
        if isinstance(run_id, bool) or not isinstance(run_id, int) or run_id <= 0:
            continue
        eligible.append((completed_at, run_id, run))
    if not eligible:
        return [{"workflow": "Keep Green", "conclusion": "unknown", "source": "github_actions", "evidence_status": "no_recent_valid_completed_run"}]
    _, run_id, run = max(eligible, key=lambda row: (row[0], row[1]))
    return [{"workflow": "Keep Green", "conclusion": run["conclusion"], "source": "github_actions", "evidence_status": "observed", "run_id": run_id, "run_url": run.get("html_url", ""), "head_sha": run.get("head_sha", ""), "updated_at": run["updated_at"]}]


def collect(repo: str, *, now: datetime, max_age_hours: int) -> list[dict]:
    if not REPO_RE.fullmatch(repo):
        raise ValueError("GITHUB_REPOSITORY must be an owner/repo name")
    endpoint = f"repos/{repo}/actions/workflows/keep-green.yml/runs?status=completed&branch=main&per_page=30"
    result = subprocess.run(["gh", "api", endpoint], check=True, capture_output=True, text=True, timeout=30)
    return observations(json.loads(result.stdout), now=now, max_age_hours=max_age_hours)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-age-hours", type=int, default=6)
    args = parser.parse_args()
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    rows = collect(repo, now=datetime.now(timezone.utc), max_age_hours=args.max_age_hours)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rows, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
