#!/usr/bin/env python3
"""Inventory the eight Buddy recovery lanes. Missing evidence is not a pass."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LANES = [
    {
        "id": "detect",
        "paths": [
            ".github/workflows/actions-failure-sweep.yml",
            ".github/workflows/keep-green.yml",
        ],
    },
    {
        "id": "branch",
        "paths": [
            ".github/workflows/branch-health-daily.yml",
            "tools/branch_health_daily.py",
        ],
    },
    {
        "id": "pr",
        "paths": [
            ".github/workflows/pr-recovery-engine.yml",
            "tools/pr_recovery_engine.py",
        ],
    },
    {
        "id": "actions",
        "paths": [
            ".github/workflows/actions-failure-watch.yml",
            ".github/workflows/actions-green-contract.yml",
        ],
    },
    {
        "id": "pages",
        "paths": [
            "website/buddy.html",
            "website/index.html",
            "website/recover.html",
            ".github/workflows/pages.yml",
        ],
    },
    {
        "id": "runtime",
        "paths": ["website/buddy.js", "website/command.html"],
    },
    {
        "id": "catalog",
        "paths": [
            "website/data/buddy-connection-catalog.json",
            "website/data/buddy-universal-connections.json",
        ],
    },
    {
        "id": "safety",
        "paths": ["SECURITY.md", "website/connections.html"],
    },
]


def status_for(paths: list[str]) -> tuple[str, list[str]]:
    missing = [p for p in paths if not (ROOT / p).exists()]
    if not missing:
        return "wired", missing
    if len(missing) < len(paths):
        return "partial", missing
    return "missing", missing


def main() -> int:
    lanes = []
    blocked = 0
    for lane in LANES:
        state, missing = status_for(lane["paths"])
        if state != "wired":
            blocked += 1
        lanes.append(
            {
                "id": lane["id"],
                "status": state,
                "required": lane["paths"],
                "missing": missing,
                "green": False,
            }
        )
    report = {
        "schema": "dreamco.buddy_recovery_systems.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "truth": "Presence of a workflow is not a verified repair. History stays immutable.",
        "lanes": lanes,
        "wired": sum(1 for row in lanes if row["status"] == "wired"),
        "blocked_or_partial": blocked,
        "auto_merge_main": False,
        "live_stripe": False,
        "history_rewritten": False,
    }
    out_dir = ROOT / "reports"
    out_dir.mkdir(exist_ok=True)
    dest = out_dir / "recovery-systems.json"
    dest.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    site = ROOT / "website" / "data"
    if site.exists():
        (site / "recovery-systems.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"wired": report["wired"], "blocked_or_partial": blocked, "path": str(dest)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
