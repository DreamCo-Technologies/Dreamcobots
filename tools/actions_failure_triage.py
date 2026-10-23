#!/usr/bin/env python3
"""Group Actions failures into read-only triage evidence without filing issues.

This is not a root-cause detector or passing CI evidence. It preserves
individual failures and labels every group as observed until verified.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_triage(rows: list[dict], *, sample_limit: int = 3) -> dict:
    if sample_limit < 1:
        raise ValueError("sample_limit must be positive")
    if not isinstance(rows, list):
        raise ValueError("failures input must be a JSON list")
    grouped: dict[tuple[str, str], dict] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("each failure must be a JSON object")
        name = row.get("name", "unknown-workflow")
        conclusion = row.get("conclusion", "unknown")
        if not isinstance(name, str) or not isinstance(conclusion, str):
            raise ValueError("workflow name and conclusion must be strings")
        key = (name, conclusion)
        if key not in grouped:
            grouped[key] = {
                "workflow": name,
                "conclusion": conclusion,
                "status": "observed",
                "count": 0,
                "sample_runs": [],
            }
        group = grouped[key]
        group["count"] += 1
        if len(group["sample_runs"]) < sample_limit:
            group["sample_runs"].append({
                "id": row.get("id"),
                "url": row.get("html_url"),
                "head_sha": row.get("head_sha"),
            })
    groups = sorted(grouped.values(), key=lambda g: (-g["count"], g["workflow"], g["conclusion"]))
    return {
        "schema": "dreamco.actions_failure_triage.v1",
        "truth_policy": {
            "observed_is_not_resolved": True,
            "passing_evidence_required_to_close": True,
            "groups_are_not_root_cause_proof": True,
            "external_publication_disabled": True,
        },
        "observed_failures": len(rows),
        "group_count": len(groups),
        "groups": groups,
    }


def render_summary(triage: dict, *, max_groups: int = 25) -> str:
    lines = [
        "## Read-only Actions failure triage", "",
        f"- Failed runs observed: **{triage['observed_failures']}**",
        f"- Workflow/conclusion groups: **{triage['group_count']}**",
        "- No issues, comments, PRs, or external notifications were created.",
        "- Grouping is for triage only; it does not prove shared root cause or resolution.",
        "- Complete run-level evidence remains in `sweep/failures.json`.", "",
    ]
    for group in triage["groups"][:max_groups]:
        sample = group["sample_runs"][0] if group["sample_runs"] else {}
        url = sample.get("url") or "unavailable"
        lines.append(f"- **{group['workflow']}** ({group['conclusion']}): {group['count']} runs; sample: {url}")
    if triage["group_count"] > max_groups:
        lines.append(f"- {triage['group_count'] - max_groups} additional groups in triage.json")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()
    rows = json.loads(args.input.read_text(encoding="utf-8"))
    triage = build_triage(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(triage, indent=2) + "\n", encoding="utf-8")
    args.summary.write_text(render_summary(triage), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
