"""
Dreamcobots AI Chatbot — tier-aware conversational interface.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.

Usage
-----
    from chatbot import Chatbot, Tier

    bot = Chatbot(tier=Tier.FREE)
    response = bot.chat("What is machine learning?")
    print(response["message"])
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tiers import Tier, get_tier_config, get_upgrade_path
from bots.ai_chatbot.tiers import (
    CHATBOT_EXTRA_FEATURES,
    CHATBOT_MODELS,
    get_chatbot_tier_info,
)
from models.registry import get_model_info
from framework import GlobalAISourcesFlow


class ChatbotTierError(Exception):
    """Raised when a chatbot feature is not available on the current tier."""


class ChatbotRequestLimitError(Exception):
    """Raised when the monthly request quota has been exhausted."""


class Chatbot:
    """
    Tier-aware AI chatbot.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling model access and feature availability.
    default_model : str | None
        Model ID to use by default.  Defaults to the cheapest model available
        on the given tier.
    """

    def __init__(self, tier: Tier = Tier.FREE, default_model: str | None = None):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._history: list[dict] = []
        self._request_count: int = 0
        self._available_models: list[str] = CHATBOT_MODELS[tier.value]
        self.flow = GlobalAISourcesFlow(bot_name="AIChatbot")

        if default_model is not None:
            if default_model not in self._available_models:
                raise ChatbotTierError(
                    f"Model '{default_model}' is not available on the "
                    f"{self.config.name} tier."
                )
            self.default_model = default_model
        else:
            self.default_model = self._available_models[0]

    # ------------------------------------------------------------------
    # Core chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str, model: str | None = None) -> dict:
        """
        Send a message and receive a response.

        Parameters
        ----------
        message : str
            The user's input message.
        model : str | None
            Override the default model for this request.

        Returns
        -------
        dict with keys: ``message``, ``model``, ``tier``,
        ``history_turns``, ``requests_used``, ``requests_remaining``.
        """
        self._check_request_limit()
        active_model = model or self.default_model
        self._check_model_access(active_model)

        self._request_count += 1
        model_info = get_model_info(active_model)
        response_text = (
            f"[{model_info.display_name}] Mock response to: {message!r}"
        )
        self._history.append({"role": "user", "content": message})
        self._history.append({"role": "assistant", "content": response_text})
        self._trim_history()

        return {
            "message": response_text,
            "model": active_model,
            "tier": self.tier.value,
            "history_turns": len(self._history) // 2,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def clear_history(self) -> None:
        """Clear conversation history."""
        self._history = []

    def get_history(self) -> list[dict]:
        """Return a copy of the current conversation history."""
        return list(self._history)

    # ------------------------------------------------------------------
    # Tier information
    # ------------------------------------------------------------------

    def describe_tier(self) -> str:
        """Print and return a description of the current chatbot tier."""
        info = get_chatbot_tier_info(self.tier)
        limit = (
            "Unlimited"
            if info["requests_per_month"] is None
            else f"{info['requests_per_month']:,}"
        )
        lines = [
            f"=== {info['name']} Chatbot Tier ===",
            f"Price  : ${info['price_usd_monthly']:.2f}/month",
            f"Requests: {limit}/month",
            f"Support : {info['support_level']}",
            "",
            "Platform features:",
        ]
        for feat in info["platform_features"]:
            lines.append(f"  ✓ {feat.replace('_', ' ').title()}")
        lines.append("")
        lines.append("Chatbot extras:")
        for feat in info["chatbot_features"]:
            lines.append(f"  ✓ {feat}")
        lines.append("")
        lines.append("Available NLP models:")
        for mid in info["available_models"]:
            m = get_model_info(mid)
            lines.append(f"  • {m.display_name}")
        output = "\n".join(lines)
        print(output)
        return output

    def show_upgrade_path(self) -> str:
        """Print details about the next available tier upgrade."""
        next_cfg = get_upgrade_path(self.tier)
        if next_cfg is None:
            msg = f"You are already on the top-tier plan ({self.config.name})."
            print(msg)
            return msg

        current_extras = set(CHATBOT_EXTRA_FEATURES[self.tier.value])
        new_extras = [
            f for f in CHATBOT_EXTRA_FEATURES[next_cfg.tier.value]
            if f not in current_extras
        ]
        current_models = set(CHATBOT_MODELS[self.tier.value])
        new_models = [
            get_model_info(mid)
            for mid in CHATBOT_MODELS[next_cfg.tier.value]
            if mid not in current_models
        ]

        lines = [
            f"=== Upgrade: {self.config.name} → {next_cfg.name} ===",
            f"New price: ${next_cfg.price_usd_monthly:.2f}/month",
            "",
            "New chatbot features:",
        ]
        for feat in new_extras:
            lines.append(f"  + {feat}")
        lines.append("")
        lines.append("New NLP models unlocked:")
        for m in new_models:
            lines.append(f"  + {m.display_name}")
        lines.append(
            f"\nTo upgrade, set tier=Tier.{next_cfg.tier.name} when "
            "constructing Chatbot or contact support."
        )
        output = "\n".join(lines)
        print(output)
        return output

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_model_access(self, model_id: str) -> None:
        if model_id not in self._available_models:
            model_info = get_model_info(model_id)
            note = model_info.paid_upgrade_note or (
                f"Upgrade to {model_info.min_tier.name} to access "
                f"'{model_info.display_name}'."
            )
            raise ChatbotTierError(
                f"Model '{model_id}' is not available on the "
                f"{self.config.name} chatbot tier. {note}"
            )

    def _check_request_limit(self) -> None:
        limit = self.config.requests_per_month
        if limit is not None and self._request_count >= limit:
            raise ChatbotRequestLimitError(
                f"Monthly request limit of {limit:,} reached on the "
                f"{self.config.name} tier. Please upgrade to continue."
            )

    def _requests_remaining(self) -> str:
        limit = self.config.requests_per_month
        if limit is None:
            return "unlimited"
        return str(max(limit - self._request_count, 0))

    def _trim_history(self) -> None:
        """Keep only the most recent turns based on tier limits."""
        max_turns_map = {
            Tier.FREE: 5,
            Tier.PRO: 50,
            Tier.ENTERPRISE: None,
        }
        max_turns = max_turns_map[self.tier]
        if max_turns is not None:
            max_entries = max_turns * 2  # each turn = user + assistant message
            if len(self._history) > max_entries:
                self._history = self._history[-max_entries:]
