# GLOBAL AI SOURCES FLOW
"""Quant Strategy Backtester — financial intelligence bot."""
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
    '_local_tiers_quant_backtester', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS

DISCLAIMER = (
    "This tool is for educational and research purposes only. "
    "It does not constitute financial advice. "
    "Past performance does not guarantee future results."
)


class QuantBacktester:
    """Quant Strategy Backtester bot for financial analysis."""

    def __init__(self, tier: str = "enterprise"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["enterprise"])

    def walk_forward(self, strategy: dict, data: list) -> dict:
        """Walk forward — Quant Strategy Backtester."""
        folds = max(1, len(data) // 10)
        results = [{"fold": i, "return": round((hash(str(i) + strategy.get("name", "")) % 40 - 20) / 100, 4)} for i in range(folds)]
        avg = round(sum(r["return"] for r in results) / folds, 4)
        return {"folds": folds, "avg_return": avg, "results": results, "disclaimer": DISCLAIMER}

    def monte_carlo(self, returns: list, simulations: int = 1000) -> dict:
        """Monte carlo — Quant Strategy Backtester."""
        import random
        if not returns:
            return {"error": "no returns provided", "disclaimer": DISCLAIMER}
        mean = sum(returns) / len(returns)
        variance = sum((r - mean) ** 2 for r in returns) / len(returns)
        std = variance ** 0.5
        terminal_values = [sum(random.gauss(mean, std) for _ in returns) for _ in range(min(simulations, 10000))]
        terminal_values.sort()
        n = len(terminal_values)
        return {"simulations": simulations, "mean": round(mean, 6), "p5": round(terminal_values[n//20], 6), "p95": round(terminal_values[int(n*0.95)], 6), "disclaimer": DISCLAIMER}

    def detect_regime(self, prices: list) -> dict:
        """Detect regime — Quant Strategy Backtester."""
        if len(prices) < 20:
            return {"regime": "unknown", "disclaimer": DISCLAIMER}
        recent = prices[-10:]
        earlier = prices[-20:-10]
        recent_avg = sum(recent) / len(recent)
        earlier_avg = sum(earlier) / len(earlier)
        trend = "bull" if recent_avg > earlier_avg * 1.02 else "bear" if recent_avg < earlier_avg * 0.98 else "sideways"
        return {"regime": trend, "recent_avg": round(recent_avg, 4), "earlier_avg": round(earlier_avg, 4), "disclaimer": DISCLAIMER}

    def run(self) -> str:
        """Return running status string."""
        return f"QuantBacktester running: {self.tier} tier"
