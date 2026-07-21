# GLOBAL AI SOURCES FLOW
"""AI Credit Risk Underwriter — financial intelligence bot."""
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
    '_local_tiers_credit_underwriter', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS

DISCLAIMER = (
    "This tool is for educational and research purposes only. "
    "It does not constitute financial advice. "
    "Past performance does not guarantee future results."
)


class CreditUnderwriter:
    """AI Credit Risk Underwriter bot for financial analysis."""

    def __init__(self, tier: str = "enterprise"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["enterprise"])

    def score_credit(self, profile: dict) -> dict:
        """Score credit — AI Credit Risk Underwriter."""
        score = min(850, max(300, int(
            profile.get("income", 50000) / 1000 +
            profile.get("credit_history_years", 5) * 10 -
            profile.get("debt_ratio", 0.3) * 100 + 500
        )))
        return {"credit_score": score, "grade": "A" if score > 750 else "B" if score > 650 else "C", "disclaimer": DISCLAIMER}

    def estimate_default(self, profile: dict) -> dict:
        """Estimate default — AI Credit Risk Underwriter."""
        debt_ratio = profile.get("debt_ratio", 0.3)
        history = profile.get("credit_history_years", 5)
        prob = round(max(0.01, min(0.99, debt_ratio * 0.5 - history * 0.02 + 0.1)), 4)
        return {"default_probability": prob, "risk_category": "high" if prob > 0.3 else "medium" if prob > 0.1 else "low", "disclaimer": DISCLAIMER}

    def detect_fraud(self, transaction: dict) -> dict:
        """Detect fraud — AI Credit Risk Underwriter."""
        amount = transaction.get("amount", 0)
        avg = transaction.get("avg_transaction", 200)
        flag = amount > avg * 5 or transaction.get("foreign", False)
        return {"fraud_flag": flag, "amount": amount, "risk_score": round(min(1.0, amount / (avg * 10)), 3), "disclaimer": DISCLAIMER}

    def run(self) -> str:
        """Return running status string."""
        return f"CreditUnderwriter running: {self.tier} tier"
