# GLOBAL AI SOURCES FLOW
"""Hedge Fund Strategy Generator — financial intelligence bot."""
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
    '_local_tiers_hedge_fund_strategy', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS

DISCLAIMER = (
    "This tool is for educational and research purposes only. "
    "It does not constitute financial advice. "
    "Past performance does not guarantee future results."
)


class HedgeFundStrategy:
    """Hedge Fund Strategy Generator bot for financial analysis."""

    def __init__(self, tier: str = "elite"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["elite"])

    def generate_long_short(self, universe: list) -> dict:
        """Generate long short — Hedge Fund Strategy Generator."""
        scores = [(s, hash(s.get("ticker", "")) % 100) for s in universe]
        longs = [s[0]["ticker"] for s in sorted(scores, key=lambda x: x[1], reverse=True)[:len(universe)//2]]
        shorts = [s[0]["ticker"] for s in sorted(scores, key=lambda x: x[1])[:len(universe)//2]]
        return {"long": longs, "short": shorts, "net_exposure": 0.0, "disclaimer": DISCLAIMER}

    def find_alpha(self, events: list) -> list:
        """Find alpha — Hedge Fund Strategy Generator."""
        return [{"event": e.get("type", ""), "ticker": e.get("ticker", ""), "alpha_est": round((hash(e.get("ticker", "")) % 20 - 10) / 100, 4)} for e in events]

    def analyze_factors(self, portfolio: dict) -> dict:
        """Analyze factors — Hedge Fund Strategy Generator."""
        holdings = portfolio.get("holdings", [])
        return {"value_tilt": round(sum(h.get("pb_ratio", 1) for h in holdings) / max(len(holdings), 1), 3), "momentum_tilt": round(sum(h.get("momentum", 0) for h in holdings) / max(len(holdings), 1), 3), "disclaimer": DISCLAIMER}

    def run(self) -> str:
        """Return running status string."""
        return f"HedgeFundStrategy running: {self.tier} tier"
