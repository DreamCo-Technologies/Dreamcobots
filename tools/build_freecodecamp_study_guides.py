"""Build a complete per-video study-guide work queue and validate detailed guides.

This tool never fetches captions/transcripts or media. It consumes the canonical
catalog, the rights manifest and independently authored guide records. A guide
is eligible only when study, derivative-summary and evaluation permissions are
separately evidenced.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "buddy/bootcamp/sources/freecodecamp/catalog.json"
MANIFEST = ROOT / "config/authorized-transcripts/manifest.json"
GUIDES = ROOT / "buddy/bootcamp/sources/freecodecamp/study-guides"
REQUIRED_SECTIONS = (
    "summary", "chapter_summaries", "learning_objectives", "key_concepts",
    "terminology", "code_patterns", "worked_examples", "exercises", "projects",
    "common_mistakes", "debugging_playbook", "prerequisites",
    "division_applications", "knowledge_checks", "answer_key", "references", "review",
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_transcript_path(value: str, root: Path) -> Path | None:
    prefix = "data/freecodecamp/authorized-transcripts/"
    if not isinstance(value, str) or not value.startswith(prefix):
        return None
    allowed = (root / prefix).resolve()
    path = (root / value).resolve()
    try:
        path.relative_to(allowed)
    except ValueError:
        return None
    return path


def validate_guide(guide: dict[str, Any], video: dict[str, Any], rights: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if guide.get("schema") != "dreamco.freecodecamp_video_study_guide.v1":
        errors.append("unsupported guide schema")
    if guide.get("video_id") != video.get("video_id"):
        errors.append("guide video ID does not match catalog")
    source = guide.get("source") if isinstance(guide.get("source"), dict) else {}
    if source.get("url") != video.get("url") or source.get("title") != video.get("title"):
        errors.append("guide source title or URL does not match canonical catalog")
    if source.get("transcript_sha256") != rights.get("transcript_sha256"):
        errors.append("guide transcript hash does not match rights manifest")
    for permission in ("study_permission", "summary_derivative_permission", "evaluation_permission"):
        if rights.get(permission) is not True:
            errors.append(f"missing {permission}")
    evidence = str(rights.get("rights_evidence_ref", "")).strip()
    if not evidence:
        errors.append("missing rights evidence reference")
    guide_rights = guide.get("rights") if isinstance(guide.get("rights"), dict) else {}
    if guide_rights.get("evidence_ref") != evidence:
        errors.append("guide rights evidence reference mismatch")
    for section in REQUIRED_SECTIONS:
        if section not in guide or guide[section] in (None, "", [], {}):
            errors.append(f"missing detailed section: {section}")
    summary = guide.get("summary") or {}
    if len(str(summary.get("executive_overview", "")).strip()) < 100:
        errors.append("executive overview must contain at least 100 characters")
    if len(str(summary.get("detailed_explanation", "")).strip()) < 500:
        errors.append("detailed explanation must contain at least 500 characters")
    if len(guide.get("chapter_summaries", [])) < 1:
        errors.append("at least one timestamped chapter summary is required")
    chapters = guide.get("chapter_summaries", [])
    if not isinstance(chapters, list):
        errors.append("chapter summaries must be a list")
        chapters = []
    starts = [x.get("start_seconds") if isinstance(x, dict) else None for x in chapters]
    if any(not isinstance(x, int) or x < 0 for x in starts) or starts != sorted(starts):
        errors.append("chapter timestamps must be non-negative integers in ascending order")
    if len(guide.get("learning_objectives", [])) < 3:
        errors.append("at least three learning objectives are required")
    if len(guide.get("key_concepts", [])) < 5:
        errors.append("at least five detailed key concepts are required")
    if len(guide.get("exercises", [])) < 3:
        errors.append("at least three original exercises are required")
    if len(guide.get("knowledge_checks", [])) < 5 or len(guide.get("answer_key", [])) < 5:
        errors.append("at least five knowledge checks and answers are required")
    review = guide.get("review") or {}
    if review.get("review_status") not in {"draft", "needs_human_review", "approved", "rejected"}:
        errors.append("review status is missing or invalid")
    return errors


def build_work_queue(catalog: dict[str, Any], manifest: dict[str, Any], guides: dict[str, dict[str, Any]] | None = None, *, root: Path = ROOT) -> dict[str, Any]:
    if catalog.get("schema") != "dreamco.freecodecamp_catalog.v1":
        raise ValueError("unsupported freeCodeCamp catalog schema")
    if (catalog.get("source") or {}).get("channel_id") != "UC8butISFwT-Wl7EV0hUK0BQ":
        raise ValueError("only the official freeCodeCamp channel catalog is accepted")
    videos = catalog.get("videos")
    if not isinstance(videos, list):
        raise ValueError("catalog videos must be a list")
    if manifest.get("schema") != "dreamco.authorized_transcript_manifest.v1":
        raise ValueError("unsupported transcript manifest schema")
    policy = manifest.get("rights_policy") or {}
    if policy.get("automatic_caption_scraping") is not False or policy.get("automatic_transcript_download") is not False:
        raise ValueError("automatic caption scraping and transcript download must remain disabled")
    if policy.get("automatic_model_training") is not False:
        raise ValueError("automatic model training must remain disabled")
    records = manifest.get("transcripts")
    if not isinstance(records, list):
        raise ValueError("transcript manifest must contain a list")
    rights_by_id: dict[str, dict[str, Any]] = {}
    for row in records:
        if not isinstance(row, dict) or not row.get("video_id") or row["video_id"] in rights_by_id:
            raise ValueError("transcript manifest video IDs must be unique and non-empty")
        rights_by_id[row["video_id"]] = row
    guide_index = guides or {}
    seen: set[str] = set()
    queue = []
    for video in videos:
        if not isinstance(video, dict):
            raise ValueError("catalog video rows must be objects")
        video_id = str(video.get("video_id", ""))
        if not video_id or video_id in seen or not video.get("url") or not video.get("title"):
            raise ValueError("catalog video IDs must be unique and each row needs title and URL")
        seen.add(video_id)
        rights = rights_by_id.get(video_id)
        status = "AWAITING_AUTHORIZED_TRANSCRIPT"
        errors: list[str] = []
        guide_status = "NOT_CREATED"
        if rights:
            if rights.get("source_url") != video.get("url"):
                status = "BLOCKED_SOURCE_MISMATCH"
            elif rights.get("rights_status") != "VERIFIED" or not str(rights.get("rights_evidence_ref", "")).strip():
                status = "BLOCKED_RIGHTS_UNVERIFIED"
            else:
                path = _safe_transcript_path(str(rights.get("transcript_path", "")), root)
                if path is None:
                    status = "BLOCKED_TRANSCRIPT_PATH"
                elif not path.is_file():
                    status = "BLOCKED_TRANSCRIPT_FILE_MISSING"
                elif rights.get("transcript_sha256") != _sha256(path):
                    status = "BLOCKED_TRANSCRIPT_HASH_MISMATCH"
                elif rights.get("study_permission") is not True or rights.get("summary_derivative_permission") is not True or rights.get("evaluation_permission") is not True:
                    status = "BLOCKED_PERMISSION_SCOPE"
                else:
                    status = "READY_FOR_DETAILED_GUIDE"
                    guide = guide_index.get(video_id)
                    if guide:
                        errors = validate_guide(guide, video, rights)
                        guide_status = "APPROVED" if not errors and (guide.get("review") or {}).get("review_status") == "approved" else "NEEDS_REVIEW"
                    else:
                        guide_status = "READY_TO_AUTHOR"
        queue.append({
            "video_id": video_id,
            "title": video["title"],
            "url": video["url"],
            "categories": video.get("categories", []),
            "duration_seconds": video.get("duration_seconds"),
            "rights_status": status,
            "guide_status": guide_status,
            "teacher_model": "GPT-6",
            "student_model": "Buddy",
            "authoring_prompt": "buddy/bootcamp/prompts/freecodecamp-video-study-guide-authoring.md",
            "authoring_status": "ready_for_teacher_authoring" if status == "READY_FOR_DETAILED_GUIDE" else "blocked_rights_pending",
            "owner_designation": "user_designated_owner_pending_review",
            "study_path_required": ["prerequisites", "chapter_by_chapter_deep_study", "best_knowledge_extraction",
                "worked_examples", "sandbox_exercises", "knowledge_checks", "independent_project",
                "teach_back", "unseen_transfer", "spaced_review"],
            "guide_validation_errors": errors,
            "transcript_hash": rights.get("transcript_sha256") if rights else None,
            "model_training_authorized": bool(rights and rights.get("training_permission") is True and rights.get("training_rights_evidence_ref")),
            "model_training_started": False,
        })
    unknown_ids = sorted(set(rights_by_id) - seen)
    if unknown_ids:
        raise ValueError("transcript manifest contains video IDs absent from catalog")
    inventory = catalog.get("inventory") or {}
    complete = catalog.get("inventory_status") == "complete" and inventory.get("complete") is True and inventory.get("observed_entry_count") == len(videos) and inventory.get("expected_entry_count") == len(videos)
    return {
        "schema": "dreamco.freecodecamp_detailed_study_guide_queue.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_inventory_status": "COMPLETE" if complete else "PARTIAL_OR_UNVERIFIED",
        "catalog_video_count": len(queue),
        "authorized_for_guide_count": sum(row["rights_status"] == "READY_FOR_DETAILED_GUIDE" for row in queue),
        "guide_approved_count": sum(row["guide_status"] == "APPROVED" for row in queue),
        "guide_needs_review_count": sum(row["guide_status"] == "NEEDS_REVIEW" for row in queue),
        "pending_or_blocked_count": sum(row["rights_status"] != "READY_FOR_DETAILED_GUIDE" for row in queue),
        "videos": queue,
        "truth_boundary": "A queue entry is not a summary. No summary is fabricated from metadata. Detailed guides require verified transcript, study, derivative-summary and evaluation permissions plus review.",
        "transcripts_downloaded": False,
        "model_training_started": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--guides-dir", type=Path, default=GUIDES)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "artifacts/freecodecamp-study-guides")
    args = parser.parse_args()
    catalog = _read_json(args.catalog)
    manifest = _read_json(args.manifest)
    guides: dict[str, dict[str, Any]] = {}
    if args.guides_dir.exists():
        for path in sorted(args.guides_dir.glob("*.json")):
            guide = _read_json(path)
            guides[str(guide.get("video_id", path.stem))] = guide
    result = build_work_queue(catalog, manifest, guides)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    target = args.out_dir / "detailed-study-guide-queue.json"
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    summary = {key: result[key] for key in ("source_inventory_status", "catalog_video_count", "authorized_for_guide_count", "guide_approved_count", "guide_needs_review_count", "pending_or_blocked_count", "transcripts_downloaded", "model_training_started")}
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
