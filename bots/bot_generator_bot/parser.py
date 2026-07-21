"""
Bot Generator Bot — Parser Module

Detects the user-specified industry and goal from natural-language input,
mapping it to a structured BotIntent that drives the rest of the generation
pipeline (tool injection → template engine → deployer).

GLOBAL AI SOURCES FLOW: participates via bot_generator_bot.py pipeline.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Industry / keyword mapping
# ---------------------------------------------------------------------------

INDUSTRY_KEYWORDS: dict[str, list[str]] = {
    "real_estate": ["real estate", "realtor", "property", "zillow", "mls", "housing", "mortgage"],
    "dental": ["dentist", "dental", "orthodontist", "teeth", "clinic"],
    "legal": ["law", "lawyer", "attorney", "legal", "paralegal", "court"],
    "ecommerce": ["ecommerce", "e-commerce", "shop", "store", "product", "retail"],
    "marketing": ["marketing", "ads", "advertising", "seo", "social media", "campaign"],
    "finance": ["finance", "fintech", "investment", "trading", "crypto", "bank"],
    "healthcare": ["healthcare", "medical", "health", "hospital", "doctor", "clinic"],
    "education": ["education", "school", "tutor", "course", "learning", "training"],
    "restaurant": ["restaurant", "food", "cafe", "catering", "dining"],
    "fitness": ["fitness", "gym", "workout", "personal trainer", "wellness"],
    "insurance": ["insurance", "policy", "broker", "coverage"],
    "automotive": ["car", "auto", "vehicle", "dealership", "mechanic"],
    "construction": ["construction", "contractor", "builder", "renovation", "remodel"],
    "logistics": ["logistics", "shipping", "freight", "delivery", "supply chain"],
    "saas": ["saas", "software", "platform", "api", "developer", "tech"],
    "consulting": ["consulting", "consultant", "advisory", "strategy"],
    "nonprofit": ["nonprofit", "charity", "foundation", "ngo", "volunteer"],
    "government": ["government", "federal", "municipal", "grant", "contract"],
    "hospitality": ["hotel", "hospitality", "travel", "tourism", "airbnb"],
    "media": ["media", "news", "journalism", "publishing", "podcast", "content"],
}

GOAL_KEYWORDS: dict[str, list[str]] = {
    "generate_leads": ["lead", "leads", "find clients", "find customers", "prospect", "outreach"],
    "scrape_data": ["scrape", "collect data", "data collection", "harvest", "extract"],
    "automate_outreach": ["outreach", "email", "message", "contact", "follow up"],
    "track_analytics": ["analytics", "track", "report", "dashboard", "metrics", "performance"],
    "manage_payments": ["payment", "stripe", "invoice", "billing", "subscription"],
    "generate_content": ["content", "post", "write", "create", "generate text"],
    "monitor_market": ["monitor", "price watch", "competitor", "market intelligence"],
}

MONETIZATION_KEYWORDS: dict[str, list[str]] = {
    "lead_sales": ["sell leads", "lead sales", "pay per lead"],
    "subscriptions": ["subscription", "monthly", "recurring", "membership"],
    "pay_per_use": ["pay per use", "pay-per-use", "usage", "credits", "tokens"],
    "agency_bulk": ["agency", "bulk", "resell", "white-label", "wholesale"],
}


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class BotIntent:
    """Structured representation of a user's bot-generation request."""
    raw_input: str
    industry: str
    goal: str
    tools: list = field(default_factory=list)
    monetization: list = field(default_factory=list)
    bot_name: Optional[str] = None
    confidence: float = 0.0

    def to_dna(self) -> dict:
        """Return the Bot DNA dictionary used by the template engine."""
        return {
            "industry": self.industry,
            "goal": self.goal,
            "tools": self.tools,
            "monetization": self.monetization,
            "bot_name": self.bot_name or _slugify(f"{self.industry}_{self.goal}_bot"),
        }


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class BotParser:
    """
    Parses natural-language input into a structured BotIntent.

    Usage::

        parser = BotParser()
        intent = parser.parse("Make me a Dentist Lead Bot")
        print(intent.to_dna())
    """

    def parse(self, user_input: str) -> BotIntent:
        """
        Parse *user_input* and return a :class:`BotIntent`.

        Parameters
        ----------
        user_input : str
            Free-form description from the user, e.g. "Make a realtor lead bot".
        """
        text = user_input.lower()

        industry = self._detect_industry(text)
        goal = self._detect_goal(text)
        tools = _default_tools_for(industry, goal)
        monetization = self._detect_monetization(text)
        bot_name = self._extract_bot_name(user_input)
        confidence = self._score_confidence(industry, goal)

        return BotIntent(
            raw_input=user_input,
            industry=industry,
            goal=goal,
            tools=tools,
            monetization=monetization,
            bot_name=bot_name,
            confidence=confidence,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _detect_industry(self, text: str) -> str:
        for industry, keywords in INDUSTRY_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    return industry
        return "general"

    def _detect_goal(self, text: str) -> str:
        for goal, keywords in GOAL_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    return goal
        return "generate_leads"

    def _detect_monetization(self, text: str) -> list:
        found = []
        for mono, keywords in MONETIZATION_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    found.append(mono)
                    break
        return found if found else ["subscriptions"]

    def _extract_bot_name(self, text: str) -> Optional[str]:
        # Pattern: "Make a <Name> Bot" / "Build a <Name>"
        match = re.search(r"(?:make|build|create|generate)\s+(?:a|an|me\s+a|me\s+an)?\s+(.+?)(?:\s+bot)?$", text, re.IGNORECASE)
        if match:
            raw = match.group(1).strip()
            return _slugify(raw) + "_bot"
        return None

    def _score_confidence(self, industry: str, goal: str) -> float:
        score = 0.0
        if industry != "general":
            score += 0.6
        if goal != "generate_leads":
            score += 0.4
        else:
            score += 0.3  # generate_leads is always a reasonable default
        return min(score, 1.0)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _slugify(text: str) -> str:
    """Convert a human-readable string to a safe Python identifier."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", "_", text)
    return text


def _default_tools_for(industry: str, goal: str) -> list:
    """Return a sensible default tool list based on industry and goal."""
    base: list[str] = []
    if goal in ("generate_leads", "scrape_data"):
        base.extend(["google_maps", "email_finder"])
        industry_extra: dict[str, list[str]] = {
            "real_estate": ["zillow_scraper", "mls_api"],
            "dental": ["yelp_scraper", "google_places"],
            "legal": ["avvo_scraper", "google_places"],
            "ecommerce": ["shopify_api", "amazon_scraper"],
            "marketing": ["linkedin_scraper", "twitter_scraper"],
            "finance": ["crunchbase_api", "linkedin_scraper"],
            "restaurant": ["yelp_scraper", "doordash_api"],
            "fitness": ["google_places", "yelp_scraper"],
            "automotive": ["google_places", "cars_com_scraper"],
        }
        base.extend(industry_extra.get(industry, []))
    if goal == "automate_outreach":
        base.extend(["email_sender", "sms_sender"])
    if goal == "track_analytics":
        base.extend(["analytics_tracker", "dashboard_renderer"])
    if goal == "manage_payments":
        base.extend(["stripe_api", "invoice_generator"])
    return list(dict.fromkeys(base))  # deduplicate preserving order
