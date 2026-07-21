"""Affiliate Bot — tier-aware affiliate marketing automation."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.affiliate_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401


class AffiliateBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class AffiliateBot:
    """Tier-aware affiliate marketing bot."""

    NICHE_LIMITS = {Tier.FREE: 3, Tier.PRO: 10, Tier.ENTERPRISE: None}
    PRODUCT_LIMITS = {Tier.FREE: 10, Tier.PRO: 50, Tier.ENTERPRISE: None}

    NICHE_DATA = {
        "tech": [
            {"id": "p001", "name": "Laptop Stand", "commission_rate": 0.08, "avg_price": 49.99, "platform": "Amazon"},
            {"id": "p002", "name": "Mechanical Keyboard", "commission_rate": 0.07, "avg_price": 89.99, "platform": "Amazon"},
            {"id": "p003", "name": "USB Hub", "commission_rate": 0.09, "avg_price": 29.99, "platform": "Amazon"},
            {"id": "p004", "name": "Monitor Arm", "commission_rate": 0.08, "avg_price": 69.99, "platform": "ShareASale"},
            {"id": "p005", "name": "Webcam HD", "commission_rate": 0.07, "avg_price": 79.99, "platform": "CJ Affiliate"},
        ],
        "fitness": [
            {"id": "p011", "name": "Resistance Bands Set", "commission_rate": 0.12, "avg_price": 24.99, "platform": "Amazon"},
            {"id": "p012", "name": "Yoga Mat Premium", "commission_rate": 0.10, "avg_price": 59.99, "platform": "Amazon"},
            {"id": "p013", "name": "Protein Powder", "commission_rate": 0.15, "avg_price": 49.99, "platform": "ShareASale"},
            {"id": "p014", "name": "Foam Roller", "commission_rate": 0.11, "avg_price": 34.99, "platform": "Amazon"},
            {"id": "p015", "name": "Smart Scale", "commission_rate": 0.09, "avg_price": 69.99, "platform": "CJ Affiliate"},
        ],
        "home": [
            {"id": "p021", "name": "Air Purifier", "commission_rate": 0.08, "avg_price": 149.99, "platform": "Amazon"},
            {"id": "p022", "name": "Robot Vacuum", "commission_rate": 0.06, "avg_price": 299.99, "platform": "Amazon"},
            {"id": "p023", "name": "Smart Thermostat", "commission_rate": 0.07, "avg_price": 179.99, "platform": "ShareASale"},
            {"id": "p024", "name": "Instant Pot", "commission_rate": 0.08, "avg_price": 89.99, "platform": "Amazon"},
            {"id": "p025", "name": "LED Strip Lights", "commission_rate": 0.12, "avg_price": 24.99, "platform": "Amazon"},
        ],
        "beauty": [
            {"id": "p031", "name": "Face Serum", "commission_rate": 0.20, "avg_price": 49.99, "platform": "ShareASale"},
            {"id": "p032", "name": "Electric Toothbrush", "commission_rate": 0.10, "avg_price": 79.99, "platform": "Amazon"},
            {"id": "p033", "name": "Hair Dryer Pro", "commission_rate": 0.08, "avg_price": 129.99, "platform": "CJ Affiliate"},
            {"id": "p034", "name": "Skincare Set", "commission_rate": 0.18, "avg_price": 89.99, "platform": "ShareASale"},
        ],
        "finance": [
            {"id": "p041", "name": "Budget Planner App", "commission_rate": 0.30, "avg_price": 9.99, "platform": "ClickBank"},
            {"id": "p042", "name": "Investment Course", "commission_rate": 0.40, "avg_price": 199.99, "platform": "ClickBank"},
            {"id": "p043", "name": "Credit Repair Guide", "commission_rate": 0.35, "avg_price": 49.99, "platform": "ClickBank"},
        ],
        "travel": [
            {"id": "p051", "name": "Travel Insurance", "commission_rate": 0.10, "avg_price": 89.99, "platform": "CJ Affiliate"},
            {"id": "p052", "name": "Packing Cubes", "commission_rate": 0.12, "avg_price": 29.99, "platform": "Amazon"},
            {"id": "p053", "name": "Travel Pillow", "commission_rate": 0.10, "avg_price": 39.99, "platform": "Amazon"},
        ],
        "food": [
            {"id": "p061", "name": "Meal Kit Subscription", "commission_rate": 0.15, "avg_price": 79.99, "platform": "ShareASale"},
            {"id": "p062", "name": "Coffee Subscription", "commission_rate": 0.12, "avg_price": 29.99, "platform": "ShareASale"},
        ],
        "gaming": [
            {"id": "p071", "name": "Gaming Headset", "commission_rate": 0.07, "avg_price": 79.99, "platform": "Amazon"},
            {"id": "p072", "name": "Gaming Chair", "commission_rate": 0.06, "avg_price": 299.99, "platform": "Amazon"},
            {"id": "p073", "name": "Controller Pro", "commission_rate": 0.07, "avg_price": 69.99, "platform": "Amazon"},
        ],
        "education": [
            {"id": "p081", "name": "Online Course Platform", "commission_rate": 0.25, "avg_price": 199.99, "platform": "ClickBank"},
            {"id": "p082", "name": "Language Learning App", "commission_rate": 0.20, "avg_price": 79.99, "platform": "ShareASale"},
        ],
        "pets": [
            {"id": "p091", "name": "Auto Pet Feeder", "commission_rate": 0.10, "avg_price": 59.99, "platform": "Amazon"},
            {"id": "p092", "name": "GPS Pet Tracker", "commission_rate": 0.08, "avg_price": 99.99, "platform": "Amazon"},
        ],
    }

    BASE_DAILY_CLICKS = {
        "tech": 80, "fitness": 70, "home": 60, "beauty": 90,
        "finance": 40, "travel": 50, "food": 65, "gaming": 75,
        "education": 45, "pets": 55,
    }
    TIER_MULTIPLIER = {Tier.FREE: 1.0, Tier.PRO: 2.5, Tier.ENTERPRISE: 5.0}

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._clicks: dict = {}
        self._tracked_niches: list = []

    def recommend_products(self, niche: str) -> list:
        """Return recommended affiliate products for a niche."""
        niche_limit = self.NICHE_LIMITS[self.tier]
        if niche_limit is not None and len(self._tracked_niches) >= niche_limit and niche not in self._tracked_niches:
            raise AffiliateBotTierError(
                f"Niche limit of {niche_limit} reached on {self.config.name} tier. Upgrade to add more niches."
            )
        if niche not in self._tracked_niches:
            self._tracked_niches.append(niche)

        products = self.NICHE_DATA.get(niche.lower(), self.NICHE_DATA["tech"])
        product_limit = self.PRODUCT_LIMITS[self.tier]
        if product_limit is not None:
            products = products[:product_limit]

        multiplier = self.TIER_MULTIPLIER[self.tier]
        return [
            {
                **p,
                "estimated_monthly_earnings": round(p["avg_price"] * p["commission_rate"] * 30 * multiplier, 2),
                "tier": self.tier.value,
            }
            for p in products
        ]

    def estimate_daily_income(self, niche: str) -> dict:
        """Estimate daily affiliate income for a niche."""
        products = self.recommend_products(niche)
        clicks = self.BASE_DAILY_CLICKS.get(niche.lower(), 60)
        multiplier = self.TIER_MULTIPLIER[self.tier]
        conversion_rate = 0.02 if self.tier == Tier.FREE else (0.035 if self.tier == Tier.PRO else 0.05)

        total_daily = 0.0
        breakdown = []
        for p in products[:5]:
            daily_sales = clicks * conversion_rate
            daily_earnings = daily_sales * p["avg_price"] * p["commission_rate"] * multiplier
            total_daily += daily_earnings
            breakdown.append({"product": p["name"], "daily_earnings": round(daily_earnings, 2)})

        return {
            "niche": niche,
            "estimated_daily_income_usd": round(total_daily, 2),
            "daily_clicks": int(clicks * multiplier),
            "conversion_rate": conversion_rate,
            "breakdown": breakdown,
            "tier": self.tier.value,
        }

    def track_clicks(self, product_id: str) -> dict:
        """Track clicks for a product and return stats."""
        self._clicks[product_id] = self._clicks.get(product_id, 0) + 1
        base_conversions = max(1, self._clicks[product_id] // 50)
        multiplier = self.TIER_MULTIPLIER[self.tier]
        return {
            "product_id": product_id,
            "total_clicks": self._clicks[product_id],
            "conversions": int(base_conversions * multiplier),
            "conversion_rate": round(base_conversions / max(self._clicks[product_id], 1) * 100, 2),
            "tier": self.tier.value,
        }

    def generate_report(self) -> dict:
        """Generate an affiliate performance report."""
        total_clicks = sum(self._clicks.values())
        multiplier = self.TIER_MULTIPLIER[self.tier]
        estimated_revenue = round(total_clicks * 0.02 * 25.0 * multiplier, 2)

        report = {
            "tracked_niches": self._tracked_niches,
            "total_products_tracked": sum(len(self.NICHE_DATA.get(n, [])) for n in self._tracked_niches),
            "total_clicks": total_clicks,
            "estimated_monthly_revenue_usd": estimated_revenue,
            "top_products": sorted(self._clicks.items(), key=lambda x: x[1], reverse=True)[:5],
            "tier": self.tier.value,
            "features": BOT_FEATURES[self.tier.value],
        }
        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            report["detailed_breakdown"] = {
                pid: {"clicks": c, "est_revenue": round(c * 0.02 * 25.0 * multiplier, 2)}
                for pid, c in self._clicks.items()
            }
        return report

    def describe_tier(self) -> str:
        info = get_bot_tier_info(self.tier)
        lines = [
            f"=== {info['name']} Affiliate Bot Tier ===",
            f"Price: ${info['price_usd_monthly']:.2f}/month",
            f"Support: {info['support_level']}",
            "Features:",
        ]
        for f in info["features"]:
            lines.append(f"  \u2713 {f}")
        output = "\n".join(lines)
        print(output)
        return output
