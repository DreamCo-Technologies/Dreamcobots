"""
CreatorEmpire bot — multi-functional creator economy tool.

Orchestrates the OnboardingEngine, StreamerEngine, EventPlanningEngine,
and MonetizationEngine into a single, tier-aware interface.

Usage
-----
    from bots.creator_empire.creator_empire import CreatorEmpireBot, Tier

    bot = CreatorEmpireBot(tier=Tier.PRO)

    # Onboard a new streamer
    profile = bot.onboard_creator("Alex", role="streamer", bio="Gaming & IRL")
    result  = bot.complete_onboarding("Alex")

    # Set up streaming
    config = bot.setup_stream("Alex", platform="twitch", niche="gaming")
    tips   = bot.get_stream_tips("gaming")

    # Plan an event
    event  = bot.create_event("Alex", "Summer Live Show", "live_show",
                               "2025-08-15", "The Venue LA")
    event  = bot.advance_event_status(event.event_id)

    # Monetization
    bot.enable_revenue_model("Alex", "subscription_basic")
    bot.record_revenue("Alex", "tip_jar", 25.00, "streamlabs")
    print(bot.get_total_revenue("Alex"))
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config, get_upgrade_path

from .tiers import (
    get_creator_tier_info,
    CREATOR_FEATURES_BY_TIER,
    CREATOR_ROLES,
)
from .onboarding import OnboardingEngine, CreatorProfile, OnboardingError
from .streamer import StreamerEngine, StreamConfig, StreamerError
from .event_planning import EventPlanningEngine, Event, EventError
from .monetization import MonetizationEngine, RevenueEntry, MonetizationError


class CreatorEmpireBot:
    """
    Multi-functional creator economy bot.

    Provides a unified interface to onboarding, streaming, event planning,
    and monetization capabilities, all governed by the platform tier system.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling module feature availability.
    """

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self._config = get_tier_config(tier)

        self._onboarding = OnboardingEngine(tier=tier)
        self._streamer = StreamerEngine(tier=tier)
        self._events = EventPlanningEngine(tier=tier)
        self._monetization = MonetizationEngine(tier=tier)

    # ------------------------------------------------------------------
    # Tier information
    # ------------------------------------------------------------------

    def describe_tier(self) -> str:
        """Print and return a description of the current CreatorEmpire tier."""
        info = get_creator_tier_info(self.tier)
        limit = (
            "Unlimited"
            if info["requests_per_month"] is None
            else f"{info['requests_per_month']:,}"
        )
        lines = [
            f"=== {info['name']} CreatorEmpire Tier ===",
            f"Price    : ${info['price_usd_monthly']:.2f}/month",
            f"API Calls: {limit}/month",
            f"Support  : {info['support_level']}",
            "",
            "Creator features:",
        ]
        for feat in info["creator_features"]:
            lines.append(f"  ✓ {feat.replace('_', ' ').title()}")
        lines.append("")
        lines.append("Monetization models:")
        for model in info["monetization_models"]:
            lines.append(f"  • {model.replace('_', ' ').title()}")
        output = "\n".join(lines)
        print(output)
        return output

    def show_upgrade_path(self) -> str:
        """Print details about the next available tier upgrade."""
        next_cfg = get_upgrade_path(self.tier)
        if next_cfg is None:
            msg = f"You are already on the top-tier plan ({self._config.name})."
            print(msg)
            return msg

        current_feats = set(CREATOR_FEATURES_BY_TIER[self.tier.value])
        new_feats = [
            f for f in CREATOR_FEATURES_BY_TIER[next_cfg.tier.value]
            if f not in current_feats
        ]

        lines = [
            f"=== Upgrade: {self._config.name} → {next_cfg.name} ===",
            f"New price: ${next_cfg.price_usd_monthly:.2f}/month",
            "",
            "New creator features unlocked:",
        ]
        for feat in new_feats:
            lines.append(f"  + {feat.replace('_', ' ').title()}")
        lines.append(
            f"\nTo upgrade, set tier=Tier.{next_cfg.tier.name} when "
            "constructing CreatorEmpireBot or contact support."
        )
        output = "\n".join(lines)
        print(output)
        return output

    # ------------------------------------------------------------------
    # Onboarding
    # ------------------------------------------------------------------

    def onboard_creator(
        self,
        name: str,
        role: str,
        bio: str = "",
        goals=None,
        platforms=None,
    ) -> CreatorProfile:
        """Create and register a new creator profile."""
        return self._onboarding.create_profile(
            name=name, role=role, bio=bio, goals=goals, platforms=platforms
        )

    def complete_onboarding(self, name: str) -> dict:
        """Mark onboarding as complete and return creator profile + action plan."""
        return self._onboarding.complete_onboarding(name)

    def get_action_plan(self, role: str) -> list[str]:
        """Return the starter action plan for a given role."""
        return self._onboarding.get_action_plan(role)

    def get_creator_profile(self, name: str) -> CreatorProfile:
        """Return the CreatorProfile for *name*."""
        return self._onboarding.get_profile(name)

    def list_creators(self) -> list[dict]:
        """Return all registered creator profiles."""
        return self._onboarding.list_profiles()

    def update_creator_profile(self, name: str, **kwargs) -> CreatorProfile:
        """Update fields on a creator profile."""
        return self._onboarding.update_profile(name, **kwargs)

    # ------------------------------------------------------------------
    # Streaming
    # ------------------------------------------------------------------

    def setup_stream(
        self,
        creator_name: str,
        platform: str,
        niche: str = "general",
        schedule=None,
        resolution: str = "1080p60",
        bitrate_kbps: int = 6000,
    ) -> StreamConfig:
        """Create a streaming configuration for a creator."""
        return self._streamer.setup_stream(
            creator_name=creator_name,
            platform=platform,
            niche=niche,
            schedule=schedule,
            resolution=resolution,
            bitrate_kbps=bitrate_kbps,
        )

    def get_go_live_checklist(self) -> list[str]:
        """Return the standard go-live checklist."""
        return self._streamer.get_go_live_checklist()

    def get_monetisation_milestones(self, platform: str) -> list[dict]:
        """Return monetisation milestones for a given streaming platform."""
        return self._streamer.get_monetisation_milestones(platform)

    def enable_stream_monetisation(self, creator_name: str) -> StreamConfig:
        """Enable streaming monetisation for a creator."""
        return self._streamer.enable_monetisation(creator_name)

    def get_stream_tips(self, niche: str) -> list[str]:
        """Return niche-specific stream optimisation tips."""
        return self._streamer.get_optimisation_tips(niche)

    def get_stream_config(self, creator_name: str) -> StreamConfig:
        """Return the stream configuration for *creator_name*."""
        return self._streamer.get_stream_config(creator_name)

    # ------------------------------------------------------------------
    # Event planning
    # ------------------------------------------------------------------

    def create_event(
        self,
        creator_name: str,
        title: str,
        event_type: str,
        date: str,
        venue_or_platform: str,
        capacity=None,
        ticket_price_usd: float = 0.0,
    ) -> Event:
        """Create a new creator event."""
        return self._events.create_event(
            creator_name=creator_name,
            title=title,
            event_type=event_type,
            date=date,
            venue_or_platform=venue_or_platform,
            capacity=capacity,
            ticket_price_usd=ticket_price_usd,
        )

    def advance_event_status(self, event_id: str) -> Event:
        """Advance an event to the next lifecycle status."""
        return self._events.advance_status(event_id)

    def cancel_event(self, event_id: str) -> Event:
        """Cancel an event."""
        return self._events.cancel_event(event_id)

    def complete_event_task(self, event_id: str, task_index: int) -> Event:
        """Mark an event planning task as done."""
        return self._events.complete_task(event_id, task_index)

    def add_event_sponsor(self, event_id: str, sponsor_name: str) -> Event:
        """Add a sponsor to an event."""
        return self._events.add_sponsor(event_id, sponsor_name)

    def get_event(self, event_id: str) -> Event:
        """Return the Event for *event_id*."""
        return self._events.get_event(event_id)

    def list_events(self, creator_name=None) -> list[dict]:
        """Return all events, optionally filtered by creator."""
        return self._events.list_events(creator_name=creator_name)

    def get_pending_event_tasks(self, event_id: str) -> list[str]:
        """Return all pending planning tasks for an event."""
        return self._events.get_pending_tasks(event_id)

    # ------------------------------------------------------------------
    # Monetization
    # ------------------------------------------------------------------

    def enable_revenue_model(self, creator_name: str, model: str) -> dict:
        """Enable a revenue model for a creator."""
        return self._monetization.enable_model(creator_name, model)

    def get_active_revenue_models(self, creator_name: str) -> list[dict]:
        """Return info dicts for all active revenue models of a creator."""
        return self._monetization.get_active_models(creator_name)

    def get_available_revenue_models(self) -> list[dict]:
        """Return all revenue models available on the current tier."""
        return self._monetization.get_available_models()

    def record_revenue(
        self,
        creator_name: str,
        model: str,
        amount_usd: float,
        platform: str,
        description: str = "",
    ) -> RevenueEntry:
        """Record a revenue transaction."""
        return self._monetization.record_revenue(
            creator_name=creator_name,
            model=model,
            amount_usd=amount_usd,
            platform=platform,
            description=description,
        )

    def get_total_revenue(self, creator_name: str) -> float:
        """Return total gross revenue for a creator."""
        return self._monetization.get_total_revenue(creator_name)

    def get_revenue_breakdown(self, creator_name: str) -> dict:
        """Return gross revenue broken down by model for a creator."""
        return self._monetization.get_revenue_by_model(creator_name)

    def get_monetization_strategy(self, role: str) -> list[str]:
        """Return recommended monetization strategy for a creator role."""
        return self._monetization.get_monetization_strategy(role)

    def get_revenue_ledger(self, creator_name=None) -> list[dict]:
        """Return all ledger entries, optionally filtered by creator."""
        return self._monetization.get_ledger(creator_name=creator_name)
