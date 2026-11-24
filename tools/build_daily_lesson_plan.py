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
CROSSWALK = ROOT / "config/generated/masterbot-55-domain-crosswalk.json"
OUTPUT = ROOT / "config/generated/daily-lesson-production-plan.json"


def build_plan(crosswalk: dict, day: str, lessons_per_domain: int = 5, queues: dict | None = None) -> dict:
    try:
        date.fromisoformat(day)
    except ValueError as exc:
        raise ValueError("day must be an ISO date") from exc
    domains = crosswalk.get("domains")
    if not isinstance(domains, list) or len(domains) != 55:
        raise ValueError("canonical crosswalk must contain exactly 55 domain divisions")
    ids = [row.get("domain_id") for row in domains]
    if len(set(ids)) != 55 or any(not isinstance(value, str) or not value for value in ids):
        raise ValueError("domain IDs must be unique and non-empty")
    if sum(row.get("mapping_status") == "proposed_exact_name_match" for row in domains) != 45:
        raise ValueError("crosswalk must contain 45 core domain proposals")
    if sum(row.get("mapping_status") == "unresolved" for row in domains) != 10:
        raise ValueError("crosswalk must preserve 10 supplemental domain profiles")
    if not isinstance(lessons_per_domain, int) or not 1 <= lessons_per_domain <= 20:
        raise ValueError("lessons_per_domain must be between 1 and 20")

    queue_by_division = {}
    if queues is not None:
        inventory = queues.get("source_inventory") or {}
        queue_rows = queues.get("divisions")
        if (
            queues.get("schema") != "dreamco.freecodecamp_division_learning_queues.v1"
            or queues.get("domain_count") != 55
            or queues.get("source_inventory_status") != "complete"
            or inventory.get("complete") is not True
            or inventory.get("observed_entry_count") != queues.get("catalog_video_count")
            or not isinstance(queue_rows, list)
            or len(queue_rows) != 55
        ):
            raise ValueError("daily plan requires verified complete 65-division source queues")
        for row in queue_rows:
            domain_id = row.get("domain_id")
            items = row.get("items")
            if domain_id in queue_by_division or not isinstance(items, list):
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
            queue_by_division[domain_id] = items
        if set(queue_by_division) != set(ids):
            raise ValueError("domain queues must cover all 55 domain IDs exactly")

    slots = []
    for domain in sorted(domains, key=lambda row: row["domain_id"]):
        candidates = queue_by_division.get(domain["domain_id"], []) if queues is not None else []
        for ordinal in range(1, lessons_per_domain + 1):
            slot = {
                "slot_id": f"{day}-domain-{domain['domain_id']}-lesson-{ordinal:02d}",
                "domain_id": domain["domain_id"],
                "domain_name": domain["domain_name"],
                "masterbot_id": domain.get("masterbot_id"),
                "mapping_status": domain.get("mapping_status"),
                "owner_review_required": domain.get("review_required", True),
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
                    raise ValueError(f"domain {domain['domain_id']} has fewer candidates than daily lesson slots")
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
        "target_lessons_per_domain": lessons_per_domain,
        "domain_count": len(domains),
        "masterbot_count": 65,
        "shared_platform_masterbot_count": 20,
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
    parser.add_argument("--lessons-per-domain", type=int, default=5)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--queues", type=Path, help="Verified division queue JSON produced by build_freecodecamp_division_queues.py")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    queues = json.loads(args.queues.read_text(encoding="utf-8")) if args.queues else None
    plan = build_plan(json.loads(CROSSWALK.read_text(encoding="utf-8")), args.day, args.lessons_per_domain, queues=queues)
    rendered = json.dumps(plan, indent=2) + "\n"
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit("daily lesson production plan is stale")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(json.dumps({k: plan[k] for k in ("day_utc", "domain_count", "target_lessons_per_domain", "daily_target", "status")}, indent=2))


if __name__ == "__main__":
    main()
