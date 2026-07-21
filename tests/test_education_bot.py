"""
Tests for bots/education_bot/tiers.py and bots/education_bot/education_bot.py
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
BOT_DIR = os.path.join(REPO_ROOT, 'bots', 'education_bot')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.education_bot.education_bot import EducationBot, EducationBotTierError, EducationBotRequestLimitError


# -----------------------------------------------------------------------
# Tier info tests
# -----------------------------------------------------------------------

class TestEducationBotTierInfo:
    def _load_tiers(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_edu_tiers", os.path.join(BOT_DIR, "tiers.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_tier_info_keys(self):
        mod = self._load_tiers()
        info = mod.get_education_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "education_features", "course_limit", "support_level"):
            assert key in info

    def test_free_price_zero(self):
        mod = self._load_tiers()
        assert mod.get_education_tier_info(Tier.FREE)["price_usd_monthly"] == 0.0

    def test_enterprise_unlimited(self):
        mod = self._load_tiers()
        assert mod.get_education_tier_info(Tier.ENTERPRISE)["requests_per_month"] is None

    def test_enterprise_unlimited_courses(self):
        mod = self._load_tiers()
        assert mod.get_education_tier_info(Tier.ENTERPRISE)["course_limit"] is None

    def test_free_fewer_courses_than_pro(self):
        mod = self._load_tiers()
        free_lim = mod.COURSE_LIMITS[Tier.FREE.value]
        pro_lim = mod.COURSE_LIMITS[Tier.PRO.value]
        assert free_lim < pro_lim


# -----------------------------------------------------------------------
# EducationBot tests
# -----------------------------------------------------------------------

class TestEducationBot:
    def test_default_tier_free(self):
        bot = EducationBot()
        assert bot.tier == Tier.FREE

    def test_create_course_returns_dict(self):
        bot = EducationBot()
        result = bot.create_course("Intro to Python", ["Variables", "Loops", "Functions"])
        assert isinstance(result, dict)

    def test_create_course_keys(self):
        bot = EducationBot()
        result = bot.create_course("Math 101", ["Algebra"])
        for key in ("course", "tier", "requests_used", "requests_remaining"):
            assert key in result
        for key in ("course_id", "title", "lessons"):
            assert key in result["course"]

    def test_create_course_increments_count(self):
        bot = EducationBot()
        bot.create_course("C1", ["L1"])
        bot.create_course("C2", ["L1"])
        assert bot._request_count == 2

    def test_free_course_limit(self):
        bot = EducationBot(tier=Tier.FREE)
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_edu_t", os.path.join(BOT_DIR, "tiers.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        limit = mod.COURSE_LIMITS[Tier.FREE.value]
        for i in range(limit):
            bot.create_course(f"Course {i}", ["Lesson"])
        with pytest.raises(EducationBotTierError):
            bot.create_course("One Too Many", ["Lesson"])

    def test_generate_quiz_returns_dict(self):
        bot = EducationBot()
        r = bot.create_course("PY", ["Vars"])
        course_id = r["course"]["course_id"]
        result = bot.generate_quiz(course_id)
        assert isinstance(result, dict)
        assert "questions" in result

    def test_generate_quiz_unknown_course_raises(self):
        bot = EducationBot()
        with pytest.raises(EducationBotTierError):
            bot.generate_quiz("NONEXISTENT")

    def test_submit_answer_returns_dict(self):
        bot = EducationBot()
        r = bot.create_course("PY", ["Vars"])
        course_id = r["course"]["course_id"]
        quiz = bot.generate_quiz(course_id)
        q_id = quiz["questions"][0]["question_id"]
        result = bot.submit_answer(course_id, q_id, "A")
        assert isinstance(result, dict)
        assert "correct" in result

    def test_get_progress_returns_dict(self):
        bot = EducationBot()
        r = bot.create_course("PY", ["Vars"])
        course_id = r["course"]["course_id"]
        result = bot.get_progress(course_id)
        assert isinstance(result, dict)
        assert "completion_pct" in result

    def test_get_progress_unknown_course_raises(self):
        bot = EducationBot()
        with pytest.raises(EducationBotTierError):
            bot.get_progress("NOPE")

    def test_request_limit_raises(self):
        bot = EducationBot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        with pytest.raises(EducationBotRequestLimitError):
            bot.create_course("Blocked", ["Lesson"])

    def test_enterprise_no_request_limit(self):
        bot = EducationBot(tier=Tier.ENTERPRISE)
        bot._request_count = 999_999
        result = bot.create_course("Unlimited", ["Lesson"])
        assert result["requests_remaining"] == "unlimited"

    def test_describe_tier_returns_string(self):
        bot = EducationBot()
        output = bot.describe_tier()
        assert isinstance(output, str)
        assert "Free" in output

    def test_show_upgrade_path_from_free(self):
        bot = EducationBot()
        output = bot.show_upgrade_path()
        assert "Pro" in output

    def test_show_upgrade_path_enterprise(self):
        bot = EducationBot(tier=Tier.ENTERPRISE)
        output = bot.show_upgrade_path()
        assert "top-tier" in output
