# GLOBAL AI SOURCES FLOW
"""Options Trading Bot — financial intelligence bot."""
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
    '_local_tiers_options_trader', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS

DISCLAIMER = (
    "This tool is for educational and research purposes only. "
    "It does not constitute financial advice. "
    "Past performance does not guarantee future results."
)


class OptionsTrader:
    """Options Trading Bot bot for financial analysis."""

    def __init__(self, tier: str = "pro"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["pro"])

    def scan_chain(self, symbol: str, expiry: str) -> list:
        """Scan chain — Options Trading Bot."""
        strikes = [90, 95, 100, 105, 110]
        return [{"symbol": symbol, "expiry": expiry, "strike": s, "call_bid": round(max(0, 100 - s) * 0.1, 2), "put_bid": round(max(0, s - 100) * 0.1, 2)} for s in strikes]

    def build_iron_condor(self, symbol: str, params: dict) -> dict:
        """Build iron condor — Options Trading Bot."""
        center = params.get("center_strike", 100)
        width = params.get("width", 5)
        return {"symbol": symbol, "legs": [
            {"type": "sell_put", "strike": center - width},
            {"type": "buy_put", "strike": center - 2 * width},
            {"type": "sell_call", "strike": center + width},
            {"type": "buy_call", "strike": center + 2 * width},
        ], "max_profit": params.get("credit", 2.0), "max_loss": round(width - params.get("credit", 2.0), 2), "disclaimer": DISCLAIMER}

    def build_spread(self, symbol: str, strategy: str, params: dict) -> dict:
        """Build spread — Options Trading Bot."""
        strike1 = params.get("strike1", 100)
        strike2 = params.get("strike2", 105)
        return {"symbol": symbol, "strategy": strategy, "legs": [
            {"action": "buy", "strike": strike1},
            {"action": "sell", "strike": strike2},
        ], "net_debit": params.get("net_debit", 1.5), "disclaimer": DISCLAIMER}

    def run(self) -> str:
        """Return running status string."""
        return f"OptionsTrader running: {self.tier} tier"
