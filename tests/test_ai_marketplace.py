import sys, os
REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, REPO_ROOT)
import pytest
from bots.ai_marketplace.tiers import (
    Tier, TierConfig, TIER_CATALOGUE, get_tier_config, list_tiers, get_upgrade_path,
    FEATURE_PLUGIN_INSTALL, FEATURE_ALERTS, FEATURE_ANALYTICS,
    FEATURE_ENTERPRISE_PLUGINS, FEATURE_CUSTOM_PLUGINS, FEATURE_WHITE_LABEL, FEATURE_API_ACCESS,
)
from bots.ai_marketplace.plugins import PluginRegistry, Plugin, PluginCategory
from bots.ai_marketplace.subscriptions import SubscriptionManager, SubscriptionPlan, PLAN_CATALOGUE
from bots.ai_marketplace.skill_packs import SkillPackRegistry, SkillPack
from bots.ai_marketplace.ai_marketplace import AIMarketplace, AIMarketplaceError, AIMarketplaceTierError


class TestTiers:
    def test_three_tiers_exist(self):
        assert len(list(Tier)) == 3

    def test_free_price(self):
        assert get_tier_config(Tier.FREE).price_usd_monthly == 0.0

    def test_pro_price(self):
        assert get_tier_config(Tier.PRO).price_usd_monthly == 49.0

    def test_enterprise_price(self):
        assert get_tier_config(Tier.ENTERPRISE).price_usd_monthly == 199.0

    def test_free_max_plugins(self):
        assert get_tier_config(Tier.FREE).max_plugins == 3

    def test_pro_max_plugins(self):
        assert get_tier_config(Tier.PRO).max_plugins == 20

    def test_enterprise_unlimited_plugins(self):
        assert get_tier_config(Tier.ENTERPRISE).max_plugins is None

    def test_enterprise_is_unlimited(self):
        assert get_tier_config(Tier.ENTERPRISE).is_unlimited_plugins()

    def test_free_is_not_unlimited(self):
        assert not get_tier_config(Tier.FREE).is_unlimited_plugins()

    def test_free_has_plugin_install(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_PLUGIN_INSTALL)

    def test_free_lacks_alerts(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_ALERTS)

    def test_pro_has_alerts(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_ALERTS)

    def test_pro_has_analytics(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_ANALYTICS)

    def test_pro_lacks_enterprise_plugins(self):
        assert not get_tier_config(Tier.PRO).has_feature(FEATURE_ENTERPRISE_PLUGINS)

    def test_enterprise_has_custom_plugins(self):
        assert get_tier_config(Tier.ENTERPRISE).has_feature(FEATURE_CUSTOM_PLUGINS)

    def test_enterprise_has_white_label(self):
        assert get_tier_config(Tier.ENTERPRISE).has_feature(FEATURE_WHITE_LABEL)

    def test_enterprise_has_api_access(self):
        assert get_tier_config(Tier.ENTERPRISE).has_feature(FEATURE_API_ACCESS)

    def test_list_tiers_three(self):
        assert len(list_tiers()) == 3

    def test_upgrade_free_to_pro(self):
        assert get_upgrade_path(Tier.FREE).tier == Tier.PRO

    def test_upgrade_pro_to_enterprise(self):
        assert get_upgrade_path(Tier.PRO).tier == Tier.ENTERPRISE

    def test_upgrade_enterprise_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None


class TestAIMarketplace:
    def test_default_tier_free(self):
        m = AIMarketplace()
        assert m.tier == Tier.FREE

    def test_instantiate_free(self):
        m = AIMarketplace(Tier.FREE)
        assert m.tier == Tier.FREE

    def test_instantiate_pro(self):
        m = AIMarketplace(Tier.PRO)
        assert m.tier == Tier.PRO

    def test_instantiate_enterprise(self):
        m = AIMarketplace(Tier.ENTERPRISE)
        assert m.tier == Tier.ENTERPRISE

    def test_browse_plugins_all(self):
        m = AIMarketplace()
        plugins = m.browse_plugins()
        assert len(plugins) >= 12

    def test_browse_plugins_by_category(self):
        m = AIMarketplace()
        plugins = m.browse_plugins(category="ai")
        assert all(p["category"] == "ai" for p in plugins)

    def test_browse_plugins_finance_category(self):
        m = AIMarketplace()
        plugins = m.browse_plugins(category="finance")
        assert len(plugins) >= 1

    def test_browse_plugins_invalid_category(self):
        m = AIMarketplace()
        with pytest.raises(AIMarketplaceError):
            m.browse_plugins(category="invalid_cat")

    def test_install_plugin_free(self):
        m = AIMarketplace(Tier.FREE)
        r = m.install_plugin("ai_model_router")
        assert r["installed"] is True

    def test_install_plugin_pro(self):
        m = AIMarketplace(Tier.PRO)
        r = m.install_plugin("ai_model_router")
        assert r["plugin_id"] == "ai_model_router"

    def test_install_plugin_enterprise(self):
        m = AIMarketplace(Tier.ENTERPRISE)
        r = m.install_plugin("ai_model_router")
        assert r["installed"] is True

    def test_install_plugin_limit_reached_free(self):
        m = AIMarketplace(Tier.FREE)
        m.install_plugin("ai_model_router")
        m.install_plugin("coupon_stacker")
        m.install_plugin("deal_alert_pro")
        with pytest.raises(AIMarketplaceTierError):
            m.install_plugin("crypto_price_tracker")

    def test_install_plugin_duplicate_raises(self):
        m = AIMarketplace(Tier.PRO)
        m.install_plugin("ai_model_router")
        with pytest.raises(AIMarketplaceError):
            m.install_plugin("ai_model_router")

    def test_uninstall_plugin(self):
        m = AIMarketplace(Tier.PRO)
        m.install_plugin("ai_model_router")
        m.uninstall_plugin("ai_model_router")
        assert "ai_model_router" not in m._installed

    def test_uninstall_not_installed_raises(self):
        m = AIMarketplace(Tier.PRO)
        with pytest.raises(AIMarketplaceError):
            m.uninstall_plugin("ai_model_router")

    def test_get_installed_plugins_empty(self):
        m = AIMarketplace(Tier.PRO)
        assert m.get_installed_plugins() == []

    def test_get_installed_plugins_after_install(self):
        m = AIMarketplace(Tier.PRO)
        m.install_plugin("ai_model_router")
        installed = m.get_installed_plugins()
        assert len(installed) == 1

    def test_search_plugins_by_name(self):
        m = AIMarketplace()
        results = m.search_plugins("coupon")
        assert any("coupon" in r["name"].lower() for r in results)

    def test_search_plugins_by_feature(self):
        m = AIMarketplace()
        results = m.search_plugins("portfolio tracking")
        assert len(results) >= 1

    def test_subscribe_raises_on_free(self):
        m = AIMarketplace(Tier.FREE)
        with pytest.raises(AIMarketplaceTierError):
            m.subscribe("user1", "starter")

    def test_subscribe_works_on_pro(self):
        m = AIMarketplace(Tier.PRO)
        r = m.subscribe("user1", "starter")
        assert r["status"] == "active"

    def test_subscribe_growth_plan(self):
        m = AIMarketplace(Tier.PRO)
        r = m.subscribe("user1", "growth")
        assert r["plan"] == "growth"

    def test_subscribe_professional_plan(self):
        m = AIMarketplace(Tier.PRO)
        r = m.subscribe("user1", "professional")
        assert r["plan"] == "professional"

    def test_subscribe_enterprise_plan(self):
        m = AIMarketplace(Tier.ENTERPRISE)
        r = m.subscribe("user1", "enterprise")
        assert r["plan"] == "enterprise"

    def test_subscribe_invalid_plan(self):
        m = AIMarketplace(Tier.PRO)
        with pytest.raises(AIMarketplaceError):
            m.subscribe("user1", "invalid_plan")

    def test_get_skill_packs_free(self):
        m = AIMarketplace(Tier.FREE)
        packs = m.get_skill_packs()
        assert len(packs) >= 6

    def test_get_skill_packs_pro(self):
        m = AIMarketplace(Tier.PRO)
        packs = m.get_skill_packs()
        assert len(packs) >= 6

    def test_purchase_skill_pack_raises_on_free(self):
        m = AIMarketplace(Tier.FREE)
        with pytest.raises(AIMarketplaceTierError):
            m.purchase_skill_pack("ecommerce_pack")

    def test_purchase_skill_pack_pro(self):
        m = AIMarketplace(Tier.PRO)
        r = m.purchase_skill_pack("ecommerce_pack")
        assert r["pack_id"] == "ecommerce_pack"

    def test_dashboard_free(self):
        m = AIMarketplace(Tier.FREE)
        assert isinstance(m.dashboard(), str)

    def test_dashboard_pro(self):
        m = AIMarketplace(Tier.PRO)
        assert isinstance(m.dashboard(), str)

    def test_dashboard_enterprise(self):
        m = AIMarketplace(Tier.ENTERPRISE)
        assert isinstance(m.dashboard(), str)

    def test_dashboard_contains_tier(self):
        m = AIMarketplace(Tier.PRO)
        assert "Pro" in m.dashboard()


class TestPluginRegistry:
    def setup_method(self):
        self.registry = PluginRegistry()

    def test_twelve_plugins_loaded(self):
        assert len(self.registry.list_plugins()) == 12

    def test_get_plugin_ai_model_router(self):
        p = self.registry.get_plugin("ai_model_router")
        assert p.name == "AI Model Router"

    def test_get_plugin_coupon_stacker(self):
        p = self.registry.get_plugin("coupon_stacker")
        assert p.category == PluginCategory.SAVINGS

    def test_get_plugin_not_found(self):
        with pytest.raises(KeyError):
            self.registry.get_plugin("nonexistent")

    def test_list_plugins_by_ai_category(self):
        plugins = self.registry.list_plugins(PluginCategory.AI)
        assert all(p.category == PluginCategory.AI for p in plugins)

    def test_list_plugins_by_finance_category(self):
        plugins = self.registry.list_plugins(PluginCategory.FINANCE)
        assert len(plugins) == 2

    def test_list_plugins_by_integration_category(self):
        plugins = self.registry.list_plugins(PluginCategory.INTEGRATION)
        assert len(plugins) == 3

    def test_list_plugins_by_tools_category(self):
        plugins = self.registry.list_plugins(PluginCategory.TOOLS)
        assert len(plugins) == 3

    def test_search_plugins_by_name(self):
        results = self.registry.search_plugins("slack")
        assert len(results) == 1

    def test_search_plugins_by_feature(self):
        results = self.registry.search_plugins("OCR scanning")
        assert len(results) >= 1

    def test_get_top_rated(self):
        top = self.registry.get_top_rated(3)
        assert len(top) == 3

    def test_get_top_rated_first_is_best(self):
        top = self.registry.get_top_rated(12)
        assert top[0].rating >= top[-1].rating

    def test_register_plugin(self):
        p = Plugin("new_plugin", "New Plugin", PluginCategory.TOOLS, "v1.0.0",
                   "A new plugin", ["feature1"], 4.0, 100, "Author")
        self.registry.register_plugin(p)
        assert self.registry.get_plugin("new_plugin").name == "New Plugin"

    def test_all_plugin_categories(self):
        categories = {p.category for p in self.registry.list_plugins()}
        expected = {PluginCategory.AI, PluginCategory.SAVINGS, PluginCategory.FINANCE,
                    PluginCategory.ALERTS, PluginCategory.INTEGRATION, PluginCategory.TOOLS,
                    PluginCategory.MARKETING}
        assert expected.issubset(categories)


class TestPluginCategory:
    def test_ai_category(self):
        assert PluginCategory.AI.value == "ai"

    def test_savings_category(self):
        assert PluginCategory.SAVINGS.value == "savings"

    def test_finance_category(self):
        assert PluginCategory.FINANCE.value == "finance"

    def test_alerts_category(self):
        assert PluginCategory.ALERTS.value == "alerts"

    def test_integration_category(self):
        assert PluginCategory.INTEGRATION.value == "integration"

    def test_tools_category(self):
        assert PluginCategory.TOOLS.value == "tools"

    def test_marketing_category(self):
        assert PluginCategory.MARKETING.value == "marketing"


class TestSubscriptionManager:
    def setup_method(self):
        self.manager = SubscriptionManager()

    def test_list_plans_returns_four(self):
        assert len(self.manager.list_plans()) == 4

    def test_get_starter_plan(self):
        plan = self.manager.get_plan(SubscriptionPlan.STARTER)
        assert plan.price_usd_monthly == 9.0

    def test_get_growth_plan(self):
        plan = self.manager.get_plan(SubscriptionPlan.GROWTH)
        assert plan.price_usd_monthly == 29.0

    def test_get_professional_plan(self):
        plan = self.manager.get_plan(SubscriptionPlan.PROFESSIONAL)
        assert plan.price_usd_monthly == 79.0

    def test_get_enterprise_plan(self):
        plan = self.manager.get_plan(SubscriptionPlan.ENTERPRISE)
        assert plan.price_usd_monthly == 299.0

    def test_subscribe_active(self):
        r = self.manager.subscribe("user1", SubscriptionPlan.STARTER)
        assert r["status"] == "active"

    def test_subscribe_returns_plan(self):
        r = self.manager.subscribe("user1", SubscriptionPlan.GROWTH)
        assert r["plan"] == "growth"

    def test_get_subscription_active(self):
        self.manager.subscribe("user1", SubscriptionPlan.STARTER)
        s = self.manager.get_subscription("user1")
        assert s["status"] == "active"

    def test_get_subscription_not_found(self):
        s = self.manager.get_subscription("unknown")
        assert s["status"] == "none"

    def test_upgrade_plan(self):
        self.manager.subscribe("user1", SubscriptionPlan.STARTER)
        r = self.manager.upgrade_plan("user1", SubscriptionPlan.GROWTH)
        assert r["plan"] == "growth"

    def test_upgrade_plan_new_user(self):
        r = self.manager.upgrade_plan("newuser", SubscriptionPlan.PROFESSIONAL)
        assert r["plan"] == "professional"

    def test_cancel_subscription(self):
        self.manager.subscribe("user1", SubscriptionPlan.STARTER)
        self.manager.cancel_subscription("user1")
        s = self.manager.get_subscription("user1")
        assert s["status"] == "cancelled"

    def test_cancel_nonexistent_no_error(self):
        self.manager.cancel_subscription("nobody")


class TestSkillPackRegistry:
    def setup_method(self):
        self.registry = SkillPackRegistry()

    def test_six_packs_loaded(self):
        assert len(self.registry.list_packs()) == 6

    def test_get_ecommerce_pack(self):
        pack = self.registry.get_pack("ecommerce_pack")
        assert pack.name == "E-Commerce Pack"

    def test_get_pack_not_found(self):
        with pytest.raises(KeyError):
            self.registry.get_pack("nonexistent")

    def test_list_packs_by_industry(self):
        packs = self.registry.list_packs(industry="finance")
        assert len(packs) == 1
        assert packs[0].pack_id == "finance_pack"

    def test_list_packs_by_marketing_industry(self):
        packs = self.registry.list_packs(industry="marketing")
        assert len(packs) == 1

    def test_list_packs_by_integration_industry(self):
        packs = self.registry.list_packs(industry="integration")
        assert len(packs) == 1

    def test_ecommerce_pack_has_four_plugins(self):
        pack = self.registry.get_pack("ecommerce_pack")
        assert len(pack.plugins) == 4

    def test_get_pack_value(self):
        individual_prices = {
            "inventory_manager": 10.0,
            "deal_alert_pro": 10.0,
            "receipt_scanner_pro": 10.0,
            "coupon_stacker": 10.0,
        }
        val = self.registry.get_pack_value("ecommerce_pack", individual_prices)
        assert val == pytest.approx(40.0 - 19.0)

    def test_ai_performance_pack_exists(self):
        pack = self.registry.get_pack("ai_performance_pack")
        assert pack.industry == "ai"


class TestExceptionHierarchy:
    def test_tier_error_is_subclass_of_base(self):
        assert issubclass(AIMarketplaceTierError, AIMarketplaceError)

    def test_tier_error_is_exception(self):
        assert issubclass(AIMarketplaceTierError, Exception)

    def test_base_error_is_exception(self):
        assert issubclass(AIMarketplaceError, Exception)

    def test_raise_tier_error_caught_as_base(self):
        with pytest.raises(AIMarketplaceError):
            raise AIMarketplaceTierError("test")
