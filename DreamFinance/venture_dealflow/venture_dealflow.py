# GLOBAL AI SOURCES FLOW
"""Venture Capital Deal Flow Bot — financial intelligence bot."""
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
    '_local_tiers_venture_dealflow', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS

DISCLAIMER = (
    "This tool is for educational and research purposes only. "
    "It does not constitute financial advice. "
    "Past performance does not guarantee future results."
)


class VentureDealflow:
    """Venture Capital Deal Flow Bot bot for financial analysis."""

    def __init__(self, tier: str = "enterprise"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["enterprise"])

    def source_deals(self, criteria: dict) -> list:
        """Source deals — Venture Capital Deal Flow Bot."""
        stage = criteria.get("stage", "seed")
        sector = criteria.get("sector", "fintech")
        return [
            {"company": f"{sector.capitalize()} Startup {i+1}", "stage": stage, "match_score": round(0.9 - i * 0.1, 2)}
            for i in range(criteria.get("limit", 5))
        ]

    def screen_deal(self, company: dict) -> dict:
        """Screen deal — Venture Capital Deal Flow Bot."""
        score = round(
            company.get("revenue_growth", 0) * 0.3 +
            company.get("team_score", 5) * 10 +
            company.get("market_size_bn", 1) * 5, 2
        )
        return {"company": company.get("name", ""), "due_diligence_score": score, "proceed": score > 50, "disclaimer": DISCLAIMER}

    def monitor_portfolio(self, portfolio: list) -> list:
        """Monitor portfolio — Venture Capital Deal Flow Bot."""
        return [{"company": c.get("name", ""), "status": "on_track" if c.get("mrr_growth", 0) > 0 else "needs_attention", "mrr_growth": c.get("mrr_growth", 0)} for c in portfolio]

    def run(self) -> str:
        """Return running status string."""
        return f"VentureDealflow running: {self.tier} tier"
