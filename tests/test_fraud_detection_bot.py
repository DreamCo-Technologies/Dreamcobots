"""
Tests for bots/fraud_detection_bot/tiers.py and bots/fraud_detection_bot/bot.py
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.fraud_detection_bot.tiers import FRAUD_DETECTION_FEATURES, get_fraud_detection_tier_info
from bots.fraud_detection_bot.bot import (
    FraudDetectionBot,
    FraudDetectionBotTierError,
    FraudDetectionBotRequestLimitError,
)


class TestFraudDetectionTierInfo:
    def test_free_tier_info_keys(self):
        info = get_fraud_detection_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "support_level", "bot_features"):
            assert key in info

    def test_free_price_is_zero(self):
        info = get_fraud_detection_tier_info(Tier.FREE)
        assert info["price_usd_monthly"] == 0.0

    def test_enterprise_unlimited(self):
        info = get_fraud_detection_tier_info(Tier.ENTERPRISE)
        assert info["requests_per_month"] is None

    def test_features_exist_for_all_tiers(self):
        for tier in Tier:
            assert tier.value in FRAUD_DETECTION_FEATURES
            assert len(FRAUD_DETECTION_FEATURES[tier.value]) > 0


class TestFraudDetectionBot:
    def test_default_tier_is_free(self):
        bot = FraudDetectionBot()
        assert bot.tier == Tier.FREE

    def test_analyze_transaction_returns_expected_keys(self):
        bot = FraudDetectionBot(tier=Tier.FREE)
        tx = {"transaction_id": "TX-001", "amount": 100.0, "merchant": "Amazon", "user_id": "USR-1"}
        result = bot.analyze_transaction(tx)
        for key in ("transaction_id", "risk_score", "fraud_flag", "reasons", "tier"):
            assert key in result

    def test_analyze_transaction_tier_value(self):
        bot = FraudDetectionBot(tier=Tier.FREE)
        result = bot.analyze_transaction({"transaction_id": "TX-001", "amount": 50.0, "merchant": "Store", "user_id": "U1"})
        assert result["tier"] == "free"

    def test_analyze_transaction_risk_score_in_range(self):
        bot = FraudDetectionBot(tier=Tier.FREE)
        result = bot.analyze_transaction({"transaction_id": "TX-002", "amount": 200.0, "merchant": "Shop", "user_id": "U1"})
        assert 0.0 <= result["risk_score"] <= 1.0

    def test_analyze_transaction_fraud_flag_type(self):
        bot = FraudDetectionBot(tier=Tier.FREE)
        result = bot.analyze_transaction({"transaction_id": "TX-003", "amount": 50000.0, "merchant": "unknown", "user_id": "U1"})
        assert isinstance(result["fraud_flag"], bool)

    def test_high_amount_raises_risk_score(self):
        bot = FraudDetectionBot(tier=Tier.FREE)
        result = bot.analyze_transaction({"transaction_id": "TX-004", "amount": 50000.0, "merchant": "Safe", "user_id": "U1"})
        assert result["risk_score"] > 0.5

    def test_reasons_is_list(self):
        bot = FraudDetectionBot(tier=Tier.FREE)
        result = bot.analyze_transaction({"transaction_id": "TX-005", "amount": 100.0, "merchant": "Store", "user_id": "U1"})
        assert isinstance(result["reasons"], list)

    def test_get_risk_score_free_raises(self):
        bot = FraudDetectionBot(tier=Tier.FREE)
        with pytest.raises(FraudDetectionBotTierError):
            bot.get_risk_score({"user_id": "U1"})

    def test_get_risk_score_pro(self):
        bot = FraudDetectionBot(tier=Tier.PRO)
        result = bot.get_risk_score({"user_id": "U1", "transaction_count": 5, "total_amount": 1000.0})
        assert "risk_score" in result
        assert "risk_level" in result

    def test_risk_level_valid_values(self):
        bot = FraudDetectionBot(tier=Tier.PRO)
        result = bot.get_risk_score({"user_id": "U2", "transaction_count": 100, "total_amount": 500000.0})
        assert result["risk_level"] in ("low", "medium", "high")

    def test_generate_report_free_raises(self):
        bot = FraudDetectionBot(tier=Tier.FREE)
        with pytest.raises(FraudDetectionBotTierError):
            bot.generate_report("monthly")

    def test_generate_report_pro(self):
        bot = FraudDetectionBot(tier=Tier.PRO)
        bot.analyze_transaction({"transaction_id": "TX-006", "amount": 100.0, "merchant": "Store", "user_id": "U1"})
        result = bot.generate_report("monthly")
        for key in ("period", "total_transactions", "flagged", "risk_distribution", "tier"):
            assert key in result

    def test_request_counter_increments(self):
        bot = FraudDetectionBot(tier=Tier.FREE)
        bot.analyze_transaction({"transaction_id": "TX-007", "amount": 50.0, "merchant": "Store", "user_id": "U1"})
        bot.analyze_transaction({"transaction_id": "TX-008", "amount": 100.0, "merchant": "Store", "user_id": "U1"})
        assert bot._request_count == 2

    def test_request_limit_exceeded(self):
        bot = FraudDetectionBot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        with pytest.raises(FraudDetectionBotRequestLimitError):
            bot.analyze_transaction({"transaction_id": "TX-OVER", "amount": 50.0, "merchant": "Store", "user_id": "U1"})

    def test_enterprise_no_request_limit(self):
        bot = FraudDetectionBot(tier=Tier.ENTERPRISE)
        bot._request_count = 9999
        result = bot.analyze_transaction({"transaction_id": "TX-ENT", "amount": 50.0, "merchant": "Store", "user_id": "U1"})
        assert "transaction_id" in result

    def test_get_stats_buddy_integration(self):
        bot = FraudDetectionBot(tier=Tier.FREE)
        stats = bot.get_stats()
        assert stats["buddy_integration"] is True

    def test_get_stats_keys(self):
        bot = FraudDetectionBot(tier=Tier.PRO)
        stats = bot.get_stats()
        assert "tier" in stats
        assert "requests_used" in stats
        assert "transactions_analyzed" in stats
