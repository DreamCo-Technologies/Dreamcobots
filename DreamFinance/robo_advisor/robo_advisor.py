# GLOBAL AI SOURCES FLOW
"""Robo-Advisory Platform Bot — financial intelligence bot."""
import sys
import os
import importlib.util
_TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.normpath(os.path.join(_TOOL_DIR, '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from framework import GlobalAISourcesFlow  # noqa: F401
# Load local tiers.py by path to avoid sys.modules conflicts with other tiers modules
_tiers_spec = importlib.util.spec_from_file_location(
    '_local_tiers_robo_advisor', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS

DISCLAIMER = (
    "This tool is for educational and research purposes only. "
    "It does not constitute financial advice. "
    "Past performance does not guarantee future results."
)


class RoboAdvisor:
    """Robo-Advisory Platform Bot bot for financial analysis."""

    def __init__(self, tier: str = "enterprise"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["enterprise"])

    def profile_risk(self, answers: dict) -> dict:
        """Profile risk — Robo-Advisory Platform Bot."""
        score = answers.get("risk_tolerance", 3) * 20 + answers.get("time_horizon", 3) * 10 - answers.get("income_volatility", 2) * 5
        profile = "aggressive" if score > 80 else "moderate" if score > 50 else "conservative"
        return {"risk_score": score, "profile": profile, "disclaimer": DISCLAIMER}

    def construct_portfolio(self, profile: dict, goal: dict) -> dict:
        """Construct portfolio — Robo-Advisory Platform Bot."""
        risk = profile.get("profile", "moderate")
        allocations = {"aggressive": {"equities": 0.8, "bonds": 0.15, "cash": 0.05},
                       "moderate": {"equities": 0.6, "bonds": 0.3, "cash": 0.1},
                       "conservative": {"equities": 0.3, "bonds": 0.5, "cash": 0.2}}
        return {"allocation": allocations.get(risk, allocations["moderate"]), "goal": goal.get("name", "growth"), "disclaimer": DISCLAIMER}

    def run(self) -> str:
        """Return running status string."""
        return f"RoboAdvisor running: {self.tier} tier"
