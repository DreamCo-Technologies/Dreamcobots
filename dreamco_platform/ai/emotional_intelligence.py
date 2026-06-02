"""Emotional intelligence scoring for support and coaching flows."""
from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean
from typing import Dict, Iterable, List
import math
import re


@dataclass
class EmotionalSignal:
    text: str
    polarity: float
    urgency: float
    empathy_gap: float
    labels: List[str] = field(default_factory=list)


class EmotionalIntelligenceEngine:
    POSITIVE = {"good", "great", "happy", "love", "calm", "trust", "confident", "thanks"}
    NEGATIVE = {"bad", "angry", "frustrated", "upset", "hate", "broken", "delay", "risk"}
    URGENT = {"now", "asap", "urgent", "immediately", "today", "blocked", "critical"}
    EMPATHY = {"feel", "understand", "sorry", "help", "support", "care", "together"}

    def tokenize(self, text: str) -> List[str]:
        return re.findall(r"[a-zA-Z']+", text.lower())

    def analyze_text(self, text: str) -> EmotionalSignal:
        tokens = self.tokenize(text)
        if not tokens:
            return EmotionalSignal(text=text, polarity=0.0, urgency=0.0, empathy_gap=0.0, labels=["neutral"])
        positive = sum(token in self.POSITIVE for token in tokens)
        negative = sum(token in self.NEGATIVE for token in tokens)
        urgent = sum(token in self.URGENT for token in tokens)
        empathy = sum(token in self.EMPATHY for token in tokens)
        polarity = (positive - negative) / max(len(tokens), 1)
        urgency = min(1.0, urgent / max(len(tokens) / 4, 1))
        empathy_gap = max(0.0, (negative + urgent - empathy) / max(len(tokens) / 3, 1))
        labels: List[str] = []
        if polarity > 0.1:
            labels.append("positive")
        elif polarity < -0.1:
            labels.append("negative")
        else:
            labels.append("neutral")
        if urgency > 0.35:
            labels.append("urgent")
        if empathy_gap > 0.2:
            labels.append("needs_empathy")
        return EmotionalSignal(text=text, polarity=round(polarity, 3), urgency=round(urgency, 3), empathy_gap=round(empathy_gap, 3), labels=labels)

    def batch_analyze(self, texts: Iterable[str]) -> List[EmotionalSignal]:
        return [self.analyze_text(text) for text in texts]

    def recommend_response_tone(self, signal: EmotionalSignal) -> Dict[str, float | str]:
        calmness = max(0.0, min(1.0, 0.7 + signal.empathy_gap / 2 - signal.urgency / 4))
        directness = max(0.1, min(1.0, 0.4 + signal.urgency / 2))
        optimism = max(0.1, min(1.0, 0.5 + signal.polarity / 2))
        if "negative" in signal.labels:
            opening = "Acknowledge frustration and confirm ownership."
        elif "positive" in signal.labels:
            opening = "Mirror the positive tone and reinforce progress."
        else:
            opening = "Use a neutral, professional acknowledgement."
        return {
            "opening": opening,
            "calmness": round(calmness, 3),
            "directness": round(directness, 3),
            "optimism": round(optimism, 3),
        }

    def team_heatmap(self, texts: Iterable[str]) -> Dict[str, float]:
        signals = self.batch_analyze(texts)
        if not signals:
            return {"morale": 0.0, "stress": 0.0, "support_need": 0.0}
        morale = mean(max(0.0, s.polarity + 0.5) for s in signals)
        stress = mean(min(1.0, abs(min(0.0, s.polarity)) + s.urgency) for s in signals)
        support_need = mean(min(1.0, s.empathy_gap + s.urgency / 2) for s in signals)
        return {
            "morale": round(morale, 3),
            "stress": round(stress, 3),
            "support_need": round(support_need, 3),
        }


def cosine_affinity(a: EmotionalSignal, b: EmotionalSignal) -> float:
    left = [a.polarity, a.urgency, 1 - a.empathy_gap]
    right = [b.polarity, b.urgency, 1 - b.empathy_gap]
    dot = sum(x * y for x, y in zip(left, right))
    mag = math.sqrt(sum(x * x for x in left)) * math.sqrt(sum(y * y for y in right))
    return round(dot / mag, 3) if mag else 0.0
