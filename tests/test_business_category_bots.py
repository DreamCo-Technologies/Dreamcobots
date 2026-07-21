"""Tests for all 30 Business bots."""
from __future__ import annotations
import sys, os
import importlib
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Business_bots.feature_1 import BusinessLaunchBot
from Business_bots.feature_2 import CRMBot
from Business_bots.feature_3 import InvoicingBot
from Business_bots.inventory_manager_bot import InventoryManagerBot
from Business_bots.expense_tracker_bot import ExpenseTrackerBot
from Business_bots.payroll_bot import PayrollBot
from Business_bots.sales_pipeline_bot import SalesPipelineBot
from Business_bots.customer_support_bot import CustomerSupportBot
from Business_bots.contract_generator_bot import ContractGeneratorBot
from Business_bots.financial_forecaster_bot import FinancialForecasterBot
from Business_bots.competitor_analyzer_bot import CompetitorAnalyzerBot
from Business_bots.brand_monitor_bot import BrandMonitorBot
from Business_bots.employee_onboarding_bot import EmployeeOnboardingBot
from Business_bots.meeting_scheduler_bot import MeetingSchedulerBot
from Business_bots.document_manager_bot import DocumentManagerBot
from Business_bots.tax_preparer_bot import TaxPreparerBot
from Business_bots.grant_finder_bot import GrantFinderBot
from Business_bots.business_plan_bot import BusinessPlanBot
from Business_bots.pricing_strategy_bot import PricingStrategyBot
from Business_bots.vendor_manager_bot import VendorManagerBot
from Business_bots.kpi_tracker_bot import KPITrackerBot
from Business_bots.market_research_bot import MarketResearchBot
from Business_bots.partnership_finder_bot import PartnershipFinderBot
from Business_bots.compliance_checker_bot import ComplianceCheckerBot
from Business_bots.pitch_deck_bot import PitchDeckBot
from Business_bots.llc_formation_bot import LLCFormationBot
from Business_bots.insurance_advisor_bot import InsuranceAdvisorBot
from Business_bots.supply_chain_bot import SupplyChainBot
from Business_bots.ecommerce_optimizer_bot import EcommerceOptimizerBot
from Business_bots.franchise_analyzer_bot import FranchiseAnalyzerBot

ALL_BOTS = [
    ("BusinessLaunchBot", BusinessLaunchBot),
    ("CRMBot", CRMBot),
    ("InvoicingBot", InvoicingBot),
    ("InventoryManagerBot", InventoryManagerBot),
    ("ExpenseTrackerBot", ExpenseTrackerBot),
    ("PayrollBot", PayrollBot),
    ("SalesPipelineBot", SalesPipelineBot),
    ("CustomerSupportBot", CustomerSupportBot),
    ("ContractGeneratorBot", ContractGeneratorBot),
    ("FinancialForecasterBot", FinancialForecasterBot),
    ("CompetitorAnalyzerBot", CompetitorAnalyzerBot),
    ("BrandMonitorBot", BrandMonitorBot),
    ("EmployeeOnboardingBot", EmployeeOnboardingBot),
    ("MeetingSchedulerBot", MeetingSchedulerBot),
    ("DocumentManagerBot", DocumentManagerBot),
    ("TaxPreparerBot", TaxPreparerBot),
    ("GrantFinderBot", GrantFinderBot),
    ("BusinessPlanBot", BusinessPlanBot),
    ("PricingStrategyBot", PricingStrategyBot),
    ("VendorManagerBot", VendorManagerBot),
    ("KPITrackerBot", KPITrackerBot),
    ("MarketResearchBot", MarketResearchBot),
    ("PartnershipFinderBot", PartnershipFinderBot),
    ("ComplianceCheckerBot", ComplianceCheckerBot),
    ("PitchDeckBot", PitchDeckBot),
    ("LLCFormationBot", LLCFormationBot),
    ("InsuranceAdvisorBot", InsuranceAdvisorBot),
    ("SupplyChainBot", SupplyChainBot),
    ("EcommerceOptimizerBot", EcommerceOptimizerBot),
    ("FranchiseAnalyzerBot", FranchiseAnalyzerBot),
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
