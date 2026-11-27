"""Evidence-based academic registrar for DreamCo Institute.

This module issues internal DreamCo credentials only. It does not claim
government accreditation or professional licensure. A SHA-256 seal detects
transcript modification; it is not a digital signature or proof of authorship.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "config" / "dreamco-institute-academic-catalog.json"


def load_catalog(path: Path = CATALOG_PATH) -> dict[str, Any]:
    catalog = json.loads(path.read_text(encoding="utf-8"))
    if catalog.get("schema") != "dreamco.institute.academic_catalog.v1":
        raise ValueError("Unsupported academic catalog schema.")
    if len(catalog.get("colleges", [])) != 5:
        raise ValueError("The Institute must define exactly five academic colleges.")
    assignments = catalog.get("division_crosswalk", {}).get("academic_assignments", [])
    ids = [row.get("domain_id") for row in assignments]
    if len(ids) != 55 or len(set(ids)) != 55:
        raise ValueError("Academic crosswalk must contain 55 unique domain divisions.")
    return catalog


def _grade(score: float) -> tuple[str, float]:
    if not 0 <= score <= 100:
        raise ValueError("Assessment scores must be between 0 and 100.")
    for minimum, letter, points in ((90, "A", 4.0), (80, "B", 3.0), (70, "C", 2.0), (0, "F", 0.0)):
        if score >= minimum:
            return letter, points
    raise AssertionError("Unreachable grade boundary.")


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required.")
    return value.strip()


def issue_transcript(
    candidate_id: str,
    college_id: str,
    course_evidence: dict[str, dict[str, Any]],
    thesis_evidence: dict[str, Any] | None = None,
    registrar_review_id: str | None = None,
    catalog: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a transcript from independently identified assessment evidence.

    Each course needs a score, assessment evidence ID, passed practicum, and
    passed independent holdout. Credits are awarded only when all conditions
    are satisfied and the course grade is at least C.
    """
    catalog = catalog or load_catalog()
    _required_text(candidate_id, "candidate_id")
    colleges = {college["id"]: college for college in catalog["colleges"]}
    if college_id not in colleges:
        raise ValueError(f"Unknown academic college: {college_id}")
    college = colleges[college_id]
    course_evidence = course_evidence or {}
    records = []
    earned_credits = 0
    weighted_points = 0.0
    attempted_credits = 0

    for course in college["courses"]:
        code = course["code"]
        evidence = course_evidence.get(code, {})
        score = float(evidence.get("score_pct", 0.0))
        letter, points = _grade(score)
        credits = int(course["credits"])
        attempted_credits += credits
        assessment_id = evidence.get("assessment_evidence_id")
        practicum_passed = evidence.get("practicum_passed") is True
        holdout_passed = evidence.get("independent_holdout_passed") is True
        eligible = bool(assessment_id) and practicum_passed and holdout_passed and points >= 2.0
        if eligible:
            earned_credits += credits
            weighted_points += points * credits
        records.append({
            "course_code": code,
            "course_title": course["title"],
            "academic_level": course["level"],
            "credits_attempted": credits,
            "credits_earned": credits if eligible else 0,
            "score_pct": score,
            "letter_grade": letter if eligible else ("INCOMPLETE" if points >= 2.0 else "F"),
            "assessment_evidence_id": assessment_id if isinstance(assessment_id, str) else None,
            "practicum_passed": practicum_passed,
            "independent_holdout_passed": holdout_passed,
            "credit_award_eligible": eligible,
        })

    gpa = round(weighted_points / earned_credits, 2) if earned_credits else 0.0
    thesis = thesis_evidence or {}
    thesis_ok = (
        bool(thesis.get("thesis_record_id"))
        and thesis.get("oral_defense_passed") is True
        and bool(thesis.get("independent_review_id"))
    )
    review_ok = bool(registrar_review_id and str(registrar_review_id).strip())
    all_credits = earned_credits == attempted_credits
    graduated = all_credits and gpa >= 3.0 and thesis_ok and review_ok
    if graduated:
        standing = "DEAN_LIST" if gpa >= 3.75 else "GOOD_STANDING"
    else:
        standing = "IN_PROGRESS" if earned_credits else "NOT_YET_EARNED"

    transcript = {
        "schema": "dreamco.institute.transcript.v1",
        "institution": catalog["institution"]["name"],
        "credential_status": "INTERNAL_DREAMCO_CREDENTIAL",
        "accreditation_disclaimer": catalog["institution"]["credential_disclaimer"],
        "registrar": catalog["institution"]["registrar"],
        "candidate_id": candidate_id.strip(),
        "college": {"id": college_id, "name": college["name"], "dean_office": college["dean"]},
        "issued_at_utc": datetime.now(timezone.utc).isoformat(),
        "academic_record": records,
        "capstone": {
            "thesis_record_id": thesis.get("thesis_record_id"),
            "oral_defense_passed": thesis.get("oral_defense_passed") is True,
            "independent_review_id": thesis.get("independent_review_id"),
            "passed": thesis_ok,
        },
        "registrar_review_id": registrar_review_id,
        "summary": {
            "credits_earned": earned_credits,
            "credits_attempted": attempted_credits,
            "credits_required": attempted_credits,
            "cumulative_gpa": gpa,
            "academic_standing": standing,
            "degree_conferred": f"DreamCo Master of Autonomous Systems — {college['code']}" if graduated else "Not conferred",
            "graduated": graduated,
        },
        "evidence_policy": "No credit without assessment ID, passed practicum, passed independent holdout, and grade C or higher. No credential without capstone defense and registrar review.",
    }
    canonical = json.dumps(transcript, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    transcript["registrar_seal_sha256"] = hashlib.sha256(canonical).hexdigest()
    transcript["seal_type"] = "integrity_checksum_not_digital_signature"
    return transcript


def verify_transcript_seal(transcript: dict[str, Any]) -> bool:
    """Verify integrity checksum only; this does not authenticate the issuer."""
    supplied = transcript.get("registrar_seal_sha256")
    if not isinstance(supplied, str):
        return False
    unsigned = {key: value for key, value in transcript.items() if key not in {"registrar_seal_sha256", "seal_type"}}
    canonical = json.dumps(unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest() == supplied


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--college-id", required=True)
    parser.add_argument("--evidence", required=True, type=Path, help="JSON file containing course_evidence, thesis_evidence, and registrar_review_id.")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    payload = json.loads(args.evidence.read_text(encoding="utf-8"))
    transcript = issue_transcript(
        args.candidate_id, args.college_id, payload.get("course_evidence", {}),
        payload.get("thesis_evidence"), payload.get("registrar_review_id"),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(transcript, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "graduated": transcript["summary"]["graduated"], "credits_earned": transcript["summary"]["credits_earned"], "gpa": transcript["summary"]["cumulative_gpa"], "seal_valid": verify_transcript_seal(transcript)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
