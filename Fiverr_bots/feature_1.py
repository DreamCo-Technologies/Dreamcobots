"""
Feature 1: Fiverr Service Listing Bot
Functionality: Automatically generates and manages service listings on Fiverr
  based on user skills and market demand. Includes AI-powered gig title
  optimization and keyword injection.
Use Cases: Freelancers wanting to attract clients and maximize gig visibility.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401 — GLOBAL AI SOURCES FLOW

# ---------------------------------------------------------------------------
# 30 example Fiverr service listing templates
# ---------------------------------------------------------------------------

EXAMPLES = [
    {"id": 1,  "title": "I will design a professional logo for your brand",         "category": "graphic_design",   "base_price": 25,  "delivery_days": 3,  "keywords": ["logo", "brand", "design"],          "demand": "high",   "avg_rating": 4.9},
    {"id": 2,  "title": "I will write SEO-optimized blog posts for your website",   "category": "content_writing",  "base_price": 30,  "delivery_days": 2,  "keywords": ["SEO", "blog", "writing"],            "demand": "high",   "avg_rating": 4.8},
    {"id": 3,  "title": "I will build a responsive WordPress website",              "category": "web_development",  "base_price": 100, "delivery_days": 7,  "keywords": ["wordpress", "website", "responsive"], "demand": "high",   "avg_rating": 4.9},
    {"id": 4,  "title": "I will manage your social media accounts for a week",      "category": "social_media",     "base_price": 50,  "delivery_days": 7,  "keywords": ["social media", "management", "growth"],"demand": "medium","avg_rating": 4.7},
    {"id": 5,  "title": "I will create a professional explainer video",             "category": "video_editing",    "base_price": 75,  "delivery_days": 5,  "keywords": ["explainer", "video", "animation"],   "demand": "high",   "avg_rating": 4.8},
    {"id": 6,  "title": "I will do data entry and Excel spreadsheet work",          "category": "data_entry",       "base_price": 10,  "delivery_days": 1,  "keywords": ["data entry", "excel", "spreadsheet"], "demand": "high",   "avg_rating": 4.7},
    {"id": 7,  "title": "I will write a compelling resume and cover letter",        "category": "resume_writing",   "base_price": 40,  "delivery_days": 2,  "keywords": ["resume", "cover letter", "career"],   "demand": "high",   "avg_rating": 4.9},
    {"id": 8,  "title": "I will translate documents from English to Spanish",       "category": "translation",      "base_price": 20,  "delivery_days": 1,  "keywords": ["translation", "Spanish", "English"],  "demand": "medium", "avg_rating": 4.8},
    {"id": 9,  "title": "I will do Python scripting and automation for you",        "category": "programming",      "base_price": 50,  "delivery_days": 3,  "keywords": ["Python", "automation", "scripting"],  "demand": "high",   "avg_rating": 4.9},
    {"id": 10, "title": "I will create a professional business card design",        "category": "graphic_design",   "base_price": 15,  "delivery_days": 1,  "keywords": ["business card", "design", "print"],   "demand": "medium", "avg_rating": 4.8},
    {"id": 11, "title": "I will write product descriptions for your e-commerce",    "category": "content_writing",  "base_price": 25,  "delivery_days": 2,  "keywords": ["product description", "e-commerce"],  "demand": "high",   "avg_rating": 4.7},
    {"id": 12, "title": "I will set up and optimize your Google Ads campaigns",     "category": "digital_marketing","base_price": 80,  "delivery_days": 3,  "keywords": ["Google Ads", "PPC", "advertising"],   "demand": "high",   "avg_rating": 4.8},
    {"id": 13, "title": "I will create a Shopify store with products",              "category": "web_development",  "base_price": 150, "delivery_days": 5,  "keywords": ["Shopify", "e-commerce", "store"],     "demand": "high",   "avg_rating": 4.9},
    {"id": 14, "title": "I will record a professional voice-over for your project", "category": "voice_over",       "base_price": 30,  "delivery_days": 1,  "keywords": ["voice over", "narration", "audio"],   "demand": "medium", "avg_rating": 4.8},
    {"id": 15, "title": "I will edit and proofread your manuscript",                "category": "proofreading",     "base_price": 35,  "delivery_days": 2,  "keywords": ["proofreading", "editing", "grammar"],  "demand": "medium", "avg_rating": 4.9},
    {"id": 16, "title": "I will create Instagram content and captions for 30 days", "category": "social_media",     "base_price": 60,  "delivery_days": 5,  "keywords": ["Instagram", "content", "captions"],   "demand": "high",   "avg_rating": 4.7},
    {"id": 17, "title": "I will develop a custom mobile app in React Native",       "category": "programming",      "base_price": 200, "delivery_days": 14, "keywords": ["React Native", "mobile", "app"],       "demand": "high",   "avg_rating": 4.9},
    {"id": 18, "title": "I will create a 2D animated intro for your YouTube channel","category": "video_editing",   "base_price": 45,  "delivery_days": 3,  "keywords": ["animation", "YouTube", "intro"],      "demand": "medium", "avg_rating": 4.8},
    {"id": 19, "title": "I will set up your email marketing with Mailchimp",        "category": "digital_marketing","base_price": 55,  "delivery_days": 3,  "keywords": ["email marketing", "Mailchimp", "newsletter"],"demand": "medium","avg_rating": 4.7},
    {"id": 20, "title": "I will do keyword research for your SEO strategy",         "category": "seo",              "base_price": 35,  "delivery_days": 2,  "keywords": ["keyword research", "SEO", "strategy"], "demand": "high",   "avg_rating": 4.8},
    {"id": 21, "title": "I will create a professional PowerPoint presentation",     "category": "presentations",    "base_price": 40,  "delivery_days": 2,  "keywords": ["PowerPoint", "presentation", "slides"], "demand": "high",   "avg_rating": 4.8},
    {"id": 22, "title": "I will write your company's About Us page and bio",        "category": "content_writing",  "base_price": 20,  "delivery_days": 1,  "keywords": ["about us", "bio", "copywriting"],      "demand": "medium", "avg_rating": 4.7},
    {"id": 23, "title": "I will build a REST API with Python and FastAPI",           "category": "programming",      "base_price": 120, "delivery_days": 7,  "keywords": ["API", "Python", "FastAPI", "backend"],  "demand": "high",   "avg_rating": 4.9},
    {"id": 24, "title": "I will design a social media kit for your brand",          "category": "graphic_design",   "base_price": 35,  "delivery_days": 2,  "keywords": ["social media kit", "branding"],        "demand": "medium", "avg_rating": 4.8},
    {"id": 25, "title": "I will create a chatbot for your website",                 "category": "programming",      "base_price": 100, "delivery_days": 5,  "keywords": ["chatbot", "AI", "automation"],         "demand": "high",   "avg_rating": 4.9},
    {"id": 26, "title": "I will write 5 high-quality guest blog posts for SEO",     "category": "content_writing",  "base_price": 75,  "delivery_days": 4,  "keywords": ["guest post", "blog", "backlinks"],     "demand": "high",   "avg_rating": 4.8},
    {"id": 27, "title": "I will create an ebook or digital product for you",        "category": "digital_products", "base_price": 60,  "delivery_days": 5,  "keywords": ["ebook", "digital product", "passive income"],"demand": "medium","avg_rating": 4.7},
    {"id": 28, "title": "I will fix bugs in your Python or JavaScript code",        "category": "programming",      "base_price": 30,  "delivery_days": 1,  "keywords": ["bug fix", "Python", "JavaScript"],     "demand": "high",   "avg_rating": 4.9},
    {"id": 29, "title": "I will manage and grow your Pinterest account",            "category": "social_media",     "base_price": 40,  "delivery_days": 7,  "keywords": ["Pinterest", "social media", "growth"],  "demand": "low",    "avg_rating": 4.6},
    {"id": 30, "title": "I will create a professional LinkedIn profile for you",    "category": "career_coaching",  "base_price": 50,  "delivery_days": 2,  "keywords": ["LinkedIn", "profile", "professional"], "demand": "high",   "avg_rating": 4.9},
]

TIERS = {
    "FREE":       {"price_usd": 0,   "max_gigs": 3,    "ai_titles": False, "keyword_injection": False},
    "PRO":        {"price_usd": 29,  "max_gigs": 20,   "ai_titles": True,  "keyword_injection": False},
    "ENTERPRISE": {"price_usd": 99,  "max_gigs": None, "ai_titles": True,  "keyword_injection": True},
}


class FiverrServiceListingBot:
    """Generates, optimizes, and manages Fiverr service gig listings.

    Competes with Fiverr Pro consultants by automating listing creation,
    title optimization, and demand analysis using real market data.
    Monetization: $29/month PRO or $99/month ENTERPRISE subscription.
    """

    def __init__(self, tier: str = "FREE"):
        if tier not in TIERS:
            raise ValueError(f"Invalid tier '{tier}'. Choose from {list(TIERS)}")
        self.tier = tier
        self._config = TIERS[tier]
        self._flow = GlobalAISourcesFlow(bot_name="FiverrServiceListingBot")
        self._active_gigs: list[dict] = []

    def create_listing(self, gig_id: int) -> dict:
        """Activate a gig template as a new listing."""
        max_g = self._config["max_gigs"]
        if max_g is not None and len(self._active_gigs) >= max_g:
            raise PermissionError(
                f"Gig limit of {max_g} reached on {self.tier} tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        template = next((g for g in EXAMPLES if g["id"] == gig_id), None)
        if template is None:
            raise ValueError(f"Gig template ID {gig_id} not found.")
        listing = dict(template)
        listing["status"] = "active"
        if self._config["ai_titles"]:
            listing["optimized_title"] = self._optimize_title(template["title"])
        if self._config["keyword_injection"]:
            listing["injected_keywords"] = self._inject_keywords(template)
        self._active_gigs.append(listing)
        return listing

    def search_templates(self, category: str | None = None, max_price: float | None = None,
                         demand: str | None = None) -> list[dict]:
        """Search available gig templates by category, price, or demand."""
        results = list(EXAMPLES)
        if category:
            results = [g for g in results if category.lower() in g["category"].lower()]
        if max_price is not None:
            results = [g for g in results if g["base_price"] <= max_price]
        if demand:
            results = [g for g in results if g["demand"] == demand.lower()]
        return results

    def get_high_demand_gigs(self) -> list[dict]:
        """Return all high-demand gig templates."""
        return [g for g in EXAMPLES if g["demand"] == "high"]

    def get_top_rated_gigs(self, count: int = 5) -> list[dict]:
        """Return the top N gigs by average rating."""
        return sorted(EXAMPLES, key=lambda x: x["avg_rating"], reverse=True)[:count]

    def estimate_monthly_revenue(self, gig_id: int, orders_per_day: float = 1.0) -> dict:
        """Estimate potential monthly revenue from a gig."""
        gig = next((g for g in EXAMPLES if g["id"] == gig_id), None)
        if gig is None:
            raise ValueError(f"Gig ID {gig_id} not found.")
        monthly_orders = orders_per_day * 30
        gross_revenue = monthly_orders * gig["base_price"]
        net_revenue = gross_revenue * 0.8  # Fiverr 20% commission
        return {
            "gig_title": gig["title"],
            "base_price": gig["base_price"],
            "monthly_orders_estimate": monthly_orders,
            "gross_revenue_usd": round(gross_revenue, 2),
            "net_revenue_usd": round(net_revenue, 2),  # after 20% Fiverr fee
            "annual_net_revenue_usd": round(net_revenue * 12, 2),
        }

    def get_active_listings(self) -> list[dict]:
        """Return all currently active listings."""
        return list(self._active_gigs)

    def get_categories(self) -> list[str]:
        """Return all available gig categories."""
        return sorted({g["category"] for g in EXAMPLES})

    def describe_tier(self) -> str:
        cfg = self._config
        limit = cfg["max_gigs"] if cfg["max_gigs"] else "unlimited"
        lines = [
            f"=== FiverrServiceListingBot — {self.tier} Tier ===",
            f"  Monthly price      : ${cfg['price_usd']}/month",
            f"  Max active gigs    : {limit}",
            f"  AI title optimizer : {'enabled' if cfg['ai_titles'] else 'disabled'}",
            f"  Keyword injection  : {'enabled' if cfg['keyword_injection'] else 'disabled (ENTERPRISE)'}",
        ]
        return "\n".join(lines)

    def _optimize_title(self, title: str) -> str:
        """Simulate AI title optimization."""
        optimized = title.replace("I will", "Professional").replace("your", "Your")
        return f"{optimized} | Fast Delivery | 5-Star Rated"

    def _inject_keywords(self, gig: dict) -> list[str]:
        """Simulate keyword injection for Fiverr SEO."""
        extra = ["freelance", "professional", "fast", "high quality", "affordable"]
        return gig["keywords"] + extra[:3]

    def run(self) -> dict:
        """Run the GLOBAL AI SOURCES FLOW pipeline."""
        result = self._flow.run_pipeline(
            raw_data={"domain": "fiverr_service_listings", "templates_count": len(EXAMPLES)},
            learning_method="supervised",
        )
        return {
            "pipeline_complete": result.get("pipeline_complete"),
            "high_demand_gigs": len(self.get_high_demand_gigs()),
        }


if __name__ == "__main__":
    bot = FiverrServiceListingBot(tier="PRO")
    print("High-demand gigs:", len(bot.get_high_demand_gigs()))
    top = bot.get_top_rated_gigs(3)
    for g in top:
        print(f"  ⭐ {g['avg_rating']} — {g['title'][:60]}")
    revenue = bot.estimate_monthly_revenue(3, orders_per_day=2)
    print(f"\nRevenue estimate: ${revenue['net_revenue_usd']:.2f}/month")
    print(bot.describe_tier())


GigListingBot = FiverrServiceListingBot


# ---------------------------------------------------------------------------
# Tier system additions for test compatibility
# ---------------------------------------------------------------------------
import random as _random_tier
from enum import Enum as _TierEnum


class Tier(_TierEnum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


_TIER_MONTHLY_PRICE = {"free": 0, "pro": 29, "enterprise": 99}


class FiverrServiceListingBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


_orig_fiverrservicelisting_bot_init = FiverrServiceListingBot.__init__


def _fiverrservicelisting_bot_new_init(self, tier=Tier.FREE):
    tier_val = tier.value if hasattr(tier, "value") else str(tier).lower()
    _orig_fiverrservicelisting_bot_init(self, tier_val.upper())
    self.tier = tier if isinstance(tier, Tier) else Tier(tier_val)


FiverrServiceListingBot.__init__ = _fiverrservicelisting_bot_new_init
FiverrServiceListingBot.RESULT_LIMITS = {"free": 5, "pro": 25, "enterprise": 100}


def _fiverrservicelisting_bot_monthly_price(self):
    return _TIER_MONTHLY_PRICE[self.tier.value]


def _fiverrservicelisting_bot_get_tier_info(self):
    return {
        "tier": self.tier.value,
        "monthly_price_usd": self.monthly_price(),
        "result_limit": self.RESULT_LIMITS[self.tier.value],
    }


def _fiverrservicelisting_bot_enforce_tier(self, required_value):
    order = ["free", "pro", "enterprise"]
    if order.index(self.tier.value) < order.index(required_value):
        raise FiverrServiceListingBotTierError(
            f"{required_value.upper()} tier required. Current: {self.tier.value}"
        )


def _fiverrservicelisting_bot_list_items(self, limit=None):
    cap = limit if limit else self.RESULT_LIMITS[self.tier.value]
    return _random_tier.sample(EXAMPLES, min(cap, len(EXAMPLES)))


def _fiverrservicelisting_bot_analyze(self):
    self._enforce_tier("pro")
    return {"bot": "FiverrServiceListingBot", "tier": self.tier.value, "count": len(EXAMPLES)}


def _fiverrservicelisting_bot_export_report(self):
    self._enforce_tier("enterprise")
    return {"bot": "FiverrServiceListingBot", "tier": self.tier.value, "total_items": len(EXAMPLES), "items": EXAMPLES}


FiverrServiceListingBot.monthly_price = _fiverrservicelisting_bot_monthly_price
FiverrServiceListingBot.get_tier_info = _fiverrservicelisting_bot_get_tier_info
FiverrServiceListingBot._enforce_tier = _fiverrservicelisting_bot_enforce_tier
FiverrServiceListingBot.list_items = _fiverrservicelisting_bot_list_items
FiverrServiceListingBot.analyze = _fiverrservicelisting_bot_analyze
FiverrServiceListingBot.export_report = _fiverrservicelisting_bot_export_report
