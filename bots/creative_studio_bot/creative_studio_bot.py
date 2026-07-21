"""
Creative Studio Bot — Main Entry Point

An AI-powered creative assistant for the DreamCobots ecosystem.

Core capabilities:
  • Music Creation        — composition, lyrics, and audio analysis (MusicCreator)
  • Film & Script Writing — screenplay generation, storyboarding, cinematography advice (FilmCreator)
  • Art & 3-D Modelling   — artwork generation, 3-D model specs, colour palettes (ArtCreator)
  • Content Strategy      — viral posts, content calendars, engagement analytics (ContentStrategyEngine)
  • Meme Generation       — meme content, trend analysis, virality prediction (MemeGenerator)

Tier limits:
  - FREE:       3 creations/day, basic tools, watermarked exports.
  - PRO:        50 creations/day, advanced AI tools, HD exports.
  - ENTERPRISE: Unlimited creations, commercial rights, white-label, API access.

Adheres to the DreamCobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.

Usage
-----
    from bots.creative_studio_bot import CreativeStudioBot, Tier

    studio = CreativeStudioBot(tier=Tier.PRO)

    track = studio.create_music("jazz", "relaxed")
    script = studio.create_film_script("thriller", "A hacker uncovers a global conspiracy")
    art = studio.create_artwork("impressionist", "sunset over Paris")
    strategy = studio.create_content_strategy("instagram", "travel photography")
    meme = studio.generate_meme("Monday mornings")
    print(studio.get_creative_dashboard())
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))

from tiers import Tier, get_tier_config, get_upgrade_path  # noqa: F401
from bots.creative_studio_bot.tiers import BOT_FEATURES, get_bot_tier_info, DAILY_CREATION_LIMITS

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401

from bots.creative_studio_bot.content_creator import MusicCreator, FilmCreator, ArtCreator
from bots.creative_studio_bot.influencer_engine import ContentStrategyEngine, MemeGenerator


class CreativeStudioBotError(Exception):
    """Raised when a tier limit or feature restriction is violated."""


class CreativeStudioBot:
    """AI-powered creative studio assistant with tier-based feature gating.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling daily limits and feature access.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self.config = get_tier_config(tier)
        self.tier_info = get_bot_tier_info(tier)
        self.flow = GlobalAISourcesFlow(bot_name="CreativeStudioBot")

        self._music = MusicCreator()
        self._film = FilmCreator()
        self._art = ArtCreator()
        self._strategy = ContentStrategyEngine()
        self._meme = MemeGenerator()

        self._daily_count: int = 0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_daily_limit(self) -> None:
        """Raise CreativeStudioBotError if the daily creation limit is exceeded."""
        limit = DAILY_CREATION_LIMITS[self.tier.value]
        if limit is not None and self._daily_count >= limit:
            upgrade = get_upgrade_path(self.tier)
            upgrade_msg = (
                f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly}/mo) for more creations."
                if upgrade
                else ""
            )
            raise CreativeStudioBotError(
                f"Daily creation limit of {limit} reached for the {self.tier.value.upper()} tier.{upgrade_msg}"
            )

    def _check_feature(self, feature: str) -> None:
        """Raise CreativeStudioBotError if the feature is not available on the current tier."""
        if feature not in BOT_FEATURES[self.tier.value]:
            upgrade = get_upgrade_path(self.tier)
            upgrade_msg = (
                f" Upgrade to {upgrade.name} for access." if upgrade else ""
            )
            raise CreativeStudioBotError(
                f"Feature '{feature}' is not available on the {self.tier.value.upper()} tier.{upgrade_msg}"
            )

    def _record_creation(self) -> None:
        self._daily_count += 1

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_music(self, genre: str, mood: str, **kwargs) -> dict:
        """Compose an original piece of music.

        Parameters
        ----------
        genre : str
            Musical genre.
        mood : str
            Desired emotional mood.
        **kwargs
            Optional: ``duration_secs`` (int, default 120).

        Returns
        -------
        dict
            Composition data from MusicCreator.
        """
        self._check_feature("music_creation")
        self._check_daily_limit()
        result = self._music.compose_music(genre, mood, kwargs.get("duration_secs", 120))
        self._record_creation()
        return result

    def create_film_script(self, genre: str, premise: str, **kwargs) -> dict:
        """Generate a screenplay.

        Parameters
        ----------
        genre : str
            Film genre.
        premise : str
            One-sentence logline.
        **kwargs
            Optional: ``num_scenes`` (int, default 5).

        Returns
        -------
        dict
            Script data from FilmCreator.
        """
        self._check_feature("film_scripting")
        self._check_daily_limit()
        result = self._film.generate_script(genre, premise, kwargs.get("num_scenes", 5))
        self._record_creation()
        return result

    def create_artwork(self, style: str, subject: str, **kwargs) -> dict:
        """Generate artwork description and parameters.

        Parameters
        ----------
        style : str
            Artistic style.
        subject : str
            Subject matter.
        **kwargs
            Optional: ``medium`` (str, default "digital").

        Returns
        -------
        dict
            Artwork data from ArtCreator.
        """
        self._check_feature("art_generation")
        self._check_daily_limit()
        result = self._art.generate_artwork(style, subject, kwargs.get("medium", "digital"))
        self._record_creation()
        return result

    def create_content_strategy(self, platform: str, niche: str, **kwargs) -> dict:
        """Generate a social media content calendar.

        Parameters
        ----------
        platform : str
            Target platform.
        niche : str
            Content niche.
        **kwargs
            Optional: ``weeks`` (int, default 4).

        Returns
        -------
        dict
            Content calendar from ContentStrategyEngine.
        """
        self._check_feature("content_calendar")
        self._check_daily_limit()
        result = self._strategy.create_content_calendar(platform, niche, kwargs.get("weeks", 4))
        self._record_creation()
        return result

    def generate_meme(self, topic: str, **kwargs) -> dict:
        """Generate meme content.

        Parameters
        ----------
        topic : str
            Subject of the meme.
        **kwargs
            Optional: ``style`` (str), ``target_audience`` (str).

        Returns
        -------
        dict
            Meme data from MemeGenerator.
        """
        self._check_feature("meme_generator")
        self._check_daily_limit()
        result = self._meme.generate_meme(
            topic,
            kwargs.get("style", "relatable"),
            kwargs.get("target_audience", "gen_z"),
        )
        self._record_creation()
        return result

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def get_creative_dashboard(self) -> dict:
        """Return a summary of bot status, tier info, and usage statistics.

        Returns
        -------
        dict
            Dashboard with tier details, feature list, and creation counts.
        """
        limit = DAILY_CREATION_LIMITS[self.tier.value]
        upgrade = get_upgrade_path(self.tier)

        return {
            "bot_name": "Creative Studio Bot",
            "tier": self.tier.value,
            "tier_display": self.config.name,
            "price_usd_monthly": self.config.price_usd_monthly,
            "daily_creation_limit": limit,
            "creations_today": self._daily_count,
            "creations_remaining": (limit - self._daily_count) if limit is not None else "unlimited",
            "features": BOT_FEATURES[self.tier.value],
            "commercial_rights": self.tier_info["commercial_rights"],
            "upgrade_available": upgrade is not None,
            "upgrade_to": upgrade.name if upgrade else None,
            "upgrade_price_usd": upgrade.price_usd_monthly if upgrade else None,
            "modules": ["MusicCreator", "FilmCreator", "ArtCreator", "ContentStrategyEngine", "MemeGenerator"],
        }

    # ------------------------------------------------------------------
    # Informational helpers
    # ------------------------------------------------------------------

    def describe_tier(self) -> str:
        """Return a human-readable tier description."""
        info = self.tier_info
        limit_str = str(info["daily_creation_limit"]) if info["daily_creation_limit"] else "Unlimited"
        return (
            f"Creative Studio Bot — {info['name']} Tier\n"
            f"  Price:           ${info['price_usd_monthly']}/month\n"
            f"  Daily limit:     {limit_str} creations\n"
            f"  Commercial use:  {'Yes' if info['commercial_rights'] else 'No'}\n"
            f"  Support:         {info['support_level']}\n"
            f"  Features:        {', '.join(info['features'])}\n"
        )
