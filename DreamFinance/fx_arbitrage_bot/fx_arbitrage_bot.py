# GLOBAL AI SOURCES FLOW
"""FX Arbitrage Bot — financial intelligence bot."""
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
    '_local_tiers_fx_arbitrage_bot', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS

DISCLAIMER = (
    "This tool is for educational and research purposes only. "
    "It does not constitute financial advice. "
    "Past performance does not guarantee future results."
)


class FXArbitrageBot:
    """FX Arbitrage Bot bot for financial analysis."""

    def __init__(self, tier: str = "elite"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["elite"])

    def find_triangular(self, rates: dict) -> list:
        """Find triangular — FX Arbitrage Bot."""
        opps = []
        pairs = list(rates.keys())
        for i in range(len(pairs)):
            for j in range(i+1, len(pairs)):
                for k in range(j+1, len(pairs)):
                    product = rates.get(pairs[i], 1) * rates.get(pairs[j], 1) * rates.get(pairs[k], 1)
                    if abs(product - 1.0) > 0.001:
                        opps.append({"path": [pairs[i], pairs[j], pairs[k]], "profit_factor": round(product, 6)})
        return opps

    def scan_discrepancies(self, rates: dict) -> list:
        """Scan discrepancies — FX Arbitrage Bot."""
        discrepancies = []
        for pair, rate in rates.items():
            implied = rates.get(f"implied_{pair}", rate)
            if abs(rate - implied) / rate > 0.0001:
                discrepancies.append({"pair": pair, "rate": rate, "implied": implied, "spread_bps": round(abs(rate - implied) / rate * 10000, 2)})
        return discrepancies

    def execute_arb(self, opportunity: dict) -> dict:
        """Execute arb — FX Arbitrage Bot."""
        profit = opportunity.get("profit_factor", 1.0) - 1.0
        return {"executed": profit > 0.0005, "expected_profit_pct": round(profit * 100, 4), "path": opportunity.get("path", []), "disclaimer": DISCLAIMER}

    def run(self) -> str:
        """Return running status string."""
        return f"FXArbitrageBot running: {self.tier} tier"
