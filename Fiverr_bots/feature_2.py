"""
Feature 2: Fiverr Order Manager Bot
Functionality: Tracks and manages incoming orders from clients. Provides
  status updates, deadline alerts, and automated client communications.
Use Cases: Sellers needing to stay organized and deliver on time.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401 — GLOBAL AI SOURCES FLOW

# ---------------------------------------------------------------------------
# 30 example order records
# ---------------------------------------------------------------------------

EXAMPLES = [
    {"id": "ORD-001", "gig": "Logo Design",           "buyer": "techstartup_co",  "price": 50,  "status": "in_progress", "due_date": "2025-05-03", "revision_count": 1, "rating": None},
    {"id": "ORD-002", "gig": "SEO Blog Post",          "buyer": "bloggerpro22",    "price": 30,  "status": "delivered",   "due_date": "2025-05-01", "revision_count": 0, "rating": 5},
    {"id": "ORD-003", "gig": "WordPress Site",         "buyer": "small_biz_jane",  "price": 150, "status": "in_progress", "due_date": "2025-05-08", "revision_count": 0, "rating": None},
    {"id": "ORD-004", "gig": "Social Media Pack",      "buyer": "coffee_brand",    "price": 60,  "status": "completed",   "due_date": "2025-04-30", "revision_count": 2, "rating": 4},
    {"id": "ORD-005", "gig": "Explainer Video",        "buyer": "saas_founder",    "price": 100, "status": "in_progress", "due_date": "2025-05-05", "revision_count": 1, "rating": None},
    {"id": "ORD-006", "gig": "Data Entry Task",        "buyer": "researcher_bob",  "price": 15,  "status": "completed",   "due_date": "2025-04-28", "revision_count": 0, "rating": 5},
    {"id": "ORD-007", "gig": "Resume Writing",         "buyer": "job_seeker_2025", "price": 45,  "status": "delivered",   "due_date": "2025-05-02", "revision_count": 1, "rating": None},
    {"id": "ORD-008", "gig": "Spanish Translation",    "buyer": "intl_docs_inc",   "price": 25,  "status": "completed",   "due_date": "2025-04-29", "revision_count": 0, "rating": 5},
    {"id": "ORD-009", "gig": "Python Automation",      "buyer": "bizops_lead",     "price": 75,  "status": "in_progress", "due_date": "2025-05-06", "revision_count": 0, "rating": None},
    {"id": "ORD-010", "gig": "Business Card Design",   "buyer": "realtor_mike",    "price": 20,  "status": "completed",   "due_date": "2025-04-27", "revision_count": 1, "rating": 4},
    {"id": "ORD-011", "gig": "Product Descriptions",   "buyer": "ecom_store_amy",  "price": 40,  "status": "delivered",   "due_date": "2025-05-01", "revision_count": 0, "rating": None},
    {"id": "ORD-012", "gig": "Google Ads Setup",       "buyer": "ad_agency_x",     "price": 90,  "status": "completed",   "due_date": "2025-04-26", "revision_count": 0, "rating": 5},
    {"id": "ORD-013", "gig": "Shopify Store",          "buyer": "fashion_brand",   "price": 180, "status": "in_progress", "due_date": "2025-05-10", "revision_count": 0, "rating": None},
    {"id": "ORD-014", "gig": "Voice Over",             "buyer": "podcast_host",    "price": 35,  "status": "delivered",   "due_date": "2025-05-01", "revision_count": 0, "rating": 5},
    {"id": "ORD-015", "gig": "Manuscript Editing",     "buyer": "author_lisa",     "price": 50,  "status": "in_progress", "due_date": "2025-05-07", "revision_count": 0, "rating": None},
    {"id": "ORD-016", "gig": "Instagram Content",      "buyer": "influencer_99",   "price": 70,  "status": "completed",   "due_date": "2025-04-25", "revision_count": 1, "rating": 4},
    {"id": "ORD-017", "gig": "React Native App",       "buyer": "app_startup_x",   "price": 250, "status": "in_progress", "due_date": "2025-05-15", "revision_count": 0, "rating": None},
    {"id": "ORD-018", "gig": "YouTube Intro",          "buyer": "gamer_youtuber",  "price": 55,  "status": "delivered",   "due_date": "2025-05-02", "revision_count": 1, "rating": None},
    {"id": "ORD-019", "gig": "Mailchimp Setup",        "buyer": "retailer_mark",   "price": 65,  "status": "completed",   "due_date": "2025-04-30", "revision_count": 0, "rating": 5},
    {"id": "ORD-020", "gig": "Keyword Research",       "buyer": "seo_agency_v",    "price": 40,  "status": "in_progress", "due_date": "2025-05-04", "revision_count": 0, "rating": None},
    {"id": "ORD-021", "gig": "PowerPoint Deck",        "buyer": "finance_co",      "price": 55,  "status": "completed",   "due_date": "2025-04-24", "revision_count": 0, "rating": 5},
    {"id": "ORD-022", "gig": "About Us Page",          "buyer": "new_brand_co",    "price": 25,  "status": "delivered",   "due_date": "2025-05-01", "revision_count": 0, "rating": None},
    {"id": "ORD-023", "gig": "FastAPI Backend",        "buyer": "startup_cto",     "price": 140, "status": "in_progress", "due_date": "2025-05-12", "revision_count": 0, "rating": None},
    {"id": "ORD-024", "gig": "Social Media Kit",       "buyer": "brand_kit_buyer", "price": 40,  "status": "completed",   "due_date": "2025-04-23", "revision_count": 1, "rating": 4},
    {"id": "ORD-025", "gig": "Chatbot Dev",            "buyer": "ecom_cmo",        "price": 120, "status": "in_progress", "due_date": "2025-05-09", "revision_count": 0, "rating": None},
    {"id": "ORD-026", "gig": "Guest Blog Posts",       "buyer": "seo_blogger",     "price": 80,  "status": "delivered",   "due_date": "2025-05-03", "revision_count": 0, "rating": None},
    {"id": "ORD-027", "gig": "Ebook Creation",         "buyer": "coach_emma",      "price": 70,  "status": "completed",   "due_date": "2025-04-22", "revision_count": 0, "rating": 5},
    {"id": "ORD-028", "gig": "Bug Fix Service",        "buyer": "dev_team_xyz",    "price": 35,  "status": "completed",   "due_date": "2025-04-21", "revision_count": 0, "rating": 5},
    {"id": "ORD-029", "gig": "Pinterest Management",   "buyer": "home_decor_shop", "price": 45,  "status": "in_progress", "due_date": "2025-05-11", "revision_count": 0, "rating": None},
    {"id": "ORD-030", "gig": "LinkedIn Profile",       "buyer": "exec_coach_tom",  "price": 60,  "status": "delivered",   "due_date": "2025-05-02", "revision_count": 1, "rating": None},
]

TIERS = {
    "FREE":       {"price_usd": 0,   "max_tracked": 10,   "auto_messages": False, "deadline_alerts": False},
    "PRO":        {"price_usd": 29,  "max_tracked": 100,  "auto_messages": True,  "deadline_alerts": True},
    "ENTERPRISE": {"price_usd": 99,  "max_tracked": None, "auto_messages": True,  "deadline_alerts": True},
}


class FiverrOrderManagerBot:
    """Tracks and manages Fiverr orders — deadlines, statuses, revenue, reviews.

    Competes with Notion/Trello for freelancer order management by providing
    Fiverr-specific metrics and automated buyer communication.
    Monetization: $29/month PRO or $99/month ENTERPRISE subscription.
    """

    def __init__(self, tier: str = "FREE"):
        if tier not in TIERS:
            raise ValueError(f"Invalid tier '{tier}'. Choose from {list(TIERS)}")
        self.tier = tier
        self._config = TIERS[tier]
        self._flow = GlobalAISourcesFlow(bot_name="FiverrOrderManagerBot")

    def _available_orders(self) -> list[dict]:
        limit = self._config["max_tracked"]
        return EXAMPLES[:limit] if limit else EXAMPLES

    def get_orders_by_status(self, status: str) -> list[dict]:
        """Return orders filtered by status."""
        valid = {"in_progress", "delivered", "completed", "cancelled"}
        if status not in valid:
            raise ValueError(f"Invalid status '{status}'. Choose from {valid}")
        return [o for o in self._available_orders() if o["status"] == status]

    def get_active_orders(self) -> list[dict]:
        """Return all orders currently in progress."""
        return self.get_orders_by_status("in_progress")

    def get_order(self, order_id: str) -> dict:
        """Retrieve a specific order by ID."""
        order = next((o for o in EXAMPLES if o["id"] == order_id), None)
        if order is None:
            raise ValueError(f"Order '{order_id}' not found.")
        return order

    def get_revenue_summary(self) -> dict:
        """Return total revenue, average order value, and top earner."""
        orders = self._available_orders()
        completed = [o for o in orders if o["status"] == "completed"]
        total_revenue = sum(o["price"] for o in completed)
        avg_value = total_revenue / len(completed) if completed else 0
        top_order = max(completed, key=lambda o: o["price"]) if completed else None
        return {
            "total_orders": len(orders),
            "completed_orders": len(completed),
            "total_revenue_usd": total_revenue,
            "avg_order_value_usd": round(avg_value, 2),
            "top_order": top_order,
            "tier": self.tier,
        }

    def send_deadline_alert(self, order_id: str) -> dict:
        """Send a deadline reminder for an order (PRO/ENTERPRISE only)."""
        if not self._config["deadline_alerts"]:
            raise PermissionError(
                "Deadline alerts require PRO or ENTERPRISE tier. Upgrade at dreamcobots.com/pricing"
            )
        order = self.get_order(order_id)
        return {
            "alert_sent": True,
            "order_id": order_id,
            "gig": order["gig"],
            "buyer": order["buyer"],
            "due_date": order["due_date"],
            "message": f"Reminder: Order {order_id} ({order['gig']}) is due on {order['due_date']}.",
        }

    def send_auto_message(self, order_id: str, message_type: str = "update") -> dict:
        """Send an automated message to a buyer (PRO/ENTERPRISE only)."""
        if not self._config["auto_messages"]:
            raise PermissionError(
                "Auto messaging requires PRO or ENTERPRISE tier. Upgrade at dreamcobots.com/pricing"
            )
        order = self.get_order(order_id)
        templates = {
            "update": f"Hi {order['buyer']}, your order {order_id} is in progress and on track!",
            "delivery": f"Hi {order['buyer']}, your order {order_id} has been delivered. Please review!",
            "review_request": f"Hi {order['buyer']}, I hope you're happy with {order['gig']}! A review would mean a lot.",
        }
        if message_type not in templates:
            raise ValueError(f"Invalid message type. Choose from {list(templates)}")
        return {
            "sent": True,
            "order_id": order_id,
            "buyer": order["buyer"],
            "message": templates[message_type],
        }

    def get_unreviewed_orders(self) -> list[dict]:
        """Return completed orders that have not been reviewed yet."""
        return [o for o in self._available_orders() if o["status"] == "completed" and o["rating"] is None]

    def get_average_rating(self) -> float:
        """Return the average rating across all rated orders."""
        rated = [o for o in self._available_orders() if o["rating"] is not None]
        if not rated:
            return 0.0
        return round(sum(o["rating"] for o in rated) / len(rated), 2)

    def describe_tier(self) -> str:
        cfg = self._config
        limit = cfg["max_tracked"] if cfg["max_tracked"] else "unlimited"
        lines = [
            f"=== FiverrOrderManagerBot — {self.tier} Tier ===",
            f"  Monthly price  : ${cfg['price_usd']}/month",
            f"  Max orders     : {limit}",
            f"  Auto messaging : {'enabled' if cfg['auto_messages'] else 'disabled'}",
            f"  Deadline alerts: {'enabled' if cfg['deadline_alerts'] else 'disabled'}",
        ]
        return "\n".join(lines)

    def run(self) -> dict:
        """Run the GLOBAL AI SOURCES FLOW pipeline."""
        result = self._flow.run_pipeline(
            raw_data={"domain": "fiverr_order_management", "orders_count": len(EXAMPLES)},
            learning_method="supervised",
        )
        return {"pipeline_complete": result.get("pipeline_complete"), "revenue": self.get_revenue_summary()}


if __name__ == "__main__":
    bot = FiverrOrderManagerBot(tier="PRO")
    active = bot.get_active_orders()
    print(f"Active orders: {len(active)}")
    revenue = bot.get_revenue_summary()
    print(f"Total revenue: ${revenue['total_revenue_usd']} from {revenue['completed_orders']} orders")
    print(f"Average rating: {bot.get_average_rating()}")
    print(bot.describe_tier())


OrderManagementBot = FiverrOrderManagerBot


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


class FiverrOrderManagerBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


_orig_fiverrordermanager_bot_init = FiverrOrderManagerBot.__init__


def _fiverrordermanager_bot_new_init(self, tier=Tier.FREE):
    tier_val = tier.value if hasattr(tier, "value") else str(tier).lower()
    _orig_fiverrordermanager_bot_init(self, tier_val.upper())
    self.tier = tier if isinstance(tier, Tier) else Tier(tier_val)


FiverrOrderManagerBot.__init__ = _fiverrordermanager_bot_new_init
FiverrOrderManagerBot.RESULT_LIMITS = {"free": 5, "pro": 25, "enterprise": 100}


def _fiverrordermanager_bot_monthly_price(self):
    return _TIER_MONTHLY_PRICE[self.tier.value]


def _fiverrordermanager_bot_get_tier_info(self):
    return {
        "tier": self.tier.value,
        "monthly_price_usd": self.monthly_price(),
        "result_limit": self.RESULT_LIMITS[self.tier.value],
    }


def _fiverrordermanager_bot_enforce_tier(self, required_value):
    order = ["free", "pro", "enterprise"]
    if order.index(self.tier.value) < order.index(required_value):
        raise FiverrOrderManagerBotTierError(
            f"{required_value.upper()} tier required. Current: {self.tier.value}"
        )


def _fiverrordermanager_bot_list_items(self, limit=None):
    cap = limit if limit else self.RESULT_LIMITS[self.tier.value]
    return _random_tier.sample(EXAMPLES, min(cap, len(EXAMPLES)))


def _fiverrordermanager_bot_analyze(self):
    self._enforce_tier("pro")
    return {"bot": "FiverrOrderManagerBot", "tier": self.tier.value, "count": len(EXAMPLES)}


def _fiverrordermanager_bot_export_report(self):
    self._enforce_tier("enterprise")
    return {"bot": "FiverrOrderManagerBot", "tier": self.tier.value, "total_items": len(EXAMPLES), "items": EXAMPLES}


FiverrOrderManagerBot.monthly_price = _fiverrordermanager_bot_monthly_price
FiverrOrderManagerBot.get_tier_info = _fiverrordermanager_bot_get_tier_info
FiverrOrderManagerBot._enforce_tier = _fiverrordermanager_bot_enforce_tier
FiverrOrderManagerBot.list_items = _fiverrordermanager_bot_list_items
FiverrOrderManagerBot.analyze = _fiverrordermanager_bot_analyze
FiverrOrderManagerBot.export_report = _fiverrordermanager_bot_export_report
