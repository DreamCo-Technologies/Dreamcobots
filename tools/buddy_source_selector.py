#!/usr/bin/env python3
"""Rank authorized learning sources and choose the cheapest useful next action.

This planner is deliberately model-agnostic. It does not fetch content itself; adapters
must enforce robots.txt, terms, authentication boundaries, rate limits, and provenance.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Source:
    source_id: str
    authority: float
    benchmark_relevance: float
    freshness: float
    coverage_gap: float
    transfer_value: float
    cost_efficiency: float
    duplicate: bool = False
    rights_ok: bool = True
    authorized: bool = True

    def score(self) -> float:
        if not self.authorized or not self.rights_ok or self.duplicate:
            return float("-inf")
        return (
            0.30 * self.authority
            + 0.20 * self.benchmark_relevance
            + 0.15 * self.freshness
            + 0.15 * self.coverage_gap
            + 0.10 * self.transfer_value
            + 0.10 * self.cost_efficiency
        )


def rank_sources(sources: Iterable[Source]) -> list[tuple[str, float]]:
    """Return highest-value authorized sources first."""
    ranked = sorted(((s.source_id, s.score()) for s in sources), key=lambda x: x[1], reverse=True)
    return [(sid, score) for sid, score in ranked if score != float("-inf")]


def choose_execution_tier(
    *,
    task_difficulty: float,
    expected_information_gain: float,
    estimated_cost: float,
    cached: bool,
    holdout: bool = False,
) -> str:
    """Choose the least expensive tier likely to produce a useful signal."""
    if holdout:
        return "highest_available_independent_evaluator"
    if task_difficulty <= 0.25 and expected_information_gain > 0.05:
        return "deterministic_or_small_local_model"
    if cached and task_difficulty <= 0.65 and expected_information_gain / max(estimated_cost, 0.001) > 1.0:
        return "cached_local_or_small_model"
    if task_difficulty <= 0.80:
        return "medium_model"
    return "advanced_model_or_multi_agent_review"


def should_repeat(previous_attempts: int, new_information_expected: float) -> bool:
    """Avoid burning compute on identical failures."""
    return previous_attempts < 2 and new_information_expected > 0.10


if __name__ == "__main__":
    demo = [
        Source("primary-benchmark-docs", .98, .99, .95, .90, .95, .90),
        Source("secondary-summary", .55, .70, .90, .40, .50, .98),
        Source("duplicate-copy", .80, .80, .80, .50, .40, .90, duplicate=True),
    ]
    for source_id, score in rank_sources(demo):
        print(f"{source_id}\t{score:.3f}")
