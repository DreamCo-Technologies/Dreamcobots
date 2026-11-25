"""Internal-first Buddy learning router for approved guides and Bootcamp lessons.

This module never invokes a model, fetches a URL, or downloads/executes material.
A caller may explicitly request a gap record; otherwise user queries stay in memory.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from buddy.learning.course_track_registry import load_course_lessons
from buddy.learning.universal_library_registry import (
    record_library_knowledge_gap,
    search_internal_library_knowledge,
)

ROOT = Path(__file__).resolve().parents[2]


def _tokens(value: str) -> set[str]:
    return {
        token for token in re.findall(r"[a-z0-9][a-z0-9_.+-]*", value.lower())
        if len(token) > 1
    }


@lru_cache(maxsize=8)
def _cached_course_lessons(root: Path):
    return tuple(load_course_lessons(root))


def _course_matches(query: str, root: Path, limit: int) -> list[dict[str, Any]]:
    query_tokens = _tokens(query)
    matches: list[dict[str, Any]] = []
    for lesson in _cached_course_lessons(root.resolve()):
        searchable = " ".join((
            lesson.title, lesson.lesson_id, lesson.track_id, lesson.category,
            lesson.objective, lesson.practice, lesson.assessment, lesson.benchmark,
        ))
        overlap = query_tokens & _tokens(searchable)
        if not overlap:
            continue
        matches.append({
            "lesson_id": lesson.lesson_id,
            "track_id": lesson.track_id,
            "title": lesson.title,
            "objective": lesson.objective,
            "practice": lesson.practice,
            "assessment": lesson.assessment,
            "benchmark": lesson.benchmark,
            "source_url": lesson.source_url,
            "guide_path": lesson.guide_path,
            "rights_mode": lesson.rights_mode,
            "score": round(len(overlap) / max(len(query_tokens), 1), 4),
            "completion_status": "queued_not_studied",
            "mastery_awarded": False,
        })
    matches.sort(key=lambda row: (-row["score"], row["track_id"], row["lesson_id"]))
    return matches[:limit]


def route_buddy_learning_query(
    query: str,
    *,
    root: Path = ROOT,
    limit: int = 5,
    record_gap: bool = False,
) -> dict[str, Any]:
    """Prefer approved internal guide content, then Bootcamp lessons, then a gap.

    record_gap=True is an explicit persistence choice. No external discovery or
    model routing is ever initiated by this function.
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")
    if len(query) > 1000:
        raise ValueError("query must be at most 1000 characters")
    if limit < 1 or limit > 25:
        raise ValueError("limit must be between 1 and 25")

    normalized_query = query.strip()
    library = search_internal_library_knowledge(normalized_query, root=root, limit=limit)
    guide_matches = library.get("matches", [])
    if guide_matches:
        guide_documents = []
        for match in guide_matches:
            guide_path = root / str(match["guide_path"])
            guide_documents.append(json.loads(guide_path.read_text(encoding="utf-8")))
        return {
            "schema": "dreamco.buddy_internal_first_learning_route.v1",
            "query": normalized_query,
            "route": "internal_approved_guide",
            "answer_source": "dreamco_approved_library_guides",
            "guide_matches": guide_matches,
            "guide_documents": guide_documents,
            "course_lessons": [],
            "knowledge_gap": None,
            "external_discovery_performed": False,
            "external_model_routing_performed": False,
            "mastery_awarded": False,
        }

    lessons = _course_matches(normalized_query, root, limit)
    seed_matches = library.get("seed_candidate_matches", [])
    if lessons:
        return {
            "schema": "dreamco.buddy_internal_first_learning_route.v1",
            "query": normalized_query,
            "route": "internal_bootcamp_lesson",
            "answer_source": "dreamco_bootcamp_curriculum",
            "guide_matches": [],
            "guide_documents": [],
            "course_lessons": lessons,
            "seed_candidate_matches": seed_matches,
            "knowledge_gap": library.get("knowledge_gap"),
            "external_discovery_performed": False,
            "external_model_routing_performed": False,
            "study_required": True,
            "mastery_awarded": False,
        }

    gap = library.get("knowledge_gap") or {
        "status": "internal_knowledge_gap",
        "reason": "No approved guide or matching Bootcamp lesson was found.",
        "external_model_routing_required": False,
    }
    gap_event = None
    if record_gap:
        gap_event = record_library_knowledge_gap(
            normalized_query,
            reason="no_approved_internal_guide_or_course_lesson",
            root=root,
        )
    return {
        "schema": "dreamco.buddy_internal_first_learning_route.v1",
        "query": normalized_query,
        "route": "internal_knowledge_gap",
        "answer_source": None,
        "guide_matches": [],
        "guide_documents": [],
        "course_lessons": [],
        "seed_candidate_matches": seed_matches,
        "knowledge_gap": gap,
        "gap_event": gap_event,
        "external_discovery_available": True,
        "external_discovery_performed": False,
        "external_model_routing_performed": False,
        "next_action": "Find first-party sources, verify version and rights, draft an original guide, then review and assess it.",
        "mastery_awarded": False,
    }
