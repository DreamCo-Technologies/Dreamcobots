"""
Tests for bots/saas_packages_bot — SaaS Domination system.

Covers: tiers, package_catalog, modular_builder, enterprise_scaler,
        and the main SaaSPackagesBot orchestrator (40+ tests).
"""

from __future__ import annotations

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

from bots.saas_packages_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    list_tiers,
    get_upgrade_path,
    FEATURE_BASIC_PACKAGES,
    FEATURE_ADVANCED_TEMPLATES,
    FEATURE_USAGE_ANALYTICS,
    FEATURE_ECOMMERCE_MODULE,
    FEATURE_CRM_MODULE,
    FEATURE_HR_MODULE,
    FEATURE_CUSTOM_BUILDER,
    FEATURE_FORTUNE500_INTEGRATIONS,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_DEDICATED_SUPPORT,
)
from bots.saas_packages_bot.package_catalog import PackageCatalog, Industry, SaaSPackage
from bots.saas_packages_bot.modular_builder import (
    ModularSaaSBuilder,
    AVAILABLE_MODULES,
    MODULE_COSTS,
    AvailableModule,
)
from bots.saas_packages_bot.enterprise_scaler import EnterpriseScaler, ScaleTier
from bots.saas_packages_bot.saas_packages_bot import (
    SaaSPackagesBot,
    SaaSPackagesBotError,
    SaaSPackagesTierError,
)


# ===========================================================================
# tiers.py
# ===========================================================================

class TestTiers:
    def test_three_tiers_exist(self):
        tiers = list_tiers()
        assert len(tiers) == 3

    def test_free_price_is_zero(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.price_usd_monthly == 0.0

    def test_pro_price(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.price_usd_monthly == 49.0

    def test_enterprise_price(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.price_usd_monthly == 199.0

    def test_free_max_packages(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.max_packages == 1

    def test_pro_max_packages(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.max_packages == 5

    def test_enterprise_unlimited_packages(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.max_packages is None
        assert cfg.is_unlimited_packages() is True

    def test_enterprise_unlimited_users(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.max_users is None
        assert cfg.is_unlimited_users() is True

    def test_free_has_basic_packages_feature(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.has_feature(FEATURE_BASIC_PACKAGES)

    def test_free_lacks_advanced_templates(self):
        cfg = get_tier_config(Tier.FREE)
        assert not cfg.has_feature(FEATURE_ADVANCED_TEMPLATES)

    def test_pro_has_crm_and_ecommerce(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_CRM_MODULE)
        assert cfg.has_feature(FEATURE_ECOMMERCE_MODULE)

    def test_enterprise_has_all_features(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        for feat in [
            FEATURE_CUSTOM_BUILDER,
            FEATURE_FORTUNE500_INTEGRATIONS,
            FEATURE_WHITE_LABEL,
            FEATURE_API_ACCESS,
            FEATURE_DEDICATED_SUPPORT,
        ]:
            assert cfg.has_feature(feat), f"Missing feature: {feat}"

    def test_upgrade_path_free_to_pro(self):
        upgrade = get_upgrade_path(Tier.FREE)
        assert upgrade is not None
        assert upgrade.tier == Tier.PRO

    def test_upgrade_path_pro_to_enterprise(self):
        upgrade = get_upgrade_path(Tier.PRO)
        assert upgrade is not None
        assert upgrade.tier == Tier.ENTERPRISE

    def test_upgrade_path_enterprise_is_none(self):
        upgrade = get_upgrade_path(Tier.ENTERPRISE)
        assert upgrade is None


# ===========================================================================
# package_catalog.py
# ===========================================================================

class TestPackageCatalog:
    @pytest.fixture
    def catalog(self):
        return PackageCatalog()

    def test_catalog_has_15_plus_packages(self, catalog):
        assert catalog.count() >= 15

    def test_list_all_packages(self, catalog):
        pkgs = catalog.list_packages()
        assert len(pkgs) >= 15

    def test_list_by_industry_ecommerce(self, catalog):
        pkgs = catalog.get_by_industry(Industry.E_COMMERCE)
        assert len(pkgs) >= 1
        for p in pkgs:
            assert p.industry == Industry.E_COMMERCE

    def test_get_package_by_id(self, catalog):
        pkg = catalog.get_package("ecom-001")
        assert pkg is not None
        assert pkg.package_id == "ecom-001"

    def test_get_package_missing_returns_none(self, catalog):
        assert catalog.get_package("nonexistent-999") is None

    def test_search_packages_by_keyword(self, catalog):
        results = catalog.search_packages("crm")
        assert len(results) >= 1

    def test_search_packages_case_insensitive(self, catalog):
        r1 = catalog.search_packages("CRM")
        r2 = catalog.search_packages("crm")
        assert len(r1) == len(r2)

    def test_search_packages_no_match(self, catalog):
        results = catalog.search_packages("zzznomatch9999")
        assert results == []

    def test_get_pricing_summary_sorted(self, catalog):
        summary = catalog.get_pricing_summary()
        prices = [s["monthly_price_usd"] for s in summary]
        assert prices == sorted(prices)

    def test_pricing_summary_has_required_keys(self, catalog):
        summary = catalog.get_pricing_summary()
        for item in summary:
            for key in ["package_id", "name", "industry", "monthly_price_usd", "setup_fee_usd"]:
                assert key in item

    def test_saas_package_to_dict(self, catalog):
        pkg = catalog.get_package("crm-001")
        assert pkg is not None
        d = pkg.to_dict()
        for key in ["package_id", "name", "industry", "description", "modules",
                    "monthly_price_usd", "setup_fee_usd", "users_included", "features"]:
            assert key in d

    def test_industries_covered(self, catalog):
        industries = {p.industry for p in catalog.list_packages()}
        expected = {Industry.E_COMMERCE, Industry.CRM, Industry.HR_AUTOMATION,
                    Industry.FINANCE, Industry.HEALTHCARE, Industry.EDUCATION,
                    Industry.LEGAL, Industry.MARKETING, Industry.LOGISTICS,
                    Industry.REAL_ESTATE}
        assert expected.issubset(industries)


# ===========================================================================
# modular_builder.py
# ===========================================================================

class TestModularBuilder:
    @pytest.fixture
    def builder(self):
        return ModularSaaSBuilder()

    def test_available_modules_count(self):
        assert len(AVAILABLE_MODULES) == 15

    def test_create_plan_returns_plan_id(self, builder):
        result = builder.create_saas_plan("u1", "My Plan", "SaaS", "Test plan")
        assert "plan_id" in result
        assert result["status"] == "created"

    def test_add_module_success(self, builder):
        plan = builder.create_saas_plan("u1", "Plan A", "E-commerce")
        pid = plan["plan_id"]
        result = builder.add_module(pid, AvailableModule.AUTH)
        assert result["module_added"] == "AUTH"
        assert result["total_modules"] == 1

    def test_add_module_case_insensitive(self, builder):
        plan = builder.create_saas_plan("u1", "Plan B", "E-commerce")
        pid = plan["plan_id"]
        result = builder.add_module(pid, "auth")
        assert "error" not in result

    def test_add_duplicate_module_returns_error(self, builder):
        plan = builder.create_saas_plan("u1", "Plan C", "SaaS")
        pid = plan["plan_id"]
        builder.add_module(pid, AvailableModule.PAYMENTS)
        result = builder.add_module(pid, AvailableModule.PAYMENTS)
        assert "error" in result

    def test_add_invalid_module_returns_error(self, builder):
        plan = builder.create_saas_plan("u1", "Plan D", "SaaS")
        pid = plan["plan_id"]
        result = builder.add_module(pid, "INVALID_MODULE_XYZ")
        assert "error" in result
        assert "available" in result

    def test_remove_module_success(self, builder):
        plan = builder.create_saas_plan("u1", "Plan E", "SaaS")
        pid = plan["plan_id"]
        builder.add_module(pid, AvailableModule.CRM)
        result = builder.remove_module(pid, AvailableModule.CRM)
        assert result["module_removed"] == "CRM"
        assert result["total_modules"] == 0

    def test_remove_nonexistent_module_returns_error(self, builder):
        plan = builder.create_saas_plan("u1", "Plan F", "SaaS")
        pid = plan["plan_id"]
        result = builder.remove_module(pid, AvailableModule.AUTH)
        assert "error" in result

    def test_calculate_plan_cost_no_modules(self, builder):
        plan = builder.create_saas_plan("u1", "Plan G", "SaaS")
        pid = plan["plan_id"]
        cost = builder.calculate_plan_cost(pid)
        assert cost["modules_cost"] == 0.0
        assert cost["base_cost"] == 29.0
        assert cost["total_monthly"] == 29.0

    def test_calculate_plan_cost_with_modules(self, builder):
        plan = builder.create_saas_plan("u1", "Plan H", "SaaS")
        pid = plan["plan_id"]
        builder.add_module(pid, AvailableModule.AUTH)
        builder.add_module(pid, AvailableModule.PAYMENTS)
        cost = builder.calculate_plan_cost(pid)
        expected_modules_cost = MODULE_COSTS[AvailableModule.AUTH] + MODULE_COSTS[AvailableModule.PAYMENTS]
        assert cost["modules_cost"] == expected_modules_cost
        assert cost["total_monthly"] == 29.0 + expected_modules_cost

    def test_generate_plan_spec(self, builder):
        plan = builder.create_saas_plan("u1", "Plan I", "Fintech")
        pid = plan["plan_id"]
        builder.add_module(pid, AvailableModule.ANALYTICS)
        spec = builder.generate_plan_spec(pid)
        assert spec["spec_version"] == "1.0"
        assert spec["plan_id"] == pid
        assert len(spec["modules"]) == 1
        assert "pricing" in spec
        assert "deployment" in spec

    def test_generate_plan_spec_backup_flag(self, builder):
        plan = builder.create_saas_plan("u1", "Plan J", "SaaS")
        pid = plan["plan_id"]
        builder.add_module(pid, AvailableModule.BACKUP)
        spec = builder.generate_plan_spec(pid)
        assert spec["deployment"]["auto_backup"] is True

    def test_list_plans_user_isolation(self, builder):
        builder.create_saas_plan("alice", "Alice Plan", "SaaS")
        builder.create_saas_plan("bob", "Bob Plan", "SaaS")
        alice_plans = builder.list_plans("alice")
        assert all(p["plan_name"] == "Alice Plan" for p in alice_plans)

    def test_get_nonexistent_plan_raises(self, builder):
        with pytest.raises(KeyError):
            builder.calculate_plan_cost("nonexistent-id")


# ===========================================================================
# enterprise_scaler.py
# ===========================================================================

class TestEnterpriseScaler:
    @pytest.fixture
    def scaler(self):
        return EnterpriseScaler()

    def test_assess_startup_tier(self, scaler):
        assert scaler.assess_scale_tier(1) == ScaleTier.STARTUP
        assert scaler.assess_scale_tier(10) == ScaleTier.STARTUP

    def test_assess_growth_tier(self, scaler):
        assert scaler.assess_scale_tier(11) == ScaleTier.GROWTH
        assert scaler.assess_scale_tier(100) == ScaleTier.GROWTH

    def test_assess_scale_tier(self, scaler):
        assert scaler.assess_scale_tier(101) == ScaleTier.SCALE
        assert scaler.assess_scale_tier(1_000) == ScaleTier.SCALE

    def test_assess_enterprise_tier(self, scaler):
        assert scaler.assess_scale_tier(1_001) == ScaleTier.ENTERPRISE
        assert scaler.assess_scale_tier(10_000) == ScaleTier.ENTERPRISE

    def test_assess_fortune500_tier(self, scaler):
        assert scaler.assess_scale_tier(10_001) == ScaleTier.FORTUNE500

    def test_assess_invalid_user_count_raises(self, scaler):
        with pytest.raises(ValueError):
            scaler.assess_scale_tier(0)

    def test_generate_scaling_plan_keys(self, scaler):
        plan = scaler.generate_scaling_plan("plan-1", 10, 500)
        for key in ["plan_id", "current_tier", "projected_tier", "infrastructure_recommendations",
                    "current_monthly_cost_usd", "projected_monthly_cost_usd", "cost_increase_usd"]:
            assert key in plan

    def test_generate_scaling_plan_cost_increases(self, scaler):
        plan = scaler.generate_scaling_plan("plan-2", 10, 1000)
        assert plan["projected_monthly_cost_usd"] > plan["current_monthly_cost_usd"]

    def test_estimate_infrastructure_cost_keys(self, scaler):
        cost = scaler.estimate_infrastructure_cost(50, [])
        for key in ["compute_usd", "storage_usd", "bandwidth_usd", "support_usd", "total_monthly_usd"]:
            assert key in cost

    def test_estimate_infrastructure_cost_modules_add_overhead(self, scaler):
        cost_no_modules = scaler.estimate_infrastructure_cost(50, [])
        cost_with_modules = scaler.estimate_infrastructure_cost(50, ["AUTH", "PAYMENTS"])
        assert cost_with_modules["total_monthly_usd"] > cost_no_modules["total_monthly_usd"]

    def test_generate_fortune500_salesforce(self, scaler):
        result = scaler.generate_fortune500_integration("Acme Corp", "SALESFORCE")
        assert result["integration_type"] == "SALESFORCE"
        assert "features" in result
        assert result["company_name"] == "Acme Corp"

    def test_generate_fortune500_invalid_type(self, scaler):
        result = scaler.generate_fortune500_integration("Corp", "INVALID")
        assert "error" in result
        assert "supported_types" in result

    def test_generate_fortune500_all_types(self, scaler):
        for itype in ["ERP", "SALESFORCE", "SAP", "ORACLE", "MICROSOFT_365", "SLACK", "JIRA"]:
            result = scaler.generate_fortune500_integration("TestCorp", itype)
            assert "error" not in result, f"Integration '{itype}' returned error"


# ===========================================================================
# saas_packages_bot.py (main orchestrator)
# ===========================================================================

class TestSaaSPackagesBotFree:
    @pytest.fixture
    def bot(self):
        return SaaSPackagesBot(tier=Tier.FREE, user_id="test_user")

    def test_run_returns_status(self, bot):
        result = bot.run()
        assert "SaaS Packages Bot" in result
        assert "FREE" in result

    def test_list_packages_limited(self, bot):
        pkgs = bot.list_packages()
        assert len(pkgs) <= 1

    def test_get_package_found(self, bot):
        result = bot.get_package("ecom-001")
        assert "error" not in result
        assert result["package_id"] == "ecom-001"

    def test_get_package_not_found(self, bot):
        result = bot.get_package("nonexistent")
        assert "error" in result

    def test_search_packages(self, bot):
        results = bot.search_packages("crm")
        assert isinstance(results, list)

    def test_describe_tier(self, bot):
        info = bot.describe_tier()
        assert info["tier"] == "free"
        assert info["price_usd_monthly"] == 0.0

    def test_dashboard_keys(self, bot):
        dash = bot.dashboard()
        for key in ["bot", "tier", "user_id", "catalog_size", "features"]:
            assert key in dash

    def test_custom_builder_blocked_on_free(self, bot):
        with pytest.raises(SaaSPackagesTierError):
            bot.create_saas_plan("Test", "SaaS")

    def test_fortune500_blocked_on_free(self, bot):
        with pytest.raises(SaaSPackagesTierError):
            bot.generate_fortune500_integration("Corp", "SALESFORCE")

    def test_chat_returns_string(self, bot):
        assert isinstance(bot.chat("hello"), str)

    def test_chat_package_keyword(self, bot):
        response = bot.chat("tell me about packages")
        assert "package" in response.lower()

    def test_assess_scale_tier_accessible_on_free(self, bot):
        tier = bot.assess_scale_tier(50)
        assert tier == ScaleTier.GROWTH


class TestSaaSPackagesBotEnterprise:
    @pytest.fixture
    def bot(self):
        return SaaSPackagesBot(tier=Tier.ENTERPRISE, user_id="enterprise_user")

    def test_list_packages_unlimited(self, bot):
        pkgs = bot.list_packages()
        assert len(pkgs) >= 15

    def test_create_and_manage_plan(self, bot):
        plan = bot.create_saas_plan("My SaaS", "Fintech", "Test plan")
        pid = plan["plan_id"]
        add_result = bot.add_module(pid, "ANALYTICS")
        assert add_result["module_added"] == "ANALYTICS"
        cost = bot.calculate_plan_cost(pid)
        assert cost["total_monthly"] > 29.0
        spec = bot.generate_plan_spec(pid)
        assert spec["plan_id"] == pid

    def test_remove_module(self, bot):
        plan = bot.create_saas_plan("Plan X", "HR")
        pid = plan["plan_id"]
        bot.add_module(pid, "AUTH")
        result = bot.remove_module(pid, "AUTH")
        assert result["total_modules"] == 0

    def test_list_plans(self, bot):
        bot.create_saas_plan("Plan 1", "SaaS")
        bot.create_saas_plan("Plan 2", "E-commerce")
        plans = bot.list_plans()
        assert len(plans) >= 2

    def test_fortune500_integration(self, bot):
        result = bot.generate_fortune500_integration("Acme Inc", "SLACK")
        assert result["integration_type"] == "SLACK"

    def test_estimate_infrastructure_cost(self, bot):
        cost = bot.estimate_infrastructure_cost(500, ["AUTH", "PAYMENTS"])
        assert cost["total_monthly_usd"] > 0

    def test_generate_scaling_plan(self, bot):
        plan = bot.generate_scaling_plan("p-1", 50, 5000)
        assert plan["projected_tier"] == ScaleTier.ENTERPRISE

    def test_describe_tier_no_upgrade(self, bot):
        info = bot.describe_tier()
        assert info["upgrade_available"] is False

    def test_chat_scale_keyword(self, bot):
        response = bot.chat("how do I scale?")
        assert isinstance(response, str)
        assert len(response) > 0
