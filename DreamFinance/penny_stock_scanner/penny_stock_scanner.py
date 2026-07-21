# GLOBAL AI SOURCES FLOW
"""Penny Stock Scanner Bot — financial intelligence bot."""
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
    '_local_tiers_penny_stock_scanner', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS

DISCLAIMER = (
    "This tool is for educational and research purposes only. "
    "It does not constitute financial advice. "
    "Past performance does not guarantee future results."
)


class PennyStockScanner:
    """Penny Stock Scanner Bot bot for financial analysis."""

    def __init__(self, tier: str = "pro"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["pro"])

    def screen_stocks(self, criteria: dict) -> list:
        """Screen stocks — Penny Stock Scanner Bot."""
        max_price = criteria.get("max_price", 5.0)
        min_volume = criteria.get("min_volume", 100000)
        stocks = criteria.get("universe", [])
        return [s for s in stocks if s.get("price", 999) <= max_price and s.get("volume", 0) >= min_volume]

    def detect_volume_spike(self, symbol: str, volume_data: list) -> dict:
        """Detect volume spike — Penny Stock Scanner Bot."""
        if not volume_data:
            return {"symbol": symbol, "spike": False, "disclaimer": DISCLAIMER}
        avg = sum(volume_data[:-1]) / max(len(volume_data) - 1, 1)
        latest = volume_data[-1]
        spike = latest > avg * 3
        return {"symbol": symbol, "spike": spike, "ratio": round(latest / avg, 2) if avg else 0, "disclaimer": DISCLAIMER}

    def get_filing_alerts(self, symbols: list) -> list:
        """Get filing alerts — Penny Stock Scanner Bot."""
        return [{"symbol": s, "filing_type": "8-K", "date": "2024-01-15", "summary": f"Material event for {s}"} for s in symbols[:5]]

    def run(self) -> str:
        """Return running status string."""
        return f"PennyStockScanner running: {self.tier} tier"
