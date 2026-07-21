"""Tests for bots/app_builder_bot/tiers.py and bots/app_builder_bot/app_builder_bot.py"""
import sys, os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.app_builder_bot.app_builder_bot import AppBuilderBot, AppBuilderBotTierError


class TestAppBuilderBotInstantiation:
    def test_default_tier_is_free(self):
        bot = AppBuilderBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = AppBuilderBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = AppBuilderBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = AppBuilderBot()
        assert bot.config is not None


class TestCreateProject:
    def test_returns_dict_with_id(self):
        bot = AppBuilderBot(tier=Tier.FREE)
        project = bot.create_project("TestApp", "web")
        assert isinstance(project, dict)
        assert "id" in project
        assert project["id"] is not None

    def test_project_has_required_keys(self):
        bot = AppBuilderBot(tier=Tier.FREE)
        project = bot.create_project("TestApp", "web")
        for key in ("id", "name", "app_type", "features", "status", "created_at"):
            assert key in project

    def test_project_name_matches(self):
        bot = AppBuilderBot(tier=Tier.FREE)
        project = bot.create_project("MyAwesomeApp", "api")
        assert project["name"] == "MyAwesomeApp"

    def test_free_project_limit_enforced(self):
        bot = AppBuilderBot(tier=Tier.FREE)
        bot.create_project("App1", "web")
        with pytest.raises(AppBuilderBotTierError):
            bot.create_project("App2", "mobile")

    def test_pro_allows_10_projects(self):
        bot = AppBuilderBot(tier=Tier.PRO)
        for i in range(10):
            project = bot.create_project(f"App{i}", "web")
            assert "id" in project

    def test_pro_limit_enforced_at_11(self):
        bot = AppBuilderBot(tier=Tier.PRO)
        for i in range(10):
            bot.create_project(f"App{i}", "web")
        with pytest.raises(AppBuilderBotTierError):
            bot.create_project("App11", "web")

    def test_enterprise_unlimited_projects(self):
        bot = AppBuilderBot(tier=Tier.ENTERPRISE)
        for i in range(15):
            project = bot.create_project(f"App{i}", "web")
            assert "id" in project


class TestAddFeature:
    def test_add_feature_returns_project(self):
        bot = AppBuilderBot(tier=Tier.FREE)
        project = bot.create_project("TestApp", "web")
        result = bot.add_feature(project["id"], "user authentication")
        assert isinstance(result, dict)

    def test_feature_appears_in_project(self):
        bot = AppBuilderBot(tier=Tier.FREE)
        project = bot.create_project("TestApp", "web")
        bot.add_feature(project["id"], "user authentication")
        assert "user authentication" in project["features"]

    def test_duplicate_feature_not_added(self):
        bot = AppBuilderBot(tier=Tier.FREE)
        project = bot.create_project("TestApp", "web")
        bot.add_feature(project["id"], "auth")
        bot.add_feature(project["id"], "auth")
        assert project["features"].count("auth") == 1


class TestGenerateCodeScaffold:
    def test_returns_dict(self):
        bot = AppBuilderBot(tier=Tier.FREE)
        project = bot.create_project("TestApp", "web")
        result = bot.generate_code_scaffold(project["id"])
        assert isinstance(result, dict)

    def test_has_scaffold_structure(self):
        bot = AppBuilderBot(tier=Tier.FREE)
        project = bot.create_project("TestApp", "web")
        result = bot.generate_code_scaffold(project["id"])
        assert "scaffold" in result
        assert "directories" in result["scaffold"]
        assert "files" in result["scaffold"]

    def test_enterprise_has_ci_cd(self):
        bot = AppBuilderBot(tier=Tier.ENTERPRISE)
        project = bot.create_project("TestApp", "api")
        result = bot.generate_code_scaffold(project["id"])
        assert "ci_cd_config" in result


class TestEstimateDevelopmentTime:
    def test_returns_dict(self):
        bot = AppBuilderBot(tier=Tier.FREE)
        project = bot.create_project("TestApp", "web")
        result = bot.estimate_development_time(project["id"])
        assert isinstance(result, dict)

    def test_has_time_estimates(self):
        bot = AppBuilderBot(tier=Tier.FREE)
        project = bot.create_project("TestApp", "web")
        result = bot.estimate_development_time(project["id"])
        for key in ("total_hours", "estimated_days", "estimated_weeks"):
            assert key in result

    def test_more_features_means_more_time(self):
        bot = AppBuilderBot(tier=Tier.PRO)
        p1 = bot.create_project("App1", "web")
        p2 = bot.create_project("App2", "web")
        for f in ["auth", "payments", "analytics", "dashboard", "notifications"]:
            bot.add_feature(p2["id"], f)
        t1 = bot.estimate_development_time(p1["id"])
        t2 = bot.estimate_development_time(p2["id"])
        assert t2["total_hours"] > t1["total_hours"]
