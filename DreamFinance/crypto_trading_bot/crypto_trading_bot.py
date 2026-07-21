# GLOBAL AI SOURCES FLOW
"""Crypto Trading Bot — financial intelligence bot."""
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
    '_local_tiers_crypto_trading_bot', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS

DISCLAIMER = (
    "This tool is for educational and research purposes only. "
    "It does not constitute financial advice. "
    "Past performance does not guarantee future results."
)


class CryptoTradingBot:
    """Crypto Trading Bot bot for financial analysis."""

    def __init__(self, tier: str = "pro"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["pro"])

    def execute_trade(self, exchange: str, order: dict) -> dict:
        """Execute trade — Crypto Trading Bot."""
        return {"exchange": exchange, "order_id": f"{exchange.upper()}-{hash(str(order)) % 1000000:06d}", "status": "filled", "price": order.get("price", 0), "qty": order.get("qty", 0), "disclaimer": DISCLAIMER}

    def dca_buy(self, symbol: str, amount: float, intervals: int) -> list:
        """Dca buy — Crypto Trading Bot."""
        chunk = round(amount / intervals, 8)
        return [{"symbol": symbol, "interval": i + 1, "amount": chunk, "action": "buy"} for i in range(intervals)]

    def setup_grid(self, symbol: str, params: dict) -> dict:
        """Setup grid — Crypto Trading Bot."""
        lower = params.get("lower", 100)
        upper = params.get("upper", 200)
        grids = params.get("grids", 10)
        step = round((upper - lower) / grids, 4)
        levels = [round(lower + i * step, 4) for i in range(grids + 1)]
        return {"symbol": symbol, "levels": levels, "step": step, "grids": grids, "disclaimer": DISCLAIMER}

    def run(self) -> str:
        """Return running status string."""
        return f"CryptoTradingBot running: {self.tier} tier"
