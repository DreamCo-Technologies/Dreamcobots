# GLOBAL AI SOURCES FLOW
"""Portfolio Rebalancing Bot — financial intelligence bot."""
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
    '_local_tiers_portfolio_rebalancer', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS

DISCLAIMER = (
    "This tool is for educational and research purposes only. "
    "It does not constitute financial advice. "
    "Past performance does not guarantee future results."
)


class PortfolioRebalancer:
    """Portfolio Rebalancing Bot bot for financial analysis."""

    def __init__(self, tier: str = "pro"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["pro"])

    def check_drift(self, portfolio: dict, targets: dict) -> dict:
        """Check drift — Portfolio Rebalancing Bot."""
        drift = {}
        for ticker, target in targets.items():
            current = portfolio.get(ticker, 0)
            drift[ticker] = round(current - target, 4)
        needs_rebalance = any(abs(d) > 0.05 for d in drift.values())
        return {"drift": drift, "needs_rebalance": needs_rebalance, "disclaimer": DISCLAIMER}

    def rebalance(self, portfolio: dict, targets: dict) -> list:
        """Rebalance — Portfolio Rebalancing Bot."""
        orders = []
        for ticker, target in targets.items():
            current = portfolio.get(ticker, 0)
            diff = round(target - current, 4)
            if abs(diff) > 0.01:
                orders.append({"ticker": ticker, "action": "buy" if diff > 0 else "sell", "weight_change": abs(diff)})
        return orders

    def run(self) -> str:
        """Return running status string."""
        return f"PortfolioRebalancer running: {self.tier} tier"
