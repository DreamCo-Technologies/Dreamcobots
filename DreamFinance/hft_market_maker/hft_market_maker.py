# GLOBAL AI SOURCES FLOW
"""High-Frequency Market Maker — financial intelligence bot."""
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
    '_local_tiers_hft_market_maker', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS

DISCLAIMER = (
    "This tool is for educational and research purposes only. "
    "It does not constitute financial advice. "
    "Past performance does not guarantee future results."
)


class HFTMarketMaker:
    """High-Frequency Market Maker bot for financial analysis."""

    def __init__(self, tier: str = "elite"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["elite"])

    def quote_spread(self, symbol: str, book: dict) -> dict:
        """Quote spread — High-Frequency Market Maker."""
        mid = (book.get("best_bid", 100) + book.get("best_ask", 100)) / 2
        spread = round(book.get("best_ask", 100) - book.get("best_bid", 100), 4)
        return {"symbol": symbol, "bid": round(mid - spread / 2, 4), "ask": round(mid + spread / 2, 4), "spread": spread, "disclaimer": DISCLAIMER}

    def optimize_spread(self, symbol: str, history: list) -> dict:
        """Optimize spread — High-Frequency Market Maker."""
        spreads = [h.get("spread", 0.01) for h in history]
        avg = round(sum(spreads) / len(spreads), 6) if spreads else 0.01
        return {"symbol": symbol, "optimal_spread": round(avg * 0.9, 6), "current_avg": avg, "disclaimer": DISCLAIMER}

    def detect_latency_arb(self, feeds: list) -> list:
        """Detect latency arb — High-Frequency Market Maker."""
        opps = []
        for i in range(len(feeds)):
            for j in range(i+1, len(feeds)):
                diff = abs(feeds[i].get("price", 0) - feeds[j].get("price", 0))
                if diff > 0.001:
                    opps.append({"feed_a": feeds[i].get("exchange"), "feed_b": feeds[j].get("exchange"), "diff": round(diff, 6)})
        return opps

    def run(self) -> str:
        """Return running status string."""
        return f"HFTMarketMaker running: {self.tier} tier"
