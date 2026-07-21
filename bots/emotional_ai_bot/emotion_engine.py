"""Emotion Engine — emotion recognition and personality-aware response adaptation."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from framework import GlobalAISourcesFlow  # noqa: F401

_flow = GlobalAISourcesFlow(bot_name="EmotionEngine")

EMOTIONS = ["joy", "sadness", "anger", "fear", "surprise", "disgust", "trust", "anticipation"]
_FREE_EMOTIONS = EMOTIONS[:4]  # joy, sadness, anger, fear

TONES = ["empathetic", "motivational", "calm", "energetic", "professional", "friendly", "supportive"]

_EMOTION_KEYWORDS: dict = {
    "joy": ["happy", "great", "wonderful", "excited", "love", "amazing", "fantastic", "glad", "elated"],
    "sadness": ["sad", "unhappy", "depressed", "down", "miserable", "grief", "lonely", "hopeless", "crying"],
    "anger": ["angry", "furious", "mad", "rage", "hate", "frustrated", "annoyed", "outraged", "irritated"],
    "fear": ["scared", "afraid", "anxious", "worried", "terrified", "nervous", "panic", "dread", "frightened"],
    "surprise": ["surprised", "shocked", "unexpected", "wow", "astonished", "amazed", "startled"],
    "disgust": ["disgusted", "gross", "revolting", "awful", "terrible", "horrible", "nasty", "repulsed"],
    "trust": ["trust", "believe", "confident", "reliable", "safe", "secure", "faith", "loyal"],
    "anticipation": ["excited", "eager", "looking forward", "hopeful", "curious", "waiting", "expecting"],
}

_TONE_RESPONSE_PREFIX: dict = {
    "empathetic": "I understand how you feel.",
    "motivational": "You have the strength to get through this!",
    "calm": "Take a breath and consider this calmly.",
    "energetic": "Let's tackle this with energy and enthusiasm!",
    "professional": "Here is a considered perspective on your situation.",
    "friendly": "Hey, let's think through this together!",
    "supportive": "I'm here for you every step of the way.",
}


class EmotionRecognizerError(Exception):
    """Raised when an EmotionRecognizer feature is unavailable on the current tier."""


class EmotionRecognizer:
    """Tier-aware emotion recognition from text and contextual data."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._state_history: dict = {}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _available_emotions(self) -> list:
        return EMOTIONS if self.tier in (Tier.PRO, Tier.ENTERPRISE) else _FREE_EMOTIONS

    def _score_text(self, text: str) -> dict:
        lower = text.lower()
        scores: dict = {}
        for emotion in self._available_emotions():
            count = sum(1 for kw in _EMOTION_KEYWORDS.get(emotion, []) if kw in lower)
            if count:
                scores[emotion] = min(1.0, count * 0.25)
        return scores

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze_text_emotion(self, text: str) -> dict:
        """Return emotion analysis dict with primary_emotion, intensity, and secondary_emotions."""
        if not text or not isinstance(text, str):
            raise ValueError("text must be a non-empty string")
        scores = self._score_text(text)
        if not scores:
            primary = "joy" if self.tier == Tier.FREE else "trust"
            return {
                "primary_emotion": primary,
                "intensity": 0.1,
                "secondary_emotions": [],
                "available_emotions": self._available_emotions(),
                "tier": self.tier.value,
            }
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary_emotion, primary_score = sorted_scores[0]
        secondary = [e for e, _ in sorted_scores[1:3]]
        return {
            "primary_emotion": primary_emotion,
            "intensity": round(primary_score, 2),
            "secondary_emotions": secondary,
            "available_emotions": self._available_emotions(),
            "tier": self.tier.value,
        }

    def analyze_environmental_shift(self, context_data: dict) -> dict:
        """Analyze environmental/contextual changes and their emotional impact (ENTERPRISE only)."""
        if self.tier != Tier.ENTERPRISE:
            upgrade = get_upgrade_path(self.tier)
            raise EmotionRecognizerError(
                f"Environmental shift analysis requires ENTERPRISE tier. Upgrade: {upgrade}"
            )
        if not isinstance(context_data, dict):
            raise ValueError("context_data must be a dict")
        changes = context_data.get("changes", [])
        shift_score = min(1.0, len(changes) * 0.2)
        dominant_shift = changes[0] if changes else "stable"
        return {
            "shift_detected": bool(changes),
            "shift_score": round(shift_score, 2),
            "dominant_shift": dominant_shift,
            "emotional_impact": "high" if shift_score > 0.6 else "moderate" if shift_score > 0.3 else "low",
            "recommendation": "Monitor closely" if shift_score > 0.6 else "Continue as normal",
            "tier": self.tier.value,
        }

    def track_emotional_state(self, user_id: str, emotion_data: dict) -> dict:
        """Track a user's emotional state history (ENTERPRISE only)."""
        if self.tier != Tier.ENTERPRISE:
            upgrade = get_upgrade_path(self.tier)
            raise EmotionRecognizerError(
                f"Emotional state tracking requires ENTERPRISE tier. Upgrade: {upgrade}"
            )
        if user_id not in self._state_history:
            self._state_history[user_id] = []
        self._state_history[user_id].append(emotion_data)
        history = self._state_history[user_id]
        emotions_seen = [e.get("primary_emotion", "unknown") for e in history]
        return {
            "user_id": user_id,
            "history_length": len(history),
            "most_frequent_emotion": max(set(emotions_seen), key=emotions_seen.count),
            "latest_emotion": emotion_data.get("primary_emotion", "unknown"),
            "trend": "improving" if len(history) >= 2 else "insufficient_data",
            "tier": self.tier.value,
        }


class PersonalityAdapterError(Exception):
    """Raised when a PersonalityAdapter feature is unavailable on the current tier."""


class PersonalityAdapter:
    """Tier-aware personality-based response tone adaptation."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def adapt_response_tone(self, message: str, user_mood: str, context: dict) -> dict:
        """Return a tone-adapted response based on user mood and context (PRO/ENTERPRISE)."""
        if self.tier == Tier.FREE:
            upgrade = get_upgrade_path(self.tier)
            raise PersonalityAdapterError(
                f"Tone adaptation requires PRO or ENTERPRISE tier. Upgrade: {upgrade}"
            )
        mood_tone_map = {
            "joy": "energetic",
            "sadness": "empathetic",
            "anger": "calm",
            "fear": "supportive",
            "surprise": "friendly",
            "disgust": "professional",
            "trust": "motivational",
            "anticipation": "motivational",
        }
        tone = mood_tone_map.get(user_mood.lower(), "friendly")
        prefix = _TONE_RESPONSE_PREFIX.get(tone, "")
        adapted = f"{prefix} {message}".strip()
        return {
            "original_message": message,
            "adapted_message": adapted,
            "tone_applied": tone,
            "user_mood": user_mood,
            "available_tones": TONES,
            "tier": self.tier.value,
        }

    def calibrate_personality(self, user_profile: dict) -> dict:
        """Calibrate personality settings from a user profile (PRO/ENTERPRISE)."""
        if self.tier == Tier.FREE:
            upgrade = get_upgrade_path(self.tier)
            raise PersonalityAdapterError(
                f"Personality calibration requires PRO or ENTERPRISE tier. Upgrade: {upgrade}"
            )
        preferred_tone = user_profile.get("preferred_tone", "friendly")
        if preferred_tone not in TONES:
            preferred_tone = "friendly"
        communication_style = user_profile.get("communication_style", "conversational")
        return {
            "calibrated": True,
            "preferred_tone": preferred_tone,
            "communication_style": communication_style,
            "personality_type": user_profile.get("personality_type", "balanced"),
            "empathy_level": user_profile.get("empathy_level", "medium"),
            "available_tones": TONES,
            "tier": self.tier.value,
        }

    def generate_personalized_response(self, prompt: str, personality_type: str) -> dict:
        """Generate a response adapted to a personality type (PRO/ENTERPRISE)."""
        if self.tier == Tier.FREE:
            upgrade = get_upgrade_path(self.tier)
            raise PersonalityAdapterError(
                f"Personalized responses require PRO or ENTERPRISE tier. Upgrade: {upgrade}"
            )
        personality_templates = {
            "analytical": "Based on the data and patterns available: {prompt}",
            "creative": "Here's a fresh perspective on that: {prompt}",
            "empathetic": "I hear you, and I want to say: {prompt}",
            "assertive": "Here's what you need to know: {prompt}",
            "balanced": "Taking everything into account: {prompt}",
        }
        template = personality_templates.get(personality_type, personality_templates["balanced"])
        response = template.format(prompt=prompt)
        return {
            "response": response,
            "personality_type": personality_type,
            "prompt": prompt,
            "tier": self.tier.value,
        }
