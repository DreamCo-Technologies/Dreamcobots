"""Tests for bots/emotional_ai_bot/ — Emotionally Intelligent AI."""
import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
AI_MODELS_DIR = os.path.join(REPO_ROOT, "bots", "ai-models-integration")
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, "models"))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.emotional_ai_bot.emotional_ai_bot import EmotionalAIBot, EmotionalAIBotError
from bots.emotional_ai_bot.emotion_engine import (
    EmotionRecognizer,
    EmotionRecognizerError,
    PersonalityAdapter,
    PersonalityAdapterError,
    EMOTIONS,
    TONES,
)
from bots.emotional_ai_bot.mental_health_coach import (
    MentalHealthCoach,
    MentalHealthCoachError,
    ProductivityCoach,
    ProductivityCoachError,
    STRATEGIES,
    FOCUS_AREAS,
)

# ===========================================================================
# EmotionRecognizer
# ===========================================================================

class TestEmotionRecognizer:

    def test_instantiate_free(self):
        er = EmotionRecognizer(Tier.FREE)
        assert er.tier == Tier.FREE

    def test_instantiate_pro(self):
        er = EmotionRecognizer(Tier.PRO)
        assert er.tier == Tier.PRO

    def test_instantiate_enterprise(self):
        er = EmotionRecognizer(Tier.ENTERPRISE)
        assert er.tier == Tier.ENTERPRISE

    def test_analyze_text_emotion_returns_dict(self):
        er = EmotionRecognizer(Tier.FREE)
        result = er.analyze_text_emotion("I feel happy and wonderful today")
        assert isinstance(result, dict)
        assert "primary_emotion" in result
        assert "intensity" in result
        assert "secondary_emotions" in result

    def test_analyze_text_emotion_joy(self):
        er = EmotionRecognizer(Tier.PRO)
        result = er.analyze_text_emotion("I am so happy and excited and love this")
        assert result["primary_emotion"] == "joy"
        assert result["intensity"] > 0

    def test_analyze_text_emotion_sadness(self):
        er = EmotionRecognizer(Tier.PRO)
        result = er.analyze_text_emotion("I feel very sad and unhappy and miserable")
        assert result["primary_emotion"] == "sadness"

    def test_analyze_text_emotion_anger(self):
        er = EmotionRecognizer(Tier.PRO)
        result = er.analyze_text_emotion("I am so angry and furious and outraged")
        assert result["primary_emotion"] == "anger"

    def test_analyze_text_emotion_fear(self):
        er = EmotionRecognizer(Tier.PRO)
        result = er.analyze_text_emotion("I am scared and anxious and worried")
        assert result["primary_emotion"] == "fear"

    def test_analyze_text_emotion_no_keywords(self):
        er = EmotionRecognizer(Tier.FREE)
        result = er.analyze_text_emotion("The cat sat on the mat")
        assert result["primary_emotion"] in EMOTIONS[:4]

    def test_analyze_text_emotion_free_tier_limits_emotions(self):
        er = EmotionRecognizer(Tier.FREE)
        result = er.analyze_text_emotion("Hello world")
        for emo in result.get("available_emotions", []):
            assert emo in EMOTIONS[:4]

    def test_analyze_text_emotion_pro_tier_all_emotions(self):
        er = EmotionRecognizer(Tier.PRO)
        result = er.analyze_text_emotion("Hello world")
        assert len(result.get("available_emotions", [])) == len(EMOTIONS)

    def test_analyze_text_emotion_invalid_raises(self):
        er = EmotionRecognizer(Tier.FREE)
        with pytest.raises(ValueError):
            er.analyze_text_emotion("")

    def test_analyze_text_emotion_non_string_raises(self):
        er = EmotionRecognizer(Tier.FREE)
        with pytest.raises(ValueError):
            er.analyze_text_emotion(None)

    def test_analyze_environmental_shift_enterprise_only(self):
        er_free = EmotionRecognizer(Tier.FREE)
        with pytest.raises(EmotionRecognizerError):
            er_free.analyze_environmental_shift({"changes": ["weather_change"]})

    def test_analyze_environmental_shift_pro_raises(self):
        er_pro = EmotionRecognizer(Tier.PRO)
        with pytest.raises(EmotionRecognizerError):
            er_pro.analyze_environmental_shift({"changes": []})

    def test_analyze_environmental_shift_enterprise_works(self):
        er = EmotionRecognizer(Tier.ENTERPRISE)
        result = er.analyze_environmental_shift({"changes": ["temperature_drop", "noise_increase"]})
        assert "shift_detected" in result
        assert result["shift_detected"] is True

    def test_analyze_environmental_shift_no_changes(self):
        er = EmotionRecognizer(Tier.ENTERPRISE)
        result = er.analyze_environmental_shift({"changes": []})
        assert result["shift_detected"] is False

    def test_analyze_environmental_shift_invalid_type(self):
        er = EmotionRecognizer(Tier.ENTERPRISE)
        with pytest.raises(ValueError):
            er.analyze_environmental_shift("bad_data")

    def test_track_emotional_state_enterprise_only(self):
        er = EmotionRecognizer(Tier.FREE)
        with pytest.raises(EmotionRecognizerError):
            er.track_emotional_state("user1", {"primary_emotion": "joy"})

    def test_track_emotional_state_enterprise_works(self):
        er = EmotionRecognizer(Tier.ENTERPRISE)
        result = er.track_emotional_state("user1", {"primary_emotion": "joy"})
        assert result["user_id"] == "user1"
        assert result["history_length"] == 1

    def test_track_emotional_state_multiple_entries(self):
        er = EmotionRecognizer(Tier.ENTERPRISE)
        er.track_emotional_state("user2", {"primary_emotion": "joy"})
        er.track_emotional_state("user2", {"primary_emotion": "sadness"})
        result = er.track_emotional_state("user2", {"primary_emotion": "joy"})
        assert result["history_length"] == 3


# ===========================================================================
# PersonalityAdapter
# ===========================================================================

class TestPersonalityAdapter:

    def test_instantiate_free(self):
        pa = PersonalityAdapter(Tier.FREE)
        assert pa.tier == Tier.FREE

    def test_adapt_response_tone_free_raises(self):
        pa = PersonalityAdapter(Tier.FREE)
        with pytest.raises(PersonalityAdapterError):
            pa.adapt_response_tone("message", "joy", {})

    def test_adapt_response_tone_pro_works(self):
        pa = PersonalityAdapter(Tier.PRO)
        result = pa.adapt_response_tone("Keep going!", "joy", {})
        assert "adapted_message" in result
        assert result["tone_applied"] in TONES

    def test_adapt_response_tone_enterprise_works(self):
        pa = PersonalityAdapter(Tier.ENTERPRISE)
        result = pa.adapt_response_tone("Stay calm", "anger", {})
        assert result["tone_applied"] == "calm"

    def test_calibrate_personality_free_raises(self):
        pa = PersonalityAdapter(Tier.FREE)
        with pytest.raises(PersonalityAdapterError):
            pa.calibrate_personality({"preferred_tone": "calm"})

    def test_calibrate_personality_pro_works(self):
        pa = PersonalityAdapter(Tier.PRO)
        result = pa.calibrate_personality({"preferred_tone": "motivational", "personality_type": "analytical"})
        assert result["calibrated"] is True
        assert result["preferred_tone"] == "motivational"

    def test_calibrate_personality_invalid_tone_defaults(self):
        pa = PersonalityAdapter(Tier.PRO)
        result = pa.calibrate_personality({"preferred_tone": "unknown_tone"})
        assert result["preferred_tone"] == "friendly"

    def test_generate_personalized_response_free_raises(self):
        pa = PersonalityAdapter(Tier.FREE)
        with pytest.raises(PersonalityAdapterError):
            pa.generate_personalized_response("Hello", "analytical")

    def test_generate_personalized_response_pro_works(self):
        pa = PersonalityAdapter(Tier.PRO)
        result = pa.generate_personalized_response("You can do it", "empathetic")
        assert "response" in result
        assert "personality_type" in result

    def test_generate_personalized_response_unknown_type_defaults(self):
        pa = PersonalityAdapter(Tier.PRO)
        result = pa.generate_personalized_response("Hello", "unknown_type")
        assert "response" in result


# ===========================================================================
# MentalHealthCoach
# ===========================================================================

class TestMentalHealthCoach:

    def test_instantiate_free(self):
        coach = MentalHealthCoach(Tier.FREE)
        assert coach.tier == Tier.FREE

    def test_assess_mental_state_free_raises(self):
        coach = MentalHealthCoach(Tier.FREE)
        with pytest.raises(MentalHealthCoachError):
            coach.assess_mental_state("u1", ["I feel great"])

    def test_assess_mental_state_pro_works(self):
        coach = MentalHealthCoach(Tier.PRO)
        result = coach.assess_mental_state("u1", ["I feel great", "things are good"])
        assert "wellness_score" in result
        assert "state" in result
        assert "disclaimer" in result

    def test_assess_mental_state_negative(self):
        coach = MentalHealthCoach(Tier.PRO)
        result = coach.assess_mental_state("u2", ["I feel bad", "very sad", "stressed"])
        assert result["state"] in ["neutral", "needs_attention"]

    def test_assess_mental_state_invalid_responses(self):
        coach = MentalHealthCoach(Tier.PRO)
        with pytest.raises(ValueError):
            coach.assess_mental_state("u3", "not a list")

    def test_provide_coping_strategy_joy(self):
        coach = MentalHealthCoach(Tier.FREE)
        result = coach.provide_coping_strategy("joy", 0.8)
        assert "strategies" in result
        assert len(result["strategies"]) >= 1

    def test_provide_coping_strategy_sadness(self):
        coach = MentalHealthCoach(Tier.PRO)
        result = coach.provide_coping_strategy("sadness", 0.7)
        assert len(result["strategies"]) > 0

    def test_provide_coping_strategy_unknown_defaults(self):
        coach = MentalHealthCoach(Tier.FREE)
        result = coach.provide_coping_strategy("unknown_emotion", 0.5)
        assert result["emotion"] == "sadness"

    def test_provide_coping_strategy_high_intensity_recommend_help(self):
        coach = MentalHealthCoach(Tier.PRO)
        result = coach.provide_coping_strategy("fear", 0.95)
        assert result["professional_help_recommended"] is True

    def test_provide_coping_strategy_free_limits_strategies(self):
        coach = MentalHealthCoach(Tier.FREE)
        result = coach.provide_coping_strategy("anger", 0.5)
        assert len(result["strategies"]) <= 2

    def test_create_wellness_plan_free_raises(self):
        coach = MentalHealthCoach(Tier.FREE)
        with pytest.raises(MentalHealthCoachError):
            coach.create_wellness_plan("u1", ["lose weight"])

    def test_create_wellness_plan_pro_works(self):
        coach = MentalHealthCoach(Tier.PRO)
        result = coach.create_wellness_plan("u1", ["reduce stress", "sleep better"])
        assert "plan" in result
        assert result["user_id"] == "u1"

    def test_create_wellness_plan_invalid_goals(self):
        coach = MentalHealthCoach(Tier.PRO)
        with pytest.raises(ValueError):
            coach.create_wellness_plan("u1", "not a list")

    def test_track_progress_free_raises(self):
        coach = MentalHealthCoach(Tier.FREE)
        with pytest.raises(MentalHealthCoachError):
            coach.track_progress("u1", {"mood_score": 7})

    def test_track_progress_pro_works(self):
        coach = MentalHealthCoach(Tier.PRO)
        result = coach.track_progress("u1", {"mood_score": 8})
        assert result["check_ins_total"] == 1

    def test_track_progress_trend(self):
        coach = MentalHealthCoach(Tier.PRO)
        coach.track_progress("u2", {"mood_score": 5})
        result = coach.track_progress("u2", {"mood_score": 8})
        assert result["trend"] in ["improving", "needs_attention"]


# ===========================================================================
# ProductivityCoach
# ===========================================================================

class TestProductivityCoach:

    def test_instantiate(self):
        pc = ProductivityCoach(Tier.FREE)
        assert pc.tier == Tier.FREE

    def test_analyze_productivity_free_raises(self):
        pc = ProductivityCoach(Tier.FREE)
        with pytest.raises(ProductivityCoachError):
            pc.analyze_productivity("u1", {"tasks_completed": 5, "tasks_planned": 10})

    def test_analyze_productivity_pro_works(self):
        pc = ProductivityCoach(Tier.PRO)
        result = pc.analyze_productivity("u1", {"tasks_completed": 8, "tasks_planned": 10, "hours_worked": 6})
        assert "completion_rate" in result
        assert "productivity_level" in result

    def test_analyze_productivity_high(self):
        pc = ProductivityCoach(Tier.PRO)
        result = pc.analyze_productivity("u1", {"tasks_completed": 9, "tasks_planned": 10, "hours_worked": 5})
        assert result["productivity_level"] == "high"

    def test_analyze_productivity_low(self):
        pc = ProductivityCoach(Tier.PRO)
        result = pc.analyze_productivity("u1", {"tasks_completed": 2, "tasks_planned": 10, "hours_worked": 8})
        assert result["productivity_level"] == "low"

    def test_create_coaching_session_free_raises(self):
        pc = ProductivityCoach(Tier.FREE)
        with pytest.raises(ProductivityCoachError):
            pc.create_coaching_session("u1", "motivation")

    def test_create_coaching_session_pro_works(self):
        pc = ProductivityCoach(Tier.PRO)
        result = pc.create_coaching_session("u1", "motivation")
        assert result["focus_area"] == "motivation"
        assert "session_plan" in result

    def test_create_coaching_session_all_focus_areas(self):
        pc = ProductivityCoach(Tier.ENTERPRISE)
        for area in FOCUS_AREAS:
            result = pc.create_coaching_session("u1", area)
            assert result["focus_area"] == area

    def test_create_coaching_session_unknown_defaults(self):
        pc = ProductivityCoach(Tier.PRO)
        result = pc.create_coaching_session("u1", "unknown_area")
        assert result["focus_area"] == "motivation"

    def test_generate_daily_affirmations_free(self):
        pc = ProductivityCoach(Tier.FREE)
        result = pc.generate_daily_affirmations({"current_mood": "happy"})
        assert "affirmations" in result
        assert len(result["affirmations"]) <= 3

    def test_generate_daily_affirmations_pro(self):
        pc = ProductivityCoach(Tier.PRO)
        result = pc.generate_daily_affirmations({"current_mood": "sad"})
        assert len(result["affirmations"]) >= 1

    def test_generate_daily_affirmations_no_profile(self):
        pc = ProductivityCoach(Tier.FREE)
        result = pc.generate_daily_affirmations({})
        assert "affirmations" in result


# ===========================================================================
# EmotionalAIBot — main class
# ===========================================================================

class TestEmotionalAIBot:

    def test_instantiate_free(self):
        bot = EmotionalAIBot(Tier.FREE)
        assert bot.tier == Tier.FREE

    def test_instantiate_pro(self):
        bot = EmotionalAIBot(Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_instantiate_enterprise(self):
        bot = EmotionalAIBot(Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_has_global_ai_sources_flow(self):
        bot = EmotionalAIBot(Tier.FREE)
        assert hasattr(bot, "flow")

    def test_analyze_emotion_returns_dict(self):
        bot = EmotionalAIBot(Tier.FREE)
        result = bot.analyze_emotion("I feel happy today")
        assert isinstance(result, dict)
        assert "primary_emotion" in result

    def test_provide_mental_health_support(self):
        bot = EmotionalAIBot(Tier.FREE)
        result = bot.provide_mental_health_support("user1", "I am feeling very sad today")
        assert "emotion_analysis" in result
        assert "coping_support" in result
        assert result["user_id"] == "user1"

    def test_create_coaching_plan_free_raises(self):
        bot = EmotionalAIBot(Tier.FREE)
        with pytest.raises(EmotionalAIBotError):
            bot.create_coaching_plan("user1", "motivation")

    def test_create_coaching_plan_pro_works(self):
        bot = EmotionalAIBot(Tier.PRO)
        result = bot.create_coaching_plan("user1", "goal_setting")
        assert "focus_area" in result

    def test_generate_wellness_report_free_raises(self):
        bot = EmotionalAIBot(Tier.FREE)
        with pytest.raises(EmotionalAIBotError):
            bot.generate_wellness_report("user1", ["reduce stress"])

    def test_generate_wellness_report_pro_works(self):
        bot = EmotionalAIBot(Tier.PRO)
        result = bot.generate_wellness_report("user1", ["reduce stress", "sleep better"])
        assert "plan" in result

    def test_get_daily_affirmations(self):
        bot = EmotionalAIBot(Tier.FREE)
        result = bot.get_daily_affirmations({"current_mood": "happy", "goals": ["grow"]})
        assert "affirmations" in result

    def test_get_emotional_dashboard(self):
        bot = EmotionalAIBot(Tier.FREE)
        dash = bot.get_emotional_dashboard()
        assert dash["bot"] == "EmotionalAIBot"
        assert "features" in dash
        assert "modules" in dash
        assert dash["tier"] == Tier.FREE.value

    def test_get_emotional_dashboard_pro(self):
        bot = EmotionalAIBot(Tier.PRO)
        dash = bot.get_emotional_dashboard()
        assert dash["tier"] == Tier.PRO.value

    def test_get_emotional_dashboard_enterprise(self):
        bot = EmotionalAIBot(Tier.ENTERPRISE)
        dash = bot.get_emotional_dashboard()
        assert dash["tier"] == Tier.ENTERPRISE.value

    def test_framework_in_dashboard(self):
        bot = EmotionalAIBot(Tier.FREE)
        dash = bot.get_emotional_dashboard()
        assert "GLOBAL AI SOURCES FLOW" in dash["framework"]
