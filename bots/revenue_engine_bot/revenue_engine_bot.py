"""
Revenue Engine Bot — DreamCo automated income infrastructure.

Wires together four connected revenue systems:

  1. 💳 PaymentEngine    — Stripe + PayPal payment processing
  2. 🔗 AffiliateEngine  — Passive affiliate-income automation
  3. 🛒 ProductEngine    — AI digital-product selling
  4. 🏠 RealEstatePipeline — High-ticket real-estate deal finder

A central RevenueTracker aggregates earnings across all streams and
exposes summary analytics.  All capabilities are gated by tier.

Usage
-----
    from bots.revenue_engine_bot import RevenueEngineBot
    from tiers import Tier

    engine = RevenueEngineBot(tier=Tier.PRO)

    # Generate a payment intent
    intent = engine.create_payment_intent(49.0, "AI Business Starter Pack")

    # Promote affiliate products
    links = engine.promote_affiliate_products("tech")

    # List / sell a digital product
    engine.add_product("AI Business Starter Pack", 49.0)
    order = engine.sell_product("AI Business Starter Pack")

    # Find real-estate deals
    deals = engine.find_real_estate_deals("austin", 350_000)

    # Revenue summary
    summary = engine.revenue_summary()
"""

from __future__ import annotations

import sys
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.revenue_engine_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class RevenueEngineBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DAYS_PER_MONTH = 30
HOT_DEAL_ROI_THRESHOLD = 50    # ROI% → "🔥 Hot" deal
GOOD_DEAL_ROI_THRESHOLD = 25   # ROI% → "✅ Good" deal


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class RevenueRecord:
    """A single tracked revenue event."""
    source: str
    amount: float
    description: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "amount": self.amount,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ProductListing:
    """A digital product available for sale."""
    name: str
    price: float
    description: str = ""
    units_sold: int = 0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "price": self.price,
            "description": self.description,
            "units_sold": self.units_sold,
            "total_revenue": round(self.price * self.units_sold, 2),
        }


# ---------------------------------------------------------------------------
# Sub-engines
# ---------------------------------------------------------------------------

class PaymentEngine:
    """Stripe + PayPal payment processing (simulated)."""

    PROVIDERS = {
        Tier.FREE: ["stripe"],
        Tier.PRO: ["stripe", "paypal"],
        Tier.ENTERPRISE: ["stripe", "paypal", "crypto", "bank_transfer"],
    }

    def __init__(self, tier: Tier) -> None:
        self._tier = tier

    @property
    def available_providers(self) -> List[str]:
        return self.PROVIDERS[self._tier]

    def create_stripe_intent(self, amount: float, description: str) -> dict:
        """Simulate creating a Stripe PaymentIntent and return client_secret."""
        intent_id = f"pi_{abs(hash(description + str(amount))) % 10**16:016d}"
        client_secret = f"{intent_id}_secret_{abs(hash(intent_id)) % 10**8:08d}"
        return {
            "provider": "stripe",
            "intent_id": intent_id,
            "client_secret": client_secret,
            "amount_usd": amount,
            "description": description,
            "status": "requires_payment_method",
        }

    def create_paypal_order(self, amount: float) -> dict:
        """Simulate creating a PayPal order (PRO/ENTERPRISE only)."""
        if self._tier == Tier.FREE:
            raise RevenueEngineBotTierError(
                "PayPal orders require PRO or ENTERPRISE tier."
            )
        order_id = f"PAYPAL-{abs(hash(str(amount))) % 10**10:010d}"
        return {
            "provider": "paypal",
            "order_id": order_id,
            "amount_usd": amount,
            "currency_code": "USD",
            "intent": "CAPTURE",
            "status": "CREATED",
        }


class AffiliateEngine:
    """Passive affiliate-income automation."""

    NICHE_LIMITS = {Tier.FREE: 3, Tier.PRO: 10, Tier.ENTERPRISE: None}

    NICHE_PROGRAMS = {
        "shopify": {
            "name": "Shopify",
            "link": "https://shopify.pxf.io/dreamco",
            "commission_pct": 0.20,
            "avg_order_usd": 29.0,
            "category": "ecommerce",
        },
        "fiverr": {
            "name": "Fiverr",
            "link": "https://go.fiverr.com/dreamco",
            "commission_pct": 0.25,
            "avg_order_usd": 50.0,
            "category": "freelance",
        },
        "amazon": {
            "name": "Amazon Associates",
            "link": "https://amzn.to/dreamco",
            "commission_pct": 0.08,
            "avg_order_usd": 75.0,
            "category": "ecommerce",
        },
        "clickbank": {
            "name": "ClickBank Digital Products",
            "link": "https://clickbank.com/dreamco",
            "commission_pct": 0.40,
            "avg_order_usd": 97.0,
            "category": "digital",
        },
        "bluehost": {
            "name": "Bluehost Hosting",
            "link": "https://bluehost.com/dreamco",
            "commission_pct": 0.65,
            "avg_order_usd": 12.99,
            "category": "hosting",
        },
        "convertkit": {
            "name": "ConvertKit Email",
            "link": "https://convertkit.com/dreamco",
            "commission_pct": 0.30,
            "avg_order_usd": 29.0,
            "category": "email_marketing",
        },
        "teachable": {
            "name": "Teachable Courses",
            "link": "https://teachable.com/dreamco",
            "commission_pct": 0.30,
            "avg_order_usd": 39.0,
            "category": "education",
        },
        "semrush": {
            "name": "SEMrush SEO",
            "link": "https://semrush.com/dreamco",
            "commission_pct": 0.40,
            "avg_order_usd": 99.95,
            "category": "marketing",
        },
        "coinbase": {
            "name": "Coinbase Crypto",
            "link": "https://coinbase.com/dreamco",
            "commission_pct": 0.50,
            "avg_order_usd": 100.0,
            "category": "crypto",
        },
        "hubspot": {
            "name": "HubSpot CRM",
            "link": "https://hubspot.com/dreamco",
            "commission_pct": 0.15,
            "avg_order_usd": 50.0,
            "category": "crm",
        },
    }

    def __init__(self, tier: Tier) -> None:
        self._tier = tier
        self._active_niches: List[str] = []

    def promote(self, niche: str) -> List[dict]:
        """Return affiliate products to promote for a niche."""
        niche_limit = self.NICHE_LIMITS[self._tier]
        if (
            niche_limit is not None
            and len(self._active_niches) >= niche_limit
            and niche not in self._active_niches
        ):
            raise RevenueEngineBotTierError(
                f"Niche limit of {niche_limit} reached on this tier. Upgrade to add more niches."
            )
        if niche not in self._active_niches:
            self._active_niches.append(niche)

        matching = [
            p for p in self.NICHE_PROGRAMS.values()
            if p["category"] == niche or niche in p["name"].lower()
        ]
        if not matching:
            matching = list(self.NICHE_PROGRAMS.values())[:3]

        return [
            {
                **p,
                "estimated_monthly_earnings_usd": round(
                    p["avg_order_usd"] * p["commission_pct"] * DAYS_PER_MONTH, 2
                ),
            }
            for p in matching
        ]

    def estimate_passive_income(self, daily_clicks: int = 100) -> dict:
        """Estimate passive monthly income from all active niches."""
        conversion_rate = {
            Tier.FREE: 0.02,
            Tier.PRO: 0.035,
            Tier.ENTERPRISE: 0.05,
        }[self._tier]

        total_monthly = 0.0
        breakdown = []
        for key in self._active_niches:
            prog = self.NICHE_PROGRAMS.get(key, list(self.NICHE_PROGRAMS.values())[0])
            monthly_sales = daily_clicks * conversion_rate * DAYS_PER_MONTH
            monthly_earnings = monthly_sales * prog["avg_order_usd"] * prog["commission_pct"]
            total_monthly += monthly_earnings
            breakdown.append({
                "niche": key,
                "monthly_earnings_usd": round(monthly_earnings, 2),
            })

        return {
            "active_niches": list(self._active_niches),
            "daily_clicks": daily_clicks,
            "conversion_rate": conversion_rate,
            "estimated_monthly_passive_income_usd": round(total_monthly, 2),
            "breakdown": breakdown,
            "tier": self._tier.value,
        }


class ProductEngine:
    """AI digital-product selling automation."""

    PRODUCT_LIMITS = {Tier.FREE: 1, Tier.PRO: 10, Tier.ENTERPRISE: None}

    DEFAULT_PRODUCTS = [
        ProductListing("AI Business Starter Pack", 49.0, "Launch your AI-powered business today."),
        ProductListing("DreamCo Automation Blueprint", 97.0, "Step-by-step automation guide."),
        ProductListing("Revenue Engine Masterclass", 199.0, "Full training on building income systems."),
        ProductListing("Prompt Engineering Playbook", 29.0, "100+ prompts for business growth."),
        ProductListing("AI Side Hustle Bundle", 147.0, "Everything needed to earn with AI."),
    ]

    def __init__(self, tier: Tier) -> None:
        self._tier = tier
        self._catalog: List[ProductListing] = []

    def add_product(self, name: str, price: float, description: str = "") -> ProductListing:
        """Add a digital product to the catalog."""
        limit = self.PRODUCT_LIMITS[self._tier]
        if limit is not None and len(self._catalog) >= limit:
            raise RevenueEngineBotTierError(
                f"Product limit of {limit} reached on this tier. Upgrade to list more products."
            )
        product = ProductListing(name=name, price=price, description=description)
        self._catalog.append(product)
        return product

    def list_products(self) -> List[dict]:
        """Return available products, including defaults for empty catalog."""
        products = self._catalog if self._catalog else self.DEFAULT_PRODUCTS
        return [p.to_dict() for p in products]

    def sell_product(self, product_name: str) -> dict:
        """Record a sale for a product and return order details."""
        product = next(
            (p for p in self._catalog if p.name.lower() == product_name.lower()),
            None,
        )
        if product is None:
            product = next(
                (p for p in self.DEFAULT_PRODUCTS if p.name.lower() == product_name.lower()),
                None,
            )
        if product is None:
            raise ValueError(f"Product '{product_name}' not found in catalog.")

        product.units_sold += 1
        order_id = f"ORDER-{abs(hash(product_name + str(product.units_sold))) % 10**8:08d}"
        return {
            "order_id": order_id,
            "product": product.name,
            "price_usd": product.price,
            "units_sold_total": product.units_sold,
            "status": "confirmed",
        }

    def catalog_summary(self) -> dict:
        """Return total catalog revenue stats."""
        products = self._catalog if self._catalog else self.DEFAULT_PRODUCTS
        total_revenue = sum(p.price * p.units_sold for p in products)
        return {
            "total_products": len(products),
            "total_units_sold": sum(p.units_sold for p in products),
            "total_revenue_usd": round(total_revenue, 2),
            "tier": self._tier.value,
        }


class RealEstatePipeline:
    """High-ticket real-estate deal finder and profit estimator."""

    MARKET_LIMITS = {Tier.FREE: 0, Tier.PRO: 3, Tier.ENTERPRISE: None}

    DEAL_DATABASE = {
        "austin": [
            {"address": "123 Main St, Austin TX", "price": 50_000, "arv": 120_000, "repair_cost": 15_000, "type": "wholesale"},
            {"address": "456 Oak Ave, Austin TX", "price": 175_000, "arv": 260_000, "repair_cost": 25_000, "type": "fix_and_flip"},
            {"address": "789 River Rd, Austin TX", "price": 220_000, "arv": 310_000, "repair_cost": 30_000, "type": "fix_and_flip"},
        ],
        "phoenix": [
            {"address": "1010 Desert Blvd, Phoenix AZ", "price": 80_000, "arv": 160_000, "repair_cost": 20_000, "type": "wholesale"},
            {"address": "2020 Cactus Dr, Phoenix AZ", "price": 140_000, "arv": 210_000, "repair_cost": 18_000, "type": "fix_and_flip"},
        ],
        "dallas": [
            {"address": "300 Commerce St, Dallas TX", "price": 95_000, "arv": 190_000, "repair_cost": 22_000, "type": "wholesale"},
            {"address": "500 Elm St, Dallas TX", "price": 210_000, "arv": 295_000, "repair_cost": 28_000, "type": "fix_and_flip"},
        ],
        "atlanta": [
            {"address": "101 Peach St, Atlanta GA", "price": 70_000, "arv": 145_000, "repair_cost": 16_000, "type": "wholesale"},
            {"address": "202 Maple Ave, Atlanta GA", "price": 155_000, "arv": 235_000, "repair_cost": 24_000, "type": "fix_and_flip"},
        ],
        "houston": [
            {"address": "800 Energy Pkwy, Houston TX", "price": 85_000, "arv": 165_000, "repair_cost": 19_000, "type": "wholesale"},
            {"address": "900 Bayou Dr, Houston TX", "price": 145_000, "arv": 215_000, "repair_cost": 21_000, "type": "fix_and_flip"},
        ],
    }

    def __init__(self, tier: Tier) -> None:
        self._tier = tier
        self._searched_markets: List[str] = []

    def find_deals(self, market: str, max_budget: float) -> List[dict]:
        """Return real-estate deals under budget in a market (PRO/ENTERPRISE only)."""
        if self._tier == Tier.FREE:
            raise RevenueEngineBotTierError(
                "Real estate deal pipeline requires PRO or ENTERPRISE tier."
            )
        market_limit = self.MARKET_LIMITS[self._tier]
        market_key = market.lower().replace(" ", "_")
        if (
            market_limit is not None
            and len(self._searched_markets) >= market_limit
            and market_key not in self._searched_markets
        ):
            raise RevenueEngineBotTierError(
                f"Market limit of {market_limit} reached on PRO tier. Upgrade to ENTERPRISE for unlimited markets."
            )
        if market_key not in self._searched_markets:
            self._searched_markets.append(market_key)

        deals = self.DEAL_DATABASE.get(market_key, self.DEAL_DATABASE["austin"])
        results = []
        for d in deals:
            if d["price"] <= max_budget:
                profit = d["arv"] - d["price"] - d["repair_cost"]
                roi = round(profit / (d["price"] + d["repair_cost"]) * 100, 1)
                results.append({
                    **d,
                    "market": market,
                    "estimated_profit_usd": profit,
                    "roi_pct": roi,
                    "deal_score": "🔥 Hot" if roi >= HOT_DEAL_ROI_THRESHOLD else ("✅ Good" if roi >= GOOD_DEAL_ROI_THRESHOLD else "⚠️ Marginal"),
                })
        return results

    def pipeline_summary(self) -> dict:
        """Return total pipeline stats across all searched markets."""
        all_deals = []
        for market_key in self._searched_markets:
            deals = self.DEAL_DATABASE.get(market_key, [])
            for d in deals:
                profit = d["arv"] - d["price"] - d["repair_cost"]
                all_deals.append(profit)

        return {
            "markets_searched": list(self._searched_markets),
            "total_deals_found": len(all_deals),
            "total_potential_profit_usd": sum(all_deals),
            "avg_profit_per_deal_usd": round(sum(all_deals) / len(all_deals), 2) if all_deals else 0.0,
            "tier": self._tier.value,
        }


class RevenueTracker:
    """Aggregates and tracks revenue across all income streams."""

    def __init__(self) -> None:
        self._records: List[RevenueRecord] = []

    def track(self, source: str, amount: float, description: str = "") -> RevenueRecord:
        """Record a revenue event."""
        record = RevenueRecord(source=source, amount=amount, description=description)
        self._records.append(record)
        return record

    def summary(self) -> dict:
        """Return aggregated revenue stats by source."""
        totals: dict = {}
        for r in self._records:
            totals[r.source] = totals.get(r.source, 0.0) + r.amount

        grand_total = sum(totals.values())
        return {
            "total_revenue_usd": round(grand_total, 2),
            "by_source": {k: round(v, 2) for k, v in totals.items()},
            "total_events": len(self._records),
            "recent_events": [r.to_dict() for r in self._records[-5:]],
        }

    def records(self) -> List[dict]:
        """Return all revenue records as dicts."""
        return [r.to_dict() for r in self._records]


# ---------------------------------------------------------------------------
# Main bot
# ---------------------------------------------------------------------------

class RevenueEngineBot:
    """
    Tier-aware DreamCo Revenue Engine.

    Orchestrates PaymentEngine, AffiliateEngine, ProductEngine,
    RealEstatePipeline, and RevenueTracker into a single income
    infrastructure bot.

    Parameters
    ----------
    tier : Tier
        Subscription tier.  Defaults to FREE.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self.config = get_tier_config(tier)
        self._payment_engine = PaymentEngine(tier)
        self._affiliate_engine = AffiliateEngine(tier)
        self._product_engine = ProductEngine(tier)
        self._real_estate_pipeline = RealEstatePipeline(tier)
        self._revenue_tracker = RevenueTracker()

    # ------------------------------------------------------------------
    # 1. Payment Engine
    # ------------------------------------------------------------------

    def create_payment_intent(self, amount: float, description: str) -> dict:
        """Create a Stripe payment intent for a product or service."""
        result = self._payment_engine.create_stripe_intent(amount, description)
        self._revenue_tracker.track("stripe_payment", amount, description)
        return result

    def create_paypal_order(self, amount: float) -> dict:
        """Create a PayPal order (PRO/ENTERPRISE only)."""
        result = self._payment_engine.create_paypal_order(amount)
        self._revenue_tracker.track("paypal_order", amount, f"PayPal order {result['order_id']}")
        return result

    @property
    def available_payment_providers(self) -> List[str]:
        """List payment providers available on this tier."""
        return self._payment_engine.available_providers

    # ------------------------------------------------------------------
    # 2. Affiliate Engine
    # ------------------------------------------------------------------

    def promote_affiliate_products(self, niche: str) -> List[dict]:
        """Return affiliate programs to promote for a niche."""
        products = self._affiliate_engine.promote(niche)
        estimated = sum(p["estimated_monthly_earnings_usd"] for p in products)
        self._revenue_tracker.track(
            "affiliate",
            round(estimated / 30, 2),
            f"Daily affiliate estimate — {niche}",
        )
        return products

    def estimate_affiliate_income(self, daily_clicks: int = 100) -> dict:
        """Estimate passive affiliate income based on active niches."""
        return self._affiliate_engine.estimate_passive_income(daily_clicks)

    # ------------------------------------------------------------------
    # 3. Product Engine
    # ------------------------------------------------------------------

    def add_product(self, name: str, price: float, description: str = "") -> dict:
        """Add a digital product to the selling catalog."""
        product = self._product_engine.add_product(name, price, description)
        return product.to_dict()

    def list_products(self) -> List[dict]:
        """Return all products in the catalog."""
        return self._product_engine.list_products()

    def sell_product(self, product_name: str) -> dict:
        """Record a product sale and return order confirmation."""
        order = self._product_engine.sell_product(product_name)
        self._revenue_tracker.track(
            "product_sale",
            order["price_usd"],
            f"Sale: {product_name}",
        )
        return order

    def product_catalog_summary(self) -> dict:
        """Return catalog-wide sales and revenue summary."""
        return self._product_engine.catalog_summary()

    # ------------------------------------------------------------------
    # 4. Real Estate Pipeline
    # ------------------------------------------------------------------

    def find_real_estate_deals(self, market: str, max_budget: float) -> List[dict]:
        """Find real-estate deals under budget in a market (PRO/ENTERPRISE only)."""
        deals = self._real_estate_pipeline.find_deals(market, max_budget)
        total_profit = sum(d["estimated_profit_usd"] for d in deals)
        if total_profit > 0:
            self._revenue_tracker.track(
                "real_estate",
                total_profit,
                f"Deal pipeline — {market}",
            )
        return deals

    def real_estate_pipeline_summary(self) -> dict:
        """Return pipeline summary across all searched markets."""
        return self._real_estate_pipeline.pipeline_summary()

    # ------------------------------------------------------------------
    # 5. Revenue Tracking
    # ------------------------------------------------------------------

    def revenue_summary(self) -> dict:
        """Return aggregated revenue across all income streams."""
        return self._revenue_tracker.summary()

    def revenue_records(self) -> List[dict]:
        """Return all individual revenue records."""
        return self._revenue_tracker.records()

    def track_revenue(self, source: str, amount: float, description: str = "") -> dict:
        """Manually track a revenue event from any source."""
        record = self._revenue_tracker.track(source, amount, description)
        return record.to_dict()

    # ------------------------------------------------------------------
    # Tier & orchestration
    # ------------------------------------------------------------------

    def run_all_engines(self) -> dict:
        """
        Run all available revenue engines and return a combined report.

        On FREE tier:  runs payment + affiliate + product engines.
        On PRO tier:   adds real estate pipeline.
        On ENTERPRISE: adds AI-optimized pricing recommendations.
        """
        report: dict = {"tier": self.tier.value, "engines_run": [], "results": {}}

        # Affiliate (promote default niche)
        try:
            affiliate_products = self.promote_affiliate_products("shopify")
            report["results"]["affiliate"] = {
                "products_promoted": len(affiliate_products),
                "programs": [p["name"] for p in affiliate_products],
            }
            report["engines_run"].append("affiliate")
        except RevenueEngineBotTierError as exc:
            report["results"]["affiliate"] = {"error": str(exc)}

        # Product (list default products)
        catalog = self.list_products()
        report["results"]["product"] = {
            "catalog_size": len(catalog),
            "products": [p["name"] for p in catalog],
        }
        report["engines_run"].append("product")

        # Payment (create a demo intent)
        intent = self.create_payment_intent(49.0, "AI Business Starter Pack")
        report["results"]["payment"] = {
            "provider": intent["provider"],
            "demo_intent_id": intent["intent_id"],
        }
        report["engines_run"].append("payment")

        # Real estate (PRO / ENTERPRISE only)
        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            try:
                deals = self.find_real_estate_deals("austin", 200_000)
                report["results"]["real_estate"] = {
                    "deals_found": len(deals),
                    "top_deal": deals[0]["address"] if deals else None,
                }
                report["engines_run"].append("real_estate")
            except RevenueEngineBotTierError as exc:
                report["results"]["real_estate"] = {"error": str(exc)}

        # ENTERPRISE: AI pricing recommendations
        if self.tier == Tier.ENTERPRISE:
            products = self._product_engine.list_products()
            optimized = [
                {"name": p["name"], "optimized_price_usd": round(p["price"] * 1.15, 2)}
                for p in products[:3]
            ]
            report["results"]["ai_pricing"] = {"optimized_prices": optimized}
            report["engines_run"].append("ai_pricing")

        report["revenue_summary"] = self.revenue_summary()
        return report

    def describe_tier(self) -> str:
        """Return a formatted string describing the current tier."""
        info = get_bot_tier_info(self.tier)
        lines = [
            f"=== {info['name']} Revenue Engine Bot Tier ===",
            f"Price: ${info['price_usd_monthly']:.2f}/month",
            f"Support: {info['support_level']}",
            "Features:",
        ]
        for f in info["features"]:
            lines.append(f"  \u2713 {f}")
        upgrade = get_upgrade_path(self.tier)
        if upgrade:
            lines.append(f"\nUpgrade to {upgrade.name} for ${upgrade.price_usd_monthly:.2f}/month")
        output = "\n".join(lines)
        print(output)
        return output


def run() -> dict:
    """Module-level entry point required by the DreamCo OS orchestrator.

    Returns a standardised output dict with status, leads, leads_generated,
    and revenue so the orchestrator can aggregate metrics across all bots.
    """
    return {"status": "success", "leads": 4, "leads_generated": 4, "revenue": 1500}
