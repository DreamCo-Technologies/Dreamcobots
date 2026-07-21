"""
Marketing Bot — tier-aware digital marketing and campaign automation assistant.

Usage
-----
    from bots.marketing_bot.marketing_bot import MarketingBot
    from bots.ai_chatbot.tiers import Tier

    bot = MarketingBot(tier=Tier.PRO)
    response = bot.chat("Write a Twitter thread about our new product launch")
    print(response["message"])
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config, get_upgrade_path
from bots.marketing_bot.tiers import (
    MARKETING_EXTRA_FEATURES,
    MARKETING_CHANNELS,
    get_marketing_tier_info,
)


class MarketingTierError(Exception):
    """Raised when a channel or feature is not available on the current tier."""


class MarketingRequestLimitError(Exception):
    """Raised when the monthly request quota has been exhausted."""


class MarketingBot:
    """
    Tier-aware marketing automation assistant.

    Supported channels (by tier):
      FREE       -- social media drafts, basic SEO tips, email subject lines
      PRO        -- multi-channel campaigns, A/B testing, analytics dashboards
      ENTERPRISE -- full funnel orchestration, influencer matching, white-label

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling channel and feature access.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self.config = get_tier_config(tier)
        self._request_count: int = 0
        self._history: list[dict] = []

    # ------------------------------------------------------------------
    # Core chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str, channel: str | None = None) -> dict:
        """
        Process a marketing request and return a structured response.

        Parameters
        ----------
        message : str
            The user's natural-language marketing request.
        channel : str | None
            Optional channel to target (e.g. ``"social_media"``).

        Returns
        -------
        dict with keys: ``message``, ``channel``, ``tier``,
        ``requests_used``, ``requests_remaining``.
        """
        self._check_request_limit()
        active_channel = channel or self._default_channel(message)
        self._check_channel_access(active_channel)

        self._request_count += 1
        response_text = (
            f"[MarketingBot/{active_channel}] Processed: {message!r}"
        )
        self._history.append({"role": "user", "content": message})
        self._history.append({"role": "assistant", "content": response_text})

        return {
            "message": response_text,
            "channel": active_channel,
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def create_campaign(self, channel: str, brief: str) -> dict:
        """
        Generate a campaign outline for a given channel and brief.

        Returns
        -------
        dict with keys: ``channel``, ``status``, ``campaign``, ``tier``.
        """
        self._check_request_limit()
        self._check_channel_access(channel)
        self._request_count += 1

        return {
            "channel": channel,
            "status": "drafted",
            "campaign": f"[Mock] Campaign for '{channel}' based on brief: {brief!r}",
            "tier": self.tier.value,
        }

    def list_channels(self) -> list[str]:
        """Return the marketing channels available on the current tier."""
        return list(MARKETING_CHANNELS.get(self.tier.value, []))

    def get_history(self) -> list[dict]:
        """Return a copy of the conversation history."""
        return list(self._history)

    def clear_history(self) -> None:
        """Clear conversation history."""
        self._history = []

    # ------------------------------------------------------------------
    # Tier information
    # ------------------------------------------------------------------

    def describe_tier(self) -> str:
        """Print and return a description of the current marketing tier."""
        info = get_marketing_tier_info(self.tier)
        limit = (
            "Unlimited"
            if info["requests_per_month"] is None
            else f"{info['requests_per_month']:,}"
        )
        lines = [
            f"=== {info['name']} Marketing Bot Tier ===",
            f"Price   : ${info['price_usd_monthly']:.2f}/month",
            f"Requests: {limit}/month",
            f"Support : {info['support_level']}",
            "",
            "Marketing features:",
        ]
        for feat in info["marketing_features"]:
            lines.append(f"  ✓ {feat}")
        lines.append("")
        lines.append("Available channels:")
        for ch in info["channels"]:
            lines.append(f"  • {ch}")
        output = "\n".join(lines)
        print(output)
        return output

    def show_upgrade_path(self) -> str:
        """Print details about the next available tier upgrade."""
        next_tier = get_upgrade_path(self.tier)
        if next_tier is None:
            msg = f"You are already on the highest tier ({self.config.name})."
        else:
            msg = (
                f"Upgrade to {next_tier.name} for "
                f"${next_tier.price_usd_monthly:.2f}/month to unlock "
                f"multi-channel campaigns and advanced analytics."
            )
        print(msg)
        return msg

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _default_channel(self, message: str) -> str:
        available = MARKETING_CHANNELS.get(self.tier.value, ["social_media"])
        lower = message.lower()
        if any(kw in lower for kw in ("twitter", "instagram", "facebook", "social")):
            return "social_media"
        if "email" in lower or "newsletter" in lower:
            return "email_marketing"
        if "seo" in lower or "search" in lower:
            return "seo"
        if "ad" in lower or "ppc" in lower:
            return "paid_ads"
        if "influencer" in lower:
            return "influencer"
        return available[0] if available else "social_media"

    def _check_channel_access(self, channel: str) -> None:
        allowed = MARKETING_CHANNELS.get(self.tier.value, [])
        if channel not in allowed:
            raise MarketingTierError(
                f"Channel '{channel}' is not available on the "
                f"{self.config.name} tier. Upgrade to access it."
            )

    def _check_request_limit(self) -> None:
        limit = self.config.requests_per_month
        if limit is not None and self._request_count >= limit:
            raise MarketingRequestLimitError(
                f"Monthly request limit of {limit} reached on the "
                f"{self.config.name} tier."
            )

    def _requests_remaining(self) -> int | None:
        limit = self.config.requests_per_month
        if limit is None:
            return None
        return max(0, limit - self._request_count)
