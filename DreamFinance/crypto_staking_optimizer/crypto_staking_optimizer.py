# GLOBAL AI SOURCES FLOW
"""Crypto Staking Optimizer — financial intelligence bot."""
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
    '_local_tiers_crypto_staking_optimizer', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS

DISCLAIMER = (
    "This tool is for educational and research purposes only. "
    "It does not constitute financial advice. "
    "Past performance does not guarantee future results."
)


class CryptoStakingOptimizer:
    """Crypto Staking Optimizer bot for financial analysis."""

    def __init__(self, tier: str = "pro"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["pro"])

    def find_staking_pools(self, chains: list) -> list:
        """Find staking pools — Crypto Staking Optimizer."""
        pools = []
        for chain in chains:
            pools.append({"chain": chain, "apy": round(5 + hash(chain) % 15, 2), "lock_days": 7 + hash(chain) % 21})
        return sorted(pools, key=lambda p: p["apy"], reverse=True)

    def select_validator(self, chain: str, validators: list) -> dict:
        """Select validator — Crypto Staking Optimizer."""
        if not validators:
            return {"error": "no validators provided", "disclaimer": DISCLAIMER}
        best = max(validators, key=lambda v: v.get("uptime", 0) - v.get("commission", 0.1) * 10)
        return {"selected": best, "chain": chain, "disclaimer": DISCLAIMER}

    def compound_rewards(self, stakes: list) -> dict:
        """Compound rewards — Crypto Staking Optimizer."""
        total = sum(s.get("pending_rewards", 0) for s in stakes)
        compounded = [{"chain": s.get("chain"), "compounded": s.get("pending_rewards", 0)} for s in stakes]
        return {"total_compounded": round(total, 6), "operations": compounded, "disclaimer": DISCLAIMER}

    def run(self) -> str:
        """Return running status string."""
        return f"CryptoStakingOptimizer running: {self.tier} tier"
