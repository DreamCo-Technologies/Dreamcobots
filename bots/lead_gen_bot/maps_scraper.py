"""Maps Scraper Bot — tier-aware Google Maps–style local business lead generator."""
import json
import os
import sys

from bots.lead_gen_bot.tiers import Tier, get_tier_config, get_upgrade_path, BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401


class MapsScraperBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class MapsScraperBot:
    """Tier-aware Google Maps–style local business lead generator.

    Collects realistic mock leads for local businesses.  The data layer is
    designed to be swapped for a live API (e.g. SerpAPI / Google Places)
    without changing the public interface.
    """

    PITCH_LIMITS = {Tier.FREE: 5, Tier.PRO: 50, Tier.ENTERPRISE: None}

    MOCK_LEADS = [
        {"name": "Elite Cuts Barbershop", "phone": "312-555-1111", "city": "Chicago"},
        {"name": "Prime Roofing Co", "phone": "312-555-2222", "city": "Chicago"},
        {"name": "Windy City Plumbing", "phone": "312-555-3333", "city": "Chicago"},
        {"name": "Lakeview Dental Clinic", "phone": "312-555-4444", "city": "Chicago"},
        {"name": "Southside Auto Repair", "phone": "312-555-5555", "city": "Chicago"},
        {"name": "North Shore Landscaping", "phone": "847-555-6666", "city": "Evanston"},
        {"name": "Oak Park Bakery", "phone": "708-555-7777", "city": "Oak Park"},
        {"name": "Naperville Pest Control", "phone": "630-555-8888", "city": "Naperville"},
    ]

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self.name = "Maps Scraper Bot"

    def run(self) -> str:
        """Collect local business leads and persist them to data/leads.json."""
        leads = self.get_mock_realistic_leads()
        self.save(leads)
        return f"📍 Collected {len(leads)} local business leads"

    def get_mock_realistic_leads(self) -> list:
        """Return mock realistic local business leads.

        Replace this method body with a live API call such as::

            response = requests.get(
                "https://serpapi.com/search",
                params={"engine": "google_maps", "q": "barbershop", "api_key": API_KEY},
            )
            return response.json().get("local_results", [])
        """
        limit = self.PITCH_LIMITS[self.tier]
        return self.MOCK_LEADS if limit is None else self.MOCK_LEADS[:limit]

    def save(self, leads: list) -> None:
        """Append *leads* to data/leads.json, creating the file if necessary."""
        os.makedirs("data", exist_ok=True)
        with open("data/leads.json", "a") as f:
            for lead in leads:
                f.write(json.dumps(lead) + "\n")

    def describe_tier(self) -> str:
        """Return a human-readable tier description."""
        info = get_bot_tier_info(self.tier)
        tier_name = info.get("name") or info.get("tier", str(self.tier.value)).title()
        lines = [
            f"=== {tier_name} Maps Scraper Bot Tier ===",
            f"Price: ${info['price_usd_monthly']:.2f}/month",
            "Features:",
        ]
        for feat in info["features"]:
            lines.append(f"  ✓ {feat}")
        return "\n".join(lines)


# Alias so controller / generator can load this class as "Bot"
Bot = MapsScraperBot
