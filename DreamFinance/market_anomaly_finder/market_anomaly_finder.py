# GLOBAL AI SOURCES FLOW
"""Real-Time Market Anomaly Finder — financial intelligence bot."""
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
    '_local_tiers_market_anomaly_finder', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS

DISCLAIMER = (
    "This tool is for educational and research purposes only. "
    "It does not constitute financial advice. "
    "Past performance does not guarantee future results."
)


class MarketAnomalyFinder:
    """Real-Time Market Anomaly Finder bot for financial analysis."""

    def __init__(self, tier: str = "enterprise"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["enterprise"])

    def detect_anomaly(self, data: dict) -> dict:
        """Detect anomaly — Real-Time Market Anomaly Finder."""
        value = data.get("value", 0)
        mean = data.get("mean", 0)
        std = data.get("std", 1)
        z = round((value - mean) / std, 3) if std else 0
        return {"z_score": z, "is_anomaly": abs(z) > 2.5, "severity": "high" if abs(z) > 3 else "medium", "disclaimer": DISCLAIMER}

    def alert_dark_pool(self, print_data: dict) -> dict:
        """Alert dark pool — Real-Time Market Anomaly Finder."""
        size = print_data.get("size", 0)
        threshold = print_data.get("threshold", 1_000_000)
        return {"alert": size > threshold, "size": size, "threshold": threshold, "disclaimer": DISCLAIMER}

    def flag_options(self, activity: dict) -> dict:
        """Flag options — Real-Time Market Anomaly Finder."""
        unusual = activity.get("volume", 0) > activity.get("open_interest", 1) * 3
        return {"flagged": unusual, "ratio": round(activity.get("volume", 0) / max(activity.get("open_interest", 1), 1), 3), "disclaimer": DISCLAIMER}

    def run(self) -> str:
        """Return running status string."""
        return f"MarketAnomalyFinder running: {self.tier} tier"
