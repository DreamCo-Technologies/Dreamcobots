# GLOBAL AI SOURCES FLOW
"""Tax Efficiency Planner — financial intelligence bot."""
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
    '_local_tiers_tax_optimizer', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS

DISCLAIMER = (
    "This tool is for educational and research purposes only. "
    "It does not constitute financial advice. "
    "Past performance does not guarantee future results."
)


class TaxOptimizer:
    """Tax Efficiency Planner bot for financial analysis."""

    def __init__(self, tier: str = "pro"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["pro"])

    def harvest_losses(self, portfolio: dict) -> list:
        """Harvest losses — Tax Efficiency Planner."""
        harvests = []
        for ticker, holding in portfolio.items():
            cost = holding.get("cost_basis", 0)
            current = holding.get("current_value", 0)
            if current < cost:
                harvests.append({"ticker": ticker, "loss": round(current - cost, 2), "action": "sell_to_harvest"})
        return harvests

    def defer_gains(self, portfolio: dict) -> dict:
        """Defer gains — Tax Efficiency Planner."""
        short_term = {t: h for t, h in portfolio.items() if h.get("holding_days", 0) < 365 and h.get("current_value", 0) > h.get("cost_basis", 0)}
        return {"deferrable_positions": list(short_term.keys()), "recommendation": "hold until long-term", "count": len(short_term), "disclaimer": DISCLAIMER}

    def check_wash_sales(self, trades: list) -> list:
        """Check wash sales — Tax Efficiency Planner."""
        flagged = []
        for i, trade in enumerate(trades):
            if trade.get("action") == "sell" and trade.get("loss", 0) < 0:
                window_trades = [t for j, t in enumerate(trades) if abs(i - j) <= 30 and t.get("ticker") == trade.get("ticker") and t.get("action") == "buy"]
                if window_trades:
                    flagged.append({"trade": trade, "wash_sale_risk": True})
        return flagged

    def run(self) -> str:
        """Return running status string."""
        return f"TaxOptimizer running: {self.tier} tier"
