# GLOBAL AI SOURCES FLOW
"""Dividend Investing Bot — financial intelligence bot."""
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
    '_local_tiers_dividend_investor', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS

DISCLAIMER = (
    "This tool is for educational and research purposes only. "
    "It does not constitute financial advice. "
    "Past performance does not guarantee future results."
)


class DividendInvestor:
    """Dividend Investing Bot bot for financial analysis."""

    def __init__(self, tier: str = "pro"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["pro"])

    def screen_aristocrats(self, stocks: list) -> list:
        """Screen aristocrats — Dividend Investing Bot."""
        return [s for s in stocks if s.get("consecutive_dividend_years", 0) >= 25]

    def score_sustainability(self, stock: dict) -> dict:
        """Score sustainability — Dividend Investing Bot."""
        payout = stock.get("payout_ratio", 0.5)
        fcf_coverage = stock.get("fcf_coverage", 1.0)
        score = round(min(100, (1 - payout) * 50 + fcf_coverage * 50), 2)
        return {"sustainability_score": score, "payout_ratio": payout, "safe": payout < 0.6 and fcf_coverage > 1.0, "disclaimer": DISCLAIMER}

    def automate_drip(self, portfolio: dict) -> dict:
        """Automate drip — Dividend Investing Bot."""
        total_divs = sum(h.get("annual_dividend", 0) * h.get("shares", 0) for h in portfolio.get("holdings", []))
        return {"annual_dividends": round(total_divs, 2), "drip_enabled": True, "reinvestment_schedule": "quarterly", "disclaimer": DISCLAIMER}

    def run(self) -> str:
        """Return running status string."""
        return f"DividendInvestor running: {self.tier} tier"
