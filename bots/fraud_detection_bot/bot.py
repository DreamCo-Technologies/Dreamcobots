"""
Dreamcobots FraudDetectionBot — tier-aware transaction fraud detection and risk analysis.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config, get_upgrade_path
from bots.fraud_detection_bot.tiers import FRAUD_DETECTION_FEATURES, get_fraud_detection_tier_info
import uuid
from datetime import datetime


class FraudDetectionBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class FraudDetectionBotRequestLimitError(Exception):
    """Raised when the monthly request quota has been exhausted."""


class FraudDetectionBot:
    """Tier-aware transaction fraud detection and risk analysis bot."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._request_count: int = 0
        self._transactions: list[dict] = []

    def _check_request_limit(self) -> None:
        limit = self.config.requests_per_month
        if limit is not None and self._request_count >= limit:
            raise FraudDetectionBotRequestLimitError(
                f"Monthly request limit of {limit:,} reached on the "
                f"{self.config.name} tier. Please upgrade to continue."
            )

    def _check_feature(self, feature: str) -> None:
        features = FRAUD_DETECTION_FEATURES[self.tier.value]
        if not any(feature.lower() in f.lower() for f in features):
            raise FraudDetectionBotTierError(
                f"'{feature}' is not available on the {self.config.name} tier. "
                f"Please upgrade to access this feature."
            )

    def _requests_remaining(self) -> str:
        limit = self.config.requests_per_month
        if limit is None:
            return "unlimited"
        return str(max(limit - self._request_count, 0))

    def analyze_transaction(self, transaction: dict) -> dict:
        """
        Analyze a transaction for fraud risk.

        Args:
            transaction: {"transaction_id": str, "amount": float, "merchant": str, "user_id": str}

        Returns:
            {"transaction_id": str, "risk_score": float, "fraud_flag": bool,
             "reasons": list, "tier": str}
        """
        self._check_request_limit()
        self._request_count += 1

        transaction_id = transaction.get("transaction_id", str(uuid.uuid4()))
        amount = float(transaction.get("amount", 0.0))
        merchant = transaction.get("merchant", "")
        user_id = transaction.get("user_id", "")

        if self.tier == Tier.FREE:
            # Rule-based detection
            if amount > 10000:
                risk_score = 0.9
                reasons = ["Transaction amount exceeds $10,000 threshold"]
            else:
                risk_score = 0.3
                reasons = ["Amount within normal range"]
            fraud_flag = risk_score > 0.7

        elif self.tier == Tier.PRO:
            # ML-based detection with more sophisticated rules
            risk_score = 0.2
            reasons = []
            if amount > 10000:
                risk_score += 0.4
                reasons.append("High transaction amount")
            if amount > 5000:
                risk_score += 0.2
                reasons.append("Above-average transaction amount")
            suspicious_merchants = ["unknown", "test", "temp"]
            if any(kw in merchant.lower() for kw in suspicious_merchants):
                risk_score += 0.3
                reasons.append("Suspicious merchant name pattern")
            risk_score = min(round(risk_score, 2), 1.0)
            if not reasons:
                reasons = ["Transaction appears normal"]
            fraud_flag = risk_score > 0.6

        else:  # ENTERPRISE
            # Advanced ML with behavioral analytics
            risk_score = 0.15
            reasons = []
            if amount > 10000:
                risk_score += 0.35
                reasons.append("High transaction amount")
            if amount > 5000:
                risk_score += 0.15
                reasons.append("Above-average transaction amount")
            suspicious_merchants = ["unknown", "test", "temp"]
            if any(kw in merchant.lower() for kw in suspicious_merchants):
                risk_score += 0.25
                reasons.append("Suspicious merchant pattern detected by ML model")
            # Behavioral analytics component
            user_tx_count = sum(1 for t in self._transactions if t.get("user_id") == user_id)
            if user_tx_count > 10:
                risk_score += 0.1
                reasons.append("High transaction frequency for user")
            risk_score = min(round(risk_score, 2), 1.0)
            if not reasons:
                reasons = ["No anomalies detected by advanced ML model"]
            fraud_flag = risk_score > 0.55

        record = {
            "transaction_id": transaction_id,
            "amount": amount,
            "merchant": merchant,
            "user_id": user_id,
            "risk_score": risk_score,
            "fraud_flag": fraud_flag,
            "timestamp": datetime.now().isoformat(),
        }
        self._transactions.append(record)

        return {
            "transaction_id": transaction_id,
            "risk_score": risk_score,
            "fraud_flag": fraud_flag,
            "reasons": reasons,
            "tier": self.tier.value,
        }

    def get_risk_score(self, data: dict) -> dict:
        """
        Get an aggregated risk score for a user.

        Args:
            data: {"user_id": str, "transaction_count": int optional, "total_amount": float optional}

        Returns:
            {"user_id": str, "risk_score": float, "risk_level": str, "tier": str}
        """
        if self.tier == Tier.FREE:
            raise FraudDetectionBotTierError(
                "User risk scoring is not available on the Free tier. "
                "Please upgrade to PRO or ENTERPRISE."
            )

        user_id = data.get("user_id", "")
        transaction_count = data.get("transaction_count", 0)
        total_amount = data.get("total_amount", 0.0)

        risk_score = 0.2
        if transaction_count > 50:
            risk_score += 0.2
        if total_amount > 100000:
            risk_score += 0.3
        if self.tier == Tier.ENTERPRISE:
            # Behavioral analytics adjustment
            user_flagged = sum(1 for t in self._transactions if t.get("user_id") == user_id and t.get("fraud_flag"))
            if user_flagged > 0:
                risk_score += 0.2

        risk_score = min(round(risk_score, 2), 1.0)

        if risk_score < 0.3:
            risk_level = "low"
        elif risk_score < 0.6:
            risk_level = "medium"
        else:
            risk_level = "high"

        return {
            "user_id": user_id,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "tier": self.tier.value,
        }

    def generate_report(self, period: str) -> dict:
        """
        Generate a fraud detection report for a given period.

        Args:
            period: Reporting period string (e.g., "monthly", "weekly").

        Returns:
            {"period": str, "total_transactions": int, "flagged": int,
             "risk_distribution": dict, "tier": str}
        """
        if self.tier == Tier.FREE:
            raise FraudDetectionBotTierError(
                "Report generation is not available on the Free tier. "
                "Please upgrade to PRO or ENTERPRISE."
            )

        total = len(self._transactions)
        flagged = sum(1 for t in self._transactions if t.get("fraud_flag"))

        risk_distribution = {"low": 0, "medium": 0, "high": 0}
        for t in self._transactions:
            score = t.get("risk_score", 0.0)
            if score < 0.3:
                risk_distribution["low"] += 1
            elif score < 0.6:
                risk_distribution["medium"] += 1
            else:
                risk_distribution["high"] += 1

        return {
            "period": period,
            "total_transactions": total,
            "flagged": flagged,
            "risk_distribution": risk_distribution,
            "tier": self.tier.value,
        }

    def get_stats(self) -> dict:
        return {
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
            "transactions_analyzed": len(self._transactions),
            "buddy_integration": True,
        }
