# GLOBAL AI SOURCES FLOW
"""Corporate Treasury Analyzer — financial intelligence bot."""
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
    '_local_tiers_treasury_analyzer', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS

DISCLAIMER = (
    "This tool is for educational and research purposes only. "
    "It does not constitute financial advice. "
    "Past performance does not guarantee future results."
)


class TreasuryAnalyzer:
    """Corporate Treasury Analyzer bot for financial analysis."""

    def __init__(self, tier: str = "enterprise"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["enterprise"])

    def forecast_cash(self, data: dict) -> dict:
        """Forecast cash — Corporate Treasury Analyzer."""
        opening = data.get("opening_balance", 0)
        inflows = sum(data.get("inflows", []))
        outflows = sum(data.get("outflows", []))
        forecast = round(opening + inflows - outflows, 2)
        return {"opening": opening, "inflows": inflows, "outflows": outflows, "forecast_balance": forecast, "disclaimer": DISCLAIMER}

    def analyze_liquidity(self, positions: dict) -> dict:
        """Analyze liquidity — Corporate Treasury Analyzer."""
        current = positions.get("current_assets", 0)
        current_liab = positions.get("current_liabilities", 1)
        ratio = round(current / current_liab, 4)
        gaps = [{"period": k, "gap": v} for k, v in positions.get("gaps", {}).items()]
        return {"current_ratio": ratio, "gaps": gaps, "adequate": ratio > 1.0, "disclaimer": DISCLAIMER}

    def manage_fx_exposure(self, exposures: dict) -> dict:
        """Manage fx exposure — Corporate Treasury Analyzer."""
        total_usd = sum(v.get("usd_equivalent", 0) for v in exposures.values())
        hedged = sum(v.get("hedged_usd", 0) for v in exposures.values())
        hedge_ratio = round(hedged / total_usd, 4) if total_usd else 0
        return {"total_exposure_usd": round(total_usd, 2), "hedged_usd": round(hedged, 2), "hedge_ratio": hedge_ratio, "disclaimer": DISCLAIMER}

    def run(self) -> str:
        """Return running status string."""
        return f"TreasuryAnalyzer running: {self.tier} tier"
