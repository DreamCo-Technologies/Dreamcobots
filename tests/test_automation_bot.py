"""
Tests for bots/automation_bot/tiers.py and bots/automation_bot/automation_bot.py
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
BOT_DIR = os.path.join(REPO_ROOT, 'bots', 'automation_bot')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.automation_bot.automation_bot import AutomationBot, AutomationBotTierError, AutomationBotRequestLimitError


# -----------------------------------------------------------------------
# Tier info tests
# -----------------------------------------------------------------------

class TestAutomationBotTierInfo:
    def _load_tiers(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_auto_tiers", os.path.join(BOT_DIR, "tiers.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_tier_info_keys(self):
        mod = self._load_tiers()
        info = mod.get_automation_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "automation_features", "task_limit", "support_level"):
            assert key in info

    def test_free_price_zero(self):
        mod = self._load_tiers()
        info = mod.get_automation_tier_info(Tier.FREE)
        assert info["price_usd_monthly"] == 0.0

    def test_enterprise_unlimited_requests(self):
        mod = self._load_tiers()
        info = mod.get_automation_tier_info(Tier.ENTERPRISE)
        assert info["requests_per_month"] is None

    def test_enterprise_unlimited_tasks(self):
        mod = self._load_tiers()
        info = mod.get_automation_tier_info(Tier.ENTERPRISE)
        assert info["task_limit"] is None

    def test_free_fewer_tasks_than_pro(self):
        mod = self._load_tiers()
        free_limit = mod.TASK_LIMITS[Tier.FREE.value]
        pro_limit = mod.TASK_LIMITS[Tier.PRO.value]
        assert free_limit < pro_limit

    def test_all_tiers_have_features(self):
        mod = self._load_tiers()
        for tier in Tier:
            info = mod.get_automation_tier_info(tier)
            assert len(info["automation_features"]) > 0


# -----------------------------------------------------------------------
# AutomationBot tests
# -----------------------------------------------------------------------

class TestAutomationBot:
    def test_default_tier_free(self):
        bot = AutomationBot()
        assert bot.tier == Tier.FREE

    def test_create_task_returns_dict(self):
        bot = AutomationBot()
        result = bot.create_task("report", "daily@08:00", {"type": "send_email"})
        assert isinstance(result, dict)

    def test_create_task_keys(self):
        bot = AutomationBot()
        result = bot.create_task("job1", "daily@09:00", {"type": "notify"})
        for key in ("task", "tier", "requests_used", "requests_remaining"):
            assert key in result

    def test_create_task_increments_request_count(self):
        bot = AutomationBot()
        bot.create_task("t1", "daily@08:00", {})
        bot.create_task("t2", "daily@09:00", {})
        assert bot._request_count == 2

    def test_task_appears_in_list(self):
        bot = AutomationBot()
        bot.create_task("my_task", "daily@08:00", {})
        names = [t["name"] for t in bot.list_tasks()]
        assert "my_task" in names

    def test_free_tier_task_limit(self):
        bot = AutomationBot(tier=Tier.FREE)
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_auto_t", os.path.join(BOT_DIR, "tiers.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        limit = mod.TASK_LIMITS[Tier.FREE.value]
        for i in range(limit):
            bot.create_task(f"task_{i}", "daily@08:00", {})
        with pytest.raises(AutomationBotTierError):
            bot.create_task("one_too_many", "daily@10:00", {})

    def test_duplicate_task_name_raises(self):
        bot = AutomationBot()
        bot.create_task("dup", "daily@08:00", {})
        with pytest.raises(AutomationBotTierError):
            bot.create_task("dup", "daily@09:00", {})

    def test_webhook_trigger_free_raises(self):
        bot = AutomationBot(tier=Tier.FREE)
        with pytest.raises(AutomationBotTierError):
            bot.create_task("hook", "webhook://my-hook", {})

    def test_webhook_trigger_pro_ok(self):
        bot = AutomationBot(tier=Tier.PRO)
        result = bot.create_task("hook", "webhook://my-hook", {})
        assert result["task"]["trigger"] == "webhook://my-hook"

    def test_run_task_returns_dict(self):
        bot = AutomationBot()
        bot.create_task("runner", "daily@08:00", {})
        result = bot.run_task("runner")
        assert isinstance(result, dict)
        assert result["task_name"] == "runner"

    def test_run_task_increments_run_count(self):
        bot = AutomationBot()
        bot.create_task("r", "daily@08:00", {})
        bot.run_task("r")
        bot.run_task("r")
        assert bot._tasks["r"]["runs"] == 2

    def test_run_nonexistent_task_raises(self):
        bot = AutomationBot()
        with pytest.raises(AutomationBotTierError):
            bot.run_task("ghost")

    def test_delete_task(self):
        bot = AutomationBot()
        bot.create_task("del_me", "daily@08:00", {})
        bot.delete_task("del_me")
        names = [t["name"] for t in bot.list_tasks()]
        assert "del_me" not in names

    def test_delete_nonexistent_task_raises(self):
        bot = AutomationBot()
        with pytest.raises(AutomationBotTierError):
            bot.delete_task("no_such")

    def test_request_limit_raises(self):
        bot = AutomationBot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        with pytest.raises(AutomationBotRequestLimitError):
            bot.create_task("x", "daily@08:00", {})

    def test_enterprise_no_request_limit(self):
        bot = AutomationBot(tier=Tier.ENTERPRISE)
        bot._request_count = 999_999
        result = bot.create_task("infinite", "daily@08:00", {})
        assert result["requests_remaining"] == "unlimited"

    def test_describe_tier_returns_string(self):
        bot = AutomationBot()
        output = bot.describe_tier()
        assert isinstance(output, str)
        assert "Free" in output

    def test_show_upgrade_path_from_free(self):
        bot = AutomationBot()
        output = bot.show_upgrade_path()
        assert "Pro" in output

    def test_show_upgrade_path_enterprise(self):
        bot = AutomationBot(tier=Tier.ENTERPRISE)
        output = bot.show_upgrade_path()
        assert "top-tier" in output
