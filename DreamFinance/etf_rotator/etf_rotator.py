# GLOBAL AI SOURCES FLOW
"""ETF Rotation Strategy AI — financial intelligence bot."""
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
    '_local_tiers_etf_rotator', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS

DISCLAIMER = (
    "This tool is for educational and research purposes only. "
    "It does not constitute financial advice. "
    "Past performance does not guarantee future results."
)


class ETFRotator:
    """ETF Rotation Strategy AI bot for financial analysis."""

    def __init__(self, tier: str = "pro"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["pro"])

    def score_momentum(self, etfs: list) -> dict:
        """Score momentum — ETF Rotation Strategy AI."""
        scored = [{"ticker": e.get("ticker", ""), "momentum": round(e.get("return_1m", 0) * 0.4 + e.get("return_3m", 0) * 0.3 + e.get("return_6m", 0) * 0.3, 4)} for e in etfs]
        scored.sort(key=lambda x: x["momentum"], reverse=True)
        return {"ranked": scored, "top_pick": scored[0]["ticker"] if scored else None, "disclaimer": DISCLAIMER}

    def optimize_factors(self, etfs: list) -> dict:
        """Optimize factors — ETF Rotation Strategy AI."""
        weights = {e.get("ticker", f"ETF{i}"): round(1 / len(etfs), 4) for i, e in enumerate(etfs)}
        return {"factor_weights": weights, "strategy": "equal_weight_factor", "disclaimer": DISCLAIMER}

    def generate_signal(self, portfolio: dict) -> dict:
        """Generate signal — ETF Rotation Strategy AI."""
        drift = {k: round(v - portfolio.get("targets", {}).get(k, v), 4) for k, v in portfolio.get("current", {}).items()}
        action = "rebalance" if any(abs(d) > 0.05 for d in drift.values()) else "hold"
        return {"signal": action, "drift": drift, "disclaimer": DISCLAIMER}

    def run(self) -> str:
        """Return running status string."""
        return f"ETFRotator running: {self.tier} tier"
