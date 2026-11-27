"""Build a rights-gated transcript intake queue and weekly Buddy test coverage audit."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "buddy/bootcamp/sources/freecodecamp/catalog.json"
MANIFEST = ROOT / "config/authorized-transcripts/manifest.json"
TEST_EVIDENCE = ROOT / "config/authorized-transcripts/weekly-test-evidence.json"
ALLOWED_TRANSCRIPT_ROOT = ROOT / "data/freecodecamp/authorized-transcripts"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_transcript_path(value: str, root: Path) -> Path | None:
    if not isinstance(value, str) or not value.startswith("data/freecodecamp/authorized-transcripts/"):
        return None
    allowed = root / "data/freecodecamp/authorized-transcripts"
    path = (root / value).resolve()
    try:
        path.relative_to(allowed.resolve())
    except ValueError:
        return None
    return path


def build_intake(catalog: dict[str, Any], manifest: dict[str, Any], *, root: Path = ROOT) -> dict[str, Any]:
    if catalog.get("schema") != "dreamco.freecodecamp_catalog.v1":
        raise ValueError("unsupported FreeCodeCamp catalog schema")
    if (catalog.get("source") or {}).get("channel_id") != "UC8butISFwT-Wl7EV0hUK0BQ":
        raise ValueError("catalog must be the official freeCodeCamp YouTube channel")
    if not isinstance(catalog.get("videos"), list):
        raise ValueError("FreeCodeCamp catalog videos must be a list")
    if manifest.get("schema") != "dreamco.authorized_transcript_manifest.v1":
        raise ValueError("unsupported authorized transcript manifest schema")
    policy = manifest.get("rights_policy") or {}
    if policy.get("automatic_caption_scraping") is not False or policy.get("automatic_transcript_download") is not False:
        raise ValueError("automatic caption scraping and transcript download must remain disabled")
    if policy.get("automatic_model_training") is not False:
        raise ValueError("automatic model training must remain disabled")
    transcripts = manifest.get("transcripts")
    if not isinstance(transcripts, list):
        raise ValueError("authorized transcript manifest must contain a transcript list")
    by_video: dict[str, dict[str, Any]] = {}
    for record in transcripts:
        if not isinstance(record, dict):
            raise ValueError("transcript manifest entries must be objects")
        video_id = str(record.get("video_id", ""))
        if not video_id or video_id in by_video:
            raise ValueError("authorized transcript video IDs must be unique and non-empty")
        by_video[video_id] = record

    queue = []
    seen = set()
    for video in catalog["videos"]:
        if not isinstance(video, dict):
            continue
        video_id = str(video.get("video_id", ""))
        source_url = str(video.get("url", ""))
        if not video_id or not source_url:
            raise ValueError("catalog videos require non-empty video IDs and source URLs")
        if video_id in seen:
            raise ValueError("catalog video IDs must be unique")
        seen.add(video_id)
        record = by_video.get(video_id)
        status = "PERMISSION_REQUEST_REQUIRED"
        transcript_present = False
        study_allowed = False
        evaluation_allowed = False
        training_allowed = False
        evidence_ref = None
        reason = "No authorized transcript asset is registered."
        if record:
            if record.get("source_url") != source_url:
                status, reason = "BLOCKED_SOURCE_MISMATCH", "Manifest source URL does not match the canonical catalog."
            elif record.get("rights_status") != "VERIFIED" or not str(record.get("rights_evidence_ref", "")).strip():
                status, reason = "BLOCKED_RIGHTS_UNVERIFIED", "Rights status or evidence reference is missing."
            else:
                relative = record.get("transcript_path")
                candidate = _safe_transcript_path(relative, root) if isinstance(relative, str) else None
                if candidate is None:
                    status, reason = "BLOCKED_TRANSCRIPT_PATH", "Transcript path must stay inside the authorized transcript directory."
                elif not candidate.is_file():
                    status, reason = "BLOCKED_TRANSCRIPT_FILE_MISSING", "Authorized transcript file is missing."
                elif record.get("transcript_sha256") != _sha256(candidate):
                    status, reason = "BLOCKED_TRANSCRIPT_HASH_MISMATCH", "Transcript content hash does not match the manifest."
                elif record.get("study_permission") is not True or record.get("evaluation_permission") is not True:
                    status, reason = "BLOCKED_STUDY_OR_EVALUATION_PERMISSION", "Separate study and weekly evaluation permissions are required."
                else:
                    status = "AUTHORIZED_FOR_STUDY_AND_WEEKLY_EVALUATION"
                    reason = "Transcript file, source, hash, rights evidence, study permission, and evaluation permission verified."
                    transcript_present = True
                    study_allowed = True
                    evaluation_allowed = True
                    training_allowed = (
                        record.get("training_permission") is True
                        and bool(str(record.get("training_rights_evidence_ref", "")).strip())
                    )
                    evidence_ref = record.get("rights_evidence_ref")
        queue.append({
            "video_id": video_id,
            "title": str(video.get("title", "")),
            "source_url": source_url,
            "status": status,
            "reason": reason,
            "transcript_asset_present": transcript_present,
            "study_permission_verified": study_allowed,
            "weekly_evaluation_permission_verified": evaluation_allowed,
            "model_training_authorized": training_allowed,
            "rights_evidence_ref": evidence_ref,
            "automatic_caption_scraping": False,
            "automatic_transcript_download": False,
        })

    unknown_manifest_ids = sorted(set(by_video) - seen)
    if unknown_manifest_ids:
        raise ValueError("transcript manifest contains video IDs absent from the canonical catalog")
    authorized = sum(row["transcript_asset_present"] for row in queue)
    pending = sum(row["status"] == "PERMISSION_REQUEST_REQUIRED" for row in queue)
    blocked = len(queue) - authorized - pending
    return {
        "schema": "dreamco.freecodecamp_transcript_intake.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "catalog_video_count": len(queue),
        "source_inventory_status": catalog.get("inventory_status", "unknown"),
        "source_inventory_complete": catalog.get("inventory_status") == "complete",
        "authorized_transcript_count": authorized,
        "permission_request_count": pending,
        "blocked_manifest_record_count": blocked,
        "unknown_manifest_video_ids": unknown_manifest_ids,
        "queue": queue,
        "truth_boundary": "This is a permission and intake queue, not a transcript downloader. Public metadata does not grant transcript, study, evaluation, or training rights.",
        "content_downloaded": False,
        "model_training_started": False,
    }


def audit_weekly_tests(
    intake: dict[str, Any],
    evidence: dict[str, Any],
    *,
    now: datetime | None = None,
    max_age_days: int = 7,
) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    if isinstance(max_age_days, bool) or not isinstance(max_age_days, int) or max_age_days < 1:
        raise ValueError("max_age_days must be a positive integer")
    if now.tzinfo is None:
        raise ValueError("audit clock must be timezone-aware")
    if evidence.get("schema") != "dreamco.freecodecamp_weekly_buddy_test_evidence.v1":
        raise ValueError("unsupported weekly Buddy test evidence schema")
    records = evidence.get("records")
    if not isinstance(records, list):
        raise ValueError("weekly Buddy test evidence records must be a list")
    by_video = {}
    for record in records:
        if not isinstance(record, dict) or not record.get("video_id") or record["video_id"] in by_video:
            raise ValueError("weekly test evidence video IDs must be unique and non-empty")
        by_video[record["video_id"]] = record

    known_video_ids = {str(row.get("video_id", "")) for row in intake.get("queue", [])}
    unknown_evidence_ids = sorted(set(by_video) - known_video_ids)
    eligible = [row for row in intake.get("queue", []) if row.get("weekly_evaluation_permission_verified") is True]
    results = []
    missing = []
    failed = []
    for transcript in eligible:
        record = by_video.get(transcript["video_id"])
        if not record:
            missing.append(transcript["video_id"])
            continue
        try:
            tested_at = datetime.fromisoformat(str(record.get("tested_at", "")).replace("Z", "+00:00"))
        except ValueError:
            tested_at = None
        result_hash = str(record.get("result_sha256", ""))
        valid = (
            tested_at is not None
            and tested_at.tzinfo is not None
            and timedelta(0) <= now - tested_at <= timedelta(days=max_age_days)
            and record.get("status") == "PASS"
            and bool(str(record.get("buddy_model_id", "")).strip())
            and bool(str(record.get("buddy_model_version", "")).strip())
            and bool(str(record.get("run_id", "")).strip())
            and bool(str(record.get("suite_id", "")).strip())
            and record.get("evaluation_permission_ref") == transcript.get("rights_evidence_ref")
            and len(result_hash) == 64
            and all(ch in "0123456789abcdef" for ch in result_hash)
        )
        if valid:
            results.append(transcript["video_id"])
        else:
            failed.append(transcript["video_id"])

    if intake.get("source_inventory_complete") is not True:
        status = "BLOCKED_PARTIAL_SOURCE_CATALOG"
    elif not eligible:
        status = "BLOCKED_NO_AUTHORIZED_TRANSCRIPTS"
    elif failed:
        status = "FAILED_WEEKLY_BUDDY_TEST_EVIDENCE"
    elif missing:
        status = "BLOCKED_MISSING_WEEKLY_BUDDY_TESTS"
    else:
        status = "COMPLETE"

    return {
        "schema": "dreamco.freecodecamp_weekly_buddy_test_audit.v1",
        "generated_at": now.isoformat(),
        "window_days": max_age_days,
        "status": status,
        "source_inventory_complete": intake.get("source_inventory_complete") is True,
        "authorized_transcript_count": len(eligible),
        "tested_transcript_count": len(results),
        "missing_video_ids": missing,
        "failed_or_stale_video_ids": failed,
        "unknown_evidence_video_ids": unknown_evidence_ids,
        "passed_video_ids": results,
        "buddy_test_execution_performed_by_audit": False,
        "model_training_authorized": False,
        "truth_boundary": "The audit validates submitted Buddy test evidence. It does not execute Buddy or infer that a transcript was tested.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--test-evidence", type=Path, default=TEST_EVIDENCE)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "artifacts/freecodecamp-transcripts")
    args = parser.parse_args()
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    evidence = json.loads(args.test_evidence.read_text(encoding="utf-8"))
    intake = build_intake(catalog, manifest)
    audit = audit_weekly_tests(intake, evidence)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "transcript-intake-queue.json").write_text(json.dumps(intake, indent=2) + "\n", encoding="utf-8")
    (args.out_dir / "weekly-buddy-test-audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    summary = {
        "catalog_video_count": intake["catalog_video_count"],
        "authorized_transcript_count": intake["authorized_transcript_count"],
        "permission_request_count": intake["permission_request_count"],
        "source_inventory_status": intake["source_inventory_status"],
        "weekly_buddy_test_status": audit["status"],
        "weekly_buddy_test_count": audit["tested_transcript_count"],
        "content_downloaded": False,
        "model_training_started": False,
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
