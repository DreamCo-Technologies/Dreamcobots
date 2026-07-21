"""
base_bot.py – Abstract base class for all DreamCObots.

Every concrete bot (occupational, app, business, side-hustle) inherits from
``BaseBot``.  The base class wires together:

* NLPEngine       – tokenisation, sentiment, intent detection.
* AdaptiveLearning – interaction history, pattern learning, fine-tune hooks.
* DatasetManager  – dataset registration and selling pipeline.
* MonetizationManager – pricing plans and revenue tracking.

Concrete bots only need to override ``_build_response`` (and optionally
``_setup_datasets`` / ``_setup_plans``) to become fully functional.
"""

import time
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .adaptive_learning import AdaptiveLearning
from .dataset_manager import DatasetManager
from .monetization import MonetizationManager, PricingModel, PricingPlan
from .nlp_engine import NLPEngine


class BaseBot(ABC):
    """
    Abstract base for every DreamCobot.

    Parameters
    ----------
    bot_id   : Unique identifier for this bot instance.
    name     : Human-readable display name.
    domain   : Occupational/business domain (e.g. "healthcare", "legal").
    category : Top-level category: "occupational", "app", "business",
               "side_hustle", or "marketing".
    """

    def __init__(
        self,
        bot_id: Optional[str] = None,
        name: str = "DreamCobot",
        domain: str = "general",
        category: str = "general",
    ):
        self.bot_id: str = bot_id or str(uuid.uuid4())
        self.name: str = name
        self.domain: str = domain
        self.category: str = category
        self.created_at: float = time.time()

        # Core subsystems
        self.nlp = NLPEngine()
        self.learning = AdaptiveLearning(bot_id=self.bot_id)
        self.datasets = DatasetManager(owner_bot_id=self.bot_id)
        self.monetization = MonetizationManager(bot_id=self.bot_id)

        # Emotional state (simple valence/arousal model)
        self._emotion_valence: float = 0.0   # [-1 negative … +1 positive]
        self._emotion_arousal: float = 0.5   # [0 calm … 1 excited]

        # One-time initialisation hooks
        self._setup_datasets()
        self._setup_plans()

    # ------------------------------------------------------------------
    # Public chat interface
    # ------------------------------------------------------------------

    def chat(self, user_input: str, user_id: str = "anonymous") -> str:
        """
        Process a user message and return the bot's response.

        Steps
        -----
        1. Run full NLP pipeline.
        2. Update emotional state based on sentiment.
        3. Build a context-aware response via ``_build_response``.
        4. Record the interaction for adaptive learning.
        5. Return the response string.
        """
        nlp_result = self.nlp.process(user_input)
        self._update_emotion(nlp_result["sentiment_score"])
        response = self._build_response(nlp_result, user_id)
        self.learning.record_interaction(
            user_id=user_id,
            user_input=user_input,
            intent=nlp_result["intent"],
            sentiment=nlp_result["sentiment"],
            sentiment_score=nlp_result["sentiment_score"],
            bot_response=response,
        )
        return response

    def end_session(self, user_id: str = "anonymous") -> None:
        """Signal end of session to trigger adaptive learning updates."""
        self.learning.end_session()
        self.nlp.clear_context()

    # ------------------------------------------------------------------
    # Emotional intelligence helpers
    # ------------------------------------------------------------------

    def current_emotion(self) -> Dict[str, Any]:
        """Return the bot's current emotional state."""
        if self._emotion_valence > 0.3:
            label = "happy"
        elif self._emotion_valence < -0.3:
            label = "concerned"
        else:
            label = "neutral"
        return {
            "label": label,
            "valence": round(self._emotion_valence, 3),
            "arousal": round(self._emotion_arousal, 3),
        }

    def _update_emotion(self, sentiment_score: float) -> None:
        """Smoothly shift emotional state toward the user's sentiment."""
        alpha = 0.3   # EMA smoothing factor
        self._emotion_valence = round(
            (1 - alpha) * self._emotion_valence + alpha * sentiment_score, 3
        )
        self._emotion_arousal = min(
            1.0, self._emotion_arousal + abs(sentiment_score) * 0.05
        )

    # ------------------------------------------------------------------
    # Dataset convenience
    # ------------------------------------------------------------------

    def sell_dataset(self, dataset_id: str, buyer_id: str) -> str:
        """Attempt to sell a dataset and return a confirmation message."""
        try:
            record = self.datasets.sell_dataset(dataset_id, buyer_id)
        except ValueError as exc:
            return f"Sale declined: {exc}"
        if record is None:
            return "Sale could not be completed. Please try again."
        ds = self.datasets.get_dataset(dataset_id)
        name = ds.name if ds else dataset_id
        return (
            f"Thank you! Dataset '{name}' has been sold to buyer '{buyer_id}'. "
            f"Sale ID: {record.sale_id}"
        )

    # ------------------------------------------------------------------
    # Diagnostic / status
    # ------------------------------------------------------------------

    def status(self) -> Dict[str, Any]:
        return {
            "bot_id": self.bot_id,
            "name": self.name,
            "domain": self.domain,
            "category": self.category,
            "emotion": self.current_emotion(),
            "top_intents": self.learning.top_intents(),
            "datasets": self.datasets.sales_summary(),
            "revenue": self.monetization.revenue_summary(),
        }

    # ------------------------------------------------------------------
    # Abstract / overridable hooks
    # ------------------------------------------------------------------

    @abstractmethod
    def _build_response(self, nlp_result: Dict[str, Any], user_id: str) -> str:
        """
        Build and return a response string given the NLP analysis result.

        Subclasses receive the full NLP result dict (tokens, sentiment,
        intent, entities, context_summary) and the user ID.
        """

    def _setup_datasets(self) -> None:
        """
        Override to register domain-specific datasets at initialisation time.
        Called once from ``__init__``.
        """

    def _setup_plans(self) -> None:
        """
        Override to add pricing plans at initialisation time.
        Called once from ``__init__``.
        """
        self.monetization.add_plan(PricingPlan(
            plan_id="free",
            name="Free",
            model=PricingModel.FREEMIUM,
            price_usd=9.99,
            description="10 free interactions, then $9.99/month.",
            features=["Basic Q&A", "Job/task guidance"],
            free_tier_limit=10,
        ))
        self.monetization.add_plan(PricingPlan(
            plan_id="pro",
            name="Pro",
            model=PricingModel.SUBSCRIPTION,
            price_usd=29.99,
            description="Unlimited interactions + dataset access.",
            features=["Unlimited interactions", "Dataset downloads", "Priority support"],
        ))

    # ------------------------------------------------------------------
    # Shared response utilities available to subclasses
    # ------------------------------------------------------------------

    def _emotion_prefix(self) -> str:
        """Return an emotion-aware conversational opener."""
        label = self.current_emotion()["label"]
        prefixes = {
            "happy":     "Great to hear from you! ",
            "concerned": "I sense some frustration – let me help. ",
            "neutral":   "",
        }
        return prefixes.get(label, "")

    def _dataset_offer(self) -> str:
        datasets = self.datasets.list_datasets()
        if not datasets:
            return ""
        names = ", ".join(f"'{d.name}'" for d in datasets[:3])
        return f"\n\n💡 *Available datasets*: {names}. Ask me to sell you one!"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name='{self.name}' domain='{self.domain}'>"
