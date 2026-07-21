"""
DreamCo Sandbox — Performance Rating System

Evaluates a bot's performance based on:
  - Task success rate (higher is better)
  - Error rate        (lower is better)
  - Task complexity   (weighted score; harder tasks count more)

Ratings are expressed as a 1–5 star score and a human-readable label.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Complexity weights — tasks can declare a complexity tier
# ---------------------------------------------------------------------------

COMPLEXITY_WEIGHTS: Dict[str, float] = {
    "trivial": 0.5,
    "easy": 1.0,
    "medium": 2.0,
    "hard": 3.0,
    "extreme": 5.0,
}

_DEFAULT_COMPLEXITY_WEIGHT = COMPLEXITY_WEIGHTS["medium"]


# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------


@dataclass
class TaskResult:
    """Record of a single task execution."""

    task_type: str
    success: bool
    complexity: str = "medium"
    error_message: Optional[str] = None

    @property
    def complexity_weight(self) -> float:
        return COMPLEXITY_WEIGHTS.get(self.complexity, _DEFAULT_COMPLEXITY_WEIGHT)


@dataclass
class BotRating:
    """Final performance rating for one bot."""

    bot_name: str
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    error_rate: float           # 0.0 – 1.0
    success_rate: float         # 0.0 – 1.0
    weighted_score: float       # 0.0 – 100.0
    star_rating: float          # 1.0 – 5.0
    label: str                  # e.g. "Excellent", "Good", …
    task_breakdown: Dict[str, int] = field(default_factory=dict)

    # Convenience -----------------------------------------------------------------

    def as_dict(self) -> Dict:
        return {
            "bot_name": self.bot_name,
            "total_tasks": self.total_tasks,
            "successful_tasks": self.successful_tasks,
            "failed_tasks": self.failed_tasks,
            "error_rate": round(self.error_rate, 4),
            "success_rate": round(self.success_rate, 4),
            "weighted_score": round(self.weighted_score, 2),
            "star_rating": self.star_rating,
            "label": self.label,
            "task_breakdown": self.task_breakdown,
        }


# ---------------------------------------------------------------------------
# Rating thresholds
# ---------------------------------------------------------------------------

_RATING_THRESHOLDS = [
    (90.0, 5.0, "Excellent"),
    (75.0, 4.0, "Good"),
    (55.0, 3.0, "Average"),
    (35.0, 2.0, "Below Average"),
    (0.0,  1.0, "Poor"),
]


def _score_to_stars(score: float) -> tuple[float, str]:
    """Map a weighted score (0–100) to (stars, label)."""
    for threshold, stars, label in _RATING_THRESHOLDS:
        if score >= threshold:
            return stars, label
    return 1.0, "Poor"


# ---------------------------------------------------------------------------
# PerformanceRatingSystem
# ---------------------------------------------------------------------------


class PerformanceRatingSystem:
    """
    Evaluates a collection of :class:`TaskResult` objects for one bot and
    produces a :class:`BotRating`.

    Scoring formula
    ---------------
    * Weighted success score = sum(weight_i for successful tasks_i) /
                               sum(weight_i for all tasks_i) × 100
    * Error penalty = error_rate × 20  (deducted from success score)
    * Final score clamped to [0, 100]

    Parameters
    ----------
    bot_name : str
        Display name of the bot under evaluation.
    """

    def __init__(self, bot_name: str) -> None:
        self.bot_name = bot_name
        self._results: List[TaskResult] = []

    # ------------------------------------------------------------------
    # Data ingestion
    # ------------------------------------------------------------------

    def record(self, result: TaskResult) -> None:
        """Add a :class:`TaskResult` to the evaluation pool."""
        self._results.append(result)

    def record_many(self, results: List[TaskResult]) -> None:
        """Bulk-add a list of :class:`TaskResult` objects."""
        self._results.extend(results)

    def reset(self) -> None:
        """Clear all recorded results."""
        self._results.clear()

    # ------------------------------------------------------------------
    # Computation
    # ------------------------------------------------------------------

    def compute_rating(self) -> BotRating:
        """
        Compute and return the :class:`BotRating` for the bot.

        Returns a rating of 1-star / "Poor" with all-zero counts when no
        results have been recorded.
        """
        if not self._results:
            return BotRating(
                bot_name=self.bot_name,
                total_tasks=0,
                successful_tasks=0,
                failed_tasks=0,
                error_rate=0.0,
                success_rate=0.0,
                weighted_score=0.0,
                star_rating=1.0,
                label="Poor",
            )

        total = len(self._results)
        successful = sum(1 for r in self._results if r.success)
        failed = total - successful

        success_rate = successful / total
        error_rate = failed / total

        # Weighted success score
        total_weight = sum(r.complexity_weight for r in self._results)
        success_weight = sum(r.complexity_weight for r in self._results if r.success)
        raw_score = (success_weight / total_weight * 100) if total_weight > 0 else 0.0

        # Error penalty
        penalty = error_rate * 20.0
        final_score = max(0.0, min(100.0, raw_score - penalty))

        stars, label = _score_to_stars(final_score)

        # Task-type breakdown
        breakdown: Dict[str, int] = {}
        for r in self._results:
            breakdown[r.task_type] = breakdown.get(r.task_type, 0) + 1

        return BotRating(
            bot_name=self.bot_name,
            total_tasks=total,
            successful_tasks=successful,
            failed_tasks=failed,
            error_rate=round(error_rate, 4),
            success_rate=round(success_rate, 4),
            weighted_score=round(final_score, 2),
            star_rating=stars,
            label=label,
            task_breakdown=breakdown,
        )

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    @property
    def result_count(self) -> int:
        """Number of task results recorded so far."""
        return len(self._results)
