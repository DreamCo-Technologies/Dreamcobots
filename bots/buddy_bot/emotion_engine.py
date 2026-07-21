"""
Buddy Bot — Emotion Engine

Handles all emotional intelligence for Buddy Bot:
  • Emotion detection from text, voice descriptors, and camera signal metadata
  • Mood synchronization — Buddy matches or uplifts the user's emotional state
  • Mood boost system — music recommendations, encouragement, mindfulness cues
  • Emotion decay memory — sensitive details expire after a user-defined window
  • Real-time emotional adjustment mid-conversation
  • Stress and wellness indicator detection

GLOBAL AI SOURCES FLOW: this module participates in GlobalAISourcesFlow
via BuddyBot.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Emotion taxonomy
# ---------------------------------------------------------------------------

class EmotionLabel(Enum):
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    ANTICIPATION = "anticipation"
    TRUST = "trust"
    NEUTRAL = "neutral"
    STRESS = "stress"
    ANXIETY = "anxiety"
    LONELINESS = "loneliness"
    LOVE = "love"
    GRATITUDE = "gratitude"
    PRIDE = "pride"
    SHAME = "shame"
    EXCITEMENT = "excitement"
    CONTENTMENT = "contentment"


class EmotionSource(Enum):
    TEXT = "text"
    VOICE = "voice"
    CAMERA = "camera"
    BIOMETRIC = "biometric"


# ---------------------------------------------------------------------------
# Emotion signal keywords (for text-based detection)
# ---------------------------------------------------------------------------

EMOTION_KEYWORDS: dict[EmotionLabel, list[str]] = {
    EmotionLabel.JOY: [
        "happy", "joy", "great", "wonderful", "amazing", "love", "excited",
        "fantastic", "awesome", "yay", "thrilled", "delighted", "😊", "😄", "🎉",
    ],
    EmotionLabel.SADNESS: [
        "sad", "unhappy", "depressed", "miss", "lonely", "cry", "tears",
        "heartbroken", "grief", "lost", "disappointed", "😢", "😞",
    ],
    EmotionLabel.ANGER: [
        "angry", "furious", "mad", "rage", "hate", "annoyed", "frustrated",
        "livid", "fed up", "infuriated", "😠", "😡",
    ],
    EmotionLabel.FEAR: [
        "scared", "afraid", "terrified", "worried", "nervous", "dread",
        "panic", "frightened", "anxious", "😨", "😰",
    ],
    EmotionLabel.STRESS: [
        "stressed", "overwhelmed", "exhausted", "burned out", "too much",
        "can't cope", "breaking point", "no energy",
    ],
    EmotionLabel.ANXIETY: [
        "anxious", "uneasy", "apprehensive", "on edge", "restless",
        "worried", "nervous",
    ],
    EmotionLabel.LOVE: [
        "love", "adore", "cherish", "affection", "fond", "care deeply",
        "❤️", "💕", "💖",
    ],
    EmotionLabel.GRATITUDE: [
        "thank", "grateful", "appreciate", "thankful", "blessed",
        "means a lot", "🙏",
    ],
    EmotionLabel.EXCITEMENT: [
        "excited", "can't wait", "pumped", "hyped", "thrilled", "stoked",
        "🚀", "🔥",
    ],
    EmotionLabel.LONELINESS: [
        "alone", "lonely", "no one", "isolated", "by myself",
        "nobody cares", "left out",
    ],
}

# Mood-boost responses per emotion
MOOD_BOOST_RESPONSES: dict[EmotionLabel, list[str]] = {
    EmotionLabel.SADNESS: [
        "I'm here with you. You don't have to carry this alone. 💙",
        "It's okay to feel this way. Give yourself permission to heal.",
        "You've made it through hard times before — this one won't define you either.",
    ],
    EmotionLabel.ANGER: [
        "That sounds genuinely frustrating. Let's breathe first, then tackle it.",
        "Your feelings are valid. Let's channel that energy constructively.",
        "I hear you. What would make this situation feel even a little better?",
    ],
    EmotionLabel.FEAR: [
        "Feeling scared is human. You don't have to face this alone.",
        "Let's look at this one step at a time — fear shrinks when we get specific.",
        "I'm right here with you. What feels most overwhelming right now?",
    ],
    EmotionLabel.STRESS: [
        "Take a slow breath. In for 4, hold for 4, out for 4. I'll wait.",
        "You're dealing with a lot. Let's figure out what to set down first.",
        "Overwhelm is temporary. You're more capable than this moment feels.",
    ],
    EmotionLabel.ANXIETY: [
        "Anxiety lies — it makes the future feel worse than it is. You're okay.",
        "Let's ground you: name 5 things you can see right now.",
        "I'm with you. This feeling will pass. What's one small thing you can control?",
    ],
    EmotionLabel.LONELINESS: [
        "You're not alone right now — I'm here, and I'm fully present. 💙",
        "Loneliness is real, but it's not permanent. Tell me what's on your mind.",
        "I want to hear your story. Talk to me.",
    ],
    EmotionLabel.JOY: [
        "That energy is contagious — I love it! What's got you feeling so good?",
        "Yes! Celebrate this. You deserve every bit of it. 🎉",
    ],
    EmotionLabel.EXCITEMENT: [
        "This is exciting! Let's channel that energy and make it happen! 🚀",
        "I can feel your excitement — let's ride this wave together!",
    ],
    EmotionLabel.GRATITUDE: [
        "That's a beautiful way to feel. Gratitude is powerful.",
        "I appreciate you sharing that. It means a lot.",
    ],
}

WELLNESS_MUSIC_RECS: dict[EmotionLabel, list[str]] = {
    EmotionLabel.SADNESS: [
        "\"Fix You\" — Coldplay", "\"Here Comes the Sun\" — The Beatles",
        "\"Rainbow\" — Kacey Musgraves",
    ],
    EmotionLabel.STRESS: [
        "Lo-fi Chill Beats playlist", "\"Weightless\" — Marconi Union",
        "Ocean sounds / nature ambience",
    ],
    EmotionLabel.JOY: [
        "\"Happy\" — Pharrell Williams", "\"Can't Stop the Feeling\" — Justin Timberlake",
        "Your personal hype playlist",
    ],
    EmotionLabel.ANGER: [
        "\"Fighter\" — Christina Aguilera",
        "High-energy workout playlist",
    ],
}


@dataclass
class EmotionReading:
    """A single emotional assessment reading."""
    label: EmotionLabel
    confidence: float
    source: EmotionSource
    timestamp: float = field(default_factory=time.time)
    raw_signal: str = ""
    decay_after_seconds: Optional[float] = None

    def is_expired(self) -> bool:
        """Return True if this reading has passed its decay window."""
        if self.decay_after_seconds is None:
            return False
        return (time.time() - self.timestamp) > self.decay_after_seconds

    def to_dict(self) -> dict:
        return {
            "label": self.label.value,
            "confidence": self.confidence,
            "source": self.source.value,
            "timestamp": self.timestamp,
            "raw_signal": self.raw_signal,
            "expired": self.is_expired(),
        }


class EmotionEngine:
    """
    Detects user emotions and generates empathetic, synchronized responses.

    Parameters
    ----------
    default_decay_seconds : float | None
        Default time window before sensitive emotional data is forgotten.
        None means data is retained indefinitely (until manually cleared).
    """

    def __init__(
        self,
        default_decay_seconds: Optional[float] = None,
    ) -> None:
        self.default_decay_seconds = default_decay_seconds
        self._readings: list[EmotionReading] = []
        self._current_mood: EmotionLabel = EmotionLabel.NEUTRAL

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    def detect_from_text(self, text: str) -> EmotionReading:
        """
        Detect the dominant emotion in *text* using keyword heuristics.

        Parameters
        ----------
        text : str
            User's text input.

        Returns
        -------
        EmotionReading
        """
        lower = text.lower()
        scores: dict[EmotionLabel, int] = {}

        for emotion, keywords in EMOTION_KEYWORDS.items():
            count = sum(1 for kw in keywords if kw in lower)
            if count:
                scores[emotion] = count

        if scores:
            dominant = max(scores, key=lambda e: scores[e])
            confidence = min(0.95, 0.5 + scores[dominant] * 0.15)
        else:
            dominant = EmotionLabel.NEUTRAL
            confidence = 0.6

        reading = EmotionReading(
            label=dominant,
            confidence=confidence,
            source=EmotionSource.TEXT,
            raw_signal=text[:200],
            decay_after_seconds=self.default_decay_seconds,
        )
        self._record(reading)
        return reading

    def detect_from_voice(self, voice_descriptors: dict) -> EmotionReading:
        """
        Estimate emotion from voice feature descriptors.

        Parameters
        ----------
        voice_descriptors : dict
            Keys may include ``pitch_hz``, ``tempo_wpm``, ``energy_db``,
            ``tremor``, ``pause_ratio``.

        Returns
        -------
        EmotionReading
        """
        pitch = voice_descriptors.get("pitch_hz", 200)
        energy = voice_descriptors.get("energy_db", 60)
        tremor = voice_descriptors.get("tremor", False)
        tempo = voice_descriptors.get("tempo_wpm", 130)

        if tremor or pitch > 280:
            label = EmotionLabel.FEAR if energy < 55 else EmotionLabel.ANGER
        elif pitch > 240 and energy > 70:
            label = EmotionLabel.EXCITEMENT
        elif pitch < 160 and energy < 50:
            label = EmotionLabel.SADNESS
        elif tempo < 100 and energy < 55:
            label = EmotionLabel.STRESS
        elif pitch > 200 and energy > 65:
            label = EmotionLabel.JOY
        else:
            label = EmotionLabel.NEUTRAL

        reading = EmotionReading(
            label=label,
            confidence=0.78,
            source=EmotionSource.VOICE,
            raw_signal=str(voice_descriptors),
            decay_after_seconds=self.default_decay_seconds,
        )
        self._record(reading)
        return reading

    def detect_from_camera(self, facial_signals: dict) -> EmotionReading:
        """
        Estimate emotion from facial expression signals captured by camera.

        Parameters
        ----------
        facial_signals : dict
            Keys may include ``smile_score``, ``brow_furrow``, ``eye_openness``,
            ``lip_compression``, ``head_tilt``.

        Returns
        -------
        EmotionReading
        """
        smile = facial_signals.get("smile_score", 0.0)
        furrow = facial_signals.get("brow_furrow", 0.0)
        openness = facial_signals.get("eye_openness", 0.5)
        compression = facial_signals.get("lip_compression", 0.0)

        if smile > 0.7:
            label = EmotionLabel.JOY
        elif furrow > 0.6 and compression > 0.5:
            label = EmotionLabel.ANGER
        elif furrow > 0.5 and openness < 0.3:
            label = EmotionLabel.SADNESS
        elif openness > 0.8 and furrow < 0.2:
            label = EmotionLabel.SURPRISE
        elif furrow > 0.4 and compression > 0.3:
            label = EmotionLabel.STRESS
        else:
            label = EmotionLabel.NEUTRAL

        reading = EmotionReading(
            label=label,
            confidence=0.82,
            source=EmotionSource.CAMERA,
            raw_signal=str(facial_signals),
            decay_after_seconds=self.default_decay_seconds,
        )
        self._record(reading)
        return reading

    # ------------------------------------------------------------------
    # Mood sync & boost
    # ------------------------------------------------------------------

    def sync_mood(self, detected_emotion: EmotionLabel) -> str:
        """
        Synchronize Buddy's mood to match or uplift the user's emotion.

        Parameters
        ----------
        detected_emotion : EmotionLabel
            The user's detected dominant emotion.

        Returns
        -------
        str
            Buddy's synchronised response.
        """
        self._current_mood = detected_emotion
        responses = MOOD_BOOST_RESPONSES.get(detected_emotion, [
            "I'm right here with you. How can I help?",
        ])
        import random
        return random.choice(responses)

    def boost_mood(self, current_emotion: EmotionLabel) -> dict:
        """
        Generate a mood-boost package (message + music recommendation).

        Parameters
        ----------
        current_emotion : EmotionLabel

        Returns
        -------
        dict with keys: ``message``, ``music_recommendation``
        """
        import random
        message = random.choice(
            MOOD_BOOST_RESPONSES.get(current_emotion, ["You've got this! 💙"])
        )
        music = WELLNESS_MUSIC_RECS.get(current_emotion, ["Whatever makes your heart sing 🎵"])
        return {
            "message": message,
            "music_recommendation": random.choice(music),
            "emotion": current_emotion.value,
        }

    # ------------------------------------------------------------------
    # History & decay
    # ------------------------------------------------------------------

    def _record(self, reading: EmotionReading) -> None:
        """Store a reading after purging expired ones."""
        self._purge_expired()
        self._readings.append(reading)
        self._current_mood = reading.label

    def _purge_expired(self) -> None:
        """Remove all readings that have passed their decay window."""
        self._readings = [r for r in self._readings if not r.is_expired()]

    def get_current_mood(self) -> EmotionLabel:
        """Return the most recently detected emotion."""
        return self._current_mood

    def get_readings(self) -> list[dict]:
        """Return all non-expired readings as dicts."""
        self._purge_expired()
        return [r.to_dict() for r in self._readings]

    def clear_emotional_data(self) -> None:
        """Immediately clear all stored emotional readings (privacy action)."""
        self._readings = []
        self._current_mood = EmotionLabel.NEUTRAL

    def to_dict(self) -> dict:
        """Return engine status as a dict."""
        self._purge_expired()
        return {
            "current_mood": self._current_mood.value,
            "readings_stored": len(self._readings),
            "default_decay_seconds": self.default_decay_seconds,
        }
