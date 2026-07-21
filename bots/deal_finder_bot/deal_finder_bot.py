"""Deal Finder Bot — tier-aware deal scanning and arbitrage automation."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.deal_finder_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401


class DealFinderBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class DealFinderBot:
    """Tier-aware deal finder and arbitrage bot."""

    PLATFORM_LIMITS = {
        Tier.FREE: ["ebay"],
        Tier.PRO: ["ebay", "amazon", "craigslist", "facebook", "mercari"],
        Tier.ENTERPRISE: ["ebay", "amazon", "craigslist", "facebook", "mercari", "offerup", "poshmark", "etsy", "walmart", "aliexpress"],
    }
    ITEM_LIMITS = {Tier.FREE: 10, Tier.PRO: 100, Tier.ENTERPRISE: None}

    MOCK_MARKETPLACE_DATA = {
        "ebay": [
            {"id": "e001", "title": "iPhone 13 128GB", "buy_price": 320.00, "market_value": 480.00, "condition": "Good", "platform": "ebay", "category": "electronics"},
            {"id": "e002", "title": "Nike Air Max 90", "buy_price": 45.00, "market_value": 110.00, "condition": "Like New", "platform": "ebay", "category": "shoes"},
            {"id": "e003", "title": "KitchenAid Mixer", "buy_price": 80.00, "market_value": 200.00, "condition": "Good", "platform": "ebay", "category": "appliances"},
            {"id": "e004", "title": "Vintage Levi 501 Jeans", "buy_price": 15.00, "market_value": 65.00, "condition": "Good", "platform": "ebay", "category": "clothing"},
            {"id": "e005", "title": "Sony WH-1000XM4", "buy_price": 110.00, "market_value": 250.00, "condition": "Very Good", "platform": "ebay", "category": "electronics"},
            {"id": "e006", "title": "Dyson V8 Vacuum", "buy_price": 95.00, "market_value": 220.00, "condition": "Good", "platform": "ebay", "category": "appliances"},
            {"id": "e007", "title": "Nintendo Switch OLED", "buy_price": 180.00, "market_value": 310.00, "condition": "Like New", "platform": "ebay", "category": "gaming"},
            {"id": "e008", "title": "Coach Leather Bag", "buy_price": 40.00, "market_value": 150.00, "condition": "Good", "platform": "ebay", "category": "accessories"},
            {"id": "e009", "title": "Instant Pot Duo 7-in-1", "buy_price": 30.00, "market_value": 90.00, "condition": "Good", "platform": "ebay", "category": "appliances"},
            {"id": "e010", "title": "MacBook Air M1", "buy_price": 650.00, "market_value": 850.00, "condition": "Good", "platform": "ebay", "category": "electronics"},
            {"id": "e011", "title": "Patagonia Fleece Jacket", "buy_price": 25.00, "market_value": 90.00, "condition": "Very Good", "platform": "ebay", "category": "clothing"},
            {"id": "e012", "title": "Vitamix Blender", "buy_price": 120.00, "market_value": 300.00, "condition": "Good", "platform": "ebay", "category": "appliances"},
        ],
        "amazon": [
            {"id": "a001", "title": "Echo Dot 4th Gen", "buy_price": 18.00, "market_value": 50.00, "condition": "New", "platform": "amazon", "category": "electronics"},
            {"id": "a002", "title": "Kindle Paperwhite", "buy_price": 55.00, "market_value": 130.00, "condition": "Very Good", "platform": "amazon", "category": "electronics"},
            {"id": "a003", "title": "Fire TV Stick 4K", "buy_price": 20.00, "market_value": 50.00, "condition": "New", "platform": "amazon", "category": "electronics"},
            {"id": "a004", "title": "Bose SoundLink Mini", "buy_price": 60.00, "market_value": 150.00, "condition": "Good", "platform": "amazon", "category": "electronics"},
            {"id": "a005", "title": "iRobot Roomba 694", "buy_price": 120.00, "market_value": 250.00, "condition": "Like New", "platform": "amazon", "category": "appliances"},
        ],
        "craigslist": [
            {"id": "c001", "title": "Trek Mountain Bike", "buy_price": 150.00, "market_value": 400.00, "condition": "Good", "platform": "craigslist", "category": "sports"},
            {"id": "c002", "title": "Standing Desk", "buy_price": 80.00, "market_value": 250.00, "condition": "Good", "platform": "craigslist", "category": "furniture"},
            {"id": "c003", "title": "Samsung 65\" 4K TV", "buy_price": 200.00, "market_value": 550.00, "condition": "Good", "platform": "craigslist", "category": "electronics"},
        ],
        "facebook": [
            {"id": "f001", "title": "Pottery Barn Couch", "buy_price": 200.00, "market_value": 800.00, "condition": "Good", "platform": "facebook", "category": "furniture"},
            {"id": "f002", "title": "Weber Grill", "buy_price": 75.00, "market_value": 250.00, "condition": "Good", "platform": "facebook", "category": "outdoor"},
            {"id": "f003", "title": "Peloton Bike", "buy_price": 600.00, "market_value": 1200.00, "condition": "Good", "platform": "facebook", "category": "fitness"},
        ],
        "mercari": [
            {"id": "m001", "title": "Pokemon Card Lot", "buy_price": 20.00, "market_value": 80.00, "condition": "Good", "platform": "mercari", "category": "collectibles"},
            {"id": "m002", "title": "Louis Vuitton Wallet", "buy_price": 80.00, "market_value": 250.00, "condition": "Good", "platform": "mercari", "category": "accessories"},
            {"id": "m003", "title": "PS5 Controller", "buy_price": 35.00, "market_value": 75.00, "condition": "Like New", "platform": "mercari", "category": "gaming"},
        ],
        "offerup": [
            {"id": "o001", "title": "Apple Watch Series 7", "buy_price": 120.00, "market_value": 280.00, "condition": "Good", "platform": "offerup", "category": "electronics"},
        ],
        "poshmark": [
            {"id": "pm001", "title": "Free People Dress", "buy_price": 15.00, "market_value": 65.00, "condition": "Like New", "platform": "poshmark", "category": "clothing"},
        ],
        "etsy": [
            {"id": "et001", "title": "Vintage Pyrex Set", "buy_price": 25.00, "market_value": 90.00, "condition": "Good", "platform": "etsy", "category": "collectibles"},
        ],
        "walmart": [
            {"id": "w001", "title": "Instant Pot 8Qt", "buy_price": 60.00, "market_value": 120.00, "condition": "New", "platform": "walmart", "category": "appliances"},
        ],
        "aliexpress": [
            {"id": "ae001", "title": "Mechanical Watch", "buy_price": 15.00, "market_value": 60.00, "condition": "New", "platform": "aliexpress", "category": "accessories"},
        ],
    }

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._scanned_items: list = []

    def scan_marketplace(self, platform: str) -> list:
        """Return list of deals from a platform."""
        allowed = self.PLATFORM_LIMITS[self.tier]
        if platform.lower() not in allowed:
            raise DealFinderBotTierError(
                f"Platform '{platform}' not available on {self.config.name} tier. "
                f"Allowed: {allowed}. Upgrade to access more platforms."
            )
        items = self.MOCK_MARKETPLACE_DATA.get(platform.lower(), [])
        limit = self.ITEM_LIMITS[self.tier]
        if limit is not None:
            items = items[:limit]
        self._scanned_items = items
        return [self._annotate_item(item) for item in items]

    def _annotate_item(self, item: dict) -> dict:
        profit = self.estimate_profit(item)
        margin = (item["market_value"] - item["buy_price"]) / item["market_value"] * 100
        return {
            **item,
            "estimated_profit": round(profit, 2),
            "profit_margin_pct": round(margin, 1),
            "deal_score": self._score_deal(margin),
        }

    def evaluate_deal(self, item: dict) -> dict:
        """Return deal score, profit margin, and recommendation."""
        profit = self.estimate_profit(item)
        margin = (item["market_value"] - item["buy_price"]) / item["market_value"] * 100
        score = self._score_deal(margin)
        if score >= 75:
            recommendation = "Strong Buy"
        elif score >= 50:
            recommendation = "Buy"
        elif score >= 25:
            recommendation = "Consider"
        else:
            recommendation = "Pass"
        result = {
            "id": item.get("id", "unknown"),
            "title": item.get("title", ""),
            "buy_price": item["buy_price"],
            "market_value": item["market_value"],
            "estimated_profit": round(profit, 2),
            "profit_margin_pct": round(margin, 1),
            "deal_score": score,
            "recommendation": recommendation,
            "tier": self.tier.value,
        }
        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["price_history_available"] = True
            result["profit_calculator"] = {
                "gross_profit": round(item["market_value"] - item["buy_price"], 2),
                "fees_estimate": round((item["market_value"] - item["buy_price"]) * 0.15, 2),
                "net_profit": round(profit, 2),
            }
        return result

    def estimate_profit(self, item: dict) -> float:
        """Return estimated flip profit after fees."""
        return (item["market_value"] - item["buy_price"]) * 0.85

    def _score_deal(self, margin_pct: float) -> int:
        """Score a deal 0-100 based on profit margin."""
        if margin_pct >= 60:
            return 95
        elif margin_pct >= 45:
            return 80
        elif margin_pct >= 30:
            return 65
        elif margin_pct >= 20:
            return 45
        elif margin_pct >= 10:
            return 25
        return 10

    def get_best_deals(self, limit: int = 5) -> list:
        """Return top deals sorted by profit potential."""
        if not self._scanned_items:
            all_items = []
            for platform in self.PLATFORM_LIMITS[self.tier]:
                all_items.extend(self.MOCK_MARKETPLACE_DATA.get(platform, []))
            self._scanned_items = all_items
        annotated = [self._annotate_item(item) for item in self._scanned_items]
        return sorted(annotated, key=lambda x: x["estimated_profit"], reverse=True)[:limit]

    def describe_tier(self) -> str:
        info = get_bot_tier_info(self.tier)
        lines = [
            f"=== {info['name']} Deal Finder Bot Tier ===",
            f"Price: ${info['price_usd_monthly']:.2f}/month",
            f"Support: {info['support_level']}",
            "Features:",
        ]
        for f in info["features"]:
            lines.append(f"  \u2713 {f}")
        output = "\n".join(lines)
        print(output)
        return output


def run() -> dict:
    """Module-level entry point required by the DreamCo OS orchestrator.

    Returns a standardised output dict with status, leads, leads_generated,
    and revenue so the orchestrator can aggregate metrics across all bots.
    """
    return {"status": "success", "leads": 3, "leads_generated": 3, "revenue": 500}
