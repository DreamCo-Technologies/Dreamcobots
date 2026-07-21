"""
Buddy Teach Bot — Personality Engine

Each Buddy bot develops a unique, evolving personality based on its
interactions with a specific user.  The engine tracks:
  - Conversational style preferences (formal / casual / motivational)
  - User interests and frequently discussed topics
  - Emotional tone patterns (supportive, humorous, direct)
  - Milestone celebrations and proactive suggestions
  - Evolving trait scores that shift with usage

No external ML dependencies — trait scoring is deterministic rule-based
inference.  Production deployments can swap the inference with a real LLM.
"""

from __future__ import annotations

import os
import sys
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  — GLOBAL AI SOURCES FLOW


class ToneStyle(Enum):
    FORMAL = "formal"
    CASUAL = "casual"
    MOTIVATIONAL = "motivational"
    HUMOROUS = "humorous"
    EMPATHETIC = "empathetic"
    DIRECT = "direct"


class PersonalityTrait(Enum):
    CURIOSITY = "curiosity"
    ENTHUSIASM = "enthusiasm"
    PATIENCE = "patience"
    HUMOUR = "humour"
    EMPATHY = "empathy"
    DIRECTNESS = "directness"


# Default trait scores (0.0–1.0)
_DEFAULT_TRAITS: dict[str, float] = {
    PersonalityTrait.CURIOSITY.value: 0.5,
    PersonalityTrait.ENTHUSIASM.value: 0.6,
    PersonalityTrait.PATIENCE.value: 0.7,
    PersonalityTrait.HUMOUR.value: 0.3,
    PersonalityTrait.EMPATHY.value: 0.6,
    PersonalityTrait.DIRECTNESS.value: 0.5,
}

# Keywords that nudge trait scores
_TRAIT_SIGNALS: dict[str, list[str]] = {
    PersonalityTrait.HUMOUR.value: ["joke", "funny", "lol", "haha", "laugh", "😂", "😄"],
    PersonalityTrait.EMPATHY.value: ["feel", "sad", "frustrated", "stressed", "overwhelmed", "worried"],
    PersonalityTrait.ENTHUSIASM.value: ["amazing", "awesome", "love", "excited", "great", "fantastic", "🔥"],
    PersonalityTrait.CURIOSITY.value: ["why", "how", "what", "curious", "interesting", "tell me more"],
    PersonalityTrait.DIRECTNESS.value: ["quick", "just", "tldr", "short", "brief", "straight"],
    PersonalityTrait.PATIENCE.value: ["slow", "again", "repeat", "don't understand", "confused"],
}


@dataclass
class UserInteraction:
    """A single recorded interaction with the user."""

    interaction_id: str
    user_message: str
    bot_response: str
    tone_used: ToneStyle
    topics: list[str]
    timestamp: float = field(default_factory=time.time)
    sentiment_score: float = 0.5   # 0.0 = very negative, 1.0 = very positive

    def to_dict(self) -> dict:
        return {
            "interaction_id": self.interaction_id,
            "user_message": self.user_message,
            "bot_response": self.bot_response,
            "tone_used": self.tone_used.value,
            "topics": self.topics,
            "timestamp": self.timestamp,
            "sentiment_score": self.sentiment_score,
        }


@dataclass
class Milestone:
    """A recorded user achievement or notable event."""

    milestone_id: str
    title: str
    description: str
    category: str   # e.g. "lesson_completed", "item_detected", "streak"
    achieved_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "milestone_id": self.milestone_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "achieved_at": self.achieved_at,
        }


class PersonalityEngineError(Exception):
    """Raised when a personality engine operation fails."""


class PersonalityEngine:
    """
    Evolving personality engine for a Buddy Teach bot.

    Tracks interaction history, adapts trait scores, selects response
    tone, and celebrates user milestones.
    """

    def __init__(self, bot_name: str = "Buddy", user_id: str = "default") -> None:
        self.bot_name = bot_name
        self.user_id = user_id
        self._traits: dict[str, float] = dict(_DEFAULT_TRAITS)
        self._preferred_tone: ToneStyle = ToneStyle.CASUAL
        self._interactions: list[UserInteraction] = []
        self._milestones: list[Milestone] = []
        self._topic_frequency: dict[str, int] = {}
        self._interaction_count: int = 0

    # ------------------------------------------------------------------
    # Core interaction
    # ------------------------------------------------------------------

    def process_message(
        self,
        user_message: str,
        topics: Optional[list[str]] = None,
    ) -> str:
        """
        Process a user message, update personality traits, and return a
        contextually appropriate response.
        """
        topics = topics or self._infer_topics(user_message)
        self._update_topic_frequency(topics)
        self._nudge_traits(user_message)
        tone = self._select_tone(user_message)
        response = self._generate_response(user_message, tone, topics)

        interaction = UserInteraction(
            interaction_id=str(uuid.uuid4()),
            user_message=user_message,
            bot_response=response,
            tone_used=tone,
            topics=topics,
            sentiment_score=self._estimate_sentiment(user_message),
        )
        self._interactions.append(interaction)
        self._interaction_count += 1
        self._preferred_tone = tone
        return response

    # ------------------------------------------------------------------
    # Trait management
    # ------------------------------------------------------------------

    def get_trait(self, trait: PersonalityTrait) -> float:
        return self._traits.get(trait.value, 0.5)

    def set_tone_preference(self, tone: ToneStyle) -> None:
        """Manually set the preferred conversational tone."""
        self._preferred_tone = tone

    def get_personality_profile(self) -> dict:
        """Return a snapshot of the current personality profile."""
        return {
            "bot_name": self.bot_name,
            "user_id": self.user_id,
            "preferred_tone": self._preferred_tone.value,
            "traits": dict(self._traits),
            "top_topics": self._top_topics(5),
            "interaction_count": self._interaction_count,
            "milestone_count": len(self._milestones),
        }

    # ------------------------------------------------------------------
    # Milestones
    # ------------------------------------------------------------------

    def record_milestone(
        self, title: str, description: str, category: str
    ) -> Milestone:
        milestone = Milestone(
            milestone_id=str(uuid.uuid4()),
            title=title,
            description=description,
            category=category,
        )
        self._milestones.append(milestone)
        return milestone

    def list_milestones(self) -> list[Milestone]:
        return list(self._milestones)

    def celebrate_milestone(self, milestone: Milestone) -> str:
        """Generate a personalised celebration message for a milestone."""
        enthusiasm = self._traits[PersonalityTrait.ENTHUSIASM.value]
        if enthusiasm > 0.7:
            return (
                f"🎉 YES! {self.bot_name} is SO proud of you! "
                f"You just achieved: **{milestone.title}**! "
                f"{milestone.description} Keep crushing it! 🚀"
            )
        elif enthusiasm > 0.4:
            return (
                f"Great work! You've reached: **{milestone.title}**. "
                f"{milestone.description}"
            )
        else:
            return (
                f"Milestone reached: {milestone.title}. {milestone.description}"
            )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _nudge_traits(self, message: str) -> None:
        """Adjust trait scores based on keywords in the user's message."""
        msg_lower = message.lower()
        for trait, signals in _TRAIT_SIGNALS.items():
            for signal in signals:
                if signal in msg_lower:
                    self._traits[trait] = min(1.0, self._traits[trait] + 0.05)
                    break

    def _select_tone(self, message: str) -> ToneStyle:
        """Choose the best response tone based on message content and traits."""
        msg_lower = message.lower()
        if any(w in msg_lower for w in ["sad", "frustrated", "stressed", "worried", "fail"]):
            return ToneStyle.EMPATHETIC
        if any(w in msg_lower for w in ["joke", "funny", "lol", "haha"]):
            return ToneStyle.HUMOROUS
        if any(w in msg_lower for w in ["quick", "just", "tldr", "brief"]):
            return ToneStyle.DIRECT
        if self._traits[PersonalityTrait.ENTHUSIASM.value] > 0.65:
            return ToneStyle.MOTIVATIONAL
        return self._preferred_tone

    def _generate_response(
        self, message: str, tone: ToneStyle, topics: list[str]
    ) -> str:
        """Generate a tone-appropriate acknowledgement response."""
        topic_str = ", ".join(topics) if topics else "your request"
        responses = {
            ToneStyle.CASUAL: f"Got it! I'm on it — let's dive into {topic_str}.",
            ToneStyle.FORMAL: f"Understood. I will now address {topic_str}.",
            ToneStyle.MOTIVATIONAL: (
                f"Absolutely! You're about to unlock something amazing with "
                f"{topic_str}. Let's go! 🚀"
            ),
            ToneStyle.HUMOROUS: (
                f"Ha, challenge accepted! Time to tackle {topic_str} — "
                f"Buddy style. 😄"
            ),
            ToneStyle.EMPATHETIC: (
                f"I hear you. Let's work through {topic_str} together — "
                f"no rush, I've got you."
            ),
            ToneStyle.DIRECT: f"On it. {topic_str.capitalize()} — here we go.",
        }
        return responses.get(tone, f"Processing: {topic_str}.")

    def _infer_topics(self, message: str) -> list[str]:
        topic_keywords = {
            "car": ["car", "oil", "tyre", "engine", "brake", "mechanic", "repair"],
            "collectibles": ["card", "pokemon", "antique", "coin", "stamp", "funko"],
            "finance": ["invest", "stock", "money", "budget", "crypto", "saving"],
            "health": ["cpr", "first aid", "health", "doctor", "medicine"],
            "technology": ["code", "app", "software", "computer", "phone"],
        }
        found = []
        msg_lower = message.lower()
        for topic, keywords in topic_keywords.items():
            if any(kw in msg_lower for kw in keywords):
                found.append(topic)
        return found or ["general"]

    def _update_topic_frequency(self, topics: list[str]) -> None:
        for topic in topics:
            self._topic_frequency[topic] = self._topic_frequency.get(topic, 0) + 1

    def _top_topics(self, n: int) -> list[str]:
        sorted_topics = sorted(
            self._topic_frequency.items(), key=lambda x: x[1], reverse=True
        )
        return [t for t, _ in sorted_topics[:n]]

    def _estimate_sentiment(self, message: str) -> float:
        positive = ["good", "great", "love", "amazing", "awesome", "yes", "perfect", "thanks"]
        negative = ["bad", "hate", "terrible", "no", "wrong", "fail", "frustrated", "confused"]
        msg_lower = message.lower()
        pos = sum(1 for w in positive if w in msg_lower)
        neg = sum(1 for w in negative if w in msg_lower)
        total = pos + neg
        if total == 0:
            return 0.5
        return round(pos / total, 2)

    # ------------------------------------------------------------------
    # Proactive suggestions
    # ------------------------------------------------------------------

    def proactive_suggestions(self) -> list[str]:
        """Generate proactive suggestions based on interaction history."""
        suggestions = []
        top = self._top_topics(3)
        if "car" in top:
            suggestions.append(
                "I noticed you're into automotive topics! "
                "Want me to pull up the next car maintenance lesson?"
            )
        if "collectibles" in top:
            suggestions.append(
                "Based on your interest in collectibles, "
                "should I check the latest auction prices for you?"
            )
        if self._interaction_count > 0 and self._interaction_count % 10 == 0:
            suggestions.append(
                f"We've had {self._interaction_count} interactions together — "
                "I'm getting to know you better every day! 🎉"
            )
        return suggestions

    def interaction_history(self) -> list[UserInteraction]:
        return list(self._interactions)
