"""Tests for all 30 Marketing bots."""
from __future__ import annotations
import sys, os
import importlib
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Marketing_bots.feature_1 import SocialMediaBot
from Marketing_bots.feature_2 import EmailMarketingBot
from Marketing_bots.feature_3 import ContentCreationBot
from Marketing_bots.seo_optimizer_bot import SEOOptimizerBot
from Marketing_bots.ad_campaign_bot import AdCampaignBot
from Marketing_bots.influencer_finder_bot import InfluencerFinderBot
from Marketing_bots.hashtag_analyzer_bot import HashtagAnalyzerBot
from Marketing_bots.competitor_spy_bot import CompetitorSpyBot
from Marketing_bots.landing_page_bot import LandingPageBot
from Marketing_bots.lead_magnet_bot import LeadMagnetBot
from Marketing_bots.sales_funnel_bot import SalesFunnelBot
from Marketing_bots.chatbot_builder_bot import ChatbotBuilderBot
from Marketing_bots.video_marketing_bot import VideoMarketingBot
from Marketing_bots.podcast_promoter_bot import PodcastPromoterBot
from Marketing_bots.affiliate_marketer_bot import AffiliateMarketerBot
from Marketing_bots.press_release_bot import PressReleaseBot
from Marketing_bots.brand_story_bot import BrandStoryBot
from Marketing_bots.viral_content_bot import ViralContentBot
from Marketing_bots.customer_review_bot import CustomerReviewBot
from Marketing_bots.newsletter_bot import NewsletterBot
from Marketing_bots.webinar_bot import WebinarBot
from Marketing_bots.retargeting_bot import RetargetingBot
from Marketing_bots.google_ads_bot import GoogleAdsBot
from Marketing_bots.social_proof_bot import SocialProofBot
from Marketing_bots.ab_testing_bot import ABTestingBot
from Marketing_bots.conversion_optimizer_bot import ConversionOptimizerBot
from Marketing_bots.event_promoter_bot import EventPromoterBot
from Marketing_bots.referral_marketing_bot import ReferralMarketingBot
from Marketing_bots.loyalty_program_bot import LoyaltyProgramBot
from Marketing_bots.analytics_reporter_bot import AnalyticsReporterBot

ALL_BOTS = [
    ("SocialMediaBot", SocialMediaBot),
    ("EmailMarketingBot", EmailMarketingBot),
    ("ContentCreationBot", ContentCreationBot),
    ("SEOOptimizerBot", SEOOptimizerBot),
    ("AdCampaignBot", AdCampaignBot),
    ("InfluencerFinderBot", InfluencerFinderBot),
    ("HashtagAnalyzerBot", HashtagAnalyzerBot),
    ("CompetitorSpyBot", CompetitorSpyBot),
    ("LandingPageBot", LandingPageBot),
    ("LeadMagnetBot", LeadMagnetBot),
    ("SalesFunnelBot", SalesFunnelBot),
    ("ChatbotBuilderBot", ChatbotBuilderBot),
    ("VideoMarketingBot", VideoMarketingBot),
    ("PodcastPromoterBot", PodcastPromoterBot),
    ("AffiliateMarketerBot", AffiliateMarketerBot),
    ("PressReleaseBot", PressReleaseBot),
    ("BrandStoryBot", BrandStoryBot),
    ("ViralContentBot", ViralContentBot),
    ("CustomerReviewBot", CustomerReviewBot),
    ("NewsletterBot", NewsletterBot),
    ("WebinarBot", WebinarBot),
    ("RetargetingBot", RetargetingBot),
    ("GoogleAdsBot", GoogleAdsBot),
    ("SocialProofBot", SocialProofBot),
    ("ABTestingBot", ABTestingBot),
    ("ConversionOptimizerBot", ConversionOptimizerBot),
    ("EventPromoterBot", EventPromoterBot),
    ("ReferralMarketingBot", ReferralMarketingBot),
    ("LoyaltyProgramBot", LoyaltyProgramBot),
    ("AnalyticsReporterBot", AnalyticsReporterBot),
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
