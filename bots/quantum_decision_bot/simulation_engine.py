"""
Simulation Engine — DreamCo Quantum Decision Bot.

Runs Monte Carlo simulations for a given scenario.  Each simulation
introduces random variation (Gaussian noise) to model real-world
uncertainty, producing a distribution of profit and risk outcomes.

Inspired by the Double-Slit Experiment: observation (simulation) of all
possible paths before acting reveals the best reality to collapse into.
"""

from __future__ import annotations

import random
from typing import List


# GLOBAL AI SOURCES FLOW
from framework import GlobalAISourcesFlow  # noqa: F401


def run_simulations(scenario: dict, runs: int = 100) -> List[dict]:
    """
    Run *runs* Monte Carlo simulations for *scenario* and return a list of
    outcome dicts, each containing ``profit``, ``risk``, and ``run_index``.

    Parameters
    ----------
    scenario : dict
        Must contain:
        - ``base_profit``  (float) — expected profit under nominal conditions.
        - ``risk``         (float) — base risk score (1–10 scale).
        Optionally:
        - ``volatility``   (float, default 0.2) — std-dev multiplier for noise.

    runs : int
        Number of simulation iterations. Clamped to a minimum of 1.

    Returns
    -------
    list[dict]
        Each entry: ``{"run_index": int, "profit": float, "risk": float}``.
    """
    runs = max(1, int(runs))
    base_profit: float = float(scenario.get("base_profit", 0.0))
    base_risk: float = float(scenario.get("risk", 5.0))
    volatility: float = float(scenario.get("volatility", 0.2))

    outcomes: List[dict] = []
    for i in range(runs):
        noise = random.gauss(1.0, volatility)
        # Clamp noise so profit never goes fully negative unless intentional
        noise = max(0.1, noise)
        sim_profit = round(base_profit * noise, 2)
        sim_risk = round(min(10.0, max(0.0, base_risk * (1.0 / noise))), 2)
        outcomes.append({"run_index": i, "profit": sim_profit, "risk": sim_risk})

    return outcomes


def summarise_outcomes(outcomes: List[dict]) -> dict:
    """
    Return statistical summary of simulation outcomes.

    Keys: ``count``, ``avg_profit``, ``min_profit``, ``max_profit``,
    ``avg_risk``, ``profitable_runs``, ``profitable_pct``.
    """
    if not outcomes:
        return {
            "count": 0,
            "avg_profit": 0.0,
            "min_profit": 0.0,
            "max_profit": 0.0,
            "avg_risk": 0.0,
            "profitable_runs": 0,
            "profitable_pct": 0.0,
        }

    profits = [o["profit"] for o in outcomes]
    risks = [o["risk"] for o in outcomes]
    profitable = [p for p in profits if p > 0]

    count = len(outcomes)
    return {
        "count": count,
        "avg_profit": round(sum(profits) / count, 2),
        "min_profit": round(min(profits), 2),
        "max_profit": round(max(profits), 2),
        "avg_risk": round(sum(risks) / count, 2),
        "profitable_runs": len(profitable),
        "profitable_pct": round(len(profitable) / count * 100, 1),
    }
