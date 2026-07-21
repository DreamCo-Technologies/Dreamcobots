"""Tests for bots/software_bot/tiers.py and bots/software_bot/software_bot.py"""
import sys, os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.software_bot.software_bot import SoftwareBot, SoftwareBotTierError


class TestSoftwareBotInstantiation:
    def test_default_tier_is_free(self):
        bot = SoftwareBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = SoftwareBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = SoftwareBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = SoftwareBot()
        assert bot.config is not None


class TestListAppCategories:
    def test_returns_list(self):
        bot = SoftwareBot(tier=Tier.FREE)
        result = bot.list_app_categories()
        assert isinstance(result, list)

    def test_free_has_3_categories(self):
        bot = SoftwareBot(tier=Tier.FREE)
        result = bot.list_app_categories()
        assert len(result) == 3

    def test_pro_has_10_categories(self):
        bot = SoftwareBot(tier=Tier.PRO)
        result = bot.list_app_categories()
        assert len(result) == 10

    def test_enterprise_has_more_than_10(self):
        bot = SoftwareBot(tier=Tier.ENTERPRISE)
        result = bot.list_app_categories()
        assert len(result) > 10


class TestGenerateAppIdea:
    def test_returns_dict(self):
        bot = SoftwareBot(tier=Tier.FREE)
        result = bot.generate_app_idea("productivity")
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        bot = SoftwareBot(tier=Tier.FREE)
        result = bot.generate_app_idea("productivity")
        for key in ("name", "description", "target_market", "monetization"):
            assert key in result

    def test_free_cannot_access_restricted_category(self):
        bot = SoftwareBot(tier=Tier.FREE)
        with pytest.raises(SoftwareBotTierError):
            bot.generate_app_idea("health")

    def test_pro_can_access_10_categories(self):
        bot = SoftwareBot(tier=Tier.PRO)
        result = bot.generate_app_idea("health")
        assert isinstance(result, dict)

    def test_enterprise_has_market_analysis(self):
        bot = SoftwareBot(tier=Tier.ENTERPRISE)
        result = bot.generate_app_idea("productivity")
        assert "market_analysis" in result


class TestEstimateRevenue:
    def test_returns_dict(self):
        bot = SoftwareBot(tier=Tier.FREE)
        result = bot.estimate_revenue({"name": "TestApp", "monetization": "Subscription"})
        assert isinstance(result, dict)

    def test_has_projections(self):
        bot = SoftwareBot(tier=Tier.FREE)
        result = bot.estimate_revenue({"name": "TestApp"})
        assert "daily_revenue_usd" in result
        assert "monthly_revenue_usd" in result
        assert "annual_revenue_usd" in result

    def test_enterprise_higher_revenue_than_free(self):
        free_bot = SoftwareBot(tier=Tier.FREE)
        ent_bot = SoftwareBot(tier=Tier.ENTERPRISE)
        free_rev = free_bot.estimate_revenue({"name": "App"})
        ent_rev = ent_bot.estimate_revenue({"name": "App"})
        assert ent_rev["daily_revenue_usd"]["high"] >= free_rev["daily_revenue_usd"]["high"]


class TestCreateAppTemplate:
    def test_returns_dict(self):
        bot = SoftwareBot(tier=Tier.FREE)
        idea = {"name": "TestApp", "category": "productivity", "monetization": "Subscription"}
        result = bot.create_app_template(idea)
        assert isinstance(result, dict)

    def test_has_tech_stack(self):
        bot = SoftwareBot(tier=Tier.FREE)
        idea = {"name": "TestApp", "category": "productivity"}
        result = bot.create_app_template(idea)
        assert "tech_stack" in result
        assert "core_features" in result

    def test_enterprise_has_ci_cd(self):
        bot = SoftwareBot(tier=Tier.ENTERPRISE)
        idea = {"name": "TestApp", "category": "productivity"}
        result = bot.create_app_template(idea)
        assert "ci_cd_pipeline" in result
