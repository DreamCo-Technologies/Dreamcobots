"""Stack & Profit AI Bot — tier-aware deal stacking, penny hunting, receipt scanning, flip finding, and coupon stacking."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.stack_and_profit_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401

_DEALS_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'first_50_deals.json')


def _load_deals() -> list:
    """Load the preloaded first-50-deals dataset."""
    with open(_DEALS_PATH, 'r') as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class StackAndProfitBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# AI Engines (inline — single-file approach matching repo style)
# ---------------------------------------------------------------------------

class ProfitEngine:
    """Calculates net profit for a deal after coupon, cashback, and fees."""

    @staticmethod
    def calculate(deal: dict) -> dict:
        """Return finalCost and profit for a deal dict."""
        price = float(deal.get("current", deal.get("price", 0)))
        coupon = float(deal.get("coupon", 0))
        cashback = float(deal.get("cashback", 0))
        resale = float(deal.get("resale", 0))
        final_cost = max(0.0, price - coupon - cashback)
        profit = resale - final_cost if resale > 0 else cashback + coupon
        return {
            "final_cost": round(final_cost, 2),
            "profit": round(profit, 2),
        }


class RankingAI:
    """Scores and ranks deals by profit, effort, and payout speed."""

    @staticmethod
    def score(deal: dict) -> int:
        """Return a 0–100 score for a deal."""
        score = 0
        profit = float(deal.get("profit", 0))
        effort = int(deal.get("effort", 3))
        fast_payout = bool(deal.get("fast_payout", False))
        if profit > 100:
            score += 40
        elif profit > 50:
            score += 30
        elif profit > 20:
            score += 20
        elif profit > 5:
            score += 10
        if effort <= 1:
            score += 30
        elif effort == 2:
            score += 20
        else:
            score += 5
        if fast_payout:
            score += 20
        # Category bonus: electronics & appliances highest resale
        category = deal.get("category", "")
        if category in ("electronics", "appliances"):
            score += 10
        return min(score, 100)

    @classmethod
    def rank(cls, deals: list) -> list:
        """Return deals sorted descending by score."""
        scored = [{**d, "rank_score": cls.score(d)} for d in deals]
        return sorted(scored, key=lambda x: x["rank_score"], reverse=True)


class AlertEngine:
    """Determines which deals warrant user alerts."""

    MIN_PROFIT_ALERT = 20.0
    MIN_SCORE_ALERT = 50

    @classmethod
    def should_alert(cls, deal: dict) -> bool:
        """Return True if the deal meets alert thresholds."""
        profit = float(deal.get("profit", 0))
        score = RankingAI.score(deal)
        return profit >= cls.MIN_PROFIT_ALERT or score >= cls.MIN_SCORE_ALERT

    @classmethod
    def filter_alerts(cls, deals: list) -> list:
        """Return only deals that should trigger alerts."""
        return [d for d in deals if cls.should_alert(d)]


# ---------------------------------------------------------------------------
# Sub-bots
# ---------------------------------------------------------------------------

class DealBot:
    """Finds price drops and profitable items across deal sources."""

    SOURCE_LIMITS = {
        Tier.FREE: 1,
        Tier.PRO: 10,
        Tier.ENTERPRISE: None,  # all
    }
    ITEM_LIMITS = {
        Tier.FREE: 5,
        Tier.PRO: 50,
        Tier.ENTERPRISE: None,
    }
    DEAL_TYPES = {"clearance", "price_drop", "coupon_stack", "rebate_stack", "resale_flip"}

    def __init__(self, tier: Tier, deals: list):
        self.tier = tier
        self._all_deals = deals

    def run(self, min_profit: float = 15.0) -> list:
        """Return profitable deals filtered by minimum profit threshold."""
        profitable = [d for d in self._all_deals if float(d.get("profit", 0)) >= min_profit
                      and d.get("type") in self.DEAL_TYPES]
        limit = self.ITEM_LIMITS[self.tier]
        if limit is not None:
            profitable = profitable[:limit]
        return [ProfitEngine.calculate(d) | d for d in profitable]


class PennyBot:
    """Finds $0.01 or extreme low-price deals."""

    PENNY_THRESHOLD = 1.00

    def __init__(self, tier: Tier, deals: list):
        self.tier = tier
        self._all_deals = deals

    def run(self) -> list:
        """Return penny deals (current price <= $1.00)."""
        pennies = [d for d in self._all_deals if float(d.get("current", 99)) <= self.PENNY_THRESHOLD]
        if self.tier == Tier.FREE:
            pennies = pennies[:3]
        return pennies


class ReceiptBot:
    """Scans receipts and stacks cashback opportunities."""

    def __init__(self, tier: Tier, deals: list):
        self.tier = tier
        self._all_deals = deals

    def scan_receipt(self, items: list) -> dict:
        """Match purchased items to cashback sources. Returns matched opportunities."""
        if self.tier == Tier.FREE:
            raise StackAndProfitBotTierError(
                "Receipt scanning requires PRO or ENTERPRISE tier."
            )
        cashback_deals = [d for d in self._all_deals if d.get("type") == "cashback"]
        matched = []
        total_cashback = 0.0
        for item_name in items:
            for deal in cashback_deals:
                if any(word.lower() in deal["name"].lower() for word in item_name.split()):
                    matched.append(deal)
                    total_cashback += float(deal.get("cashback", 0))
                    break
        return {
            "items_submitted": len(items),
            "matches_found": len(matched),
            "matched_deals": matched,
            "total_cashback_usd": round(total_cashback, 2),
            "tier": self.tier.value,
        }

    def get_cashback_sources(self) -> list:
        """Return available cashback sources."""
        sources = [d for d in self._all_deals if d.get("type") == "cashback"]
        if self.tier == Tier.FREE:
            sources = sources[:2]
        return sources


class FlipBot:
    """Finds local resale opportunities and calculates flip profit."""

    FLIP_TYPES = {"local_flip", "resale_flip"}

    def __init__(self, tier: Tier, deals: list):
        self.tier = tier
        self._all_deals = deals

    def run(self, min_profit: float = 20.0) -> list:
        """Return flip opportunities sorted by profit."""
        if self.tier == Tier.FREE:
            raise StackAndProfitBotTierError(
                "FlipBot requires PRO or ENTERPRISE tier."
            )
        flips = [
            d for d in self._all_deals
            if d.get("type") in self.FLIP_TYPES
            and float(d.get("profit", 0)) >= min_profit
        ]
        if self.tier == Tier.PRO:
            flips = flips[:10]
        return RankingAI.rank(flips)

    def estimate_flip_profit(self, current_price: float, resale_price: float,
                              fees_pct: float = 0.13) -> dict:
        """Calculate net profit for a flip after platform fees."""
        gross = resale_price - current_price
        fees = resale_price * fees_pct
        net = gross - fees
        return {
            "current_price": round(current_price, 2),
            "resale_price": round(resale_price, 2),
            "gross_profit": round(gross, 2),
            "platform_fees": round(fees, 2),
            "net_profit": round(net, 2),
            "roi_pct": round((net / current_price) * 100, 1) if current_price > 0 else 0,
        }


class CouponBot:
    """Stacks coupons and discounts for maximum savings."""

    COUPON_SOURCES = {
        Tier.FREE: ["Ibotta", "Fetch Rewards", "Honey"],
        Tier.PRO: ["Ibotta", "Fetch Rewards", "Honey", "Rakuten", "Target Cartwheel",
                   "Kroger Digital Coupons", "Walgreens App Deals", "CVS App Deals",
                   "Amazon Coupons", "Target Coupons"],
        Tier.ENTERPRISE: None,  # all
    }

    def __init__(self, tier: Tier, deals: list):
        self.tier = tier
        self._all_deals = deals

    def run(self) -> list:
        """Return all coupon/rebate deals with stacked savings calculated."""
        coupon_types = {"coupon_stack", "rebate_stack"}
        coupon_deals = [d for d in self._all_deals if d.get("type") in coupon_types]
        sources = self.COUPON_SOURCES[self.tier]
        if sources is not None:
            coupon_deals = [d for d in coupon_deals if d.get("source") in sources]
        return [
            {
                **d,
                "stacked_savings": round(float(d.get("coupon", 0)) + float(d.get("cashback", 0)), 2),
                "final_price": round(float(d.get("current", 0)) - float(d.get("coupon", 0)) - float(d.get("cashback", 0)), 2),
            }
            for d in coupon_deals
        ]

    def get_available_sources(self) -> list:
        """Return available coupon sources for this tier."""
        sources = self.COUPON_SOURCES[self.tier]
        if sources is None:
            return [d["source"] for d in self._all_deals if d.get("type") in ("coupon_stack", "rebate_stack")]
        return sources


# ---------------------------------------------------------------------------
# Main Bot
# ---------------------------------------------------------------------------

class StackAndProfitBot:
    """
    Tier-aware Stack & Profit AI bot.

    Orchestrates dealBot, pennyBot, receiptBot, flipBot, couponBot plus
    AI profit ranking and alert engine. Covers the full DreamCo $1,000
    launch plan deal-sourcing pipeline.
    """

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._deals = _load_deals()
        # Sub-bots
        self.deal_bot = DealBot(tier, self._deals)
        self.penny_bot = PennyBot(tier, self._deals)
        self.receipt_bot = ReceiptBot(tier, self._deals)
        self.flip_bot = FlipBot(tier, self._deals)
        self.coupon_bot = CouponBot(tier, self._deals)
        # AI engines
        self.profit_engine = ProfitEngine()
        self.ranking_ai = RankingAI()
        self.alert_engine = AlertEngine()

    # ------------------------------------------------------------------
    # Orchestration
    # ------------------------------------------------------------------

    def run_all_bots(self, min_profit: float = 15.0) -> dict:
        """
        Run all bots and return a combined result dict.

        FREE tier: deal_bot + penny_bot + coupon_bot only.
        PRO/ENTERPRISE: all five bots.
        """
        result = {
            "tier": self.tier.value,
            "deal_bot": self.deal_bot.run(min_profit=min_profit),
            "penny_bot": self.penny_bot.run(),
            "coupon_bot": self.coupon_bot.run(),
        }
        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["flip_bot"] = self.flip_bot.run(min_profit=min_profit)
            result["receipt_bot_sources"] = self.receipt_bot.get_cashback_sources()
        return result

    # ------------------------------------------------------------------
    # AI helpers
    # ------------------------------------------------------------------

    def rank_deals(self, deals: list) -> list:
        """Return deals ranked by AI profit score."""
        return self.ranking_ai.rank(deals)

    def load_preloaded_deals(self) -> list:
        """Return the preloaded deals dataset."""
        return list(self._deals)

    def get_alerts(self, deals: list, min_profit: float = None) -> list:
        """Return only deals that meet alert thresholds."""
        if min_profit is not None:
            return [d for d in deals if float(d.get("profit", 0)) >= min_profit and AlertEngine.should_alert(d)]
        return self.alert_engine.filter_alerts(deals)

    def calculate_profit(self, deal: dict) -> dict:
        """Return finalCost and profit for a deal."""
        return self.profit_engine.calculate(deal)

    # ------------------------------------------------------------------
    # Deal feed
    # ------------------------------------------------------------------

    def get_top_deals(self, limit: int = 10) -> list:
        """Return top deals across all types ranked by AI score."""
        all_profitable = [d for d in self._deals if float(d.get("profit", 0)) > 0]
        ranked = self.ranking_ai.rank(all_profitable)
        item_limit = {Tier.FREE: 5, Tier.PRO: 25, Tier.ENTERPRISE: None}[self.tier]
        if item_limit is not None:
            ranked = ranked[:item_limit]
        return ranked[:limit]

    def get_deals_by_category(self, category: str) -> list:
        """Return deals filtered by category."""
        return [d for d in self._deals if d.get("category", "").lower() == category.lower()]

    def get_deals_by_type(self, deal_type: str) -> list:
        """Return deals filtered by type."""
        return [d for d in self._deals if d.get("type", "").lower() == deal_type.lower()]

    # ------------------------------------------------------------------
    # Monetization helpers (PRO / ENTERPRISE)
    # ------------------------------------------------------------------

    def get_affiliate_deals(self) -> list:
        """Return deals with affiliate link potential (PRO/ENTERPRISE only)."""
        if self.tier == Tier.FREE:
            raise StackAndProfitBotTierError(
                "Affiliate deal feed requires PRO or ENTERPRISE tier."
            )
        return [d for d in self._deals if d.get("source") in (
            "Amazon Lightning Deals", "Rakuten", "Honey", "Ibotta",
            "Target Cartwheel", "Kroger Digital Coupons",
        )]

    def get_subscription_summary(self) -> dict:
        """Return subscription tier summary and upgrade path."""
        info = get_bot_tier_info(self.tier)
        upgrade = get_upgrade_path(self.tier)
        summary = {
            "current_tier": info,
            "upgrade_available": upgrade is not None,
        }
        if upgrade is not None:
            summary["next_tier"] = {
                "name": upgrade.name,
                "price_usd_monthly": upgrade.price_usd_monthly,
            }
        return summary

    # ------------------------------------------------------------------
    # Tier description
    # ------------------------------------------------------------------

    def describe_tier(self) -> str:
        info = get_bot_tier_info(self.tier)
        lines = [
            f"=== {info['name']} Stack & Profit AI Bot Tier ===",
            f"Price: ${info['price_usd_monthly']:.2f}/month",
            f"Support: {info['support_level']}",
            "Features:",
        ]
        for f in info["features"]:
            lines.append(f"  \u2713 {f}")
        output = "\n".join(lines)
        print(output)
        return output
