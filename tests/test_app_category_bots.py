"""Tests for all 30 App bots."""
from __future__ import annotations
import sys, os
import importlib
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from App_bots.feature_1 import OnboardingBot
from App_bots.feature_2 import SupportBot
from App_bots.feature_3 import NotificationBot
from App_bots.analytics_bot import AnalyticsBot
from App_bots.user_retention_bot import UserRetentionBot
from App_bots.monetization_bot import MonetizationBot
from App_bots.push_notification_bot import PushNotificationBot
from App_bots.ab_testing_bot import ABTestingBot
from App_bots.crash_reporter_bot import CrashReporterBot
from App_bots.user_segmentation_bot import UserSegmentationBot
from App_bots.in_app_purchase_bot import InAppPurchaseBot
from App_bots.subscription_manager_bot import SubscriptionManagerBot
from App_bots.review_collector_bot import ReviewCollectorBot
from App_bots.referral_program_bot import ReferralProgramBot
from App_bots.gamification_bot import GamificationBot
from App_bots.personalization_bot import PersonalizationBot
from App_bots.churn_predictor_bot import ChurnPredictorBot
from App_bots.onboarding_funnel_bot import OnboardingFunnelBot
from App_bots.app_store_optimizer_bot import AppStoreOptimizerBot
from App_bots.session_tracker_bot import SessionTrackerBot
from App_bots.feature_flag_bot import FeatureFlagBot
from App_bots.user_feedback_bot import UserFeedbackBot
from App_bots.deep_link_bot import DeepLinkBot
from App_bots.social_sharing_bot import SocialSharingBot
from App_bots.payment_gateway_bot import PaymentGatewayBot
from App_bots.localization_bot import LocalizationBot
from App_bots.accessibility_bot import AccessibilityBot
from App_bots.performance_monitor_bot import PerformanceMonitorBot
from App_bots.beta_tester_bot import BetaTesterBot
from App_bots.api_rate_limiter_bot import APIRateLimiterBot

ALL_BOTS = [
    ("OnboardingBot", OnboardingBot),
    ("SupportBot", SupportBot),
    ("NotificationBot", NotificationBot),
    ("AnalyticsBot", AnalyticsBot),
    ("UserRetentionBot", UserRetentionBot),
    ("MonetizationBot", MonetizationBot),
    ("PushNotificationBot", PushNotificationBot),
    ("ABTestingBot", ABTestingBot),
    ("CrashReporterBot", CrashReporterBot),
    ("UserSegmentationBot", UserSegmentationBot),
    ("InAppPurchaseBot", InAppPurchaseBot),
    ("SubscriptionManagerBot", SubscriptionManagerBot),
    ("ReviewCollectorBot", ReviewCollectorBot),
    ("ReferralProgramBot", ReferralProgramBot),
    ("GamificationBot", GamificationBot),
    ("PersonalizationBot", PersonalizationBot),
    ("ChurnPredictorBot", ChurnPredictorBot),
    ("OnboardingFunnelBot", OnboardingFunnelBot),
    ("AppStoreOptimizerBot", AppStoreOptimizerBot),
    ("SessionTrackerBot", SessionTrackerBot),
    ("FeatureFlagBot", FeatureFlagBot),
    ("UserFeedbackBot", UserFeedbackBot),
    ("DeepLinkBot", DeepLinkBot),
    ("SocialSharingBot", SocialSharingBot),
    ("PaymentGatewayBot", PaymentGatewayBot),
    ("LocalizationBot", LocalizationBot),
    ("AccessibilityBot", AccessibilityBot),
    ("PerformanceMonitorBot", PerformanceMonitorBot),
    ("BetaTesterBot", BetaTesterBot),
    ("APIRateLimiterBot", APIRateLimiterBot),
]


def _get_tier(BotClass):
    """Get the Tier enum from BotClass's module."""
    return sys.modules[BotClass.__module__].Tier


class TestInstantiation:
    @pytest.mark.parametrize("name,BotClass", ALL_BOTS)
    def test_default_instantiation(self, name, BotClass):
        assert BotClass() is not None

    @pytest.mark.parametrize("name,BotClass", ALL_BOTS)
    def test_free_tier(self, name, BotClass):
        T = _get_tier(BotClass)
        bot = BotClass(tier=T.FREE)
        assert bot.tier.value == "free"

    @pytest.mark.parametrize("name,BotClass", ALL_BOTS)
    def test_pro_tier(self, name, BotClass):
        T = _get_tier(BotClass)
        bot = BotClass(tier=T.PRO)
        assert bot.tier.value == "pro"

    @pytest.mark.parametrize("name,BotClass", ALL_BOTS)
    def test_enterprise_tier(self, name, BotClass):
        T = _get_tier(BotClass)
        bot = BotClass(tier=T.ENTERPRISE)
        assert bot.tier.value == "enterprise"


class TestTierPricing:
    @pytest.mark.parametrize("name,BotClass", ALL_BOTS)
    def test_free_price_is_zero(self, name, BotClass):
        T = _get_tier(BotClass)
        assert BotClass(tier=T.FREE).monthly_price() == 0

    @pytest.mark.parametrize("name,BotClass", ALL_BOTS)
    def test_pro_price_is_positive(self, name, BotClass):
        T = _get_tier(BotClass)
        assert BotClass(tier=T.PRO).monthly_price() > 0

    @pytest.mark.parametrize("name,BotClass", ALL_BOTS)
    def test_enterprise_price_gte_pro(self, name, BotClass):
        T = _get_tier(BotClass)
        assert BotClass(tier=T.ENTERPRISE).monthly_price() >= BotClass(tier=T.PRO).monthly_price()


class TestListItems:
    @pytest.mark.parametrize("name,BotClass", ALL_BOTS)
    def test_list_items_returns_list(self, name, BotClass):
        assert isinstance(BotClass().list_items(), list)

    @pytest.mark.parametrize("name,BotClass", ALL_BOTS)
    def test_list_items_respects_limit(self, name, BotClass):
        T = _get_tier(BotClass)
        bot = BotClass(tier=T.FREE)
        assert len(bot.list_items()) <= bot.RESULT_LIMITS["free"]

    @pytest.mark.parametrize("name,BotClass", ALL_BOTS)
    def test_pro_gets_more_results(self, name, BotClass):
        bot = BotClass()
        assert bot.RESULT_LIMITS["pro"] >= bot.RESULT_LIMITS["free"]


class TestTierEnforcement:
    @pytest.mark.parametrize("name,BotClass", ALL_BOTS)
    def test_analyze_requires_pro(self, name, BotClass):
        T = _get_tier(BotClass)
        bot = BotClass(tier=T.FREE)
        TierError = getattr(sys.modules[BotClass.__module__], BotClass.__name__ + "TierError", Exception)
        with pytest.raises((TierError, Exception)):
            bot.analyze()

    @pytest.mark.parametrize("name,BotClass", ALL_BOTS)
    def test_export_requires_enterprise(self, name, BotClass):
        T = _get_tier(BotClass)
        bot = BotClass(tier=T.PRO)
        TierError = getattr(sys.modules[BotClass.__module__], BotClass.__name__ + "TierError", Exception)
        with pytest.raises((TierError, Exception)):
            bot.export_report()

    @pytest.mark.parametrize("name,BotClass", ALL_BOTS)
    def test_enterprise_can_export(self, name, BotClass):
        T = _get_tier(BotClass)
        bot = BotClass(tier=T.ENTERPRISE)
        result = bot.export_report()
        assert isinstance(result, dict)

    @pytest.mark.parametrize("name,BotClass", ALL_BOTS)
    def test_pro_can_analyze(self, name, BotClass):
        T = _get_tier(BotClass)
        bot = BotClass(tier=T.PRO)
        result = bot.analyze()
        assert isinstance(result, dict)


class TestGetTierInfo:
    @pytest.mark.parametrize("name,BotClass", ALL_BOTS)
    def test_tier_info_has_required_keys(self, name, BotClass):
        info = BotClass().get_tier_info()
        assert "tier" in info
        assert "monthly_price_usd" in info
        assert "result_limit" in info
