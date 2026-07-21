"""
adaptive_learning.py – Context-aware adaptive learning for DreamCObots.

Tracks interaction history, recognises usage patterns, adjusts response
confidence weights, and supports lightweight model fine-tuning hooks so bots
grow more human-like over time.
"""

import json
import math
import time
from collections import defaultdict, Counter
from typing import Any, Dict, List, Optional


class AdaptiveLearning:
    """
    Adaptive learning engine attached to each bot instance.

    Capabilities
    ------------
    * Stores a capped interaction history.
    * Accumulates intent frequency to bias future responses.
    * Tracks per-user preferences and emotional history.
    * Exposes a ``fine_tune_hook`` that production code can replace with a
      real ML update call (e.g. LoRA fine-tune, RLHF reward signal).
    * Serialises / deserialises state to JSON for persistence.
    """

    MAX_HISTORY = 500          # maximum stored interactions
    DECAY_FACTOR = 0.95        # weight decay applied per session boundary

    def __init__(self, bot_id: str):
        self.bot_id = bot_id
        self._history: List[Dict[str, Any]] = []
        self._intent_freq: Counter = Counter()
        self._sentiment_history: List[str] = []
        self._user_profiles: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {"interactions": 0, "preferred_intents": Counter(), "sentiment_sum": 0.0}
        )
        self._response_weights: Dict[str, float] = {}
        self._session_count: int = 0

    # ------------------------------------------------------------------
    # Core interaction recording
    # ------------------------------------------------------------------

    def record_interaction(
        self,
        user_id: str,
        user_input: str,
        intent: str,
        sentiment: str,
        sentiment_score: float,
        bot_response: str,
    ) -> None:
        """Record a single turn in the conversation."""
        entry = {
            "timestamp": time.time(),
            "user_id": user_id,
            "input": user_input,
            "intent": intent,
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "response": bot_response,
        }
        self._history.append(entry)
        if len(self._history) > self.MAX_HISTORY:
            self._history.pop(0)

        self._intent_freq[intent] += 1
        self._sentiment_history.append(sentiment)

        profile = self._user_profiles[user_id]
        profile["interactions"] += 1
        profile["preferred_intents"][intent] += 1
        profile["sentiment_sum"] += sentiment_score

    # ------------------------------------------------------------------
    # Pattern recognition helpers
    # ------------------------------------------------------------------

    def top_intents(self, n: int = 5) -> List[str]:
        """Return the n most-frequent intents across all interactions."""
        return [intent for intent, _ in self._intent_freq.most_common(n)]

    def user_sentiment_trend(self, user_id: str) -> str:
        """Return 'improving', 'worsening', or 'stable' for the given user."""
        profile = self._user_profiles.get(user_id)
        if not profile or profile["interactions"] == 0:
            return "stable"
        avg = profile["sentiment_sum"] / profile["interactions"]
        if avg > 0.15:
            return "improving"
        if avg < -0.15:
            return "worsening"
        return "stable"

    def get_response_weight(self, intent: str) -> float:
        """
        Return a learned confidence weight for a given intent.
        Higher weight → bot is more confident / elaborate in that domain.
        """
        base = 1.0
        freq = self._intent_freq.get(intent, 0)
        if freq:
            base += math.log1p(freq) * 0.1
        return round(min(base + self._response_weights.get(intent, 0.0), 3.0), 3)

    def reinforce(self, intent: str, reward: float) -> None:
        """
        Apply a positive (reward > 0) or negative (reward < 0) reinforcement
        signal to adjust future response confidence for the given intent.
        """
        current = self._response_weights.get(intent, 0.0)
        self._response_weights[intent] = round(current + reward * 0.05, 3)

    # ------------------------------------------------------------------
    # Fine-tune hook (overridable for production ML integration)
    # ------------------------------------------------------------------

    def fine_tune_hook(self, new_data: List[Dict[str, Any]]) -> None:
        """
        Placeholder called at session boundaries with new interaction data.

        Override this method in a subclass to trigger a real model update,
        e.g. submitting reward signals to an RLHF pipeline or computing LoRA
        weight deltas.
        """
        # Default: apply weight decay to prevent over-fitting to old data
        for intent in list(self._response_weights):
            self._response_weights[intent] *= self.DECAY_FACTOR

    def end_session(self) -> None:
        """Signal the end of a user session; triggers learning updates."""
        self._session_count += 1
        self.fine_tune_hook(self._history[-50:])    # last 50 turns

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bot_id": self.bot_id,
            "session_count": self._session_count,
            "intent_freq": dict(self._intent_freq),
            "response_weights": self._response_weights,
            "history_size": len(self._history),
        }

    def save(self, filepath: str) -> None:
        with open(filepath, "w") as fh:
            json.dump(self.to_dict(), fh, indent=2)

    @classmethod
    def load(cls, filepath: str) -> "AdaptiveLearning":
        with open(filepath) as fh:
            data = json.load(fh)
        instance = cls(bot_id=data["bot_id"])
        instance._intent_freq = Counter(data.get("intent_freq", {}))
        instance._response_weights = data.get("response_weights", {})
        instance._session_count = data.get("session_count", 0)
        return instance
