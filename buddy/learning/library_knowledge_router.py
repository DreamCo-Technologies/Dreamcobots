"""Internal-first Buddy library learning route with explicitly approved metadata discovery."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from buddy.learning.library_registry_discovery import search_public_registry
from buddy.learning.universal_library_registry import (
    ROOT,
    record_library_knowledge_gap,
    search_internal_library_knowledge,
)

CATEGORY_PROVIDERS = {
    "JAVASCRIPT / TYPESCRIPT CORE": ("npm",),
    "UTILITY LIBRARIES": ("npm",),
    "FRONTEND FRAMEWORKS": ("npm",),
    "META-FRAMEWORKS": ("npm",),
    "STATE MANAGEMENT": ("npm",),
    "CSS / STYLING": ("npm",),
    "UI COMPONENT LIBRARIES": ("npm",),
    "ANIMATION & MOTION": ("npm",),
    "3D / CANVAS / WEBGL": ("npm",),
    "DATA VISUALIZATION": ("npm",),
    "BUILD TOOLS": ("npm",),
    "TESTING": ("npm",),
    "REACT NATIVE / MOBILE": ("npm",),
    "NODE.JS BACKEND FRAMEWORKS": ("npm",),
    "PYTHON WEB FRAMEWORKS": ("pypi-exact",),
    "PYTHON DATA / ML / AI": ("pypi-exact",),
    "AI / LLM SDKs": ("npm", "huggingface-models"),
    "DATABASES & ORMS": ("npm",),
    "DATABASES (DIRECT)": ("npm",),
    "GRAPHQL": ("npm",),
    "REST / API PATTERNS": ("npm",),
    "RUST ECOSYSTEM": ("crates",),
    "GO ECOSYSTEM": (),
    "JAVA / KOTLIN ECOSYSTEM": (),
    "C# / .NET ECOSYSTEM": ("nuget",),
    "BLOCKCHAIN / WEB3": ("npm",),
    "FILE / MEDIA PROCESSING": ("npm",),
    "SEARCH": ("npm",),
    "RICH TEXT / EDITORS": ("npm",),
    "CLI TOOLING": ("npm",),
    "OTHER LANGUAGES & RUNTIMES": (),
}


def route_library_question(
    query: str,
    *,
    root: Path = ROOT,
    gap_root: Path | None = None,
    external_discovery: bool = False,
    persist_gap: bool = False,
    query_is_redacted: bool = False,
    requested_by: str = "buddy",
    limit: int = 5,
    registry_opener: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Search internal guides first; external metadata is opt-in and never executes code."""
    internal = search_internal_library_knowledge(query, root=root, limit=limit)
    if internal["matches"]:
        return {
            "schema": "dreamco.buddy_library_route.v1",
            "route": "internal_approved_guide",
            "internal": internal,
            "registry_candidates": [],
            "external_discovery_performed": False,
            "external_model_call_performed": False,
            "gap_recorded": False,
            "next_action": "study_internal_guide_and_complete_its_practice_and_assessment",
        }

    gap = None
    if persist_gap:
        if not query_is_redacted:
            raise PermissionError("redact the query before persisting a knowledge gap")
        gap = record_library_knowledge_gap(query, root=gap_root or root, requested_by=requested_by, query_is_redacted=True)

    registry_results = []
    provider_errors = []
    if external_discovery:
        for candidate in internal.get("seed_candidate_matches", [])[:3]:
            for provider in CATEGORY_PROVIDERS.get(
                candidate.get("categories", [""])[0], ()
            )[:2]:
                try:
                    result = search_public_registry(
                        provider,
                        str(candidate.get("name", "")),
                        allow_network=True,
                        limit=min(limit, 20),
                        root=root,
                        opener=registry_opener,
                    )
                    registry_results.append({
                        "candidate_id": candidate.get("candidate_id"),
                        "candidate_name": candidate.get("name"),
                        "discovery": result,
                    })
                except (ValueError, PermissionError, RuntimeError) as exc:
                    provider_errors.append({
                        "candidate_id": candidate.get("candidate_id"),
                        "provider": provider,
                        "error": str(exc),
                    })

    return {
        "schema": "dreamco.buddy_library_route.v1",
        "route": "internal_knowledge_gap",
        "internal": internal,
        "registry_candidates": registry_results,
        "provider_errors": provider_errors,
        "external_discovery_performed": bool(registry_results or provider_errors),
        "external_model_call_performed": False,
        "gap_recorded": gap is not None,
        "gap_event": gap,
        "next_action": (
            "review_metadata_candidates_and_rights_then_author_original_guide"
            if registry_results else
            "use_authorized_first_party_catalog_discovery_then_author_original_guide"
        ),
        "truth_boundary": (
            "Registry results are metadata candidates only. No package source, dataset, model weights "
            "or executable code is downloaded or run; no training permission is inferred."
        ),
    }
