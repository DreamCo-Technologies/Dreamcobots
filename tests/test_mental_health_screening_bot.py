import sys, os
REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, REPO_ROOT)

TOOL_DIR = os.path.join(REPO_ROOT, 'healthcare-tools', 'mental_health_screening_bot')
sys.path.insert(0, TOOL_DIR)

import pytest
from mental_health_screening_bot import MentalHealthScreeningBot


class TestMentalHealthScreeningBotInstantiation:
    def test_default_tier_is_free(self):
        bot = MentalHealthScreeningBot()
        assert bot.tier == "free"

    def test_pro_tier(self):
        bot = MentalHealthScreeningBot(tier="pro")
        assert bot.tier == "pro"


class TestPHQ2:
    def test_positive_screen(self):
        bot = MentalHealthScreeningBot()
        result = bot.run_phq2([2, 2])
        assert result["positive_screen"] is True
        assert result["score"] == 4

    def test_negative_screen(self):
        bot = MentalHealthScreeningBot()
        result = bot.run_phq2([0, 1])
        assert result["positive_screen"] is False

    def test_insufficient_responses(self):
        bot = MentalHealthScreeningBot()
        with pytest.raises(ValueError):
            bot.run_phq2([1])

    def test_result_has_disclaimer(self):
        bot = MentalHealthScreeningBot()
        result = bot.run_phq2([0, 0])
        assert "disclaimer" in result


class TestPHQ9:
    def test_free_tier_raises_permission(self):
        bot = MentalHealthScreeningBot(tier="free")
        with pytest.raises(PermissionError):
            bot.run_phq9([0] * 9)

    def test_minimal_severity(self):
        bot = MentalHealthScreeningBot(tier="pro")
        result = bot.run_phq9([0] * 9)
        assert result["severity"] == "Minimal"

    def test_severe_severity(self):
        bot = MentalHealthScreeningBot(tier="pro")
        result = bot.run_phq9([3] * 9)
        assert result["severity"] == "Severe"

    def test_crisis_resources_on_item_9(self):
        bot = MentalHealthScreeningBot(tier="pro")
        responses = [0] * 8 + [2]
        result = bot.run_phq9(responses)
        assert len(result["crisis_resources"]) > 0

    def test_insufficient_responses(self):
        bot = MentalHealthScreeningBot(tier="pro")
        with pytest.raises(ValueError):
            bot.run_phq9([1, 2])


class TestGAD7:
    def test_free_tier_raises_permission(self):
        bot = MentalHealthScreeningBot(tier="free")
        with pytest.raises(PermissionError):
            bot.run_gad7([0] * 7)

    def test_minimal_anxiety(self):
        bot = MentalHealthScreeningBot(tier="pro")
        result = bot.run_gad7([0] * 7)
        assert result["severity"] == "Minimal Anxiety"

    def test_severe_anxiety(self):
        bot = MentalHealthScreeningBot(tier="pro")
        result = bot.run_gad7([3] * 7)
        assert result["severity"] == "Severe Anxiety"

    def test_insufficient_responses(self):
        bot = MentalHealthScreeningBot(tier="pro")
        with pytest.raises(ValueError):
            bot.run_gad7([1, 2])


class TestGetQuestions:
    def test_phq9_has_9_questions(self):
        bot = MentalHealthScreeningBot()
        qs = bot.get_questions("PHQ-9")
        assert len(qs) == 9

    def test_gad7_has_7_questions(self):
        bot = MentalHealthScreeningBot()
        qs = bot.get_questions("GAD-7")
        assert len(qs) == 7

    def test_phq2_has_2_questions(self):
        bot = MentalHealthScreeningBot()
        qs = bot.get_questions("PHQ-2")
        assert len(qs) == 2

    def test_unknown_instrument_raises(self):
        bot = MentalHealthScreeningBot()
        with pytest.raises(ValueError):
            bot.get_questions("UNKNOWN")
