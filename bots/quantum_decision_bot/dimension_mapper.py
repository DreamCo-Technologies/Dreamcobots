"""
Dimension Mapper — DreamCo Quantum Decision Bot.

Maps a decision context across four strategic dimensions:

  • Time     — short-term vs long-term horizon
  • Capital  — low vs high investment requirement
  • Risk     — safe vs aggressive tolerance
  • Scale    — local vs global market scope

Each dimension is normalised to a 0–10 score so that the system can find
the intersection of best outcomes across all axes simultaneously — analogous
to how quantum systems explore entire state spaces at once.
"""

from __future__ import annotations

from typing import Dict, List

# GLOBAL AI SOURCES FLOW
from framework import GlobalAISourcesFlow  # noqa: F401

# ---------------------------------------------------------------------------
# Dimension ranges
# ---------------------------------------------------------------------------

_TIME_HORIZONS = {
    "immediate": 1,
    "short": 3,
    "medium": 5,
    "long": 7,
    "very_long": 10,
}

_CAPITAL_LEVELS = {
    "zero": 0,
    "low": 2,
    "medium": 5,
    "high": 8,
    "unlimited": 10,
}

_RISK_LEVELS = {
    "minimal": 1,
    "low": 3,
    "moderate": 5,
    "high": 7,
    "extreme": 10,
}

_SCALE_LEVELS = {
    "personal": 1,
    "local": 3,
    "regional": 5,
    "national": 7,
    "global": 10,
}


class DimensionMapper:
    """
    Maps a decision context across time, capital, risk, and scale dimensions.

    Usage::

        mapper = DimensionMapper()
        profile = mapper.map(context)
        score = mapper.optimality_score(profile)
    """

    # ------------------------------------------------------------------
    # Mapping
    # ------------------------------------------------------------------

    def map(self, context: dict) -> Dict[str, float]:
        """
        Convert a context dict into normalised dimension scores (0–10).

        Context keys (all optional with sensible defaults):

        - ``time_horizon``  : str key from _TIME_HORIZONS or float 0–10
        - ``budget``        : float (USD). Mapped to capital score.
        - ``risk_level``    : str key from _RISK_LEVELS or float 0–10
        - ``scale_goal``    : str key from _SCALE_LEVELS or float 0–10
        """
        time_score = self._resolve_dimension(
            context.get("time_horizon", "medium"), _TIME_HORIZONS, default=5.0
        )
        capital_score = self._budget_to_capital(context.get("budget"))
        risk_score = self._resolve_dimension(
            context.get("risk_level", "moderate"), _RISK_LEVELS, default=5.0
        )
        scale_score = self._resolve_dimension(
            context.get("scale_goal", "local"), _SCALE_LEVELS, default=3.0
        )

        return {
            "time": round(time_score, 2),
            "capital": round(capital_score, 2),
            "risk": round(risk_score, 2),
            "scale": round(scale_score, 2),
        }

    # ------------------------------------------------------------------
    # Optimality scoring
    # ------------------------------------------------------------------

    def optimality_score(self, profile: Dict[str, float]) -> float:
        """
        Compute an overall optimality score (0–100) from a dimension profile.

        Higher score = dimensions are well-balanced for success.
        The scoring rewards:
        - Moderate time horizons (neither too rushed nor too far)
        - Lower capital requirements
        - Lower risk exposure
        - Higher scale potential
        """
        time = profile.get("time", 5.0)
        capital = profile.get("capital", 5.0)
        risk = profile.get("risk", 5.0)
        scale = profile.get("scale", 3.0)

        # Ideal time: medium (5) → score peaks at centre
        time_component = max(0.0, 10.0 - abs(time - 5.0) * 2)
        # Lower capital = easier entry
        capital_component = max(0.0, 10.0 - capital)
        # Lower risk = higher score contribution
        risk_component = max(0.0, 10.0 - risk)
        # Higher scale = higher ceiling
        scale_component = scale

        raw = (time_component + capital_component + risk_component + scale_component) / 4.0
        return round(raw * 10, 2)  # scale to 0–100

    # ------------------------------------------------------------------
    # Multi-path intersection
    # ------------------------------------------------------------------

    def find_optimal_intersection(self, paths: List[dict]) -> List[dict]:
        """
        Given a list of path dicts (each with a ``profile`` and ``score``),
        return the subset whose dimension profiles are closest to ideal
        (time≈5, capital≈2, risk≈3, scale≈7).

        Returns paths sorted by optimality score, descending.
        """
        ideal = {"time": 5.0, "capital": 2.0, "risk": 3.0, "scale": 7.0}
        scored = []
        for path in paths:
            profile = path.get("profile", {})
            distance = sum(
                abs(profile.get(k, 5.0) - v) for k, v in ideal.items()
            )
            scored.append({**path, "_dim_distance": round(distance, 4)})
        return sorted(scored, key=lambda p: p["_dim_distance"])

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_dimension(value, lookup: dict, default: float = 5.0) -> float:
        if isinstance(value, (int, float)):
            return max(0.0, min(10.0, float(value)))
        if isinstance(value, str):
            return float(lookup.get(value.lower(), default))
        return default

    @staticmethod
    def _budget_to_capital(budget) -> float:
        """Map a USD budget to a capital score (0–10)."""
        if budget is None:
            return 5.0
        budget = float(budget)
        if budget == 0:
            return 0.0
        if budget < 500:
            return 2.0
        if budget < 5_000:
            return 4.0
        if budget < 25_000:
            return 6.0
        if budget < 100_000:
            return 8.0
        return 10.0
