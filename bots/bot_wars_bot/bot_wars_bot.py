"""
DreamCo Bot Wars Bot — Main Entry Point.

Composes all Bot Wars sub-systems into a single platform:

  • Competition Engine   — create/join competitions, submit bots, score and rank them
  • Challenge Manager   — global DreamCo Bot Wars campaigns and challenges
  • Drag-Drop Builder   — visual, no-code bot composition for non-developers

Architecture:
    DreamCoBots
    │
    ├── buddybot
    │
    ├── ai_level_up_bot
    │
    ├── bot_wars_bot
    │     ├── competition_engine
    │     ├── challenge_manager
    │     └── drag_drop_builder
    │
    └── ...

Usage
-----
    from bots.bot_wars_bot import BotWarsBot, Tier

    bot = BotWarsBot(tier=Tier.PRO)
    comp = bot.create_competition("Summer Showdown", "creativity", "Best creative bot!", 500)
    print(comp)
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from bots.bot_wars_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_VIEW_COMPETITIONS,
    FEATURE_COMMUNITY_LEADERBOARD,
    FEATURE_JOIN_COMPETITIONS,
    FEATURE_DRAG_DROP_BUILDER,
    FEATURE_HOST_PRIVATE_TOURNAMENTS,
)
from bots.bot_wars_bot.competition_engine import CompetitionEngine, CompetitionEngineError
from bots.bot_wars_bot.challenge_manager import ChallengeManager, ChallengeManagerError
from bots.bot_wars_bot.drag_drop_builder import DragDropBuilder, DragDropBuilderError

from typing import Optional
from framework import GlobalAISourcesFlow  # noqa: F401


class BotWarsBotError(Exception):
    """Base exception for Bot Wars Bot errors."""


class BotWarsTierError(BotWarsBotError):
    """Raised when accessing a feature unavailable on the current tier."""


class BotWarsBot:
    """DreamCo Bot Wars Bot orchestrator.

    Combines the Competition Engine, Challenge Manager, and Drag-Drop Builder
    into a unified Bot Wars platform.

    Parameters
    ----------
    tier : Tier
        Subscription tier (FREE / PRO / ENTERPRISE).
    """

    TIER_ORDER = [Tier.FREE, Tier.PRO, Tier.ENTERPRISE]

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.bot_name = "Bot Wars Bot"
        self.version = "1.0"
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)

        # Initialise sub-systems
        self.competition_engine = CompetitionEngine()
        self.challenge_manager = ChallengeManager()
        self.drag_drop_builder = DragDropBuilder()

    # ------------------------------------------------------------------
    # Competition Engine delegations
    # ------------------------------------------------------------------

    def create_competition(
        self,
        name: str,
        category: str,
        description: str,
        prize_usd: float = 0.0,
    ) -> dict:
        """Create a new competition (PRO+)."""
        self._require_tier(Tier.PRO)
        return self.competition_engine.create_competition(name, category, description, prize_usd)

    def list_competitions(self, category: Optional[str] = None) -> list:
        """List all competitions (FREE+)."""
        return self.competition_engine.list_competitions(category)

    def submit_bot(
        self,
        competition_id: str,
        user_id: str,
        bot_name: str,
        bot_description: str,
    ) -> dict:
        """Submit a bot to a competition (PRO+)."""
        self._require_tier(Tier.PRO)
        return self.competition_engine.submit_bot(
            competition_id, user_id, bot_name, bot_description
        )

    def score_submission(
        self,
        competition_id: str,
        submission_id: str,
        scores: dict,
    ) -> dict:
        """Score a competition submission (PRO+)."""
        self._require_tier(Tier.PRO)
        return self.competition_engine.score_submission(
            competition_id, submission_id, scores
        )

    def get_leaderboard(self, competition_id: str) -> list:
        """Get the competition leaderboard (FREE+)."""
        return self.competition_engine.get_leaderboard(competition_id)

    # ------------------------------------------------------------------
    # Challenge Manager delegations
    # ------------------------------------------------------------------

    def create_challenge(
        self,
        title: str,
        challenge_type: str,
        description: str,
        duration_days: int,
        reward_tokens: int,
    ) -> dict:
        """Create a global challenge (PRO+)."""
        self._require_tier(Tier.PRO)
        return self.challenge_manager.create_challenge(
            title, challenge_type, description, duration_days, reward_tokens
        )

    def join_challenge(
        self,
        challenge_id: str,
        user_id: str,
        team_name: Optional[str] = None,
    ) -> dict:
        """Join a challenge (PRO+)."""
        self._require_tier(Tier.PRO)
        return self.challenge_manager.join_challenge(challenge_id, user_id, team_name)

    def submit_solution(
        self,
        challenge_id: str,
        user_id: str,
        solution_description: str,
    ) -> dict:
        """Submit a solution to a challenge (PRO+)."""
        self._require_tier(Tier.PRO)
        return self.challenge_manager.submit_solution(
            challenge_id, user_id, solution_description
        )

    # ------------------------------------------------------------------
    # Drag-Drop Builder delegations
    # ------------------------------------------------------------------

    def build_bot_project(
        self,
        user_id: str,
        bot_name: str,
        description: str,
    ) -> dict:
        """Create a new drag-drop bot project (PRO+)."""
        self._require_tier(Tier.PRO)
        return self.drag_drop_builder.create_bot_project(user_id, bot_name, description)

    def add_component(
        self,
        project_id: str,
        component_type: str,
        config: dict,
    ) -> dict:
        """Add a component to a bot project (PRO+)."""
        self._require_tier(Tier.PRO)
        return self.drag_drop_builder.add_component(project_id, component_type, config)

    def validate_bot(self, project_id: str) -> dict:
        """Validate a bot project (PRO+)."""
        self._require_tier(Tier.PRO)
        return self.drag_drop_builder.validate_bot(project_id)

    def export_bot(self, project_id: str) -> dict:
        """Export a bot project for the marketplace (PRO+)."""
        self._require_tier(Tier.PRO)
        return self.drag_drop_builder.export_bot(project_id)

    # ------------------------------------------------------------------
    # Enterprise-only
    # ------------------------------------------------------------------

    def host_private_tournament(
        self,
        name: str,
        description: str,
        prize_usd: float = 0.0,
    ) -> dict:
        """Host a white-label private tournament (ENTERPRISE only)."""
        self._require_tier(Tier.ENTERPRISE)
        return self.competition_engine.create_competition(
            name=name,
            category="corporate",
            description=description,
            prize_usd=prize_usd,
        )

    # ------------------------------------------------------------------
    # Tier info
    # ------------------------------------------------------------------

    def get_tier_info(self) -> dict:
        """Return details about the current subscription tier."""
        cfg = self.config
        return {
            "tier": cfg.tier.value,
            "name": cfg.name,
            "price_usd_monthly": cfg.price_usd_monthly,
            "max_bot_submissions": cfg.max_bot_submissions,
            "features": cfg.features,
            "support_level": cfg.support_level,
        }

    def get_upgrade_info(self) -> dict | None:
        """Return upgrade path info, or None if already at the highest tier."""
        upgrade = get_upgrade_path(self.tier)
        if upgrade is None:
            return None
        return {
            "upgrade_to": upgrade.name,
            "tier": upgrade.tier.value,
            "price_usd_monthly": upgrade.price_usd_monthly,
            "additional_features": [
                f for f in upgrade.features if f not in self.config.features
            ],
        }

    # ------------------------------------------------------------------
    # Chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str) -> str:
        """Simple message routing for Bot Wars Bot interactions.

        Returns a contextual response based on keywords in the message.
        """
        msg = message.lower()
        if "competition" in msg or "compete" in msg:
            comps = self.list_competitions()
            return (
                f"There are currently {len(comps)} competition(s) available. "
                "Use list_competitions() to see them all!"
            )
        if "challenge" in msg:
            challenges = self.challenge_manager.list_active_challenges()
            return (
                f"There are {len(challenges)} active challenge(s). "
                "Use join_challenge() to participate!"
            )
        if "tier" in msg or "upgrade" in msg or "plan" in msg:
            upgrade = self.get_upgrade_info()
            if upgrade:
                return (
                    f"You are on the {self.tier.value.upper()} tier. "
                    f"Upgrade to {upgrade['upgrade_to']} for "
                    f"${upgrade['price_usd_monthly']}/mo to unlock more features."
                )
            return f"You are on the {self.tier.value.upper()} tier — our highest plan!"
        if "build" in msg or "bot" in msg:
            return (
                "Use the Drag-Drop Builder to create bots visually! "
                "Start with build_bot_project()."
            )
        return (
            f"Welcome to {self.bot_name}! "
            "You can compete, build bots, and join challenges. How can I help?"
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_tier(self, required: Tier) -> None:
        """Raise BotWarsTierError if self.tier is below the required tier."""
        required_idx = self.TIER_ORDER.index(required)
        current_idx = self.TIER_ORDER.index(self.tier)
        if current_idx < required_idx:
            raise BotWarsTierError(
                f"This feature requires the {required.value.upper()} tier or higher. "
                f"You are on the {self.tier.value.upper()} tier. "
                "Please upgrade your subscription."
            )
