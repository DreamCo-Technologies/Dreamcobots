#!/usr/bin/env python3
"""Turn a failed GitHub Actions run into safe Buddy diagnosis recommendations."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.buddy_failure_learning import recommend


def build_observations(run: dict[str, Any]) -> list[dict[str, Any]]:
    """Create one bounded observation per failed job; omit successful/skipped jobs."""
    observations = []
    for job in run.get("jobs", []):
        if job.get("conclusion") not in {"failure", "timed_out", "action_required"}:
            continue
        failed_steps = [
            step for step in job.get("steps", [])
            if step.get("conclusion") in {"failure", "timed_out", "action_required"}
        ]
        step = failed_steps[-1] if failed_steps else {}
        observations.append({
            "repository": run.get("repository", ""),
            "workflow": run.get("name", ""),
            "job": job.get("name", ""),
            "failed_step": step.get("name", "failed job; step detail unavailable"),
            "error_signature": " | ".join(filter(None, [
                str(job.get("conclusion", "")),
                str(step.get("conclusion", "")),
                str(step.get("name", "")),
            ])),
            "run_id": str(run.get("id") or run.get("databaseId") or ""),
            "run_url": run.get("url", ""),
            "head_sha": run.get("headSha", ""),
        })
    return observations


def build_report(run: dict[str, Any], history: dict[str, Any],
                 memory: dict[str, Any]) -> dict[str, Any]:
    observations = build_observations(run)
    return {
        "schema": "dreamco.buddy.historical_failure_diagnosis.v1",
        "source_run": {
            "id": run.get("id") or run.get("databaseId"),
            "name": run.get("name"),
            "conclusion": run.get("conclusion"),
            "url": run.get("url"),
            "headSha": run.get("headSha"),
        },
        "observation_count": len(observations),
        "recommendations": [
            {"observation": obs, "recommendation": recommend(obs, memory, history)}
            for obs in observations
        ],
        "policy": {
            "historical_matches_are_investigation_only": True,
            "historical_commits_auto_applied": False,
            "unverified_records_training_eligible": False,
            "incident_memory_written": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--historical-index", required=True, type=Path)
    parser.add_argument("--memory", type=Path)\n    parser.add_argument("--repository", default="")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    run = json.loads(args.run.read_text(encoding="utf-8"))\n    if args.repository:\n        run["repository"] = args.repository
    history = json.loads(args.historical_index.read_text(encoding="utf-8"))
    memory = json.loads(args.memory.read_text(encoding="utf-8")) if args.memory and args.memory.exists() else {"incidents": []}
    report = build_report(run, history, memory)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\\n", encoding="utf-8")
    print(json.dumps({"ok": True, "observations": report["observation_count"],
                      "output": str(args.output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
