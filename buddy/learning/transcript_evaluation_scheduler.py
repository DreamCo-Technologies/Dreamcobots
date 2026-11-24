"""Weekly Buddy transcript evaluation planning with rights and provenance gates.

This module creates a plan only. It never downloads media, ingests transcripts,
executes evaluations, or trains model weights.
"""
from __future__ import annotations

import re
from datetime import date, datetime, timedelta, timezone
from typing import Any

_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def monday_of_week(value: str | None = None) -> date:
    day = date.fromisoformat(value) if value else datetime.now(timezone.utc).date()
    return day - timedelta(days=day.weekday())


def build_weekly_transcript_evaluation_plan(
    catalog: dict[str, Any], week_start: str | None = None
) -> dict[str, Any]:
    monday = monday_of_week(week_start)
    due = monday + timedelta(days=6)
    videos = catalog.get("videos", [])
    if not isinstance(videos, list):
        raise ValueError("catalog videos must be a list")

    seen: set[str] = set()
    eligible: list[dict[str, Any]] = []
    blocked: list[dict[str, str]] = []
    for video in videos:
        if not isinstance(video, dict):
            raise ValueError("catalog video records must be objects")
        video_id = video.get("video_id")
        if not isinstance(video_id, str) or not video_id.strip():
            raise ValueError("every catalog record requires a video_id")
        if video_id in seen:
            raise ValueError(f"duplicate video_id in catalog: {video_id}")
        seen.add(video_id)

        digest = video.get("transcript_sha256")
        rights_ok = (
            video.get("rights_status") == "rights_cleared"
            and video.get("transcript_status") == "rights_cleared_and_ingested"
            and video.get("transcript_evaluation_authorized") is True
            and isinstance(digest, str)
            and _SHA256.fullmatch(digest) is not None
        )
        if rights_ok:
            eligible.append({
                "video_id": video_id,
                "transcript_sha256": digest,
                "week_start": monday.isoformat(),
                "due_by": due.isoformat(),
                "status": "queued_for_weekly_buddy_evaluation",
                "execution_status": "PLAN_ONLY_NOT_EXECUTED",
                "evaluation_suite": [
                    "transcript_comprehension",
                    "source_grounded_question_answering",
                    "factual_consistency",
                    "citation_and_provenance",
                    "retention_and_transfer",
                ],
            })
        else:
            blocked.append({
                "video_id": video_id,
                "status": "blocked_transcript_rights_or_provenance",
                "reason": (
                    "requires rights-cleared transcript, immutable SHA-256, "
                    "and explicit evaluation authorization"
                ),
            })

    status = (
        "PLAN_ONLY_NOT_EXECUTED" if eligible
        else "BLOCKED_NO_RIGHTS_CLEARED_TRANSCRIPTS" if blocked
        else "NO_TRANSCRIPT_RECORDS"
    )
    return {
        "schema": "dreamco.weekly_transcript_evaluation_plan.v1",
        "frequency": "weekly",
        "week_start": monday.isoformat(),
        "due_by": due.isoformat(),
        "every_eligible_transcript_once_per_week": True,
        "eligible_transcript_count": len(eligible),
        "blocked_transcript_count": len(blocked),
        "status": status,
        "eligible": eligible,
        "blocked": blocked,
        "transcript_content_included": False,
        "media_download_performed": False,
        "transcript_ingestion_performed": False,
        "model_training_allowed": False,
        "buddy_evaluation_executed": False,
    }


def validate_weekly_transcript_evaluation_plan(plan: dict[str, Any]) -> None:
    if plan.get("schema") != "dreamco.weekly_transcript_evaluation_plan.v1":
        raise ValueError("weekly transcript evaluation schema missing")
    if plan.get("frequency") != "weekly" or plan.get("every_eligible_transcript_once_per_week") is not True:
        raise ValueError("weekly transcript coverage contract missing")
    if any(plan.get(key) is not False for key in (
        "transcript_content_included", "media_download_performed",
        "transcript_ingestion_performed", "model_training_allowed",
        "buddy_evaluation_executed",
    )):
        raise ValueError("planner must not claim content ingestion, training, or execution")
    monday = date.fromisoformat(plan["week_start"])
    if monday.weekday() != 0 or date.fromisoformat(plan["due_by"]) != monday + timedelta(days=6):
        raise ValueError("weekly evaluation dates must cover Monday through Sunday")
    eligible = plan.get("eligible", [])
    blocked = plan.get("blocked", [])
    if plan.get("eligible_transcript_count") != len(eligible) or plan.get("blocked_transcript_count") != len(blocked):
        raise ValueError("weekly transcript counts do not match plan records")
    ids: set[str] = set()
    for item in eligible:
        video_id = item.get("video_id")
        if not isinstance(video_id, str) or video_id in ids:
            raise ValueError("eligible transcript IDs must be unique")
        ids.add(video_id)
        if not _SHA256.fullmatch(item.get("transcript_sha256", "")):
            raise ValueError("eligible transcript requires a valid SHA-256")
        if item.get("execution_status") != "PLAN_ONLY_NOT_EXECUTED":
            raise ValueError("planner cannot claim an evaluation was executed")
        if item.get("week_start") != plan["week_start"] or item.get("due_by") != plan["due_by"]:
            raise ValueError("eligible transcript dates do not match the plan")
        if "transcript_text" in item or "content" in item:
            raise ValueError("transcript content must not be included in the plan")
    for item in blocked:
        if item.get("video_id") in ids:
            raise ValueError("a transcript cannot be both eligible and blocked")
    expected = (
        "PLAN_ONLY_NOT_EXECUTED" if eligible
        else "BLOCKED_NO_RIGHTS_CLEARED_TRANSCRIPTS" if blocked
        else "NO_TRANSCRIPT_RECORDS"
    )
    if plan.get("status") != expected:
        raise ValueError("weekly transcript plan status is inconsistent")
