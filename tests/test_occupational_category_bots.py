"""Tests for all 30 Occupational bots."""
from __future__ import annotations
import sys, os
import importlib
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Occupational_bots.feature_1 import JobSearchBot
from Occupational_bots.feature_2 import ResumeBuilderBot
from Occupational_bots.feature_3 import InterviewPrepBot
from Occupational_bots.salary_negotiator_bot import SalaryNegotiatorBot
from Occupational_bots.career_path_bot import CareerPathBot
from Occupational_bots.skills_gap_bot import SkillsGapBot
from Occupational_bots.networking_bot import NetworkingBot
from Occupational_bots.linkedin_optimizer_bot import LinkedInOptimizerBot
from Occupational_bots.cover_letter_bot import CoverLetterBot
from Occupational_bots.job_application_tracker_bot import JobApplicationTrackerBot
from Occupational_bots.freelance_rate_bot import FreelanceRateBot
from Occupational_bots.certification_advisor_bot import CertificationAdvisorBot
from Occupational_bots.portfolio_builder_bot import PortfolioBuilderBot
from Occupational_bots.reference_checker_bot import ReferenceCheckerBot
from Occupational_bots.performance_review_bot import PerformanceReviewBot
from Occupational_bots.remote_job_finder_bot import RemoteJobFinderBot
from Occupational_bots.side_hustle_finder_bot import SideHustleFinderBot
from Occupational_bots.upskill_recommender_bot import UpskillRecommenderBot
from Occupational_bots.industry_trend_bot import IndustryTrendBot
from Occupational_bots.company_culture_bot import CompanyCultureBot
from Occupational_bots.benefits_analyzer_bot import BenefitsAnalyzerBot
from Occupational_bots.work_life_balance_bot import WorkLifeBalanceBot
from Occupational_bots.contractor_rate_bot import ContractorRateBot
from Occupational_bots.job_board_aggregator_bot import JobBoardAggregatorBot
from Occupational_bots.headhunter_bot import HeadhunterBot
from Occupational_bots.promotion_readiness_bot import PromotionReadinessBot
from Occupational_bots.mentor_finder_bot import MentorFinderBot
from Occupational_bots.gig_economy_bot import GigEconomyBot
from Occupational_bots.relocation_advisor_bot import RelocationAdvisorBot
from Occupational_bots.diversity_inclusion_bot import DiversityInclusionBot

ALL_BOTS = [
    ("JobSearchBot", JobSearchBot),
    ("ResumeBuilderBot", ResumeBuilderBot),
    ("InterviewPrepBot", InterviewPrepBot),
    ("SalaryNegotiatorBot", SalaryNegotiatorBot),
    ("CareerPathBot", CareerPathBot),
    ("SkillsGapBot", SkillsGapBot),
    ("NetworkingBot", NetworkingBot),
    ("LinkedInOptimizerBot", LinkedInOptimizerBot),
    ("CoverLetterBot", CoverLetterBot),
    ("JobApplicationTrackerBot", JobApplicationTrackerBot),
    ("FreelanceRateBot", FreelanceRateBot),
    ("CertificationAdvisorBot", CertificationAdvisorBot),
    ("PortfolioBuilderBot", PortfolioBuilderBot),
    ("ReferenceCheckerBot", ReferenceCheckerBot),
    ("PerformanceReviewBot", PerformanceReviewBot),
    ("RemoteJobFinderBot", RemoteJobFinderBot),
    ("SideHustleFinderBot", SideHustleFinderBot),
    ("UpskillRecommenderBot", UpskillRecommenderBot),
    ("IndustryTrendBot", IndustryTrendBot),
    ("CompanyCultureBot", CompanyCultureBot),
    ("BenefitsAnalyzerBot", BenefitsAnalyzerBot),
    ("WorkLifeBalanceBot", WorkLifeBalanceBot),
    ("ContractorRateBot", ContractorRateBot),
    ("JobBoardAggregatorBot", JobBoardAggregatorBot),
    ("HeadhunterBot", HeadhunterBot),
    ("PromotionReadinessBot", PromotionReadinessBot),
    ("MentorFinderBot", MentorFinderBot),
    ("GigEconomyBot", GigEconomyBot),
    ("RelocationAdvisorBot", RelocationAdvisorBot),
    ("DiversityInclusionBot", DiversityInclusionBot),
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
