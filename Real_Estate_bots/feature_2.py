"""
Feature 2: Real Estate Property Viewing Scheduler Bot
Functionality: Allows users to schedule, manage, and confirm property viewings via chat.
Use Cases: Prospective buyers wanting to view properties, agents managing their calendar.

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
# 30 example property viewing slots
# ---------------------------------------------------------------------------

EXAMPLES = [
    {"id": 1,  "property": "123 Oak St, Austin TX",          "date": "2025-05-01", "time": "10:00", "agent": "Sarah Johnson",   "status": "available"},
    {"id": 2,  "property": "456 Maple Ave, Austin TX",       "date": "2025-05-01", "time": "14:00", "agent": "Mike Davis",      "status": "available"},
    {"id": 3,  "property": "789 Pine Rd, Phoenix AZ",        "date": "2025-05-02", "time": "09:00", "agent": "Lisa Chen",       "status": "booked"},
    {"id": 4,  "property": "321 Elm Dr, Phoenix AZ",         "date": "2025-05-02", "time": "11:00", "agent": "Tom Williams",    "status": "available"},
    {"id": 5,  "property": "654 Cedar Ln, Nashville TN",     "date": "2025-05-02", "time": "15:00", "agent": "Anna Martinez",   "status": "available"},
    {"id": 6,  "property": "987 Birch Blvd, Nashville TN",   "date": "2025-05-03", "time": "10:00", "agent": "James Brown",     "status": "cancelled"},
    {"id": 7,  "property": "147 Walnut St, Denver CO",       "date": "2025-05-03", "time": "13:00", "agent": "Maria Garcia",    "status": "available"},
    {"id": 8,  "property": "258 Spruce Ave, Denver CO",      "date": "2025-05-04", "time": "10:00", "agent": "David Lee",       "status": "available"},
    {"id": 9,  "property": "369 Aspen Ct, Tampa FL",         "date": "2025-05-04", "time": "14:00", "agent": "Jennifer Wilson", "status": "booked"},
    {"id": 10, "property": "741 Palm Dr, Tampa FL",          "date": "2025-05-05", "time": "09:00", "agent": "Robert Taylor",   "status": "available"},
    {"id": 11, "property": "852 Peachtree Rd, Atlanta GA",   "date": "2025-05-05", "time": "11:00", "agent": "Patricia Moore",  "status": "available"},
    {"id": 12, "property": "963 Magnolia St, Atlanta GA",    "date": "2025-05-05", "time": "15:00", "agent": "Charles Anderson","status": "available"},
    {"id": 13, "property": "159 Mesquite Way, Dallas TX",    "date": "2025-05-06", "time": "10:00", "agent": "Linda Jackson",   "status": "available"},
    {"id": 14, "property": "267 Bluebonnet St, Dallas TX",   "date": "2025-05-06", "time": "14:00", "agent": "Mark White",      "status": "booked"},
    {"id": 15, "property": "375 Live Oak Blvd, Houston TX",  "date": "2025-05-07", "time": "09:00", "agent": "Barbara Harris",  "status": "available"},
    {"id": 16, "property": "483 Bayou Dr, Houston TX",       "date": "2025-05-07", "time": "13:00", "agent": "Steven Martin",   "status": "available"},
    {"id": 17, "property": "591 Desert Rose, Las Vegas NV",  "date": "2025-05-08", "time": "10:00", "agent": "Nancy Thompson",  "status": "available"},
    {"id": 18, "property": "628 Cactus Ave, Las Vegas NV",   "date": "2025-05-08", "time": "15:00", "agent": "George Garcia",   "status": "cancelled"},
    {"id": 19, "property": "714 Lakeside Dr, Charlotte NC",  "date": "2025-05-09", "time": "10:00", "agent": "Betty Robinson",  "status": "available"},
    {"id": 20, "property": "836 Uptown Blvd, Charlotte NC",  "date": "2025-05-09", "time": "14:00", "agent": "Edward Clark",    "status": "booked"},
    {"id": 21, "property": "922 Mission St, San Antonio TX", "date": "2025-05-10", "time": "09:00", "agent": "Dorothy Lewis",   "status": "available"},
    {"id": 22, "property": "1014 River Rd, San Antonio TX",  "date": "2025-05-10", "time": "13:00", "agent": "Ronald Lee",      "status": "available"},
    {"id": 23, "property": "1126 Sunset Blvd, Orlando FL",   "date": "2025-05-11", "time": "10:00", "agent": "Jessica Walker",  "status": "available"},
    {"id": 24, "property": "1238 Harbor View, Orlando FL",   "date": "2025-05-11", "time": "14:00", "agent": "Daniel Hall",     "status": "booked"},
    {"id": 25, "property": "1344 Magnolia Pkwy, Raleigh NC", "date": "2025-05-12", "time": "09:00", "agent": "Helen Allen",     "status": "available"},
    {"id": 26, "property": "1456 Glenwood Ave, Raleigh NC",  "date": "2025-05-12", "time": "14:00", "agent": "Kevin Young",     "status": "available"},
    {"id": 27, "property": "1562 Broadway, Salt Lake City UT","date": "2025-05-13","time": "10:00", "agent": "Karen Hernandez", "status": "available"},
    {"id": 28, "property": "1674 Main St, Salt Lake City UT","date": "2025-05-13", "time": "15:00", "agent": "Brian King",      "status": "cancelled"},
    {"id": 29, "property": "1786 Garden Way, Indianapolis IN","date": "2025-05-14","time": "10:00", "agent": "Gary Wright",     "status": "available"},
    {"id": 30, "property": "1892 Canal Blvd, Indianapolis IN","date": "2025-05-14","time": "14:00", "agent": "Sharon Lopez",    "status": "available"},
]

TIERS = {
    "FREE":       {"price_usd": 0,   "max_bookings": 3,    "reminders": False, "ai_scheduling": False},
    "PRO":        {"price_usd": 29,  "max_bookings": 30,   "reminders": True,  "ai_scheduling": False},
    "ENTERPRISE": {"price_usd": 99,  "max_bookings": None, "reminders": True,  "ai_scheduling": True},
}


class PropertyViewingSchedulerBot:
    """Schedules and manages property viewings for buyers and agents.

    Competes with Calendly and Showingtime by adding real-estate-specific
    scheduling logic, agent availability, and AI-powered time slot optimization.
    Monetization: $29/month (PRO) or $99/month (ENTERPRISE) subscription.
    """

    def __init__(self, tier: str = "FREE"):
        if tier not in TIERS:
            raise ValueError(f"Invalid tier '{tier}'. Choose from {list(TIERS)}")
        self.tier = tier
        self._config = TIERS[tier]
        self._flow = GlobalAISourcesFlow(bot_name="PropertyViewingSchedulerBot")
        self._bookings: list[dict] = []

    def get_available_slots(self, date: str | None = None) -> list[dict]:
        """Return available viewing slots, optionally filtered by date."""
        slots = [s for s in EXAMPLES if s["status"] == "available"]
        if date:
            slots = [s for s in slots if s["date"] == date]
        return slots

    def book_viewing(self, slot_id: int, buyer_name: str, buyer_email: str) -> dict:
        """Book a viewing slot for a buyer. Returns booking confirmation."""
        max_b = self._config["max_bookings"]
        if max_b is not None and len(self._bookings) >= max_b:
            raise PermissionError(
                f"Booking limit of {max_b} reached on {self.tier} tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        slot = next((s for s in EXAMPLES if s["id"] == slot_id), None)
        if slot is None:
            raise ValueError(f"Slot ID {slot_id} not found.")
        if slot["status"] != "available":
            raise ValueError(f"Slot {slot_id} is not available (status: {slot['status']}).")
        booking = {
            "booking_id": f"BOOK-{slot_id:04d}",
            "slot_id": slot_id,
            "property": slot["property"],
            "date": slot["date"],
            "time": slot["time"],
            "agent": slot["agent"],
            "buyer_name": buyer_name,
            "buyer_email": buyer_email,
            "status": "confirmed",
            "reminder_scheduled": self._config["reminders"],
        }
        self._bookings.append(booking)
        return booking

    def cancel_booking(self, booking_id: str) -> dict:
        """Cancel a booking and free up the slot."""
        booking = next((b for b in self._bookings if b["booking_id"] == booking_id), None)
        if booking is None:
            raise ValueError(f"Booking {booking_id} not found.")
        booking["status"] = "cancelled"
        return {"message": f"Booking {booking_id} cancelled successfully.", "booking": booking}

    def get_my_bookings(self) -> list[dict]:
        """Return all bookings made in this session."""
        return list(self._bookings)

    def suggest_best_time(self, preferred_date: str) -> dict | None:
        """Suggest the best available slot on a date (AI feature for ENTERPRISE)."""
        slots = self.get_available_slots(date=preferred_date)
        if not slots:
            return None
        if self._config["ai_scheduling"]:
            morning = [s for s in slots if s["time"] < "12:00"]
            if morning:
                best = morning[0]
            else:
                best = slots[0]
            best = dict(best)
            best["ai_suggestion"] = "Optimal morning slot for highest buyer engagement."
            return best
        return slots[0]

    def get_agent_schedule(self, agent_name: str) -> list[dict]:
        """Return all slots for a specific agent."""
        return [s for s in EXAMPLES if agent_name.lower() in s["agent"].lower()]

    def get_calendar_summary(self) -> dict:
        """Return a summary of the viewing calendar."""
        by_status: dict[str, int] = {}
        for s in EXAMPLES:
            by_status[s["status"]] = by_status.get(s["status"], 0) + 1
        return {
            "total_slots": len(EXAMPLES),
            "by_status": by_status,
            "total_bookings": len(self._bookings),
            "tier": self.tier,
        }

    def describe_tier(self) -> str:
        cfg = self._config
        limit = cfg["max_bookings"] if cfg["max_bookings"] else "unlimited"
        lines = [
            f"=== PropertyViewingSchedulerBot — {self.tier} Tier ===",
            f"  Monthly price    : ${cfg['price_usd']}/month",
            f"  Max bookings     : {limit}",
            f"  Reminders        : {'enabled' if cfg['reminders'] else 'disabled'}",
            f"  AI scheduling    : {'enabled' if cfg['ai_scheduling'] else 'disabled (upgrade to ENTERPRISE)'}",
        ]
        return "\n".join(lines)

    def run(self) -> dict:
        """Run the GLOBAL AI SOURCES FLOW pipeline and return a summary."""
        result = self._flow.run_pipeline(
            raw_data={"domain": "property_viewing_scheduling", "slots_count": len(EXAMPLES)},
            learning_method="supervised",
        )
        return {"pipeline_complete": result.get("pipeline_complete"), "calendar": self.get_calendar_summary()}


if __name__ == "__main__":
    bot = PropertyViewingSchedulerBot(tier="PRO")
    slots = bot.get_available_slots("2025-05-01")
    print(f"Available slots on 2025-05-01: {len(slots)}")
    if slots:
        booking = bot.book_viewing(slots[0]["id"], "John Buyer", "john@example.com")
        print(f"Booked: {booking['booking_id']} — {booking['property']}")
    print(bot.describe_tier())


ViewingSchedulerBot = PropertyViewingSchedulerBot


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


class PropertyViewingSchedulerBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


_orig_propertyviewingscheduler_bot_init = PropertyViewingSchedulerBot.__init__


def _propertyviewingscheduler_bot_new_init(self, tier=Tier.FREE):
    tier_val = tier.value if hasattr(tier, "value") else str(tier).lower()
    _orig_propertyviewingscheduler_bot_init(self, tier_val.upper())
    self.tier = Tier(tier_val)


PropertyViewingSchedulerBot.__init__ = _propertyviewingscheduler_bot_new_init
PropertyViewingSchedulerBot.RESULT_LIMITS = {"free": 5, "pro": 25, "enterprise": 100}


def _propertyviewingscheduler_bot_monthly_price(self):
    return _TIER_MONTHLY_PRICE[self.tier.value]


def _propertyviewingscheduler_bot_get_tier_info(self):
    return {
        "tier": self.tier.value,
        "monthly_price_usd": self.monthly_price(),
        "result_limit": self.RESULT_LIMITS[self.tier.value],
    }


def _propertyviewingscheduler_bot_enforce_tier(self, required_value):
    order = ["free", "pro", "enterprise"]
    if order.index(self.tier.value) < order.index(required_value):
        raise PropertyViewingSchedulerBotTierError(
            f"{required_value.upper()} tier required. Current: {self.tier.value}"
        )


def _propertyviewingscheduler_bot_list_items(self, limit=None):
    cap = limit if limit else self.RESULT_LIMITS[self.tier.value]
    return _random_tier.sample(EXAMPLES, min(cap, len(EXAMPLES)))


def _propertyviewingscheduler_bot_analyze(self):
    self._enforce_tier("pro")
    return {"bot": "PropertyViewingSchedulerBot", "tier": self.tier.value, "count": len(EXAMPLES)}


def _propertyviewingscheduler_bot_export_report(self):
    self._enforce_tier("enterprise")
    return {"bot": "PropertyViewingSchedulerBot", "tier": self.tier.value, "total_items": len(EXAMPLES), "items": EXAMPLES}


PropertyViewingSchedulerBot.monthly_price = _propertyviewingscheduler_bot_monthly_price
PropertyViewingSchedulerBot.get_tier_info = _propertyviewingscheduler_bot_get_tier_info
PropertyViewingSchedulerBot._enforce_tier = _propertyviewingscheduler_bot_enforce_tier
PropertyViewingSchedulerBot.list_items = _propertyviewingscheduler_bot_list_items
PropertyViewingSchedulerBot.analyze = _propertyviewingscheduler_bot_analyze
PropertyViewingSchedulerBot.export_report = _propertyviewingscheduler_bot_export_report
