"""Evidence-driven study scheduler for Buddy.

Selects the next study resource from capability gaps rather than a fixed list.
It records provenance/category metadata and creates a study->practice->benchmark
loop. This module does not download or ingest external material by itself.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class Resource:
    id: int
    name: str
    category: str
    url: str
    methods: tuple[str, ...] = ()


@dataclass
class Capability:
    name: str
    category: str
    score: float = 0.0
    failed_benchmarks: int = 0
    mastered: bool = False
    studied_resources: set[int] = field(default_factory=set)


def priority(resource: Resource, gaps: Iterable[Capability]) -> float:
    relevant = [g for g in gaps if g.category.lower() in resource.category.lower() or resource.category.lower() in g.category.lower()]
    if not relevant:
        return 0.05
    gap = max((1.0 - g.score) + min(g.failed_benchmarks, 5) * 0.1 for g in relevant)
    return gap + (0.25 if any(not g.mastered for g in relevant) else 0.0)


def choose_next(resources: Iterable[Resource], gaps: Iterable[Capability], *, recent: set[int] | None = None) -> Resource | None:
    recent = recent or set()
    candidates = [r for r in resources if r.id not in recent]
    return max(candidates, key=lambda r: priority(r, gaps), default=None)


def study_plan(resource: Resource, capability: Capability) -> dict:
    return {
        "resource_id": resource.id,
        "resource": resource.name,
        "capability": capability.name,
        "category": capability.category,
        "steps": [
            "retrieve_authorized_primary_material",
            "extract_concepts_and_examples",
            "practice_in_sandbox",
            "run_targeted_benchmark",
            "store_evidence_and_provenance",
            "retest_failed_cases",
            "promote_only_after_repeated_validation",
        ],
        "promotion_rule": "repeated validated success with no critical regression",
    }
