"""Registry-backed Buddy course lessons routed through the shared study scheduler.

This module exposes original DreamCo curriculum as queued study resources. It
never downloads course media, ingests transcripts, trains weights, or awards
mastery. Completion is recorded only by the evidence workflow.
"""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Any

from buddy.learning.study_resource_scheduler import Capability, Resource, choose_next, study_plan

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "config/buddy-course-track-registry.json"
DEFAULT_CROSSWALK = ROOT / "config/generated/masterbot-55-domain-crosswalk.json"
DEFAULT_MASTERBOTS = ROOT / "config/masterbot-65-registry.json"


@dataclass(frozen=True)
class CourseLesson:
    resource_id: int
    lesson_id: str
    track_id: str
    title: str
    category: str
    objective: str
    practice: str
    assessment: str
    benchmark: str
    source_url: str
    guide_path: str
    rights_mode: str
    delivery: str


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _stable_id(track_id: str, lesson_id: str) -> int:
    digest = hashlib.sha256(f"{track_id}:{lesson_id}".encode("utf-8")).digest()
    return (int.from_bytes(digest[:8], "big") & 0x7FFFFFFFFFFFFFFF) or 1


def _rows(track: dict, data: dict) -> list[dict]:
    parser = track["parser"]
    if parser == "tolkien":
        return [
            *[{"id": row["id"], "title": row["id"].replace("-", " ").title(),
               "objective": "; ".join(row.get("lessons", [])),
               "practice": row.get("practice", ""),
               "assessment": "Complete the original exercise with citations, item-level rights review and independent assessment."}
              for row in data.get("curriculum", [])],
            *[{"id": row["id"], "title": row["title"], "objective": row["outcome"],
               "practice": row["lab"], "assessment": row["assessment"]}
              for row in data.get("extended_study_path", [])],
        ]
    if parser == "lessons":
        return [
            {"id": row["id"], "title": row["title"], "objective": row["outcome"],
             "practice": row["lab"], "assessment": row["assessment"]}
            for row in data.get("lessons", [])
        ]
    if parser == "modules":
        return [
            {"id": row["id"], "title": row["title"], "objective": row["objective"],
             "practice": row["practice"], "assessment": row["rubric"], "benchmark": row["benchmark"]}
            for row in data.get("modules", [])
        ]
    if parser == "onet":
        return [
            {"id": row["id"], "title": row["name"],
             "objective": f"Understand the O*NET subject {row['name']} and apply its occupational evidence without inferring qualification or authority.",
             "practice": "Build an original subject guide, connect relevant tasks and tools, and classify AI/human responsibilities.",
             "assessment": "Pass a source-grounded subject assessment and task-specific suitability review."}
            for row in data.get("subject_inventory", [])
        ]
    if parser == "huggingface":
        return [
            {"id": row["id"], "title": row["id"].replace("-", " ").title(),
             "objective": row.get("description", ""),
             "practice": f"Build a small original sandbox exercise for the {row.get('family', 'unclassified')} task family; inspect model and dataset cards before use.",
             "assessment": "Complete a task-specific benchmark, rights review and independent holdout."}
            for row in data.get("task_families", [])
        ]
    if parser == "freecodecamp_video_catalog":
        inventory = data.get("inventory") or {}
        videos = data.get("videos") or []
        if int(data.get("video_count", -1)) != len(videos):
            raise ValueError("freeCodeCamp video catalog count does not match its video rows")
        if int(inventory.get("observed_entry_count", -1)) != len(videos):
            raise ValueError("freeCodeCamp observed inventory count does not match video rows")
        return [
            {
                "id": f"fcc-video-{row['video_id']}",
                "title": row["title"],
                "objective": row.get("description") or "Study the video only after an authorized transcript or equivalent source is available; title and metadata are not lesson content.",
                "practice": "Locate item-level study, derivative-summary and evaluation permissions; if authorized, create an original timestamped guide with exercises and answer key. Otherwise remain metadata-only.",
                "assessment": "Do not mark studied or mastered from a title, video URL or metadata row. Require a rights-cleared source, detailed guide, original exercise and independent assessment.",
                "benchmark": "FreeCodeCamp detailed video study-guide acceptance suite.",
                "source_url": row["url"],
            }
            for row in videos
        ]
    if parser == "huggingface_learning_map":
        courses = [
            {"id": row["id"], "title": row["title"], "objective": row["topics"],
             "practice": "Complete the official course activities where available and create an original DreamCo transfer project.",
             "assessment": row["assessment"], "benchmark": "Course-specific independent benchmark."}
            for row in data.get("official_courses", [])
        ]
        modules = [
            {"id": row["id"], "title": row["title"], "objective": row["objective"],
             "practice": row["practice"], "assessment": row["assessment"], "benchmark": row["benchmark"]}
            for row in data.get("ecosystem_modules", [])
        ]
        return courses + modules
    if parser == "freecodecamp":
        certs = [
            {"id": row["id"], "title": row["name"],
             "objective": "; ".join(row.get("skills", [])),
             "practice": "Complete original exercises and projects aligned to the official learning outcomes.",
             "assessment": "Complete the official requirements where authorized plus an independent DreamCo transfer task."}
            for row in data.get("official_platform_inventory", {}).get("core_certifications", [])
        ]
        phases = [
            {"id": row["id"], "title": row["id"].replace("-", " ").title(),
             "objective": "; ".join(row.get("focus", [])),
             "practice": "Complete original practical exercises and a capstone.",
             "assessment": "; ".join(row.get("exit_evidence", []))}
            for row in data.get("study_sequence", [])
        ]
        videos = [
            {"id": f"video-track-{name}", "title": name.replace("_", " ").title(),
             "objective": f"Build a complete original study path for the {name.replace('_', ' ')} video subject area.",
             "practice": "Refresh official video metadata; create a detailed guide only when authorized transcript or equivalent source evidence is available.",
             "assessment": "Verify unique video inventory, rights state, detailed guide coverage, practice and independent assessment."}
            for name in data.get("video_learning_tracks", [])
        ]
        return certs + phases + videos
    raise ValueError(f"unsupported course track parser: {parser}")


@lru_cache(maxsize=4)
def load_course_lessons(root: Path = ROOT) -> list[CourseLesson]:
    registry = _read(root / "config/buddy-course-track-registry.json")
    if registry.get("schema") != "dreamco.buddy_course_track_registry.v1":
        raise ValueError("unsupported Buddy course-track registry schema")
    crosswalk = _read(root / "config/generated/masterbot-55-domain-crosswalk.json")
    masterbots = _read(root / "config/masterbot-65-registry.json")
    if len(crosswalk.get("domains", [])) != 55 or len(masterbots.get("divisions", [])) != 65:
        raise ValueError("course-track routing requires the canonical 55-domain and 65-MasterBot registries")
    lessons: list[CourseLesson] = []
    seen: set[str] = set()
    resource_ids: set[int] = set()
    for track in registry.get("tracks", []):
        data = _read(root / track["source"])
        for row in _rows(track, data):
            lesson_id = str(row.get("id", "")).strip()
            title = str(row.get("title", "")).strip()
            if not lesson_id or not title:
                raise ValueError(f"track {track['id']} contains a lesson without a stable ID/title")
            key = f"{track['id']}:{lesson_id}"
            if key in seen:
                raise ValueError(f"duplicate course lesson ID: {key}")
            seen.add(key)
            rid = _stable_id(track["id"], lesson_id)
            if rid in resource_ids:
                raise ValueError("stable course resource ID collision")
            resource_ids.add(rid)
            lessons.append(CourseLesson(
                resource_id=rid,
                lesson_id=lesson_id,
                track_id=track["id"],
                title=title,
                category=track["category"],
                objective=str(row.get("objective", "")).strip(),
                practice=str(row.get("practice", "")).strip(),
                assessment=str(row.get("assessment", "")).strip(),
                benchmark=str(row.get("benchmark", "independent task and regression suite")).strip(),
                source_url=str(row.get("source_url") or track["source_url"]),
                guide_path=track["guide"],
                rights_mode=track["rights"],
                delivery=track["delivery"],
            ))
    return lessons


def resources_for_division(division: str, root: Path = ROOT) -> list[Resource]:
    crosswalk = _read(root / "config/generated/masterbot-55-domain-crosswalk.json")
    names = {row.get("domain_name") for row in crosswalk.get("domains", [])}
    if division not in names:
        raise ValueError(f"unknown canonical division: {division}")
    return [
        Resource(id=lesson.resource_id, name=lesson.title, category=lesson.category, url=lesson.source_url,
                 methods=("study_original_dreamco_guide", "practice_in_sandbox", "complete_assessment",
                          "run_independent_benchmark", "record_evidence"))
        for lesson in load_course_lessons(root)
    ]


def resources_for_masterbot(masterbot: str, root: Path = ROOT) -> list[Resource]:
    registry = _read(root / "config/masterbot-65-registry.json")
    names = {row.get("name") for row in registry.get("divisions", [])}
    if masterbot not in names:
        raise ValueError(f"unknown MasterBot lane: {masterbot}")
    return [
        Resource(id=lesson.resource_id, name=lesson.title, category=lesson.category, url=lesson.source_url,
                 methods=("study_original_dreamco_guide", "practice_in_sandbox", "complete_assessment",
                          "run_independent_benchmark", "record_evidence"))
        for lesson in load_course_lessons(root)
    ]


def plan_next_for_division(
    division: str,
    gaps: Iterable[Capability],
    root: Path = ROOT,
    *,
    recent: set[int] | None = None,
) -> dict | None:
    resources = resources_for_division(division, root)
    gap_list = list(gaps)
    chosen = choose_next(resources, gap_list, recent=recent)
    if chosen is None:
        return None
    lesson = next(row for row in load_course_lessons(root) if row.resource_id == chosen.id)
    capability = next((gap for gap in gap_list if gap.category.lower() == lesson.category.lower()), gap_list[0] if gap_list else Capability(name=division, category=lesson.category))
    plan = study_plan(chosen, capability)
    plan.update({
        "division": division,
        "track_id": lesson.track_id,
        "lesson_id": lesson.lesson_id,
        "objective": lesson.objective,
        "practice": lesson.practice,
        "assessment": lesson.assessment,
        "benchmark": lesson.benchmark,
        "guide_path": lesson.guide_path,
        "rights_mode": lesson.rights_mode,
        "completion_status": "queued_not_studied",
        "mastery_awarded": False,
        "model_weight_training_authorized": False,
        "paid_compute_authorized": False,
    })
    return plan
