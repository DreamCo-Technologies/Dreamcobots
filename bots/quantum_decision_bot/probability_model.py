"""
Probability Model — DreamCo Quantum Decision Bot.

Converts simulation outcomes into a single composite score that balances
expected profit against risk exposure.  The model can be updated (trained)
with real-world results so it self-improves over time.

Inspired by Quantum Wave Function Collapse: many possibilities are scored and
the highest-probability path is selected.
"""

from __future__ import annotations

from typing import List

# GLOBAL AI SOURCES FLOW
from framework import GlobalAISourcesFlow  # noqa: F401


class ProbabilityModel:
    """
    Scores simulation outcomes and maintains a simple self-improving
    weight system.

    Parameters
    ----------
    profit_weight : float
        How much weight to give average profit in the composite score.
    risk_weight : float
        How much weight to give average risk in the composite score
        (subtracted from score — higher risk lowers the score).
    """

    DEFAULT_PROFIT_WEIGHT = 1.0
    DEFAULT_RISK_WEIGHT = 0.5

    def __init__(
        self,
        profit_weight: float = DEFAULT_PROFIT_WEIGHT,
        risk_weight: float = DEFAULT_RISK_WEIGHT,
    ) -> None:
        self.profit_weight = float(profit_weight)
        self.risk_weight = float(risk_weight)
        self._outcomes_history: List[dict] = []

    # ------------------------------------------------------------------
    # Core scoring
    # ------------------------------------------------------------------

    def score_outcomes(self, outcomes: List[dict]) -> float:
        """
        Compute a composite score for a list of simulation outcomes.

        Score = (avg_profit * profit_weight) - (avg_risk * risk_weight)

        Returns
        -------
        float
            Composite score.  Higher = better.  Can be negative if risk
            dominates.
        """
        if not outcomes:
            return 0.0

        profits = [o["profit"] for o in outcomes]
        risks = [o["risk"] for o in outcomes]

        avg_profit = sum(profits) / len(profits)
        avg_risk = sum(risks) / len(risks)

        return round(
            avg_profit * self.profit_weight - avg_risk * self.risk_weight,
            4,
        )

    def probability_of_profit(self, outcomes: List[dict]) -> float:
        """
        Return probability (0.0–1.0) that a random outcome from *outcomes*
        will be profitable (profit > 0).
        """
        if not outcomes:
            return 0.0
        positive = sum(1 for o in outcomes if o["profit"] > 0)
        return round(positive / len(outcomes), 4)

    # ------------------------------------------------------------------
    # Learning / adaptation
    # ------------------------------------------------------------------

    def learn(self, scenario_name: str, predicted_score: float, actual_profit: float) -> dict:
        """
        Record an actual outcome to improve future scoring.

        Adjusts ``profit_weight`` upward when the system under-estimated
        profit, and adjusts ``risk_weight`` upward when it over-estimated.
        Returns a summary of the adjustment made.
        """
        entry = {
            "scenario": scenario_name,
            "predicted_score": predicted_score,
            "actual_profit": actual_profit,
        }
        self._outcomes_history.append(entry)

        # Simple gradient: nudge weights based on prediction error
        error = actual_profit - predicted_score
        if error > 0:
            # System was too conservative — increase profit sensitivity
            self.profit_weight = round(min(2.0, self.profit_weight + 0.01), 4)
        elif error < 0:
            # System was too optimistic — increase risk sensitivity
            self.risk_weight = round(min(2.0, self.risk_weight + 0.01), 4)

        return {
            "scenario": scenario_name,
            "error": round(error, 4),
            "new_profit_weight": self.profit_weight,
            "new_risk_weight": self.risk_weight,
        }

    def get_weights(self) -> dict:
        """Return current model weights."""
        return {
            "profit_weight": self.profit_weight,
            "risk_weight": self.risk_weight,
        }

    def get_history_count(self) -> int:
        """Return the number of learning iterations recorded."""
        return len(self._outcomes_history)

    def reset_weights(self) -> None:
        """Reset model weights to defaults."""
        self.profit_weight = self.DEFAULT_PROFIT_WEIGHT
        self.risk_weight = self.DEFAULT_RISK_WEIGHT
