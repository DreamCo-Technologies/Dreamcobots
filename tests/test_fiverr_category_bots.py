"""Tests for all 30 Fiverr bots."""
from __future__ import annotations
import sys, os
import importlib
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Fiverr_bots.feature_1 import GigListingBot
from Fiverr_bots.feature_2 import OrderManagementBot
from Fiverr_bots.feature_3 import ReviewCollectorBot
from Fiverr_bots.pricing_optimizer_bot import PricingOptimizerBot
from Fiverr_bots.inbox_automation_bot import InboxAutomationBot
from Fiverr_bots.gig_ranking_bot import GigRankingBot
from Fiverr_bots.client_finder_bot import ClientFinderBot
from Fiverr_bots.portfolio_builder_bot import PortfolioBuilderBot
from Fiverr_bots.upsell_bot import UpsellBot
from Fiverr_bots.deadline_tracker_bot import DeadlineTrackerBot
from Fiverr_bots.revision_manager_bot import RevisionManagerBot
from Fiverr_bots.dispute_resolver_bot import DisputeResolverBot
from Fiverr_bots.earnings_tracker_bot import EarningsTrackerBot
from Fiverr_bots.niche_analyzer_bot import NicheAnalyzerBot
from Fiverr_bots.competitor_spy_bot import CompetitorSpyBot
from Fiverr_bots.proposal_writer_bot import ProposalWriterBot
from Fiverr_bots.client_retention_bot import ClientRetentionBot
from Fiverr_bots.package_optimizer_bot import PackageOptimizerBot
from Fiverr_bots.response_time_bot import ResponseTimeBot
from Fiverr_bots.skill_tagger_bot import SkillTaggerBot
from Fiverr_bots.gig_description_optimizer_bot import GigDescriptionOptimizerBot
from Fiverr_bots.order_completion_bot import OrderCompletionBot
from Fiverr_bots.milestone_tracker_bot import MilestoneTrackerBot
from Fiverr_bots.buyer_persona_bot import BuyerPersonaBot
from Fiverr_bots.seasonal_pricing_bot import SeasonalPricingBot
from Fiverr_bots.gig_image_optimizer_bot import GigImageOptimizerBot
from Fiverr_bots.service_expansion_bot import ServiceExpansionBot
from Fiverr_bots.cross_sell_bot import CrossSellBot
from Fiverr_bots.feedback_analyzer_bot import FeedbackAnalyzerBot
from Fiverr_bots.level_up_bot import LevelUpBot

ALL_BOTS = [
    ("GigListingBot", GigListingBot),
    ("OrderManagementBot", OrderManagementBot),
    ("ReviewCollectorBot", ReviewCollectorBot),
    ("PricingOptimizerBot", PricingOptimizerBot),
    ("InboxAutomationBot", InboxAutomationBot),
    ("GigRankingBot", GigRankingBot),
    ("ClientFinderBot", ClientFinderBot),
    ("PortfolioBuilderBot", PortfolioBuilderBot),
    ("UpsellBot", UpsellBot),
    ("DeadlineTrackerBot", DeadlineTrackerBot),
    ("RevisionManagerBot", RevisionManagerBot),
    ("DisputeResolverBot", DisputeResolverBot),
    ("EarningsTrackerBot", EarningsTrackerBot),
    ("NicheAnalyzerBot", NicheAnalyzerBot),
    ("CompetitorSpyBot", CompetitorSpyBot),
    ("ProposalWriterBot", ProposalWriterBot),
    ("ClientRetentionBot", ClientRetentionBot),
    ("PackageOptimizerBot", PackageOptimizerBot),
    ("ResponseTimeBot", ResponseTimeBot),
    ("SkillTaggerBot", SkillTaggerBot),
    ("GigDescriptionOptimizerBot", GigDescriptionOptimizerBot),
    ("OrderCompletionBot", OrderCompletionBot),
    ("MilestoneTrackerBot", MilestoneTrackerBot),
    ("BuyerPersonaBot", BuyerPersonaBot),
    ("SeasonalPricingBot", SeasonalPricingBot),
    ("GigImageOptimizerBot", GigImageOptimizerBot),
    ("ServiceExpansionBot", ServiceExpansionBot),
    ("CrossSellBot", CrossSellBot),
    ("FeedbackAnalyzerBot", FeedbackAnalyzerBot),
    ("LevelUpBot", LevelUpBot),
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
