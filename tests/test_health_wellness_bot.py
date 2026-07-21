"""
Tests for bots/health_wellness_bot/tiers.py and bots/health_wellness_bot/health_wellness_bot.py
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
BOT_DIR = os.path.join(REPO_ROOT, 'bots', 'health_wellness_bot')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.health_wellness_bot.health_wellness_bot import (
    HealthWellnessBot,
    HealthWellnessBotTierError,
    HealthWellnessBotRequestLimitError,
)


# -----------------------------------------------------------------------
# Tier info tests
# -----------------------------------------------------------------------

class TestHealthWellnessBotTierInfo:
    def _load_tiers(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_health_tiers", os.path.join(BOT_DIR, "tiers.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_tier_info_keys(self):
        mod = self._load_tiers()
        info = mod.get_health_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "health_features", "support_level"):
            assert key in info

    def test_free_price_zero(self):
        mod = self._load_tiers()
        assert mod.get_health_tier_info(Tier.FREE)["price_usd_monthly"] == 0.0

    def test_enterprise_unlimited(self):
        mod = self._load_tiers()
        assert mod.get_health_tier_info(Tier.ENTERPRISE)["requests_per_month"] is None

    def test_all_tiers_have_features(self):
        mod = self._load_tiers()
        for tier in Tier:
            assert len(mod.get_health_tier_info(tier)["health_features"]) > 0


# -----------------------------------------------------------------------
# HealthWellnessBot tests
# -----------------------------------------------------------------------

class TestHealthWellnessBot:
    def test_default_tier_free(self):
        bot = HealthWellnessBot()
        assert bot.tier == Tier.FREE

    def test_calculate_bmi_returns_dict(self):
        bot = HealthWellnessBot()
        result = bot.calculate_bmi(70.0, 1.75)
        assert isinstance(result, dict)

    def test_calculate_bmi_keys(self):
        bot = HealthWellnessBot()
        result = bot.calculate_bmi(70.0, 1.75)
        for key in ("bmi", "category", "tier", "requests_used", "requests_remaining"):
            assert key in result

    def test_bmi_normal_range(self):
        bot = HealthWellnessBot()
        result = bot.calculate_bmi(70.0, 1.75)  # BMI ~22.9
        assert 18.0 <= result["bmi"] <= 30.0

    def test_bmi_category_normal(self):
        bot = HealthWellnessBot()
        result = bot.calculate_bmi(70.0, 1.75)
        assert result["category"] in ("Normal weight", "Normal", "Healthy")

    def test_bmi_underweight(self):
        bot = HealthWellnessBot()
        result = bot.calculate_bmi(40.0, 1.75)  # very low BMI
        assert "Underweight" in result["category"]

    def test_log_workout_returns_dict(self):
        bot = HealthWellnessBot()
        result = bot.log_workout("running", 30)
        assert isinstance(result, dict)

    def test_log_workout_keys(self):
        bot = HealthWellnessBot()
        result = bot.log_workout("cycling", 45, calories_burned=300)
        for key in ("workout", "tier", "requests_used", "requests_remaining"):
            assert key in result

    def test_log_workout_increments_count(self):
        bot = HealthWellnessBot()
        bot.log_workout("run", 20)
        bot.log_workout("swim", 30)
        assert bot._request_count == 2

    def test_log_nutrition_free_no_macros(self):
        bot = HealthWellnessBot(tier=Tier.FREE)
        result = bot.log_nutrition("Lunch", 600)
        assert isinstance(result, dict)

    def test_log_nutrition_macros_pro_only(self):
        bot = HealthWellnessBot(tier=Tier.FREE)
        with pytest.raises(HealthWellnessBotTierError):
            bot.log_nutrition("Lunch", 600, macros={"protein": 30, "carbs": 60, "fat": 20})

    def test_log_nutrition_macros_pro_ok(self):
        bot = HealthWellnessBot(tier=Tier.PRO)
        result = bot.log_nutrition("Lunch", 600, macros={"protein": 30, "carbs": 60, "fat": 20})
        assert isinstance(result, dict)
        entry = result.get("nutrition_entry") or result.get("nutrition")
        assert entry is not None
        assert "macros" in entry

    def test_get_health_summary_returns_dict(self):
        bot = HealthWellnessBot()
        bot.log_workout("run", 30)
        bot.log_nutrition("Breakfast", 400)
        result = bot.get_health_summary()
        assert isinstance(result, dict)
        assert "total_workouts" in result

    def test_request_limit_raises(self):
        bot = HealthWellnessBot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        with pytest.raises(HealthWellnessBotRequestLimitError):
            bot.calculate_bmi(70.0, 1.75)

    def test_enterprise_no_request_limit(self):
        bot = HealthWellnessBot(tier=Tier.ENTERPRISE)
        bot._request_count = 999_999
        result = bot.calculate_bmi(70.0, 1.75)
        assert result["requests_remaining"] == "unlimited"

    def test_describe_tier_returns_string(self):
        bot = HealthWellnessBot()
        output = bot.describe_tier()
        assert isinstance(output, str)
        assert "Free" in output

    def test_show_upgrade_path_from_free(self):
        bot = HealthWellnessBot()
        output = bot.show_upgrade_path()
        assert "Pro" in output

    def test_show_upgrade_path_enterprise(self):
        bot = HealthWellnessBot(tier=Tier.ENTERPRISE)
        output = bot.show_upgrade_path()
        assert "top-tier" in output
