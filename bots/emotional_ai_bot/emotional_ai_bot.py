"""Emotional AI Bot — tier-aware emotion recognition, mental health coaching, and productivity support.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.emotional_ai_bot.tiers import BOT_FEATURES, get_bot_tier_info
from bots.emotional_ai_bot.emotion_engine import EmotionRecognizer, PersonalityAdapter, EmotionRecognizerError
from bots.emotional_ai_bot.mental_health_coach import MentalHealthCoach, ProductivityCoach
from framework import GlobalAISourcesFlow  # noqa: F401


class EmotionalAIBotError(Exception):
    """Raised when an EmotionalAIBot feature is unavailable on the current tier."""


class EmotionalAIBot:
    """Tier-aware emotionally intelligent AI assistant.

    Provides emotion recognition, mental health coaching, and productivity support.

    Tiers:
        FREE       — basic emotion detection (4 emotions), 3 affirmations/day
        PRO        — full 8-emotion detection, wellness plans, coaching, progress tracking
        ENTERPRISE — everything in PRO plus historical analytics, environmental shift
                     analysis, API access, and dedicated support
    """

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self.flow = GlobalAISourcesFlow(bot_name="EmotionalAIBot")
        self._emotion_recognizer = EmotionRecognizer(tier)
        self._personality_adapter = PersonalityAdapter(tier)
        self._mental_health_coach = MentalHealthCoach(tier)
        self._productivity_coach = ProductivityCoach(tier)

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def analyze_emotion(self, text: str) -> dict:
        """Analyze the emotion in the provided text.

        Args:
            text: Natural-language text to analyse.

        Returns:
            Emotion analysis dict with primary_emotion, intensity, secondary_emotions.
        """
        return self._emotion_recognizer.analyze_text_emotion(text)

    def provide_mental_health_support(self, user_id: str, message: str) -> dict:
        """Analyse the message emotion and return matching coping strategies.

        Args:
            user_id: Unique user identifier.
            message:  User's current message describing their emotional state.

        Returns:
            Dict with emotion analysis and coping strategies.
        """
        emotion_result = self._emotion_recognizer.analyze_text_emotion(message)
        primary = emotion_result.get("primary_emotion", "sadness")
        intensity = emotion_result.get("intensity", 0.5)
        coping = self._mental_health_coach.provide_coping_strategy(primary, intensity)
        return {
            "user_id": user_id,
            "emotion_analysis": emotion_result,
            "coping_support": coping,
            "tier": self.tier.value,
        }

    def create_coaching_plan(self, user_id: str, focus_area: str) -> dict:
        """Create a structured coaching session for the given focus area (PRO/ENTERPRISE).

        Args:
            user_id:    Unique user identifier.
            focus_area: One of time_management, motivation, stress_reduction, goal_setting,
                        habit_formation, work_life_balance.

        Returns:
            Coaching session plan dict.

        Raises:
            EmotionalAIBotError: If the current tier does not support coaching sessions.
        """
        if self.tier == Tier.FREE:
            upgrade = get_upgrade_path(self.tier)
            raise EmotionalAIBotError(
                f"Coaching plans require PRO or ENTERPRISE tier. Upgrade: {upgrade}"
            )
        return self._productivity_coach.create_coaching_session(user_id, focus_area)

    def generate_wellness_report(self, user_id: str, goals: list) -> dict:
        """Generate a personalised wellness plan (PRO/ENTERPRISE).

        Args:
            user_id: Unique user identifier.
            goals:   List of wellness goals.

        Returns:
            Wellness plan dict.

        Raises:
            EmotionalAIBotError: If the current tier does not support wellness reports.
        """
        if self.tier == Tier.FREE:
            upgrade = get_upgrade_path(self.tier)
            raise EmotionalAIBotError(
                f"Wellness reports require PRO or ENTERPRISE tier. Upgrade: {upgrade}"
            )
        return self._mental_health_coach.create_wellness_plan(user_id, goals)

    def get_daily_affirmations(self, user_profile: dict) -> dict:
        """Return daily affirmations based on the user's profile.

        Args:
            user_profile: Dict with optional keys current_mood, goals.

        Returns:
            Affirmations dict.
        """
        return self._productivity_coach.generate_daily_affirmations(user_profile)

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def get_emotional_dashboard(self) -> dict:
        """Return a summary dashboard of available EmotionalAIBot features."""
        return {
            "bot": "EmotionalAIBot",
            "tier": self.tier.value,
            "features": BOT_FEATURES[self.tier.value],
            "tier_info": get_bot_tier_info(self.tier),
            "modules": {
                "emotion_recognition": "EmotionRecognizer",
                "personality_adapter": "PersonalityAdapter",
                "mental_health_coach": "MentalHealthCoach",
                "productivity_coach": "ProductivityCoach",
            },
            "framework": "GLOBAL AI SOURCES FLOW",
        }
