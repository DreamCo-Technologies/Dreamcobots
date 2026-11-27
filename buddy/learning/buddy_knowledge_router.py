"""Internal-first Buddy learning router for approved guides and Bootcamp lessons.

This module never invokes a model, fetches a URL, or downloads/executes material.
A caller may explicitly request a gap record; otherwise user queries stay in memory.
"""
from __future__ import annotations

import hashlib
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
    normalized = value.lower().replace("huggingface", "hugging face")
    return {
        token for token in re.findall(r"[a-z0-9][a-z0-9_.+-]*", normalized)
        if len(token) > 1 and any(char.isalpha() for char in token)
    }


@lru_cache(maxsize=8)
def _cached_course_lessons(root: Path):
    return tuple(load_course_lessons(root))


def _supporting_guide(path: str, root: Path) -> dict[str, Any]:
    """Read a bounded excerpt from a repository-local supporting guide, never a remote URL."""
    if not isinstance(path, str) or not path.strip():
        return {"status": "not_in_repository", "path": path, "excerpt": ""}
    repo_root = root.resolve()
    candidate = (repo_root / path).resolve()
    if not candidate.is_relative_to(repo_root):
        return {"status": "blocked_path", "path": path, "excerpt": ""}
    if not candidate.is_file():
        return {"status": "not_in_repository", "path": path, "excerpt": ""}
    try:
        content = candidate.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return {"status": "unreadable", "path": path, "excerpt": ""}
    return {
        "status": "supporting_guide_available",
        "path": path,
        "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "excerpt": content[:6000],
        "truncated": len(content) > 6000,
        "guide_role": "supporting_reference_not_a_lesson_specific_completion_or_mastery_claim",
        "lesson_specific_guide_complete": False,
    }


def _exact_seed_candidate_ids(query: str, root: Path) -> set[str]:
    """Resolve exact candidate names from the complete local seed catalog.

    Search indexes are intentionally bounded and relevance-ranked; an exact
    name must not disappear merely because broader candidates outrank it.
    Candidate discovery remains unverified and never grants execution rights.
    """
    curriculum_path = root / "config/buddy-universal-library-curriculum.json"
    curriculum = json.loads(curriculum_path.read_text(encoding="utf-8")) if curriculum_path.is_file() else {}
    seed_path = root / curriculum.get("seed_catalog", "data/buddy-library-seed-catalog.json")
    if not seed_path.is_file():
        return set()
    catalog = json.loads(seed_path.read_text(encoding="utf-8"))
    return {
        f"candidate-discovery-{row.get('id')}"
        for row in catalog.get("candidates", [])
        if row.get("status") == "seed_candidate_unverified"
        and str(row.get("name", "")).strip().casefold() == query.strip().casefold()
        and row.get("id")
    }



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
        track_text = lesson.track_id.replace("-", " ").replace("_", " ")
        if lesson.track_id == "huggingface-full":
            track_text += " hugging face"
        track_overlap = query_tokens & _tokens(track_text)
        track_score = round(len(track_overlap) / max(len(query_tokens), 1), 4)
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
            "internal_guide": _supporting_guide(lesson.guide_path, root),
            "rights_mode": lesson.rights_mode,
            "score": round(len(overlap) / max(len(query_tokens), 1), 4),
            "track_match_score": track_score,
            "completion_status": "queued_not_studied",
            "mastery_awarded": False,
        })
    best_track_score = max((row["track_match_score"] for row in matches), default=0.0)
    # When the query explicitly names a curriculum track, do not dilute the
    # result set with unrelated generic tracks that happen to share body words.
    if best_track_score > 0:
        matches = [row for row in matches if row["track_match_score"] == best_track_score]
    matches.sort(key=lambda row: (-row["track_match_score"], -row["score"], row["track_id"], row["lesson_id"]))
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
    library = search_internal_library_knowledge(normalized_query, root=root, limit=100)
    guide_matches = library.get("matches", [])
    seed_matches = library.get("seed_candidate_matches", [])

    # Approved internal guides are authoritative and must short-circuit course
    # matching; this avoids unnecessary work and preserves internal-first order.
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

    # Exact seed candidates must be resolved against the full internal lesson
    # catalog, not hidden by the normal result limit.
    exact_candidate_ids = _exact_seed_candidate_ids(normalized_query, root)
    if exact_candidate_ids:
        all_lessons = _course_matches(
            normalized_query, root, limit=len(_cached_course_lessons(root.resolve()))
        )
        exact_candidate_lessons = [
            row for row in all_lessons if row["lesson_id"] in exact_candidate_ids
        ]
        if exact_candidate_lessons:
            supporting_guide_count = sum(
                row["internal_guide"]["status"] == "supporting_guide_available"
                for row in exact_candidate_lessons
            )
            missing_supporting_guide_count = len(exact_candidate_lessons) - supporting_guide_count
            return {
                "schema": "dreamco.buddy_internal_first_learning_route.v1",
                "query": normalized_query,
                "route": "internal_bootcamp_lesson",
                "answer_source": "dreamco_bootcamp_candidate_discovery",
                "guide_matches": [],
                "guide_documents": [],
                "course_lessons": exact_candidate_lessons,
                "supporting_guide_count": supporting_guide_count,
                "missing_supporting_guide_count": missing_supporting_guide_count,
                "seed_candidate_matches": seed_matches,
                "knowledge_gap": library.get("knowledge_gap"),
                "external_discovery_available": False,
                "external_discovery_requires_explicit_opt_in": True,
                "external_discovery_performed": False,
                "external_model_routing_performed": False,
                "study_required": True,
                "candidate_verification_required": True,
                "next_action": (
                    "Ask the user before external research; after approval, verify the candidate against "
                    "authoritative first-party sources, pin its exact version, review license and rights, "
                    "then author and assess an original study guide."
                ),
                "mastery_awarded": False,
            }

    lessons = _course_matches(normalized_query, root, limit)

    if lessons:
        supporting_guide_count = sum(
            row["internal_guide"]["status"] == "supporting_guide_available"
            for row in lessons
        )
        missing_supporting_guide_count = len(lessons) - supporting_guide_count
        return {
            "schema": "dreamco.buddy_internal_first_learning_route.v1",
            "query": normalized_query,
            "route": "internal_bootcamp_lesson",
            "answer_source": "dreamco_bootcamp_curriculum",
            "guide_matches": [],
            "guide_documents": [],
            "course_lessons": lessons,
            "supporting_guide_count": supporting_guide_count,
            "missing_supporting_guide_count": missing_supporting_guide_count,
            "seed_candidate_matches": seed_matches,
            "knowledge_gap": library.get("knowledge_gap"),
            "external_discovery_available": False,
            "external_discovery_requires_explicit_opt_in": supporting_guide_count == 0,
            "external_discovery_performed": False,
            "external_model_routing_performed": False,
            "study_required": True,
            "next_action": (
                "Study the repository-local supporting guide and complete the original practice. "
                "If it does not cover the requested lesson, ask the user before external research; "
                "then verify a first-party source, release and rights before drafting an original guide."
            ),
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
            "[redacted]",
            reason="no_approved_internal_guide_or_course_lesson",
            root=root,
            query_is_redacted=True,
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
        "external_discovery_available": False,
        "external_discovery_requires_explicit_opt_in": True,
        "external_discovery_performed": False,
        "external_model_routing_performed": False,
        "next_action": "Ask the user before external research; then verify first-party sources, version and rights, draft an original guide, and review and assess it.",
        "mastery_awarded": False,
    }
