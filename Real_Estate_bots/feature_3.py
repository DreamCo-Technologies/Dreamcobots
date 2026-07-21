"""
Feature 3: Real Estate Market Analysis Bot
Functionality: Analyzes market trends and provides data-driven insights for
  investors and buyers across 30 US metro markets.
Use Cases: Investors making data-driven decisions, agents advising clients.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401 — GLOBAL AI SOURCES FLOW

# ---------------------------------------------------------------------------
# 30 real US metro market data examples
# ---------------------------------------------------------------------------

EXAMPLES = [
    {"id": 1,  "city": "Austin",         "state": "TX", "median_price": 520000, "price_change_yoy_pct": 6.2,  "inventory_months": 2.1, "days_on_market": 18, "price_per_sqft": 285, "cap_rate_avg_pct": 4.8, "population_growth_pct": 3.1},
    {"id": 2,  "city": "Phoenix",        "state": "AZ", "median_price": 410000, "price_change_yoy_pct": 4.8,  "inventory_months": 2.8, "days_on_market": 22, "price_per_sqft": 210, "cap_rate_avg_pct": 5.2, "population_growth_pct": 2.4},
    {"id": 3,  "city": "Nashville",      "state": "TN", "median_price": 455000, "price_change_yoy_pct": 5.5,  "inventory_months": 1.9, "days_on_market": 15, "price_per_sqft": 260, "cap_rate_avg_pct": 5.0, "population_growth_pct": 2.8},
    {"id": 4,  "city": "Denver",         "state": "CO", "median_price": 580000, "price_change_yoy_pct": 3.2,  "inventory_months": 3.1, "days_on_market": 28, "price_per_sqft": 295, "cap_rate_avg_pct": 4.2, "population_growth_pct": 1.9},
    {"id": 5,  "city": "Tampa",          "state": "FL", "median_price": 395000, "price_change_yoy_pct": 7.1,  "inventory_months": 2.5, "days_on_market": 20, "price_per_sqft": 230, "cap_rate_avg_pct": 5.5, "population_growth_pct": 3.4},
    {"id": 6,  "city": "Charlotte",      "state": "NC", "median_price": 375000, "price_change_yoy_pct": 5.9,  "inventory_months": 2.2, "days_on_market": 17, "price_per_sqft": 218, "cap_rate_avg_pct": 5.3, "population_growth_pct": 2.9},
    {"id": 7,  "city": "Atlanta",        "state": "GA", "median_price": 400000, "price_change_yoy_pct": 4.4,  "inventory_months": 2.7, "days_on_market": 24, "price_per_sqft": 225, "cap_rate_avg_pct": 4.9, "population_growth_pct": 2.1},
    {"id": 8,  "city": "Dallas",         "state": "TX", "median_price": 415000, "price_change_yoy_pct": 3.8,  "inventory_months": 3.0, "days_on_market": 26, "price_per_sqft": 215, "cap_rate_avg_pct": 4.6, "population_growth_pct": 2.3},
    {"id": 9,  "city": "Houston",        "state": "TX", "median_price": 340000, "price_change_yoy_pct": 3.1,  "inventory_months": 3.4, "days_on_market": 30, "price_per_sqft": 190, "cap_rate_avg_pct": 5.4, "population_growth_pct": 2.0},
    {"id": 10, "city": "Las Vegas",      "state": "NV", "median_price": 420000, "price_change_yoy_pct": 4.9,  "inventory_months": 2.6, "days_on_market": 21, "price_per_sqft": 220, "cap_rate_avg_pct": 4.7, "population_growth_pct": 2.5},
    {"id": 11, "city": "Raleigh",        "state": "NC", "median_price": 430000, "price_change_yoy_pct": 6.8,  "inventory_months": 1.8, "days_on_market": 14, "price_per_sqft": 240, "cap_rate_avg_pct": 5.1, "population_growth_pct": 3.3},
    {"id": 12, "city": "Orlando",        "state": "FL", "median_price": 380000, "price_change_yoy_pct": 6.4,  "inventory_months": 2.3, "days_on_market": 19, "price_per_sqft": 225, "cap_rate_avg_pct": 5.6, "population_growth_pct": 3.0},
    {"id": 13, "city": "San Antonio",    "state": "TX", "median_price": 295000, "price_change_yoy_pct": 4.1,  "inventory_months": 2.9, "days_on_market": 25, "price_per_sqft": 180, "cap_rate_avg_pct": 5.8, "population_growth_pct": 2.2},
    {"id": 14, "city": "Indianapolis",   "state": "IN", "median_price": 260000, "price_change_yoy_pct": 5.2,  "inventory_months": 2.4, "days_on_market": 20, "price_per_sqft": 160, "cap_rate_avg_pct": 6.2, "population_growth_pct": 1.5},
    {"id": 15, "city": "Columbus",       "state": "OH", "median_price": 285000, "price_change_yoy_pct": 4.7,  "inventory_months": 2.6, "days_on_market": 22, "price_per_sqft": 170, "cap_rate_avg_pct": 5.9, "population_growth_pct": 1.7},
    {"id": 16, "city": "Salt Lake City", "state": "UT", "median_price": 510000, "price_change_yoy_pct": 3.5,  "inventory_months": 3.2, "days_on_market": 27, "price_per_sqft": 275, "cap_rate_avg_pct": 4.3, "population_growth_pct": 2.6},
    {"id": 17, "city": "Jacksonville",   "state": "FL", "median_price": 335000, "price_change_yoy_pct": 5.8,  "inventory_months": 2.5, "days_on_market": 21, "price_per_sqft": 195, "cap_rate_avg_pct": 5.7, "population_growth_pct": 2.7},
    {"id": 18, "city": "Memphis",        "state": "TN", "median_price": 230000, "price_change_yoy_pct": 4.3,  "inventory_months": 2.7, "days_on_market": 24, "price_per_sqft": 145, "cap_rate_avg_pct": 7.1, "population_growth_pct": 0.8},
    {"id": 19, "city": "Richmond",       "state": "VA", "median_price": 370000, "price_change_yoy_pct": 5.0,  "inventory_months": 2.1, "days_on_market": 18, "price_per_sqft": 210, "cap_rate_avg_pct": 5.0, "population_growth_pct": 1.8},
    {"id": 20, "city": "Louisville",     "state": "KY", "median_price": 255000, "price_change_yoy_pct": 4.6,  "inventory_months": 2.8, "days_on_market": 23, "price_per_sqft": 155, "cap_rate_avg_pct": 6.0, "population_growth_pct": 1.2},
    {"id": 21, "city": "Oklahoma City",  "state": "OK", "median_price": 235000, "price_change_yoy_pct": 3.9,  "inventory_months": 3.1, "days_on_market": 27, "price_per_sqft": 140, "cap_rate_avg_pct": 6.4, "population_growth_pct": 1.3},
    {"id": 22, "city": "Kansas City",    "state": "MO", "median_price": 285000, "price_change_yoy_pct": 4.2,  "inventory_months": 2.9, "days_on_market": 24, "price_per_sqft": 165, "cap_rate_avg_pct": 6.1, "population_growth_pct": 1.4},
    {"id": 23, "city": "Minneapolis",    "state": "MN", "median_price": 370000, "price_change_yoy_pct": 2.8,  "inventory_months": 3.5, "days_on_market": 31, "price_per_sqft": 205, "cap_rate_avg_pct": 4.5, "population_growth_pct": 1.1},
    {"id": 24, "city": "Pittsburgh",     "state": "PA", "median_price": 230000, "price_change_yoy_pct": 3.3,  "inventory_months": 3.3, "days_on_market": 29, "price_per_sqft": 145, "cap_rate_avg_pct": 6.5, "population_growth_pct": 0.5},
    {"id": 25, "city": "Cincinnati",     "state": "OH", "median_price": 245000, "price_change_yoy_pct": 4.0,  "inventory_months": 2.8, "days_on_market": 25, "price_per_sqft": 150, "cap_rate_avg_pct": 6.3, "population_growth_pct": 0.9},
    {"id": 26, "city": "Boise",          "state": "ID", "median_price": 465000, "price_change_yoy_pct": 5.4,  "inventory_months": 2.4, "days_on_market": 20, "price_per_sqft": 265, "cap_rate_avg_pct": 4.4, "population_growth_pct": 4.1},
    {"id": 27, "city": "Spokane",        "state": "WA", "median_price": 380000, "price_change_yoy_pct": 4.5,  "inventory_months": 2.6, "days_on_market": 22, "price_per_sqft": 215, "cap_rate_avg_pct": 4.8, "population_growth_pct": 2.0},
    {"id": 28, "city": "Albuquerque",    "state": "NM", "median_price": 300000, "price_change_yoy_pct": 4.8,  "inventory_months": 2.5, "days_on_market": 21, "price_per_sqft": 175, "cap_rate_avg_pct": 5.6, "population_growth_pct": 1.0},
    {"id": 29, "city": "Tucson",         "state": "AZ", "median_price": 310000, "price_change_yoy_pct": 5.1,  "inventory_months": 2.7, "days_on_market": 23, "price_per_sqft": 180, "cap_rate_avg_pct": 5.5, "population_growth_pct": 1.6},
    {"id": 30, "city": "El Paso",        "state": "TX", "median_price": 225000, "price_change_yoy_pct": 4.6,  "inventory_months": 2.9, "days_on_market": 25, "price_per_sqft": 135, "cap_rate_avg_pct": 6.6, "population_growth_pct": 1.1},
]

TIERS = {
    "FREE":       {"price_usd": 0,   "markets": 5,    "forecasting": False, "export": False},
    "PRO":        {"price_usd": 49,  "markets": 15,   "forecasting": True,  "export": False},
    "ENTERPRISE": {"price_usd": 199, "markets": None, "forecasting": True,  "export": True},
}


class MarketAnalysisBot:
    """Analyzes real estate market trends across 30 US metros.

    Competes with CoStar and Mashvisor by providing cap rate analysis,
    price forecasts, and investor scoring in one bot.
    Monetization: $49/month PRO or $199/month ENTERPRISE subscription.
    """

    def __init__(self, tier: str = "FREE"):
        if tier not in TIERS:
            raise ValueError(f"Invalid tier '{tier}'. Choose from {list(TIERS)}")
        self.tier = tier
        self._config = TIERS[tier]
        self._flow = GlobalAISourcesFlow(bot_name="MarketAnalysisBot")

    def _get_markets(self) -> list[dict]:
        limit = self._config["markets"]
        return EXAMPLES[:limit] if limit else EXAMPLES

    def get_market_overview(self, city: str) -> dict:
        """Return detailed market overview for a city."""
        market = next((m for m in EXAMPLES if m["city"].lower() == city.lower()), None)
        if market is None:
            raise ValueError(f"City '{city}' not found. Available: {[m['city'] for m in EXAMPLES]}")
        result = dict(market)
        result["market_type"] = "Seller's" if market["inventory_months"] < 3 else "Buyer's"
        result["investment_grade"] = self._grade_market(market)
        if self._config["forecasting"]:
            result["forecast_12mo_price_change_pct"] = round(market["price_change_yoy_pct"] * 0.9, 1)
            result["forecast_24mo_price_change_pct"] = round(market["price_change_yoy_pct"] * 1.7, 1)
        return result

    def get_top_investment_markets(self, count: int = 5) -> list[dict]:
        """Return top N markets ranked by investment score."""
        markets = self._get_markets()
        scored = [
            {**m, "investment_score": self._score_market(m)}
            for m in markets
        ]
        scored.sort(key=lambda x: x["investment_score"], reverse=True)
        return scored[:count]

    def compare_markets(self, city1: str, city2: str) -> dict:
        """Compare two markets side by side."""
        m1 = self.get_market_overview(city1)
        m2 = self.get_market_overview(city2)
        winner = city1 if self._score_market(m1) >= self._score_market(m2) else city2
        return {
            city1: m1,
            city2: m2,
            "recommended": winner,
        }

    def get_high_cap_rate_markets(self, min_cap_rate: float = 5.5) -> list[dict]:
        """Return markets with average cap rates above the threshold."""
        return [m for m in self._get_markets() if m["cap_rate_avg_pct"] >= min_cap_rate]

    def get_fastest_growing_markets(self, count: int = 5) -> list[dict]:
        """Return the fastest-growing markets by YoY price change."""
        markets = sorted(self._get_markets(), key=lambda m: m["price_change_yoy_pct"], reverse=True)
        return markets[:count]

    def export_report(self, city: str) -> dict:
        """Export a full investment report for a city (ENTERPRISE only)."""
        if not self._config["export"]:
            raise PermissionError(
                "Report export requires ENTERPRISE tier. Upgrade at dreamcobots.com/pricing"
            )
        overview = self.get_market_overview(city)
        return {
            "report_type": "Investment Market Report",
            "generated_by": "DreamCo MarketAnalysisBot",
            "tier": self.tier,
            "market": overview,
            "comparable_markets": self.compare_markets(
                city, "Austin" if city != "Austin" else "Nashville"
            ),
        }

    def describe_tier(self) -> str:
        cfg = self._config
        limit = cfg["markets"] if cfg["markets"] else "all 30"
        lines = [
            f"=== MarketAnalysisBot — {self.tier} Tier ===",
            f"  Monthly price : ${cfg['price_usd']}/month",
            f"  Markets access: {limit}",
            f"  Forecasting   : {'enabled' if cfg['forecasting'] else 'disabled'}",
            f"  Export reports: {'enabled' if cfg['export'] else 'disabled (ENTERPRISE only)'}",
        ]
        return "\n".join(lines)

    def _grade_market(self, market: dict) -> str:
        score = self._score_market(market)
        if score >= 80:
            return "A+"
        if score >= 70:
            return "A"
        if score >= 60:
            return "B+"
        if score >= 50:
            return "B"
        return "C"

    def _score_market(self, market: dict) -> int:
        growth_score = min(30, int(market["price_change_yoy_pct"] * 4))
        cap_score = min(30, int(market["cap_rate_avg_pct"] * 4))
        pop_score = min(20, int(market["population_growth_pct"] * 6))
        days_score = max(0, 20 - int(market["days_on_market"] / 2))
        return growth_score + cap_score + pop_score + days_score

    def run(self) -> dict:
        """Run the GLOBAL AI SOURCES FLOW pipeline."""
        result = self._flow.run_pipeline(
            raw_data={"domain": "real_estate_market_analysis", "markets_count": len(EXAMPLES)},
            learning_method="supervised",
        )
        return {
            "pipeline_complete": result.get("pipeline_complete"),
            "top_markets": self.get_top_investment_markets(3),
        }


if __name__ == "__main__":
    bot = MarketAnalysisBot(tier="PRO")
    top = bot.get_top_investment_markets(5)
    print("Top 5 Investment Markets:")
    for m in top:
        print(f"  {m['city']}, {m['state']} — Score: {m['investment_score']} — Cap Rate: {m['cap_rate_avg_pct']}%")
    print(bot.describe_tier())

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


class MarketAnalysisBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


_orig_marketanalysis_bot_init = MarketAnalysisBot.__init__


def _marketanalysis_bot_new_init(self, tier=Tier.FREE):
    tier_val = tier.value if hasattr(tier, "value") else str(tier).lower()
    _orig_marketanalysis_bot_init(self, tier_val.upper())
    self.tier = Tier(tier_val)


MarketAnalysisBot.__init__ = _marketanalysis_bot_new_init
MarketAnalysisBot.RESULT_LIMITS = {"free": 5, "pro": 25, "enterprise": 100}


def _marketanalysis_bot_monthly_price(self):
    return _TIER_MONTHLY_PRICE[self.tier.value]


def _marketanalysis_bot_get_tier_info(self):
    return {
        "tier": self.tier.value,
        "monthly_price_usd": self.monthly_price(),
        "result_limit": self.RESULT_LIMITS[self.tier.value],
    }


def _marketanalysis_bot_enforce_tier(self, required_value):
    order = ["free", "pro", "enterprise"]
    if order.index(self.tier.value) < order.index(required_value):
        raise MarketAnalysisBotTierError(
            f"{required_value.upper()} tier required. Current: {self.tier.value}"
        )


def _marketanalysis_bot_list_items(self, limit=None):
    cap = limit if limit else self.RESULT_LIMITS[self.tier.value]
    return _random_tier.sample(EXAMPLES, min(cap, len(EXAMPLES)))


def _marketanalysis_bot_analyze(self):
    self._enforce_tier("pro")
    return {"bot": "MarketAnalysisBot", "tier": self.tier.value, "count": len(EXAMPLES)}


def _marketanalysis_bot_export_report(self, city=None):
    try:
        self._enforce_tier("enterprise")
    except MarketAnalysisBotTierError as exc:
        raise PermissionError(
            "Report export requires ENTERPRISE tier. Upgrade at dreamcobots.com/pricing"
        ) from exc
    target_city = city if city else EXAMPLES[0].get("city", "")
    overview = self.get_market_overview(target_city) if target_city else {}
    return {
        "report_type": "Investment Market Report",
        "generated_by": "DreamCo MarketAnalysisBot",
        "bot": "MarketAnalysisBot",
        "tier": self.tier.value,
        "total_items": len(EXAMPLES),
        "market": overview,
        "items": EXAMPLES,
    }


MarketAnalysisBot.monthly_price = _marketanalysis_bot_monthly_price
MarketAnalysisBot.get_tier_info = _marketanalysis_bot_get_tier_info
MarketAnalysisBot._enforce_tier = _marketanalysis_bot_enforce_tier
MarketAnalysisBot.list_items = _marketanalysis_bot_list_items
MarketAnalysisBot.analyze = _marketanalysis_bot_analyze
MarketAnalysisBot.export_report = _marketanalysis_bot_export_report
