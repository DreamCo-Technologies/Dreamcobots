# GLOBAL AI SOURCES FLOW
"""DeFi Yield Farming Bot — financial intelligence bot."""
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
    '_local_tiers_defi_yield_farmer', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS

DISCLAIMER = (
    "This tool is for educational and research purposes only. "
    "It does not constitute financial advice. "
    "Past performance does not guarantee future results."
)


class DeFiYieldFarmer:
    """DeFi Yield Farming Bot bot for financial analysis."""

    def __init__(self, tier: str = "pro"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["pro"])

    def manage_position(self, pool: dict) -> dict:
        """Manage position — DeFi Yield Farming Bot."""
        tvl = pool.get("tvl", 0)
        apy = pool.get("apy", 0)
        est_daily = round(tvl * apy / 365, 2)
        return {"pool": pool.get("name", "unknown"), "tvl": tvl, "daily_yield_est": est_daily, "status": "active", "disclaimer": DISCLAIMER}

    def calculate_il(self, entry: dict, current: dict) -> dict:
        """Calculate il — DeFi Yield Farming Bot."""
        p0_a, p0_b = entry.get("price_a", 1), entry.get("price_b", 1)
        p1_a, p1_b = current.get("price_a", 1), current.get("price_b", 1)
        ratio_a = p1_a / p0_a if p0_a else 1
        ratio_b = p1_b / p0_b if p0_b else 1
        il = round(2 * (ratio_a * ratio_b) ** 0.5 / (ratio_a + ratio_b) - 1, 6)
        return {"impermanent_loss": il, "il_pct": round(il * 100, 4), "disclaimer": DISCLAIMER}

    def schedule_harvest(self, positions: list) -> list:
        """Schedule harvest — DeFi Yield Farming Bot."""
        return [{"pool": p.get("name", ""), "harvest_in_hours": max(1, int(100 / max(p.get("apy", 1), 0.01)))} for p in positions]

    def run(self) -> str:
        """Return running status string."""
        return f"DeFiYieldFarmer running: {self.tier} tier"
