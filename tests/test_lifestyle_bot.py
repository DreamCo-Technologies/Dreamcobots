"""
Tests for bots/lifestyle_bot/tiers.py and bots/lifestyle_bot/lifestyle_bot.py
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
BOT_DIR = os.path.join(REPO_ROOT, 'bots', 'lifestyle_bot')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.lifestyle_bot.lifestyle_bot import LifestyleBot, LifestyleBotTierError, LifestyleBotRequestLimitError


# -----------------------------------------------------------------------
# Tier info tests
# -----------------------------------------------------------------------

class TestLifestyleBotTierInfo:
    def _load_tiers(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_life_tiers", os.path.join(BOT_DIR, "tiers.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_tier_info_keys(self):
        mod = self._load_tiers()
        info = mod.get_lifestyle_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "lifestyle_features", "habit_limit", "support_level"):
            assert key in info

    def test_free_price_zero(self):
        mod = self._load_tiers()
        assert mod.get_lifestyle_tier_info(Tier.FREE)["price_usd_monthly"] == 0.0

    def test_enterprise_unlimited(self):
        mod = self._load_tiers()
        assert mod.get_lifestyle_tier_info(Tier.ENTERPRISE)["requests_per_month"] is None

    def test_free_fewer_habits_than_pro(self):
        mod = self._load_tiers()
        free_lim = mod.HABIT_LIMITS[Tier.FREE.value]
        pro_lim = mod.HABIT_LIMITS[Tier.PRO.value]
        # PRO has None (unlimited) or higher limit
        assert free_lim is not None
        assert pro_lim is None or pro_lim > free_lim


# -----------------------------------------------------------------------
# LifestyleBot tests
# -----------------------------------------------------------------------

class TestLifestyleBot:
    def test_default_tier_free(self):
        bot = LifestyleBot()
        assert bot.tier == Tier.FREE

    def test_track_habit_returns_dict(self):
        bot = LifestyleBot()
        result = bot.track_habit("exercise", True)
        assert isinstance(result, dict)

    def test_track_habit_keys(self):
        bot = LifestyleBot()
        result = bot.track_habit("meditation", False)
        for key in ("habit_name", "completed", "tier", "requests_used", "requests_remaining"):
            assert key in result

    def test_track_habit_increments_count(self):
        bot = LifestyleBot()
        bot.track_habit("run", True)
        bot.track_habit("read", False)
        assert bot._request_count == 2

    def test_free_habit_limit(self):
        bot = LifestyleBot(tier=Tier.FREE)
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_life_t", os.path.join(BOT_DIR, "tiers.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        limit = mod.HABIT_LIMITS[Tier.FREE.value]
        # Track distinct habits up to the limit
        for i in range(limit):
            bot.track_habit(f"habit_{i}", True)
        with pytest.raises(LifestyleBotTierError):
            bot.track_habit("overflow_habit", True)

    def test_set_goal_returns_dict(self):
        bot = LifestyleBot()
        result = bot.set_goal("Run 5K", "2025-06-01")
        assert isinstance(result, dict)
        assert "goal" in result

    def test_set_goal_keys(self):
        bot = LifestyleBot()
        result = bot.set_goal("Read 12 books", "2025-12-31")
        for key in ("goal", "tier", "requests_used", "requests_remaining"):
            assert key in result
        assert "target_date" in result["goal"]

    def test_get_habits_summary_returns_dict(self):
        bot = LifestyleBot()
        bot.track_habit("run", True)
        bot.track_habit("run", False)
        result = bot.get_habits_summary()
        assert isinstance(result, dict)
        assert "habits" in result

    def test_log_mood_pro_only(self):
        bot = LifestyleBot(tier=Tier.FREE)
        with pytest.raises(LifestyleBotTierError):
            bot.log_mood("happy", "Great day")

    def test_log_mood_pro_ok(self):
        bot = LifestyleBot(tier=Tier.PRO)
        result = bot.log_mood("happy", "Great day")
        assert isinstance(result, dict)
        assert "mood_entry" in result or "mood" in result

    def test_request_limit_raises(self):
        bot = LifestyleBot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        with pytest.raises(LifestyleBotRequestLimitError):
            bot.track_habit("run", True)

    def test_enterprise_no_request_limit(self):
        bot = LifestyleBot(tier=Tier.ENTERPRISE)
        bot._request_count = 999_999
        result = bot.track_habit("run", True)
        assert result["requests_remaining"] == "unlimited"

    def test_describe_tier_returns_string(self):
        bot = LifestyleBot()
        output = bot.describe_tier()
        assert isinstance(output, str)
        assert "Free" in output

    def test_show_upgrade_path_from_free(self):
        bot = LifestyleBot()
        output = bot.show_upgrade_path()
        assert "Pro" in output

    def test_show_upgrade_path_enterprise(self):
        bot = LifestyleBot(tier=Tier.ENTERPRISE)
        output = bot.show_upgrade_path()
        assert "top-tier" in output
