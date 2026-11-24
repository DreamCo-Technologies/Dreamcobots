#!/usr/bin/env python3
"""Build a truthful weekly due-work report for approved Buddy transcripts.

This planner never downloads transcripts and never fabricates model results.
A real Buddy inference adapter and an approved transcript manifest are required
before any item can be marked evaluated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config/buddy-weekly-transcript-evaluation.json"
MANIFEST = ROOT / "config/authorized-transcripts/manifest.json"
LEDGER = ROOT / "config/generated/buddy-transcript-evaluation-ledger.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_manifest(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if payload.get("schema") != "dreamco.authorized_transcript_manifest.v1":
        raise ValueError("invalid transcript manifest schema")
    transcripts = payload.get("transcripts")
    if not isinstance(transcripts, list):
        raise ValueError("manifest transcripts must be a list")
    seen: set[str] = set()
    for item in transcripts:
        required = ("transcript_id", "transcript_sha256", "source_url", "rights_evidence_ref", "division_ids")
        if not isinstance(item, dict) or any(not item.get(key) for key in required):
            raise ValueError("each transcript requires id, digest, source URL, rights evidence and division IDs")
        if item["transcript_id"] in seen:
            raise ValueError(f"duplicate transcript_id: {item['transcript_id']}")
        seen.add(item["transcript_id"])
        digest = item["transcript_sha256"]
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise ValueError(f"invalid SHA-256 for {item['transcript_id']}")
        divisions = item["division_ids"]
        if not isinstance(divisions, list) or not divisions or any(type(x) is not int or not 1 <= x <= 65 for x in divisions):
            raise ValueError(f"invalid division_ids for {item['transcript_id']}")
        if item.get("rights_status") != "approved" or item.get("evaluation_allowed") is not True:
            raise ValueError(f"transcript {item['transcript_id']} is not approved for evaluation")
    return transcripts


def iso_week(value: date) -> str:
    year, week, _ = value.isocalendar()
    return f"{year}-W{week:02d}"


def build_report(policy: dict[str, Any], manifest_path: Path, ledger_path: Path, today: date) -> dict[str, Any]:
    week = iso_week(today)
    blocked: list[str] = []
    transcripts: list[dict[str, Any]] = []
    manifest_present = manifest_path.exists()
    if not manifest_present:
        blocked.append("approved_transcript_manifest_missing")
    else:
        transcripts = validate_manifest(read_json(manifest_path))

    ledger_records: list[dict[str, Any]] = []
    if ledger_path.exists():
        prior = read_json(ledger_path)
        if prior.get("schema") != "dreamco.buddy_transcript_evaluation_ledger.v1":
            raise ValueError("invalid transcript evaluation ledger schema")
        ledger_records = prior.get("evaluations", [])
        if not isinstance(ledger_records, list):
            raise ValueError("ledger evaluations must be a list")

    due: list[dict[str, Any]] = []
    for item in transcripts:
        matching = [
            record for record in ledger_records
            if record.get("transcript_id") == item["transcript_id"]
            and record.get("transcript_sha256") == item["transcript_sha256"]
            and record.get("iso_week") == week
            and record.get("result") in ("passed", "failed", "error")
            and record.get("buddy_model_id")
            and record.get("buddy_model_version")
            and record.get("evaluation_suite_version")
            and record.get("rights_evidence_ref") == item["rights_evidence_ref"]
            and record.get("run_id")
        ]
        if not matching:
            due.append({
                "transcript_id": item["transcript_id"],
                "transcript_sha256": item["transcript_sha256"],
                "source_url": item["source_url"],
                "division_ids": item["division_ids"],
                "rights_evidence_ref": item["rights_evidence_ref"],
                "status": "due_not_evaluated",
            })

    if manifest_present and not transcripts:
        blocked.append("no_authorized_transcripts_registered")
    if transcripts:
        blocked.append("real_buddy_evaluation_adapter_not_registered")
    status = "blocked" if blocked else ("all_transcripts_evaluated" if not due else "evaluation_due")
    return {
        "schema": "dreamco.buddy_weekly_transcript_evaluation_report.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "iso_week": week,
        "status": status,
        "transcript_count": len(transcripts),
        "evaluated_count": len(transcripts) - len(due),
        "due_count": len(due),
        "coverage_target": 1.0,
        "coverage": None if not transcripts else (len(transcripts) - len(due)) / len(transcripts),
        "blocked_reasons": blocked,
        "due_transcripts": due,
        "synthetic_evaluations_created": 0,
        "policy": str(policy.get("requirement", "")),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--ledger", type=Path, default=LEDGER)
    parser.add_argument("--output", type=Path, default=ROOT / "config/generated/buddy-weekly-transcript-evaluation.json")
    parser.add_argument("--date", type=date.fromisoformat, default=date.today())
    args = parser.parse_args()
    policy = read_json(POLICY)
    report = build_report(policy, args.manifest, args.ledger, args.date)
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
