"""
Performance analytics layer for the DreamCo Global AI Learning System.

Normalizes sandbox test metrics and computes global and regional rankings
for all tested AI/ML methods.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import datetime
import uuid

from .tiers import Tier, TierConfig, get_tier_config, FEATURE_ANALYTICS
from .sandbox import SandboxTestResult, SandboxStatus
from .classifier import ClassifiedMethod
from framework import GlobalAISourcesFlow  # noqa: F401


@dataclass
class MethodRanking:
    """Global and regional ranking for a tested AI/ML method.

    Attributes
    ----------
    method_id : str
        ID of the ClassifiedMethod.
    method_title : str
        Human-readable method title.
    global_rank : int
        Rank across all methods (1 = best).
    regional_rank : int
        Rank within the method's country/region.
    region : str
        Country or region label.
    composite_score : float
        Weighted normalised score (0.0–1.0).
    accuracy_score : float
        Normalised accuracy contribution.
    convergence_score : float
        Normalised convergence contribution.
    efficiency_score : float
        Normalised efficiency (inverse of resource consumption).
    test_count : int
        Number of sandbox runs contributing to this ranking.
    computed_at : datetime.datetime
        UTC timestamp of computation.
    """

    method_id: str
    method_title: str
    global_rank: int
    regional_rank: int
    region: str
    composite_score: float
    accuracy_score: float
    convergence_score: float
    efficiency_score: float
    test_count: int
    computed_at: datetime.datetime


class AnalyticsTierError(Exception):
    """Raised when the current tier does not support analytics."""


# Weights for the composite score
_W_ACCURACY = 0.50
_W_CONVERGENCE = 0.30
_W_EFFICIENCY = 0.20


def _normalise(values: List[float]) -> List[float]:
    """Min-max normalise a list of floats to [0.0, 1.0]."""
    if not values:
        return values
    lo, hi = min(values), max(values)
    if hi == lo:
        return [1.0] * len(values)
    return [(v - lo) / (hi - lo) for v in values]


class PerformanceAnalyticsLayer:
    """Computes normalised performance rankings from sandbox test results.

    Parameters
    ----------
    tier : Tier
        Subscription tier (FREE and above support analytics).
    """

    def __init__(self, tier: Tier) -> None:
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)
        self._rankings: List[MethodRanking] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compute_rankings(
        self,
        test_results: List[SandboxTestResult],
        methods: List[ClassifiedMethod],
    ) -> List[MethodRanking]:
        """Compute global and regional rankings from sandbox results.

        Parameters
        ----------
        test_results : List[SandboxTestResult]
            Completed sandbox test results.
        methods : List[ClassifiedMethod]
            Corresponding classified methods (matched by method_id).

        Returns
        -------
        List[MethodRanking]
            Rankings sorted best-first by composite_score.

        Raises
        ------
        AnalyticsTierError
            If the current tier does not have FEATURE_ANALYTICS.
        """
        self._check_tier()

        method_map = {m.id: m for m in methods}
        completed = [r for r in test_results if r.status == SandboxStatus.COMPLETED]
        if not completed:
            return []

        # Aggregate metrics per method (average over multiple runs)
        aggregated: dict = {}
        for r in completed:
            if r.method_id not in aggregated:
                aggregated[r.method_id] = {
                    "accuracies": [],
                    "convergences": [],
                    "resources": [],
                    "count": 0,
                }
            entry = aggregated[r.method_id]
            if r.accuracy is not None:
                entry["accuracies"].append(r.accuracy)
            if r.convergence_rate is not None:
                entry["convergences"].append(r.convergence_rate)
            if r.resource_consumption is not None:
                entry["resources"].append(r.resource_consumption)
            entry["count"] += 1

        method_ids = list(aggregated.keys())
        avg_accuracy = [
            sum(aggregated[mid]["accuracies"]) / len(aggregated[mid]["accuracies"])
            if aggregated[mid]["accuracies"] else 0.0
            for mid in method_ids
        ]
        avg_convergence = [
            sum(aggregated[mid]["convergences"]) / len(aggregated[mid]["convergences"])
            if aggregated[mid]["convergences"] else 0.0
            for mid in method_ids
        ]
        avg_resource = [
            sum(aggregated[mid]["resources"]) / len(aggregated[mid]["resources"])
            if aggregated[mid]["resources"] else 50.0
            for mid in method_ids
        ]
        # Efficiency = 1 - normalised_resource (less CPU is better)
        inv_resource = [100.0 - v for v in avg_resource]

        norm_acc = _normalise(avg_accuracy)
        norm_conv = _normalise(avg_convergence)
        norm_eff = _normalise(inv_resource)

        composite = [
            _W_ACCURACY * a + _W_CONVERGENCE * c + _W_EFFICIENCY * e
            for a, c, e in zip(norm_acc, norm_conv, norm_eff)
        ]

        now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        entries = []
        for i, mid in enumerate(method_ids):
            m = method_map.get(mid)
            title = m.title if m else mid
            region = m.country_of_origin if m else "Unknown"
            entries.append({
                "method_id": mid,
                "title": title,
                "region": region,
                "composite": composite[i],
                "accuracy": norm_acc[i],
                "convergence": norm_conv[i],
                "efficiency": norm_eff[i],
                "count": aggregated[mid]["count"],
            })

        # Sort by composite score descending for global rank
        entries.sort(key=lambda x: x["composite"], reverse=True)

        # Regional ranks
        regional_counters: dict = {}
        rankings: List[MethodRanking] = []
        for global_rank, entry in enumerate(entries, start=1):
            region = entry["region"]
            regional_counters[region] = regional_counters.get(region, 0) + 1
            regional_rank = regional_counters[region]

            ranking = MethodRanking(
                method_id=entry["method_id"],
                method_title=entry["title"],
                global_rank=global_rank,
                regional_rank=regional_rank,
                region=region,
                composite_score=round(entry["composite"], 4),
                accuracy_score=round(entry["accuracy"], 4),
                convergence_score=round(entry["convergence"], 4),
                efficiency_score=round(entry["efficiency"], 4),
                test_count=entry["count"],
                computed_at=now,
            )
            rankings.append(ranking)

        self._rankings = rankings
        return rankings

    def get_global_matrix(self) -> List[MethodRanking]:
        """Return the most recently computed ranking matrix."""
        return list(self._rankings)

    def get_top_methods(self, n: int = 10) -> List[MethodRanking]:
        """Return the top *n* methods by composite score."""
        return sorted(self._rankings, key=lambda r: r.composite_score, reverse=True)[:n]

    def get_stats(self) -> dict:
        """Return a summary of analytics activity."""
        return {
            "total_ranked": len(self._rankings),
            "top_method": self._rankings[0].method_title if self._rankings else None,
            "top_score": self._rankings[0].composite_score if self._rankings else None,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_tier(self) -> None:
        if not self.config.has_feature(FEATURE_ANALYTICS):
            raise AnalyticsTierError(
                f"Performance analytics is not available on the "
                f"{self.config.name} tier. Please upgrade."
            )
