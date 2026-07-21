# GLOBAL AI SOURCES FLOW
"""ESG Investment Optimizer — financial intelligence bot."""
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
    '_local_tiers_esg_optimizer', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS

DISCLAIMER = (
    "This tool is for educational and research purposes only. "
    "It does not constitute financial advice. "
    "Past performance does not guarantee future results."
)


class ESGOptimizer:
    """ESG Investment Optimizer bot for financial analysis."""

    def __init__(self, tier: str = "enterprise"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["enterprise"])

    def score_esg(self, company: dict) -> dict:
        """Score esg — ESG Investment Optimizer."""
        e = company.get("environmental_score", 50)
        s = company.get("social_score", 50)
        g = company.get("governance_score", 50)
        total = round((e + s + g) / 3, 2)
        return {"environmental": e, "social": s, "governance": g, "total_esg": total, "grade": "A" if total > 75 else "B" if total > 50 else "C", "disclaimer": DISCLAIMER}

    def track_carbon(self, portfolio: list) -> dict:
        """Track carbon — ESG Investment Optimizer."""
        total = sum(h.get("carbon_tons", 0) for h in portfolio)
        return {"total_carbon_tons": round(total, 2), "holdings": len(portfolio), "avg_per_holding": round(total / len(portfolio), 2) if portfolio else 0, "disclaimer": DISCLAIMER}

    def measure_impact(self, portfolio: list) -> dict:
        """Measure impact — ESG Investment Optimizer."""
        scores = [h.get("impact_score", 0) for h in portfolio]
        avg = round(sum(scores) / len(scores), 2) if scores else 0
        return {"avg_impact_score": avg, "positive_count": sum(1 for s in scores if s > 50), "disclaimer": DISCLAIMER}

    def run(self) -> str:
        """Return running status string."""
        return f"ESGOptimizer running: {self.tier} tier"
