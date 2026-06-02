"""Bot emotional intelligence layer."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
import math
import re


@dataclass
class EmotionVector:
    valence: float
    arousal: float
    dominance: float
    primary_emotion: str

    def as_dict(self) -> Dict[str, float | str]:
        return {
            "valence": self.valence,
            "arousal": self.arousal,
            "dominance": self.dominance,
            "primary_emotion": self.primary_emotion,
        }


class EmotionDetector:
    """Heuristic emotion detector for conversational messages."""

    POSITIVE = {"great", "thanks", "love", "happy", "excited", "relieved", "awesome"}
    NEGATIVE = {"bad", "angry", "upset", "sad", "worried", "hate", "frustrated", "panic"}
    LOW_ENERGY = {"tired", "exhausted", "burned", "down", "slow", "drained"}
    HIGH_ENERGY = {"urgent", "now", "immediately", "asap", "excited", "panic", "angry"}
    POWERLESS = {"stuck", "confused", "helpless", "lost", "unclear"}
    IN_CONTROL = {"ready", "confident", "prepared", "planned", "decided"}
    LABELS = {
        "joy": {"happy", "great", "love", "awesome", "relieved"},
        "anger": {"angry", "furious", "hate", "frustrated"},
        "fear": {"worried", "panic", "afraid", "concerned"},
        "sadness": {"sad", "down", "drained", "exhausted"},
        "neutral": set(),
    }

    def _tokens(self, message: str) -> List[str]:
        return re.findall(r"[a-zA-Z']+", message.lower())

    def _score_axis(self, tokens: List[str], positive: set[str], negative: set[str]) -> float:
        pos = sum(token in positive for token in tokens)
        neg = sum(token in negative for token in tokens)
        total = max(1, len(tokens))
        return max(-1.0, min(1.0, (pos - neg) / math.sqrt(total)))

    def analyze(self, message: str) -> EmotionVector:
        tokens = self._tokens(message)
        valence = self._score_axis(tokens, self.POSITIVE, self.NEGATIVE)
        arousal = self._score_axis(tokens, self.HIGH_ENERGY, self.LOW_ENERGY)
        dominance = self._score_axis(tokens, self.IN_CONTROL, self.POWERLESS)
        label_scores = {
            label: sum(token in vocab for token in tokens)
            for label, vocab in self.LABELS.items()
        }
        primary = max(label_scores, key=label_scores.get) if any(label_scores.values()) else "neutral"
        if primary == "neutral":
            if valence > 0.25:
                primary = "joy"
            elif valence < -0.25 and arousal > 0:
                primary = "anger"
            elif valence < -0.25:
                primary = "sadness"
        return EmotionVector(round(valence, 3), round(arousal, 3), round(dominance, 3), primary)


class EmotionAdaptor:
    """Adjusts tone and style from an emotion vector."""

    STYLE_MAP = {
        "joy": {"tone": "warm", "pace": "brisk", "acknowledgement": "Celebrate momentum."},
        "anger": {"tone": "calm", "pace": "measured", "acknowledgement": "De-escalate and focus on fixes."},
        "fear": {"tone": "reassuring", "pace": "steady", "acknowledgement": "Reduce uncertainty with concrete next steps."},
        "sadness": {"tone": "gentle", "pace": "supportive", "acknowledgement": "Offer encouragement and achievable actions."},
        "neutral": {"tone": "professional", "pace": "balanced", "acknowledgement": "Stay concise and helpful."},
    }

    def style_for(self, emotion: EmotionVector) -> Dict[str, str]:
        base = dict(self.STYLE_MAP.get(emotion.primary_emotion, self.STYLE_MAP["neutral"]))
        if emotion.arousal > 0.3:
            base["response_length"] = "short"
        elif emotion.valence < -0.2:
            base["response_length"] = "detailed"
        else:
            base["response_length"] = "medium"
        return base

    def adapt_response(self, response: str, emotion: EmotionVector) -> str:
        style = self.style_for(emotion)
        prefix = {
            "calm": "I hear the urgency. ",
            "reassuring": "You're not alone in this. ",
            "gentle": "Thanks for sharing that. ",
            "warm": "That's great to hear. ",
            "professional": "Understood. ",
        }[style["tone"]]
        return f"{prefix}{response} ({style['acknowledgement']})"
