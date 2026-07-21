"""Tests for all 30 Real Estate bots."""
from __future__ import annotations
import sys, os
import importlib
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Real_Estate_bots.feature_1 import PropertyListingsBot
from Real_Estate_bots.feature_2 import ViewingSchedulerBot
from Real_Estate_bots.feature_3 import MarketAnalysisBot
from Real_Estate_bots.mortgage_calculator_bot import MortgageCalculatorBot
from Real_Estate_bots.property_valuation_bot import PropertyValuationBot
from Real_Estate_bots.flip_profit_calculator_bot import FlipProfitCalculatorBot
from Real_Estate_bots.rental_income_bot import RentalIncomeBot
from Real_Estate_bots.foreclosure_finder_bot import ForeclosureFinderBot
from Real_Estate_bots.lease_generator_bot import LeaseGeneratorBot
from Real_Estate_bots.tenant_screening_bot import TenantScreeningBot
from Real_Estate_bots.neighborhood_scorer_bot import NeighborhoodScorerBot
from Real_Estate_bots.deal_analyzer_bot import DealAnalyzerBot
from Real_Estate_bots.cash_flow_bot import CashFlowBot
from Real_Estate_bots.property_alert_bot import PropertyAlertBot
from Real_Estate_bots.auction_finder_bot import AuctionFinderBot
from Real_Estate_bots.fix_and_flip_bot import FixAndFlipBot
from Real_Estate_bots.roi_tracker_bot import ROITrackerBot
from Real_Estate_bots.comparable_sales_bot import ComparableSalesBot
from Real_Estate_bots.zoning_research_bot import ZoningResearchBot
from Real_Estate_bots.tax_lien_bot import TaxLienBot
from Real_Estate_bots.commercial_analyzer_bot import CommercialAnalyzerBot
from Real_Estate_bots.multifamily_analyzer_bot import MultifamilyAnalyzerBot
from Real_Estate_bots.short_sale_finder_bot import ShortSaleFinderBot
from Real_Estate_bots.property_management_bot import PropertyManagementBot
from Real_Estate_bots.insurance_estimator_bot import InsuranceEstimatorBot
from Real_Estate_bots.renovation_cost_bot import RenovationCostBot
from Real_Estate_bots.wholesaler_bot import WholesalerBot
from Real_Estate_bots.off_market_finder_bot import OffMarketFinderBot
from Real_Estate_bots.investor_matchmaker_bot import InvestorMatchmakerBot
from Real_Estate_bots.land_analyzer_bot import LandAnalyzerBot

ALL_BOTS = [
    ("PropertyListingsBot", PropertyListingsBot),
    ("ViewingSchedulerBot", ViewingSchedulerBot),
    ("MarketAnalysisBot", MarketAnalysisBot),
    ("MortgageCalculatorBot", MortgageCalculatorBot),
    ("PropertyValuationBot", PropertyValuationBot),
    ("FlipProfitCalculatorBot", FlipProfitCalculatorBot),
    ("RentalIncomeBot", RentalIncomeBot),
    ("ForeclosureFinderBot", ForeclosureFinderBot),
    ("LeaseGeneratorBot", LeaseGeneratorBot),
    ("TenantScreeningBot", TenantScreeningBot),
    ("NeighborhoodScorerBot", NeighborhoodScorerBot),
    ("DealAnalyzerBot", DealAnalyzerBot),
    ("CashFlowBot", CashFlowBot),
    ("PropertyAlertBot", PropertyAlertBot),
    ("AuctionFinderBot", AuctionFinderBot),
    ("FixAndFlipBot", FixAndFlipBot),
    ("ROITrackerBot", ROITrackerBot),
    ("ComparableSalesBot", ComparableSalesBot),
    ("ZoningResearchBot", ZoningResearchBot),
    ("TaxLienBot", TaxLienBot),
    ("CommercialAnalyzerBot", CommercialAnalyzerBot),
    ("MultifamilyAnalyzerBot", MultifamilyAnalyzerBot),
    ("ShortSaleFinderBot", ShortSaleFinderBot),
    ("PropertyManagementBot", PropertyManagementBot),
    ("InsuranceEstimatorBot", InsuranceEstimatorBot),
    ("RenovationCostBot", RenovationCostBot),
    ("WholesalerBot", WholesalerBot),
    ("OffMarketFinderBot", OffMarketFinderBot),
    ("InvestorMatchmakerBot", InvestorMatchmakerBot),
    ("LandAnalyzerBot", LandAnalyzerBot),
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
