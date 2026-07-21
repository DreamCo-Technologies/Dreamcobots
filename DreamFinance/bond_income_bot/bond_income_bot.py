# GLOBAL AI SOURCES FLOW
"""Bonds & Fixed Income Bot — financial intelligence bot."""
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
    '_local_tiers_bond_income_bot', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS

DISCLAIMER = (
    "This tool is for educational and research purposes only. "
    "It does not constitute financial advice. "
    "Past performance does not guarantee future results."
)


class BondIncomeBot:
    """Bonds & Fixed Income Bot bot for financial analysis."""

    def __init__(self, tier: str = "pro"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["pro"])

    def screen_bonds(self, criteria: dict) -> list:
        """Screen bonds — Bonds & Fixed Income Bot."""
        min_yield = criteria.get("min_yield", 0)
        max_duration = criteria.get("max_duration", 30)
        bonds = criteria.get("universe", [])
        return [b for b in bonds if b.get("yield", 0) >= min_yield and b.get("duration", 0) <= max_duration]

    def analyze_yield_curve(self, rates: dict) -> dict:
        """Analyze yield curve — Bonds & Fixed Income Bot."""
        maturities = sorted(rates.keys())
        spread_10_2 = round(rates.get("10y", 0) - rates.get("2y", 0), 4)
        shape = "normal" if spread_10_2 > 0 else "inverted" if spread_10_2 < 0 else "flat"
        return {"shape": shape, "10y_2y_spread": spread_10_2, "maturities": maturities, "disclaimer": DISCLAIMER}

    def match_duration(self, target: float, bonds: list) -> list:
        """Match duration — Bonds & Fixed Income Bot."""
        return sorted(bonds, key=lambda b: abs(b.get("duration", 0) - target))[:5]

    def run(self) -> str:
        """Return running status string."""
        return f"BondIncomeBot running: {self.tier} tier"
