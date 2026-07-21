"""
Localization Engine — content adaptation and translation for the DreamCo Localized Bot.

Provides:
  - Content adaptation to a target region's language and cultural context.
  - Lightweight message translation stubs (production would call an external API).
  - Cultural tips per region.
  - Regional bot configuration generation.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401

from bots.localized_bot.region_database import RegionDatabase

# Cultural tips keyed by region_id.
_CULTURAL_TIPS: dict[str, list[str]] = {
    "US": [
        "Direct communication style is appreciated.",
        "Punctuality is highly valued in professional settings.",
        "First names are commonly used even in business contexts.",
    ],
    "UK": [
        "Understatement and dry humour are common.",
        "Politeness and queuing etiquette are important.",
        "Titles (Mr./Ms./Dr.) are often used in formal correspondence.",
    ],
    "Japan": [
        "Indirect communication and saving face are culturally important.",
        "Bowing is a common greeting; business cards should be handled with respect.",
        "Group consensus (nemawashi) is preferred over individual decisions.",
    ],
    "China": [
        "Guanxi (relationships/connections) is central to business.",
        "Red is considered a lucky colour; avoid giving clocks as gifts.",
        "Hierarchy and respect for seniority are very important.",
    ],
    "India": [
        "Relationships and trust-building precede business deals.",
        "Time is flexible; meetings may start late.",
        "Vegetarian options are essential for business dining.",
    ],
    "Germany": [
        "Punctuality and thoroughness are highly valued.",
        "Formal titles and last names are used until invited to use first names.",
        "Detailed planning and documentation are expected.",
    ],
    "Brazil": [
        "Warm personal relationships precede business.",
        "Physical contact such as hugs is common among friends.",
        "Flexibility with time is common; patience is key.",
    ],
    "Saudi_Arabia": [
        "Islam influences business hours and etiquette.",
        "Gender-segregated spaces may exist; be respectful.",
        "Hospitality (coffee, dates) is an important business ritual.",
    ],
    "UAE": [
        "Ramadan affects business hours; be respectful of fasting.",
        "Dress modestly, especially in traditional areas.",
        "Building long-term relationships is prioritised over quick deals.",
    ],
    "Nigeria": [
        "Respect for elders and seniority is paramount.",
        "Negotiations often involve extensive conversation and relationship-building.",
        "Greetings are important and should not be rushed.",
    ],
}

_DEFAULT_CULTURAL_TIPS: list[str] = [
    "Research local customs before engaging with this region.",
    "Use formal greetings until invited to be informal.",
    "Be mindful of local public holidays and business hours.",
]

# Industry-specific adaptation notes.
_INDUSTRY_NOTES: dict[str, str] = {
    "Technology": "Emphasise innovation metrics, uptime SLAs, and developer-friendly APIs.",
    "Finance": "Highlight compliance, regulatory adherence, and risk management capabilities.",
    "Healthcare": "Focus on patient data privacy (HIPAA/GDPR) and clinical outcome improvements.",
    "Agriculture": "Use localised crop calendars and weather data integrations.",
    "Tourism": "Incorporate local language support and currency conversion features.",
    "Manufacturing": "Stress efficiency gains, downtime reduction, and supply-chain integration.",
    "Retail": "Emphasise localised payment methods and regional logistics partners.",
    "Energy": "Address local regulatory frameworks and sustainability reporting.",
}


class LocalizationEngine:
    """Adapts and translates content for target regions and industries."""

    def __init__(self) -> None:
        self._db = RegionDatabase()

    def adapt_content(
        self,
        content: str,
        target_region_id: str,
        industry: str | None = None,
    ) -> dict:
        """
        Adapt *content* for *target_region_id*, optionally tailored to *industry*.

        Returns a dict with keys:
            original, adapted, region, language, cultural_notes, industry_notes
        """
        region = self._db.get_region(target_region_id)
        cultural_notes = self.get_cultural_tips(target_region_id)
        industry_notes = (
            _INDUSTRY_NOTES.get(industry, f"Adapt content for the {industry} sector.")
            if industry
            else ""
        )
        adapted = (
            f"[{region['language_name']} / {region['region_name']}] {content}"
        )
        return {
            "original": content,
            "adapted": adapted,
            "region": region["region_name"],
            "language": region["language_name"],
            "cultural_notes": cultural_notes,
            "industry_notes": industry_notes,
        }

    def translate_message(self, text: str, target_language: str) -> dict:
        """
        Translate *text* to *target_language*.

        In production this would call an external translation API. Here we return
        a structured stub so the interface contract is satisfied.

        Returns a dict with keys:
            original, translated, target_language, confidence
        """
        translated = f"[{target_language}] {text}"
        return {
            "original": text,
            "translated": translated,
            "target_language": target_language,
            "confidence": 0.95,
        }

    def get_cultural_tips(self, region_id: str) -> list[str]:
        """Return a list of cultural tips for *region_id*."""
        return list(_CULTURAL_TIPS.get(region_id, _DEFAULT_CULTURAL_TIPS))

    def generate_regional_bot_config(self, region_id: str, bot_type: str) -> dict:
        """
        Generate a region-specific bot configuration dict.

        Returns a config dict with region-specific settings such as language,
        timezone, currency, cultural style, and greeting format.
        """
        region = self._db.get_region(region_id)
        return {
            "bot_type": bot_type,
            "region_id": region_id,
            "region_name": region["region_name"],
            "language_code": region["language_code"],
            "language_name": region["language_name"],
            "timezone": region["timezone"],
            "currency_code": region["currency_code"],
            "greeting": f"Hello from {region['region_name']}!",
            "date_format": "YYYY-MM-DD",
            "cultural_notes": self.get_cultural_tips(region_id),
            "industries": region["industries"],
        }
