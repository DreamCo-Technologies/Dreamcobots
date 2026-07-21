"""Tests for App_bots/feature_1.py, feature_2.py, feature_3.py"""
from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from App_bots.feature_1 import UserOnboardingBot, EXAMPLES as AB1_EXAMPLES
from App_bots.feature_2 import UserSupportBot, EXAMPLES as AB2_EXAMPLES
from App_bots.feature_3 import FeatureUpdateBot, EXAMPLES as AB3_EXAMPLES


# ===========================================================================
# Feature 1: UserOnboardingBot
# ===========================================================================

class TestUserOnboardingBotInstantiation:
    def test_default_tier_is_free(self):
        bot = UserOnboardingBot()
        assert bot.tier == "FREE"

    def test_pro_tier(self):
        bot = UserOnboardingBot(tier="PRO")
        assert bot.tier == "PRO"

    def test_enterprise_tier(self):
        bot = UserOnboardingBot(tier="ENTERPRISE")
        assert bot.tier == "ENTERPRISE"

    def test_invalid_tier_raises_value_error(self):
        with pytest.raises(ValueError):
            UserOnboardingBot(tier="TRIAL")

    def test_has_30_examples(self):
        assert len(AB1_EXAMPLES) == 30

    def test_examples_have_required_keys(self):
        required = {"id", "step", "category", "user_type", "required"}
        for ex in AB1_EXAMPLES:
            assert required.issubset(ex.keys()), f"Missing keys in example: {ex}"


class TestUserOnboardingBotMethods:
    def test_get_onboarding_checklist_returns_list(self):
        bot = UserOnboardingBot(tier="FREE")
        checklist = bot.get_onboarding_checklist()
        assert isinstance(checklist, list)

    def test_get_required_steps_returns_list(self):
        bot = UserOnboardingBot(tier="FREE")
        steps = bot.get_required_steps()
        assert isinstance(steps, list)
        for s in steps:
            assert s["required"] is True

    def test_complete_step_returns_dict(self):
        bot = UserOnboardingBot(tier="PRO")
        step_id = AB1_EXAMPLES[0]["id"]
        result = bot.complete_step(step_id)
        assert isinstance(result, dict)

    def test_get_progress_returns_dict(self):
        bot = UserOnboardingBot(tier="PRO")
        bot.complete_step(AB1_EXAMPLES[0]["id"])
        progress = bot.get_progress()
        assert isinstance(progress, dict)
        assert "completed" in progress or "total" in progress or len(progress) > 0

    def test_get_steps_by_category_returns_list(self):
        bot = UserOnboardingBot(tier="PRO")
        first_category = AB1_EXAMPLES[0]["category"]
        steps = bot.get_steps_by_category(first_category)
        assert isinstance(steps, list)
        for s in steps:
            assert s["category"] == first_category

    def test_get_low_completion_steps_returns_list(self):
        bot = UserOnboardingBot(tier="PRO")
        low = bot.get_low_completion_steps(threshold_pct=50.0)
        assert isinstance(low, list)

    def test_get_personalized_path_requires_pro(self):
        bot = UserOnboardingBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.get_personalized_path("freelancer", ["earn_money"])

    def test_get_personalized_path_pro_returns_list(self):
        bot = UserOnboardingBot(tier="PRO")
        first_user_type = AB1_EXAMPLES[0]["user_type"]
        path = bot.get_personalized_path(first_user_type, ["earn_money"])
        assert isinstance(path, list)

    def test_get_onboarding_analytics_returns_dict(self):
        bot = UserOnboardingBot(tier="PRO")
        analytics = bot.get_onboarding_analytics()
        assert isinstance(analytics, dict)

    def test_free_tier_limits_steps(self):
        bot = UserOnboardingBot(tier="FREE")
        steps = bot._available_steps()
        assert len(steps) <= 10

    def test_describe_tier_returns_string(self):
        bot = UserOnboardingBot(tier="FREE")
        desc = bot.describe_tier()
        assert isinstance(desc, str)

    def test_run_returns_dict(self):
        bot = UserOnboardingBot(tier="FREE")
        result = bot.run()
        assert isinstance(result, dict)
        assert "pipeline_complete" in result


# ===========================================================================
# Feature 2: UserSupportBot
# ===========================================================================

class TestUserSupportBotInstantiation:
    def test_default_tier_is_free(self):
        bot = UserSupportBot()
        assert bot.tier == "FREE"

    def test_pro_tier(self):
        bot = UserSupportBot(tier="PRO")
        assert bot.tier == "PRO"

    def test_enterprise_tier(self):
        bot = UserSupportBot(tier="ENTERPRISE")
        assert bot.tier == "ENTERPRISE"

    def test_invalid_tier_raises_value_error(self):
        with pytest.raises(ValueError):
            UserSupportBot(tier="STUDENT")

    def test_has_30_examples(self):
        assert len(AB2_EXAMPLES) == 30

    def test_examples_have_required_keys(self):
        required = {"id", "question", "answer", "category"}
        for ex in AB2_EXAMPLES:
            assert required.issubset(ex.keys()), f"Missing keys in example: {ex}"


class TestUserSupportBotMethods:
    def test_search_faq_returns_list(self):
        bot = UserSupportBot(tier="FREE")
        results = bot.search_faq("billing")
        assert isinstance(results, list)

    def test_get_answer_returns_dict(self):
        bot = UserSupportBot(tier="PRO")
        result = bot.get_answer(AB2_EXAMPLES[0]["id"])
        assert isinstance(result, dict)

    def test_get_answer_invalid_id_raises(self):
        bot = UserSupportBot(tier="PRO")
        with pytest.raises((ValueError, KeyError)):
            bot.get_answer(9999)

    def test_free_tier_limits_queries(self):
        bot = UserSupportBot(tier="FREE")
        for _ in range(10):
            bot.search_faq("test")
        with pytest.raises(PermissionError):
            bot.search_faq("overflow")

    def test_create_ticket_requires_pro(self):
        bot = UserSupportBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.create_ticket("user@test.com", "Issue", "Description")

    def test_create_ticket_pro_returns_dict(self):
        bot = UserSupportBot(tier="PRO")
        result = bot.create_ticket("user@test.com", "Issue", "Description")
        assert isinstance(result, dict)

    def test_get_questions_by_category_returns_list(self):
        bot = UserSupportBot(tier="PRO")
        first_cat = AB2_EXAMPLES[0]["category"]
        results = bot.get_questions_by_category(first_cat)
        assert isinstance(results, list)
        for r in results:
            assert r["category"] == first_cat

    def test_get_escalation_required_questions_returns_list(self):
        bot = UserSupportBot(tier="PRO")
        questions = bot.get_escalation_required_questions()
        assert isinstance(questions, list)

    def test_get_top_questions_returns_list(self):
        bot = UserSupportBot(tier="PRO")
        top = bot.get_top_questions(5)
        assert isinstance(top, list)
        assert len(top) <= 5

    def test_get_ai_answer_requires_pro(self):
        bot = UserSupportBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.get_ai_answer("How do I cancel?")

    def test_get_ai_answer_pro_returns_dict(self):
        bot = UserSupportBot(tier="PRO")
        result = bot.get_ai_answer("How do I cancel?")
        assert isinstance(result, dict)

    def test_get_support_stats_returns_dict(self):
        bot = UserSupportBot(tier="PRO")
        stats = bot.get_support_stats()
        assert isinstance(stats, dict)

    def test_describe_tier_returns_string(self):
        bot = UserSupportBot(tier="FREE")
        desc = bot.describe_tier()
        assert isinstance(desc, str)

    def test_run_returns_dict(self):
        bot = UserSupportBot(tier="FREE")
        result = bot.run()
        assert isinstance(result, dict)
        assert "pipeline_complete" in result


# ===========================================================================
# Feature 3: FeatureUpdateBot
# ===========================================================================

class TestFeatureUpdateBotInstantiation:
    def test_default_tier_is_free(self):
        bot = FeatureUpdateBot()
        assert bot.tier == "FREE"

    def test_pro_tier(self):
        bot = FeatureUpdateBot(tier="PRO")
        assert bot.tier == "PRO"

    def test_enterprise_tier(self):
        bot = FeatureUpdateBot(tier="ENTERPRISE")
        assert bot.tier == "ENTERPRISE"

    def test_invalid_tier_raises_value_error(self):
        with pytest.raises(ValueError):
            FeatureUpdateBot(tier="NANO")

    def test_has_30_examples(self):
        assert len(AB3_EXAMPLES) == 30

    def test_examples_have_required_keys(self):
        required = {"id", "version", "title", "type", "tier_required"}
        for ex in AB3_EXAMPLES:
            assert required.issubset(ex.keys()), f"Missing keys in example: {ex}"


class TestFeatureUpdateBotMethods:
    def test_get_latest_updates_returns_list(self):
        bot = FeatureUpdateBot(tier="FREE")
        updates = bot.get_latest_updates(5)
        assert isinstance(updates, list)
        assert len(updates) <= 5

    def test_get_updates_by_type_returns_list(self):
        bot = FeatureUpdateBot(tier="PRO")
        first_type = AB3_EXAMPLES[0]["type"]
        updates = bot.get_updates_by_type(first_type)
        assert isinstance(updates, list)
        for u in updates:
            assert u["type"] == first_type

    def test_get_updates_for_tier_returns_list(self):
        bot = FeatureUpdateBot(tier="PRO")
        updates = bot.get_updates_for_tier("FREE")
        assert isinstance(updates, list)

    def test_get_high_engagement_updates_returns_list(self):
        bot = FeatureUpdateBot(tier="PRO")
        updates = bot.get_high_engagement_updates(min_action_rate=40.0)
        assert isinstance(updates, list)
        for u in updates:
            assert u["action_rate"] >= 40.0

    def test_send_notification_requires_pro(self):
        bot = FeatureUpdateBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.send_notification(1, "user@test.com")

    def test_send_notification_pro_returns_dict(self):
        bot = FeatureUpdateBot(tier="PRO")
        result = bot.send_notification(1, "user@test.com")
        assert isinstance(result, dict)

    def test_get_changelog_returns_list(self):
        bot = FeatureUpdateBot(tier="FREE")
        changelog = bot.get_changelog()
        assert isinstance(changelog, list)

    def test_get_changelog_by_version_returns_list(self):
        bot = FeatureUpdateBot(tier="PRO")
        version = AB3_EXAMPLES[0]["version"]
        changelog = bot.get_changelog(version=version)
        assert isinstance(changelog, list)

    def test_get_update_analytics_returns_dict(self):
        bot = FeatureUpdateBot(tier="PRO")
        analytics = bot.get_update_analytics()
        assert isinstance(analytics, dict)

    def test_free_tier_limits_updates(self):
        bot = FeatureUpdateBot(tier="FREE")
        updates = bot._available_updates()
        assert len(updates) <= 10

    def test_describe_tier_returns_string(self):
        bot = FeatureUpdateBot(tier="FREE")
        desc = bot.describe_tier()
        assert isinstance(desc, str)

    def test_run_returns_dict(self):
        bot = FeatureUpdateBot(tier="FREE")
        result = bot.run()
        assert isinstance(result, dict)
        assert "pipeline_complete" in result
