"""Synchronize Buddy's freeCodeCamp catalog and course-queue counts.

This is metadata-only. It never downloads media or transcripts and does not
change any training-data permission.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
CATALOG = Path("buddy/bootcamp/sources/freecodecamp/catalog.json")
LEARNING_PATH = Path("config/freecodecamp-complete-learning-path.json")
POLICY = Path("config/buddy-continuous-study-policy.json")
TRACKS = Path("config/buddy-course-track-registry.json")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payloads(root: Path = ROOT) -> tuple[dict, dict]:
    catalog = read_json(root / CATALOG)
    videos = catalog.get("videos")
    inventory = catalog.get("inventory") or {}
    if not isinstance(videos, list) or catalog.get("video_count") != len(videos):
        raise ValueError("freeCodeCamp video_count does not match the catalog rows")
    ids = [row.get("video_id") for row in videos]
    if any(not isinstance(value, str) or not value for value in ids) or len(ids) != len(set(ids)):
        raise ValueError("freeCodeCamp catalog contains missing or duplicate video IDs")
    if inventory.get("observed_entry_count") != len(videos):
        raise ValueError("freeCodeCamp observed_entry_count does not match video rows")
    complete = (
        inventory.get("complete") is True
        and inventory.get("expected_entry_count") == len(videos)
        and inventory.get("observed_entry_count") == len(videos)
        and inventory.get("null_entry_count") == 0
        and inventory.get("duplicate_video_id_count") == 0
    )
    if catalog.get("inventory_status") != ("complete" if complete else "partial"):
        raise ValueError("freeCodeCamp inventory_status conflicts with its evidence")

    learning = read_json(root / LEARNING_PATH)
    learning["youtube_video_inventory"] = {
        "catalog_path": CATALOG.as_posix(),
        "observed_video_count": len(videos),
        "expected_entry_count": inventory.get("expected_entry_count"),
        "inventory_complete": complete,
        "inventory_status": "complete" if complete else "partial",
        "enumerator": inventory.get("enumerator"),
        "enumerator_version": inventory.get("enumerator_version"),
        "completeness_basis": inventory.get("completeness_basis"),
        "verified_at": catalog.get("generated_at"),
        "refresh_requirement": "Require playlist_count to match every unique parsed video ID; preserve partial status when count or enumerator evidence is missing.",
    }

    policy = read_json(root / POLICY)
    registry = read_json(root / TRACKS)
    from buddy.learning.course_track_registry import load_course_lessons
    lesson_count = len(load_course_lessons(root))
    policy.setdefault("study_assets", {})
    policy["study_assets"].update({
        "course_track_registry": "config/buddy-course-track-registry.json",
        "course_track_runtime_adapter": "buddy.learning.course_track_registry",
        "course_track_count": len(registry.get("tracks", [])),
        "course_lesson_count": lesson_count,
        "course_lesson_count_updated_at": catalog.get("generated_at"),
        "freecodecamp_video_inventory_status": "complete" if complete else "partial",
        "freecodecamp_video_count": len(videos),
        "course_track_rule": (
            "All canonical divisions and MasterBot lanes receive shared foundation queues. The registry includes "
            "12 official Hugging Face Learn courses, 18 Hugging Face ecosystem modules, all 37 Hugging Face task families, "
            "12 current/additional freeCodeCamp certifications, all seven curriculum primitives, 10 learning phases, "
            "22 video subject tracks, every currently cataloged freeCodeCamp video, Tolkien, tokenizer, CPU-first LLM, "
            "O*NET subject lessons plus task-level lessons when a verified O*NET index is present, one discovery lesson for each of 38 registered software library ecosystems, and "
            "531 unverified technology/library candidates extracted from Buddy's existing mastery curriculum. Video "
            "metadata remains metadata-only until item-level rights are reviewed; the checked-in video snapshot is "
            "partial. Ecosystem and seed-candidate discovery lessons are not verified package records or mastered "
            "library guides."
        ),
    })
    return learning, policy


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the checked-in counts are stale")
    args = parser.parse_args()
    learning, policy = build_payloads()
    outputs = {
        ROOT / LEARNING_PATH: json.dumps(learning, ensure_ascii=False, indent=2) + "\n",
        ROOT / POLICY: json.dumps(policy, ensure_ascii=False, indent=2) + "\n",
    }
    stale = [path for path, content in outputs.items()
             if not path.exists() or path.read_text(encoding="utf-8") != content]
    if args.check:
        if stale:
            raise SystemExit("freeCodeCamp learning inventory counts are stale: " + ", ".join(p.relative_to(ROOT).as_posix() for p in stale))
        print("freeCodeCamp learning inventory counts: PASS")
        return 0
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8")
    print(f"freeCodeCamp learning inventory synchronized ({learning['youtube_video_inventory']['observed_video_count']} videos; {policy['study_assets']['course_lesson_count']} queued lessons; {learning['youtube_video_inventory']['inventory_status']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
