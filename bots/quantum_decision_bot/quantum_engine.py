"""
Quantum Engine — DreamCo Quantum Decision Bot.

The core decision brain.  Inspired by Superposition and Wave Function
Collapse:

  1. Generate all possible scenario paths (superposition).
  2. Run Monte Carlo simulations on each path.
  3. Score every path using the probability model.
  4. "Collapse" to the single best path — the highest-probability, highest-
     return reality.

Returns a structured result with best path, alternatives, and a worst-case
warning so operators always know the downside before acting.
"""

from __future__ import annotations

from typing import List, Optional

# GLOBAL AI SOURCES FLOW
from framework import GlobalAISourcesFlow  # noqa: F401

from bots.quantum_decision_bot.simulation_engine import run_simulations, summarise_outcomes
from bots.quantum_decision_bot.probability_model import ProbabilityModel


# ---------------------------------------------------------------------------
# Default scenario templates
# ---------------------------------------------------------------------------

_DEFAULT_SCENARIOS = [
    {"name": "conservative",   "base_profit": 2_000,  "risk": 2.0, "volatility": 0.1},
    {"name": "moderate",       "base_profit": 10_000, "risk": 5.0, "volatility": 0.2},
    {"name": "aggressive",     "base_profit": 50_000, "risk": 8.0, "volatility": 0.35},
]


def _merge_context_into_scenario(scenario: dict, context: dict) -> dict:
    """Return a scenario with context overrides applied."""
    merged = dict(scenario)
    if "base_profit" in context:
        merged["base_profit"] = float(context["base_profit"])
    if "risk" in context:
        merged["risk"] = float(context["risk"])
    if "volatility" in context:
        merged["volatility"] = float(context["volatility"])
    return merged


# ---------------------------------------------------------------------------
# QuantumEngine
# ---------------------------------------------------------------------------

class QuantumEngine:
    """
    Core Quantum Decision Engine.

    Generates multiple scenario paths, simulates them, scores the outcomes,
    and collapses to the best reality path.

    Parameters
    ----------
    probability_model : ProbabilityModel, optional
        Shared probability model instance for scoring and learning.
    simulation_runs : int
        Number of Monte Carlo runs per scenario.
    """

    def __init__(
        self,
        probability_model: Optional[ProbabilityModel] = None,
        simulation_runs: int = 100,
    ) -> None:
        self.model = probability_model or ProbabilityModel()
        self.simulation_runs = max(1, int(simulation_runs))
        self._path_history: List[dict] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def decide(self, context: dict) -> dict:
        """
        Run the full quantum decision cycle and return a structured result.

        Parameters
        ----------
        context : dict
            Scenario context.  May override ``base_profit``, ``risk``,
            ``volatility``, or provide custom ``scenarios`` (list of dicts).

        Returns
        -------
        dict
            Keys:
            - ``best_path``   — highest-scoring scenario with full stats.
            - ``alternatives``— top-3 alternative paths.
            - ``worst_case``  — lowest-scoring scenario (risk warning).
            - ``all_paths``   — scored list of all evaluated paths.
        """
        scenarios = context.get("scenarios") or self._generate_scenarios(context)

        scored_paths: List[dict] = []
        for scenario in scenarios:
            path = self._evaluate_scenario(scenario, context)
            scored_paths.append(path)
            self._path_history.append(path)

        scored_paths.sort(key=lambda p: p["score"], reverse=True)

        best = scored_paths[0]
        worst = scored_paths[-1]
        alternatives = scored_paths[1:4]

        return {
            "best_path": best,
            "alternatives": alternatives,
            "worst_case": worst,
            "all_paths": scored_paths,
        }

    def get_path_history(self) -> List[dict]:
        """Return all paths evaluated in this engine's lifetime."""
        return list(self._path_history)

    def clear_history(self) -> None:
        """Clear the in-memory path history."""
        self._path_history.clear()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _generate_scenarios(self, context: dict) -> List[dict]:
        """
        Build the scenario list.

        If the context provides a ``base_profit`` / ``risk`` directly,
        the defaults are scaled around that anchor so comparisons remain
        meaningful.
        """
        base = float(context.get("base_profit", 10_000))
        risk = float(context.get("risk", 5.0))
        vol = float(context.get("volatility", 0.2))

        return [
            {
                "name": "conservative",
                "base_profit": base * 0.3,
                "risk": max(1.0, risk * 0.4),
                "volatility": max(0.05, vol * 0.6),
            },
            {
                "name": "moderate",
                "base_profit": base,
                "risk": risk,
                "volatility": vol,
            },
            {
                "name": "aggressive",
                "base_profit": base * 3.0,
                "risk": min(10.0, risk * 1.6),
                "volatility": min(0.6, vol * 1.6),
            },
        ]

    def _evaluate_scenario(self, scenario: dict, context: dict) -> dict:
        """
        Run simulations for a single scenario and score the outcomes.
        """
        merged = _merge_context_into_scenario(scenario, context)
        outcomes = run_simulations(merged, runs=self.simulation_runs)
        summary = summarise_outcomes(outcomes)
        score = self.model.score_outcomes(outcomes)
        prob_profit = self.model.probability_of_profit(outcomes)

        return {
            "scenario": merged.get("name", "unnamed"),
            "base_profit": merged["base_profit"],
            "risk": merged["risk"],
            "score": score,
            "probability_of_profit": prob_profit,
            "summary": summary,
        }
