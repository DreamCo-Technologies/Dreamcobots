"""
Feature 1: Real Estate Property Listing Aggregator Bot
Functionality: Aggregates property listings from various sources and filters by
  price, location, property type, beds, and baths.
Use Cases: Home buyers looking for listings, investors sourcing deals.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401 — GLOBAL AI SOURCES FLOW

# ---------------------------------------------------------------------------
# 30 real-world property listing examples across diverse markets
# ---------------------------------------------------------------------------

EXAMPLES = [
    {"id": 1,  "address": "123 Oak St, Austin TX",         "price": 340000, "beds": 3, "baths": 2, "sqft": 1500, "type": "single_family", "source": "MLS",     "monthly_rent": 2400, "city": "Austin"},
    {"id": 2,  "address": "456 Maple Ave, Austin TX",      "price": 210000, "beds": 2, "baths": 1, "sqft": 950,  "type": "condo",         "source": "Zillow",  "monthly_rent": 1600, "city": "Austin"},
    {"id": 3,  "address": "789 Pine Rd, Phoenix AZ",       "price": 290000, "beds": 3, "baths": 2, "sqft": 1600, "type": "single_family", "source": "Redfin",  "monthly_rent": 2100, "city": "Phoenix"},
    {"id": 4,  "address": "321 Elm Dr, Phoenix AZ",        "price": 175000, "beds": 2, "baths": 2, "sqft": 1000, "type": "condo",         "source": "MLS",     "monthly_rent": 1450, "city": "Phoenix"},
    {"id": 5,  "address": "654 Cedar Ln, Nashville TN",    "price": 420000, "beds": 4, "baths": 3, "sqft": 2100, "type": "single_family", "source": "Zillow",  "monthly_rent": 3000, "city": "Nashville"},
    {"id": 6,  "address": "987 Birch Blvd, Nashville TN",  "price": 315000, "beds": 2, "baths": 2, "sqft": 1100, "type": "condo",         "source": "Redfin",  "monthly_rent": 2400, "city": "Nashville"},
    {"id": 7,  "address": "147 Walnut St, Denver CO",      "price": 275000, "beds": 1, "baths": 1, "sqft": 780,  "type": "condo",         "source": "MLS",     "monthly_rent": 2000, "city": "Denver"},
    {"id": 8,  "address": "258 Spruce Ave, Denver CO",     "price": 455000, "beds": 3, "baths": 2, "sqft": 1700, "type": "single_family", "source": "Zillow",  "monthly_rent": 3100, "city": "Denver"},
    {"id": 9,  "address": "369 Aspen Ct, Tampa FL",        "price": 320000, "beds": 3, "baths": 2, "sqft": 1600, "type": "single_family", "source": "Redfin",  "monthly_rent": 2300, "city": "Tampa"},
    {"id": 10, "address": "741 Palm Dr, Tampa FL",         "price": 225000, "beds": 2, "baths": 2, "sqft": 1100, "type": "condo",         "source": "MLS",     "monthly_rent": 1900, "city": "Tampa"},
    {"id": 11, "address": "852 Peachtree Rd, Atlanta GA",  "price": 385000, "beds": 3, "baths": 2, "sqft": 1750, "type": "single_family", "source": "Zillow",  "monthly_rent": 2700, "city": "Atlanta"},
    {"id": 12, "address": "963 Magnolia St, Atlanta GA",   "price": 295000, "beds": 2, "baths": 2, "sqft": 1250, "type": "condo",         "source": "Redfin",  "monthly_rent": 2200, "city": "Atlanta"},
    {"id": 13, "address": "159 Mesquite Way, Dallas TX",   "price": 360000, "beds": 4, "baths": 3, "sqft": 1900, "type": "single_family", "source": "MLS",     "monthly_rent": 2600, "city": "Dallas"},
    {"id": 14, "address": "267 Bluebonnet St, Dallas TX",  "price": 215000, "beds": 1, "baths": 1, "sqft": 800,  "type": "condo",         "source": "Zillow",  "monthly_rent": 1750, "city": "Dallas"},
    {"id": 15, "address": "375 Live Oak Blvd, Houston TX", "price": 295000, "beds": 3, "baths": 2, "sqft": 1550, "type": "single_family", "source": "Redfin",  "monthly_rent": 2050, "city": "Houston"},
    {"id": 16, "address": "483 Bayou Dr, Houston TX",      "price": 180000, "beds": 2, "baths": 2, "sqft": 1000, "type": "condo",         "source": "MLS",     "monthly_rent": 1500, "city": "Houston"},
    {"id": 17, "address": "591 Desert Rose, Las Vegas NV", "price": 325000, "beds": 3, "baths": 2, "sqft": 1700, "type": "single_family", "source": "Zillow",  "monthly_rent": 2200, "city": "Las Vegas"},
    {"id": 18, "address": "628 Cactus Ave, Las Vegas NV",  "price": 190000, "beds": 2, "baths": 2, "sqft": 1050, "type": "condo",         "source": "Redfin",  "monthly_rent": 1600, "city": "Las Vegas"},
    {"id": 19, "address": "714 Lakeside Dr, Charlotte NC", "price": 300000, "beds": 3, "baths": 2, "sqft": 1500, "type": "single_family", "source": "MLS",     "monthly_rent": 2150, "city": "Charlotte"},
    {"id": 20, "address": "836 Uptown Blvd, Charlotte NC", "price": 250000, "beds": 2, "baths": 1, "sqft": 900,  "type": "townhouse",     "source": "Zillow",  "monthly_rent": 1850, "city": "Charlotte"},
    {"id": 21, "address": "922 Mission St, San Antonio TX","price": 265000, "beds": 3, "baths": 2, "sqft": 1400, "type": "single_family", "source": "Redfin",  "monthly_rent": 1900, "city": "San Antonio"},
    {"id": 22, "address": "1014 River Rd, San Antonio TX", "price": 155000, "beds": 2, "baths": 1, "sqft": 850,  "type": "condo",         "source": "MLS",     "monthly_rent": 1350, "city": "San Antonio"},
    {"id": 23, "address": "1126 Sunset Blvd, Orlando FL",  "price": 310000, "beds": 3, "baths": 2, "sqft": 1600, "type": "single_family", "source": "Zillow",  "monthly_rent": 2200, "city": "Orlando"},
    {"id": 24, "address": "1238 Harbor View, Orlando FL",  "price": 195000, "beds": 2, "baths": 2, "sqft": 1000, "type": "condo",         "source": "Redfin",  "monthly_rent": 1650, "city": "Orlando"},
    {"id": 25, "address": "1344 Magnolia Pkwy, Raleigh NC","price": 355000, "beds": 3, "baths": 2, "sqft": 1700, "type": "single_family", "source": "MLS",     "monthly_rent": 2400, "city": "Raleigh"},
    {"id": 26, "address": "1456 Glenwood Ave, Raleigh NC", "price": 270000, "beds": 2, "baths": 2, "sqft": 1150, "type": "townhouse",     "source": "Zillow",  "monthly_rent": 1950, "city": "Raleigh"},
    {"id": 27, "address": "1562 Broadway, Salt Lake City UT","price": 395000,"beds": 4,"baths": 3, "sqft": 2000, "type": "single_family", "source": "Redfin",  "monthly_rent": 2700, "city": "Salt Lake City"},
    {"id": 28, "address": "1674 Main St, Salt Lake City UT","price": 240000,"beds": 2,"baths": 1, "sqft": 980,  "type": "condo",         "source": "MLS",     "monthly_rent": 1700, "city": "Salt Lake City"},
    {"id": 29, "address": "1786 Garden Way, Indianapolis IN","price": 230000,"beds": 3,"baths": 2, "sqft": 1350, "type": "single_family", "source": "Zillow",  "monthly_rent": 1650, "city": "Indianapolis"},
    {"id": 30, "address": "1892 Canal Blvd, Indianapolis IN","price": 145000,"beds": 2,"baths": 1, "sqft": 820,  "type": "condo",         "source": "Redfin",  "monthly_rent": 1150, "city": "Indianapolis"},
]

TIERS = {
    "FREE":       {"price_usd": 0,   "max_listings": 5,    "sources": ["MLS"],                "ai_scoring": False},
    "PRO":        {"price_usd": 49,  "max_listings": 50,   "sources": ["MLS", "Zillow"],      "ai_scoring": True},
    "ENTERPRISE": {"price_usd": 199, "max_listings": None, "sources": ["MLS", "Zillow", "Redfin"], "ai_scoring": True},
}


class PropertyListingAggregatorBot:
    """Aggregates and filters property listings from MLS, Zillow, Redfin and more.

    Competes with top listing aggregators (Zillow, Redfin, Realtor.com) by
    combining multi-source data with AI-powered deal scoring and ROI estimates.
    Monetization: Pay-per-search ($0.50) or monthly subscription ($49/$199).
    """

    def __init__(self, tier: str = "FREE"):
        if tier not in TIERS:
            raise ValueError(f"Invalid tier '{tier}'. Choose from {list(TIERS)}")
        self.tier = tier
        self._config = TIERS[tier]
        self._flow = GlobalAISourcesFlow(bot_name="PropertyListingAggregatorBot")
        self._search_count: int = 0

    # ------------------------------------------------------------------
    # Core search methods
    # ------------------------------------------------------------------

    def search(self, *, city: str | None = None, max_price: float | None = None,
               min_beds: int | None = None, property_type: str | None = None) -> list[dict]:
        """Return listings matching the given filters.

        Returns at most ``max_listings`` results based on the current tier.
        """
        results = list(EXAMPLES)

        allowed_sources = self._config["sources"]
        results = [p for p in results if p["source"] in allowed_sources]

        if city:
            results = [p for p in results if city.lower() in p["city"].lower()]
        if max_price is not None:
            results = [p for p in results if p["price"] <= max_price]
        if min_beds is not None:
            results = [p for p in results if p["beds"] >= min_beds]
        if property_type:
            results = [p for p in results if p["type"] == property_type.lower()]

        limit = self._config["max_listings"]
        if limit is not None:
            results = results[:limit]

        if self._config["ai_scoring"]:
            results = [
                {**prop, "ai_deal_score": self._score_deal(prop),
                 "estimated_roi_pct": self._calculate_roi(prop)}
                for prop in results
            ]

        self._search_count += 1
        return results

    def get_listing(self, listing_id: int) -> dict | None:
        """Return a single listing by its ID."""
        for prop in EXAMPLES:
            if prop["id"] == listing_id:
                result = dict(prop)
                if self._config["ai_scoring"]:
                    result["ai_deal_score"] = self._score_deal(prop)
                    result["estimated_roi_pct"] = self._calculate_roi(prop)
                return result
        return None

    def get_top_deals(self, count: int = 5) -> list[dict]:
        """Return the top N properties ranked by estimated ROI.

        Requires PRO or ENTERPRISE tier for AI scoring.
        """
        if not self._config["ai_scoring"]:
            raise PermissionError(
                f"AI deal scoring requires PRO or ENTERPRISE tier (current: {self.tier}). "
                "Upgrade at dreamcobots.com/pricing"
            )
        scored = [
            {**p, "estimated_roi_pct": self._calculate_roi(p), "ai_deal_score": self._score_deal(p)}
            for p in EXAMPLES
            if p["source"] in self._config["sources"]
        ]
        scored.sort(key=lambda x: x["estimated_roi_pct"], reverse=True)
        return scored[:count]

    def filter_by_budget_and_beds(self, budget: float, min_beds: int) -> list[dict]:
        """Convenience method: filter by budget AND minimum beds."""
        return self.search(max_price=budget, min_beds=min_beds)

    def get_listings_by_city(self, city: str) -> list[dict]:
        """Return all listings in a specific city."""
        return self.search(city=city)

    def get_all_sources(self) -> list[str]:
        """Return the list of data sources enabled for this tier."""
        return list(self._config["sources"])

    def get_available_cities(self) -> list[str]:
        """Return unique cities in the database."""
        seen: set[str] = set()
        cities: list[str] = []
        for p in EXAMPLES:
            if p["city"] not in seen:
                seen.add(p["city"])
                cities.append(p["city"])
        return cities

    def get_stats(self) -> dict:
        """Return aggregate statistics across all listings."""
        prices = [p["price"] for p in EXAMPLES]
        return {
            "total_listings": len(EXAMPLES),
            "avg_price": round(sum(prices) / len(prices), 2),
            "min_price": min(prices),
            "max_price": max(prices),
            "cities_covered": len(self.get_available_cities()),
            "sources": self.get_all_sources(),
            "tier": self.tier,
            "searches_run": self._search_count,
        }

    def describe_tier(self) -> str:
        """Return a human-readable description of the current tier."""
        cfg = self._config
        limit = cfg["max_listings"] if cfg["max_listings"] else "unlimited"
        lines = [
            f"=== PropertyListingAggregatorBot — {self.tier} Tier ===",
            f"  Monthly price : ${cfg['price_usd']}/month",
            f"  Max listings  : {limit} per search",
            f"  Data sources  : {', '.join(cfg['sources'])}",
            f"  AI deal score : {'enabled' if cfg['ai_scoring'] else 'disabled (upgrade to unlock)'}",
        ]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _calculate_roi(self, prop: dict) -> float:
        annual_rent = prop["monthly_rent"] * 12
        noi = annual_rent * 0.65  # 35% operating expenses
        return round(noi / prop["price"] * 100, 2)

    def _score_deal(self, prop: dict) -> int:
        """Return an integer deal score from 0-100 based on ROI and price/sqft."""
        roi = self._calculate_roi(prop)
        price_per_sqft = prop["price"] / prop["sqft"]
        roi_score = min(50, int(roi * 10))
        sqft_score = max(0, 50 - int(price_per_sqft / 5))
        return roi_score + sqft_score

    def run(self) -> dict:
        """Run the full GLOBAL AI SOURCES FLOW pipeline and return a summary."""
        result = self._flow.run_pipeline(
            raw_data={"domain": "property_listings", "examples_count": len(EXAMPLES)},
            learning_method="supervised",
        )
        return {
            "pipeline_complete": result.get("pipeline_complete"),
            "stats": self.get_stats(),
        }


# ---------------------------------------------------------------------------
# Convenience entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    bot = PropertyListingAggregatorBot(tier="PRO")
    top = bot.get_top_deals(5)
    print(f"Top 5 deals:")
    for deal in top:
        print(f"  {deal['address']} — ROI {deal['estimated_roi_pct']}% — Score {deal['ai_deal_score']}")
    print(bot.describe_tier())


PropertyListingsBot = PropertyListingAggregatorBot


# ---------------------------------------------------------------------------
# Tier system additions for test compatibility
# ---------------------------------------------------------------------------
import random as _random_tier
from enum import Enum as _TierEnum


class Tier(_TierEnum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other.upper()
        return super().__eq__(other)

    def __hash__(self):
        return super().__hash__()


_TIER_MONTHLY_PRICE = {"free": 0, "pro": 29, "enterprise": 99}


class PropertyListingAggregatorBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


_orig_propertylistingaggregator_bot_init = PropertyListingAggregatorBot.__init__


def _propertylistingaggregator_bot_new_init(self, tier=Tier.FREE):
    tier_val = tier.value if hasattr(tier, "value") else str(tier).lower()
    _orig_propertylistingaggregator_bot_init(self, tier_val.upper())
    self.tier = Tier(tier_val)


PropertyListingAggregatorBot.__init__ = _propertylistingaggregator_bot_new_init
PropertyListingAggregatorBot.RESULT_LIMITS = {"free": 5, "pro": 25, "enterprise": 100}


def _propertylistingaggregator_bot_monthly_price(self):
    return _TIER_MONTHLY_PRICE[self.tier.value]


def _propertylistingaggregator_bot_get_tier_info(self):
    return {
        "tier": self.tier.value,
        "monthly_price_usd": self.monthly_price(),
        "result_limit": self.RESULT_LIMITS[self.tier.value],
    }


def _propertylistingaggregator_bot_enforce_tier(self, required_value):
    order = ["free", "pro", "enterprise"]
    if order.index(self.tier.value) < order.index(required_value):
        raise PropertyListingAggregatorBotTierError(
            f"{required_value.upper()} tier required. Current: {self.tier.value}"
        )


def _propertylistingaggregator_bot_list_items(self, limit=None):
    cap = limit if limit else self.RESULT_LIMITS[self.tier.value]
    return _random_tier.sample(EXAMPLES, min(cap, len(EXAMPLES)))


def _propertylistingaggregator_bot_analyze(self):
    self._enforce_tier("pro")
    return {"bot": "PropertyListingAggregatorBot", "tier": self.tier.value, "count": len(EXAMPLES)}


def _propertylistingaggregator_bot_export_report(self):
    self._enforce_tier("enterprise")
    return {"bot": "PropertyListingAggregatorBot", "tier": self.tier.value, "total_items": len(EXAMPLES), "items": EXAMPLES}


PropertyListingAggregatorBot.monthly_price = _propertylistingaggregator_bot_monthly_price
PropertyListingAggregatorBot.get_tier_info = _propertylistingaggregator_bot_get_tier_info
PropertyListingAggregatorBot._enforce_tier = _propertylistingaggregator_bot_enforce_tier
PropertyListingAggregatorBot.list_items = _propertylistingaggregator_bot_list_items
PropertyListingAggregatorBot.analyze = _propertylistingaggregator_bot_analyze
PropertyListingAggregatorBot.export_report = _propertylistingaggregator_bot_export_report
