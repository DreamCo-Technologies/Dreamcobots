"""
DreamCo Localized Bot — Main Entry Point.

Composes all Localized Bot sub-systems into a unified Cross-Cultural/Regional
bot platform for DreamCo Buddy:

  • Region Database        — 30+ global regions with industry, language, timezone data
  • Localization Engine    — content adaptation, translation, cultural tips
  • Global Leaderboard     — community voting and ranking for regional bots

Architecture:
    DreamCoBots
    │
    ├── buddybot
    │
    ├── localized_bot
    │     ├── region_database
    │     ├── localization_engine
    │     └── global_leaderboard
    │
    └── ...

Usage
-----
    from bots.localized_bot import LocalizedBot, Tier

    bot = LocalizedBot(tier=Tier.PRO)
    result = bot.adapt_content("Hello!", "Japan", industry="Technology")
    print(result)
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401

from bots.localized_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_BASIC_TRANSLATION,
    FEATURE_FULL_TRANSLATION,
    FEATURE_INDUSTRY_ADAPTION,
    FEATURE_REGIONAL_CHALLENGES,
    FEATURE_GLOBAL_LEADERBOARD_VOTE,
    FEATURE_CUSTOM_LOCALE,
    FEATURE_PRIVATE_REGIONAL_BOTS,
    FEATURE_API_ACCESS,
    FEATURE_ANALYTICS,
    FEATURE_WHITE_LABEL,
)
from bots.localized_bot.region_database import RegionDatabase
from bots.localized_bot.localization_engine import LocalizationEngine
from bots.localized_bot.global_leaderboard import GlobalLeaderboard


class LocalizedBotError(Exception):
    """Base error class for the DreamCo Localized Bot."""


class LocalizedBotTierError(LocalizedBotError):
    """Raised when the current tier does not support the requested feature."""

    def __init__(self, feature: str, required_tier: str) -> None:
        super().__init__(
            f"Feature '{feature}' requires at least the {required_tier} tier. "
            "Upgrade your plan to unlock this feature."
        )
        self.feature = feature
        self.required_tier = required_tier


class LocalizedBot:
    """
    DreamCo Localized Bot — Cross-Cultural/Regional bot system.

    Parameters
    ----------
    tier : Tier
        The subscription tier that controls feature access and region limits.
    """

    def __init__(self, tier: Tier) -> None:
        self._tier = tier
        self._config: TierConfig = get_tier_config(tier)
        self._region_db = RegionDatabase()
        self._localization = LocalizationEngine()
        self._leaderboard = GlobalLeaderboard()

    # ------------------------------------------------------------------
    # Tier helpers
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str, required_tier: str) -> None:
        if not self._config.has_feature(feature):
            raise LocalizedBotTierError(feature, required_tier)

    def _check_region_limit(self, region_id: str, regions_used: list[str]) -> None:
        """Raise LocalizedBotTierError if adding *region_id* would exceed the tier limit."""
        max_r = self._config.max_regions
        if max_r is not None and region_id not in regions_used and len(regions_used) >= max_r:
            raise LocalizedBotTierError(
                "additional_regions",
                "Pro" if self._tier == Tier.FREE else "Enterprise",
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def adapt_content(
        self,
        content: str,
        target_region_id: str,
        industry: str | None = None,
    ) -> dict:
        """
        Adapt *content* for *target_region_id*.

        Basic content adaptation is available on all tiers (FREE+).
        Industry-specific adaptation requires PRO or higher.
        """
        if industry is not None:
            self._require_feature(FEATURE_INDUSTRY_ADAPTION, "Pro")
        return self._localization.adapt_content(content, target_region_id, industry)

    def translate_message(self, text: str, target_language: str) -> dict:
        """
        Translate *text* to *target_language*.

        Basic translation is available on all tiers (FREE+).
        """
        return self._localization.translate_message(text, target_language)

    def list_regions(self) -> list:
        """Return all available regions from the database."""
        return self._region_db.list_regions()

    def get_cultural_tips(self, region_id: str) -> list[str]:
        """Return cultural tips for *region_id*. Available on all tiers (FREE+)."""
        return self._localization.get_cultural_tips(region_id)

    def register_regional_bot(
        self,
        bot_name: str,
        creator_id: str,
        region_id: str,
        description: str,
        category: str,
    ) -> dict:
        """
        Register a new bot on the Global Leaderboard.

        Requires PRO or higher (private regional bots require ENTERPRISE).
        """
        self._require_feature(FEATURE_GLOBAL_LEADERBOARD_VOTE, "Pro")
        return self._leaderboard.register_bot(
            bot_name, creator_id, region_id, description, category
        )

    def vote_for_bot(self, bot_id: str, voter_id: str, score: int) -> dict:
        """Cast a vote for a bot. Requires PRO or higher."""
        self._require_feature(FEATURE_GLOBAL_LEADERBOARD_VOTE, "Pro")
        return self._leaderboard.vote_for_bot(bot_id, voter_id, score)

    def get_leaderboard(
        self,
        region_id: str | None = None,
        category: str | None = None,
    ) -> list:
        """
        Return the global (or filtered) leaderboard.

        Available on all tiers for read access.
        """
        return self._leaderboard.get_leaderboard(region_id=region_id, category=category)

    def get_tier_info(self) -> dict:
        """Return a summary of the current tier configuration."""
        cfg = self._config
        return {
            "tier": cfg.tier.value,
            "name": cfg.name,
            "price_usd_monthly": cfg.price_usd_monthly,
            "max_regions": cfg.max_regions,
            "features": list(cfg.features),
            "support_level": cfg.support_level,
        }

    def get_upgrade_info(self) -> dict | None:
        """Return info about the next tier upgrade, or None if already at highest tier."""
        next_cfg = get_upgrade_path(self._tier)
        if next_cfg is None:
            return None
        return {
            "tier": next_cfg.tier.value,
            "name": next_cfg.name,
            "price_usd_monthly": next_cfg.price_usd_monthly,
            "max_regions": next_cfg.max_regions,
            "features": list(next_cfg.features),
        }

    def chat(self, message: str) -> str:
        """
        Simple conversational interface.

        Provides region/localization guidance based on the user's message.
        """
        msg_lower = message.lower()
        if "region" in msg_lower or "country" in msg_lower:
            regions = self._region_db.list_regions()
            names = [r["region_name"] for r in regions[:5]]
            return (
                f"I support {len(regions)} regions including: "
                + ", ".join(names)
                + " and more. Ask me to adapt content or get cultural tips!"
            )
        if "tier" in msg_lower or "plan" in msg_lower or "upgrade" in msg_lower:
            info = self.get_tier_info()
            return (
                f"You are on the {info['name']} plan (${info['price_usd_monthly']}/mo). "
                f"It includes {len(info['features'])} features and supports "
                f"{'unlimited' if info['max_regions'] is None else info['max_regions']} region(s)."
            )
        if "translate" in msg_lower:
            return (
                "I can translate messages to any supported language. "
                "Use translate_message(text, target_language) to get started."
            )
        if "cultural" in msg_lower or "tip" in msg_lower:
            return (
                "I have cultural tips for many regions. "
                "Use get_cultural_tips(region_id) to learn about a specific region."
            )
        return (
            "Hello! I'm DreamCo Localized Bot. I can help you adapt content for "
            "different regions, translate messages, and provide cultural insights. "
            "Ask me about regions, translations, or cultural tips!"
        )
