# GLOBAL AI SOURCES FLOW
"""Insurance Claim Fraud Detector — financial intelligence bot."""
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
    '_local_tiers_insurance_fraud_detector', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS

DISCLAIMER = (
    "This tool is for educational and research purposes only. "
    "It does not constitute financial advice. "
    "Past performance does not guarantee future results."
)


class InsuranceFraudDetector:
    """Insurance Claim Fraud Detector bot for financial analysis."""

    def __init__(self, tier: str = "enterprise"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["enterprise"])

    def score_claim(self, claim: dict) -> dict:
        """Score claim — Insurance Claim Fraud Detector."""
        amount = claim.get("amount", 0)
        avg = claim.get("historical_avg", 5000)
        score = round(min(1.0, amount / (avg * 3)), 3)
        return {"fraud_score": score, "flagged": score > 0.7, "reason": "high amount" if score > 0.7 else "normal", "disclaimer": DISCLAIMER}

    def analyze_network(self, network: dict) -> dict:
        """Analyze network — Insurance Claim Fraud Detector."""
        connections = network.get("connections", [])
        flagged = [c for c in connections if c.get("suspicious", False)]
        return {"flagged_nodes": len(flagged), "total_nodes": len(connections), "risk": "high" if flagged else "low", "disclaimer": DISCLAIMER}

    def verify_document(self, doc: dict) -> dict:
        """Verify document — Insurance Claim Fraud Detector."""
        checks = {"has_signature": bool(doc.get("signature")), "date_valid": bool(doc.get("date")), "issuer_known": doc.get("issuer") in ("hospital", "clinic", "insurer")}
        passed = sum(checks.values())
        return {"checks": checks, "passed": passed, "verified": passed == 3, "disclaimer": DISCLAIMER}

    def run(self) -> str:
        """Return running status string."""
        return f"InsuranceFraudDetector running: {self.tier} tier"
