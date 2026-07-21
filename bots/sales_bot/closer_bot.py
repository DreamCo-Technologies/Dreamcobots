"""Closer Bot — tier-aware auto outreach and deal closing bot."""
import json
import os
import sys

from bots.sales_bot.tiers import Tier, get_tier_config, get_upgrade_path, BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401


class CloserBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class CloserBot:
    """Tier-aware auto outreach and deal closing bot.

    Reads leads written by MapsScraperBot (or any compatible bot that
    appends JSON lines to data/leads.json) and generates a sales pitch
    for each one.
    """

    PITCH_LIMITS = {Tier.FREE: 5, Tier.PRO: 50, Tier.ENTERPRISE: None}

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self.name = "Closer Bot"

    def run(self) -> str:
        """Read leads and attempt to close deals."""
        leads = self._load_leads()
        if not leads:
            return "No leads available"

        limit = self.PITCH_LIMITS[self.tier]
        targets = leads if limit is None else leads[:limit]

        closed = 0
        for lead in targets:
            message = self.generate_pitch(lead)
            print(f"📞 Pitching {lead['name']}: {message}")
            closed += 1

        return f"💰 Attempted to close {closed} deals"

    def _load_leads(self) -> list:
        """Load leads from data/leads.json."""
        try:
            with open("data/leads.json") as f:
                return [json.loads(line) for line in f if line.strip()]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def generate_pitch(self, lead: dict) -> str:
        """Return a sales pitch string for *lead*."""
        name = lead.get("name", "Business Owner")
        return (
            f"Hey {name}, we help businesses get more customers automatically. "
            "Want more clients this week?"
        )

    def describe_tier(self) -> str:
        """Return a human-readable tier description."""
        info = get_bot_tier_info(self.tier)
        tier_name = info.get("name") or info.get("tier", str(self.tier.value)).title()
        lines = [
            f"=== {tier_name} Closer Bot Tier ===",
            f"Price: ${info['price_usd_monthly']:.2f}/month",
            "Features:",
        ]
        for feat in info["features"]:
            lines.append(f"  ✓ {feat}")
        return "\n".join(lines)


# Alias so controller / generator can load this class as "Bot"
Bot = CloserBot
