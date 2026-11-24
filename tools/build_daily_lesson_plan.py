"""Build a measurable daily production target for original DreamCo lessons.

The plan creates work slots, not fake lessons or mastery records. Slots remain
queued until an original lesson passes rights, content, sandbox and benchmark
validation and its evidence is recorded.
"""
from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config/masterbot-65-registry.json"
OUTPUT = ROOT / "config/generated/daily-lesson-production-plan.json"


def build_plan(registry: dict, day: str, lessons_per_division: int = 5, queues: dict | None = None) -> dict:
    try:
        date.fromisoformat(day)
    except ValueError as exc:
        raise ValueError("day must be an ISO date") from exc
    divisions = registry.get("divisions")
    if not isinstance(divisions, list) or len(divisions) != 65:
        raise ValueError("canonical registry must contain exactly 65 divisions")
    ids = [row.get("id") for row in divisions]
    if sorted(ids) != list(range(1, 66)):
        raise ValueError("division IDs must be unique and cover 1 through 65")
    if not isinstance(lessons_per_division, int) or not 1 <= lessons_per_division <= 20:
        raise ValueError("lessons_per_division must be between 1 and 20")

    queue_by_division = {}
    if queues is not None:
        inventory = queues.get("source_inventory") or {}
        queue_rows = queues.get("divisions")
        if (
            queues.get("schema") != "dreamco.freecodecamp_division_learning_queues.v1"
            or queues.get("division_count") != 65
            or queues.get("source_inventory_status") != "complete"
            or inventory.get("complete") is not True
            or inventory.get("observed_entry_count") != queues.get("catalog_video_count")
            or not isinstance(queue_rows, list)
            or len(queue_rows) != 65
        ):
            raise ValueError("daily plan requires verified complete 65-division source queues")
        for row in queue_rows:
            division_id = row.get("division_id")
            items = row.get("items")
            if division_id in queue_by_division or not isinstance(items, list):
                raise ValueError("division queues must have unique IDs and item lists")
            ids = [item.get("video_id") for item in items]
            if len(ids) != len(set(ids)) or any(not video_id for video_id in ids):
                raise ValueError("division queue video IDs must be unique and present")
            for item in items:
                if (
                    item.get("rights_status") != "review_required"
                    or item.get("media_download_allowed") is not False
                    or item.get("transcript_ingestion_allowed") is not False
                    or item.get("training_eligible") is not False
                ):
                    raise ValueError("daily study candidates must remain rights-review-only and non-training")
            queue_by_division[division_id] = items
        if sorted(queue_by_division) != list(range(1, 66)):
            raise ValueError("division queues must cover IDs 1 through 65")

    slots = []
    for division in sorted(divisions, key=lambda row: row["id"]):
        candidates = queue_by_division.get(division["id"], []) if queues is not None else []
        for ordinal in range(1, lessons_per_division + 1):
            slot = {
                "slot_id": f"{day}-division-{division['id']:02d}-lesson-{ordinal:02d}",
                "division_id": division["id"],
                "division_name": division["name"],
                "lesson_number": ordinal,
                "status": "queued_not_created",
                "completion_requires": [
                    "original_dreamco_authored_content",
                    "source_provenance_and_rights_review",
                    "lesson_schema_validation",
                    "sandbox_exercise_pass",
                    "target_benchmark_pass",
                    "holdout_pass",
                    "regression_pass",
                ],
            }
            if queues is not None:
                if ordinal > len(candidates):
                    raise ValueError(f"division {division['id']} has fewer candidates than daily lesson slots")
                candidate = candidates[ordinal - 1]
                slot["candidate"] = {
                    "video_id": candidate["video_id"],
                    "title": candidate["title"],
                    "url": candidate["url"],
                    "categories": candidate.get("categories", []),
                    "priority_score": candidate.get("priority_score"),
                    "assignment_status": candidate["assignment_status"],
                    "rights_status": candidate["rights_status"],
                    "media_download_allowed": False,
                    "transcript_ingestion_allowed": False,
                    "training_eligible": False,
                }
            slots.append(slot)
    return {
        "schema": "dreamco.daily_lesson_production_plan.v1",
        "day_utc": day,
        "target_lessons_per_division": lessons_per_division,
        "division_count": len(divisions),
        "daily_target": len(slots),
        "created_lessons": 0,
        "validated_lessons": 0,
        "slots": slots,
        "status": "target_planned_not_completed",
        "generated_at": f"{day}T00:00:00+00:00",
        "policy": {
            "no_placeholder_counts_as_lesson": True,
            "no_mastery_without_benchmark_evidence": True,
            "no_external_media_or_transcript_without_explicit_rights": True,
            "model_training_requires_separate_permission": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--day", default=datetime.now(timezone.utc).date().isoformat())
    parser.add_argument("--lessons-per-division", type=int, default=5)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--queues", type=Path, help="Verified division queue JSON produced by build_freecodecamp_division_queues.py")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    queues = json.loads(args.queues.read_text(encoding="utf-8")) if args.queues else None
    plan = build_plan(json.loads(REGISTRY.read_text(encoding="utf-8")), args.day, args.lessons_per_division, queues=queues)
    rendered = json.dumps(plan, indent=2) + "\n"
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit("daily lesson production plan is stale")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(json.dumps({k: plan[k] for k in ("day_utc", "division_count", "target_lessons_per_division", "daily_target", "status")}, indent=2))


if __name__ == "__main__":
    main()
