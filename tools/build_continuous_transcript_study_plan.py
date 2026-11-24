#!/usr/bin/env python3
"""Build a continuous, rights-gated Buddy transcript study queue.

The planner never fetches transcripts or runs model inference. A registered
runtime adapter must consume due items and append real, verifiable ledger rows.
"""
from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config/buddy-continuous-transcript-study.json"
MANIFEST = ROOT / "config/authorized-transcripts/manifest.json"
LEDGER = ROOT / "config/generated/buddy-continuous-study-ledger.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_manifest(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if payload.get("schema") != "dreamco.authorized_transcript_manifest.v1":
        raise ValueError("invalid authorized transcript manifest schema")
    entries = payload.get("transcripts")
    if not isinstance(entries, list):
        raise ValueError("manifest transcripts must be a list")
    seen: set[str] = set()
    for item in entries:
        required = ("transcript_id", "transcript_sha256", "source_url", "rights_evidence_ref", "division_ids")
        if not isinstance(item, dict) or any(not item.get(key) for key in required):
            raise ValueError("each transcript requires id, SHA-256, source URL, rights evidence and division IDs")
        if item["transcript_id"] in seen:
            raise ValueError(f"duplicate transcript_id: {item['transcript_id']}")
        seen.add(item["transcript_id"])
        digest = item["transcript_sha256"]
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise ValueError(f"invalid SHA-256 for {item['transcript_id']}")
        divisions = item["division_ids"]
        if (not isinstance(divisions, list) or not divisions
                or any(type(value) is not int or not 1 <= value <= 65 for value in divisions)):
            raise ValueError(f"invalid division_ids for {item['transcript_id']}")
    return entries


def is_mastered(item: dict[str, Any], evaluations: list[dict[str, Any]], mastery: dict[str, Any]) -> bool:
    valid = [
        row for row in evaluations
        if row.get("transcript_id") == item["transcript_id"]
        and row.get("transcript_sha256") == item["transcript_sha256"]
        and row.get("result") == "passed"
        and isinstance(row.get("score"), (int, float))
        and row["score"] >= mastery["minimum_score"]
        and row.get("critical_failures", 0) == 0
        and row.get("holdout_passed") is True
        and row.get("human_review") == "approved"
        and row.get("buddy_model_id")
        and row.get("buddy_model_version")
        and row.get("evaluation_suite_version")
        and row.get("run_id")
    ]
    distinct_days = {row.get("completed_at", "")[:10] for row in valid if row.get("completed_at")}
    return (
        len(valid) >= mastery["minimum_passed_evaluations"]
        and len(distinct_days) >= mastery["minimum_distinct_utc_days"]
    )


def build_plan(policy: dict[str, Any], manifest_path: Path, ledger_path: Path) -> dict[str, Any]:
    blocked: list[str] = []
    entries: list[dict[str, Any]] = []
    if not manifest_path.exists():
        blocked.append("authorized_transcript_manifest_missing")
    else:
        entries = validate_manifest(read_json(manifest_path))

    ledger: list[dict[str, Any]] = []
    if ledger_path.exists():
        payload = read_json(ledger_path)
        if payload.get("schema") != "dreamco.buddy_continuous_study_ledger.v1":
            raise ValueError("invalid continuous study ledger schema")
        ledger = payload.get("evaluations", [])
        if not isinstance(ledger, list):
            raise ValueError("ledger evaluations must be a list")

    if not policy.get("execution", {}).get("real_buddy_study_adapter_registered", False):
        blocked.append("real_buddy_study_adapter_not_registered")

    due: list[dict[str, Any]] = []
    mastered: list[str] = []
    not_authorized: list[str] = []
    for item in entries:
        if item.get("rights_status") != "approved" or item.get("study_allowed") is not True:
            not_authorized.append(item["transcript_id"])
            continue
        if not item.get("rights_evidence_ref"):
            not_authorized.append(item["transcript_id"])
            continue
        if is_mastered(item, ledger, policy["mastery"]):
            mastered.append(item["transcript_id"])
            continue
        due.append({
            "transcript_id": item["transcript_id"],
            "transcript_sha256": item["transcript_sha256"],
            "source_url": item["source_url"],
            "division_ids": item["division_ids"],
            "rights_evidence_ref": item["rights_evidence_ref"],
            "status": "due_until_mastery",
            "next_action": "run_real_buddy_study_and_holdout_evaluation"
        })

    status = "blocked" if blocked else ("mastery_pending" if due else "all_authorized_transcripts_mastered")
    return {
        "schema": "dreamco.buddy_continuous_transcript_study_plan.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "manifest_transcript_count": len(entries),
        "authorized_for_study_count": len(entries) - len(not_authorized),
        "not_authorized_count": len(not_authorized),
        "due_until_mastery_count": len(due),
        "mastered_count": len(mastered),
        "mastery_policy": policy["mastery"],
        "blocked_reasons": blocked,
        "not_authorized_transcript_ids": not_authorized,
        "mastered_transcript_ids": mastered,
        "due_transcripts": due,
        "model_training_started": False,
        "synthetic_evaluations_created": 0
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", type=Path, default=POLICY)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--ledger", type=Path, default=LEDGER)
    parser.add_argument("--output", type=Path, default=ROOT / "config/generated/buddy-continuous-study-plan.json")
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    plan = build_plan(read_json(args.policy), args.manifest, args.ledger)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in plan.items() if key not in {"due_transcripts", "mastered_transcript_ids", "not_authorized_transcript_ids"}}, indent=2))
    return 2 if args.require_ready and plan["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
