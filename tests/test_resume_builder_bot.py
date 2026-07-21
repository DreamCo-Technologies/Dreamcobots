"""Tests for bots/resume_builder_bot/tiers.py and bots/resume_builder_bot/resume_builder_bot.py"""
import sys, os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.resume_builder_bot.resume_builder_bot import ResumeBuilderBot
from bots.resume_builder_bot.tiers import BOT_FEATURES, get_bot_tier_info


class TestResumeBuilderBotInstantiation:
    def test_default_tier_is_free(self):
        bot = ResumeBuilderBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = ResumeBuilderBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = ResumeBuilderBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE


class TestBuildResume:
    def test_build_resume_returns_dict(self):
        bot = ResumeBuilderBot()
        result = bot.build_resume("Jane Doe", "Engineer", ["Python", "Django"], "BS CS")
        assert isinstance(result, dict)

    def test_build_resume_has_required_keys(self):
        bot = ResumeBuilderBot()
        result = bot.build_resume("Jane Doe", "Engineer", ["Python"], "BS CS", target_role="Senior Dev")
        for key in ["name", "contact", "summary", "experience", "skills", "education", "target_role", "template_used", "format", "tier_used"]:
            assert key in result

    def test_build_resume_name(self):
        bot = ResumeBuilderBot()
        result = bot.build_resume("John Smith", "Developer", ["Java"], "BS CS")
        assert result["name"] == "John Smith"

    def test_free_tier_uses_professional_template(self):
        bot = ResumeBuilderBot()
        result = bot.build_resume("Jane", "Eng", ["Python"], "BS")
        assert result["template_used"] == "Professional"

    def test_skills_list_preserved(self):
        bot = ResumeBuilderBot()
        result = bot.build_resume("Jane", "Eng", ["Python", "Django", "SQL"], "BS")
        assert "Python" in result["skills"]

    def test_experience_list_preserved(self):
        bot = ResumeBuilderBot()
        exp = [{"title": "Dev", "company": "ACME", "duration": "2021-2023", "bullets": ["Did stuff"]}]
        result = bot.build_resume("Jane", exp, ["Python"], "BS")
        assert result["experience"] == exp


class TestAtsScore:
    def test_ats_score_raises_on_free(self):
        bot = ResumeBuilderBot()
        with pytest.raises(PermissionError):
            bot.calculate_ats_score({})

    def test_ats_score_works_on_pro(self):
        bot = ResumeBuilderBot(tier=Tier.PRO)
        result = bot.calculate_ats_score({})
        assert "score" in result
        assert "breakdown" in result

    def test_ats_score_works_on_enterprise(self):
        bot = ResumeBuilderBot(tier=Tier.ENTERPRISE)
        result = bot.calculate_ats_score({})
        assert isinstance(result["score"], int)


class TestCoverLetter:
    def test_cover_letter_raises_on_free(self):
        bot = ResumeBuilderBot()
        with pytest.raises(PermissionError):
            bot.generate_cover_letter({}, "job desc")

    def test_cover_letter_works_on_pro(self):
        bot = ResumeBuilderBot(tier=Tier.PRO)
        result = bot.generate_cover_letter({"name": "Jane", "target_role": "Engineer"}, "Python developer role")
        assert "body" in result
        assert "subject" in result

    def test_cover_letter_word_count(self):
        bot = ResumeBuilderBot(tier=Tier.PRO)
        result = bot.generate_cover_letter({"name": "Jane"}, "test job")
        assert result["word_count"] > 0


class TestSuggestImprovements:
    def test_suggest_returns_list(self):
        bot = ResumeBuilderBot()
        result = bot.suggest_improvements({})
        assert isinstance(result, list)

    def test_suggest_has_at_least_3_items(self):
        bot = ResumeBuilderBot()
        result = bot.suggest_improvements({})
        assert len(result) >= 3

    def test_suggestion_has_area_and_suggestion(self):
        bot = ResumeBuilderBot()
        result = bot.suggest_improvements({})
        for item in result:
            assert "area" in item
            assert "suggestion" in item
            assert "priority" in item


class TestResumeBuilderBotTiers:
    def test_bot_features_has_all_tiers(self):
        assert Tier.FREE.value in BOT_FEATURES
        assert Tier.PRO.value in BOT_FEATURES
        assert Tier.ENTERPRISE.value in BOT_FEATURES

    def test_pro_has_more_features_than_free(self):
        assert len(BOT_FEATURES[Tier.PRO.value]) > len(BOT_FEATURES[Tier.FREE.value])

    def test_tier_config_price(self):
        info = get_bot_tier_info(Tier.FREE)
        assert info["price_usd_monthly"] == 0.0

    def test_run_returns_pipeline_complete(self):
        bot = ResumeBuilderBot()
        result = bot.run()
        assert result.get("pipeline_complete") is True
