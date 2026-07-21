"""
Feature 1: Business Meeting Scheduler Bot
Functionality: Integrates with calendars to check availability and schedule
  meetings automatically. Handles time zone conversion and sends confirmations.
Use Cases: Teams needing to coordinate schedules across time zones.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401 — GLOBAL AI SOURCES FLOW

# ---------------------------------------------------------------------------
# 30 example meeting slot records
# ---------------------------------------------------------------------------

EXAMPLES = [
    {"id": 1,  "title": "Q1 Strategy Review",          "organizer": "Alice Johnson",   "attendees": ["Bob","Carol","Dave"],    "date": "2025-05-05", "time": "09:00", "duration_min": 60,  "timezone": "EST", "type": "internal",    "status": "confirmed", "platform": "Zoom"},
    {"id": 2,  "title": "Client Kickoff — Acme Corp",  "organizer": "Bob Smith",       "attendees": ["Client1","Client2"],    "date": "2025-05-05", "time": "11:00", "duration_min": 90,  "timezone": "PST", "type": "client",      "status": "confirmed", "platform": "Google Meet"},
    {"id": 3,  "title": "Product Roadmap Planning",    "organizer": "Carol Lee",       "attendees": ["Dev1","PM1","Design1"], "date": "2025-05-06", "time": "10:00", "duration_min": 120, "timezone": "EST", "type": "planning",    "status": "pending",   "platform": "Teams"},
    {"id": 4,  "title": "Weekly Team Standup",         "organizer": "Dave Wilson",     "attendees": ["Team"],                 "date": "2025-05-06", "time": "09:00", "duration_min": 30,  "timezone": "CST", "type": "recurring",   "status": "confirmed", "platform": "Zoom"},
    {"id": 5,  "title": "Investor Pitch — Series A",   "organizer": "Emma Davis",      "attendees": ["Investor1","CFO"],      "date": "2025-05-07", "time": "14:00", "duration_min": 45,  "timezone": "EST", "type": "investor",    "status": "confirmed", "platform": "In-Person"},
    {"id": 6,  "title": "HR One-on-One — John",        "organizer": "Frank Garcia",    "attendees": ["John"],                 "date": "2025-05-07", "time": "15:00", "duration_min": 30,  "timezone": "PST", "type": "hr",          "status": "pending",   "platform": "Phone"},
    {"id": 7,  "title": "Sales Demo — Prospect X",     "organizer": "Grace Kim",       "attendees": ["Prospect1"],            "date": "2025-05-08", "time": "10:00", "duration_min": 60,  "timezone": "CST", "type": "sales",       "status": "confirmed", "platform": "Zoom"},
    {"id": 8,  "title": "Marketing Sprint Planning",   "organizer": "Henry Park",      "attendees": ["Mkt1","Mkt2","Design"], "date": "2025-05-08", "time": "13:00", "duration_min": 90,  "timezone": "EST", "type": "planning",    "status": "confirmed", "platform": "Google Meet"},
    {"id": 9,  "title": "Board Meeting — May",         "organizer": "Isabella Chen",   "attendees": ["Board1","Board2","CEO"],"date": "2025-05-09", "time": "09:00", "duration_min": 120, "timezone": "EST", "type": "board",       "status": "confirmed", "platform": "In-Person"},
    {"id": 10, "title": "Customer Success Review",     "organizer": "Jack Brown",      "attendees": ["Customer1","CS1"],      "date": "2025-05-09", "time": "14:00", "duration_min": 60,  "timezone": "PST", "type": "client",      "status": "pending",   "platform": "Zoom"},
    {"id": 11, "title": "New Hire Onboarding",         "organizer": "Karen White",     "attendees": ["NewHire1","HR1"],       "date": "2025-05-12", "time": "10:00", "duration_min": 60,  "timezone": "EST", "type": "hr",          "status": "confirmed", "platform": "Teams"},
    {"id": 12, "title": "Budget Review Q2",            "organizer": "Leo Martinez",    "attendees": ["CFO","CEO","Finance1"], "date": "2025-05-12", "time": "14:00", "duration_min": 90,  "timezone": "EST", "type": "finance",     "status": "confirmed", "platform": "In-Person"},
    {"id": 13, "title": "Partnership Discussion — BetaCo","organizer": "Mary Lopez","attendees": ["Partner1","BizDev1"],   "date": "2025-05-13", "time": "11:00", "duration_min": 60,  "timezone": "PST", "type": "partnership", "status": "pending",   "platform": "Zoom"},
    {"id": 14, "title": "UX Design Review",            "organizer": "Nick Taylor",     "attendees": ["Design1","PM1","Dev1"], "date": "2025-05-13", "time": "15:00", "duration_min": 60,  "timezone": "CST", "type": "internal",    "status": "confirmed", "platform": "Figma/Zoom"},
    {"id": 15, "title": "Engineering Architecture",    "organizer": "Olivia Harris",   "attendees": ["CTO","Dev1","Dev2"],   "date": "2025-05-14", "time": "10:00", "duration_min": 120, "timezone": "PST", "type": "technical",   "status": "confirmed", "platform": "Google Meet"},
    {"id": 16, "title": "Quarterly Earnings Call",     "organizer": "Paul Nelson",     "attendees": ["Analysts","IR1","CFO"],"date": "2025-05-14", "time": "16:00", "duration_min": 60,  "timezone": "EST", "type": "investor",    "status": "confirmed", "platform": "Webex"},
    {"id": 17, "title": "Vendor Contract Negotiation", "organizer": "Quinn Adams",     "attendees": ["Vendor1","Legal1"],    "date": "2025-05-15", "time": "10:00", "duration_min": 90,  "timezone": "EST", "type": "vendor",      "status": "pending",   "platform": "In-Person"},
    {"id": 18, "title": "Product Launch Prep",         "organizer": "Rachel Scott",    "attendees": ["PM1","Mkt1","Dev1"],   "date": "2025-05-15", "time": "14:00", "duration_min": 60,  "timezone": "PST", "type": "planning",    "status": "confirmed", "platform": "Zoom"},
    {"id": 19, "title": "Customer Feedback Session",   "organizer": "Sam Young",       "attendees": ["Customer2","CS2"],      "date": "2025-05-16", "time": "10:00", "duration_min": 45,  "timezone": "CST", "type": "client",      "status": "confirmed", "platform": "Phone"},
    {"id": 20, "title": "Annual Performance Reviews",  "organizer": "Tina King",       "attendees": ["Employee1","HR1"],      "date": "2025-05-16", "time": "13:00", "duration_min": 60,  "timezone": "EST", "type": "hr",          "status": "pending",   "platform": "In-Person"},
    {"id": 21, "title": "Security Audit Review",       "organizer": "Uma Clark",       "attendees": ["CTO","Security1"],     "date": "2025-05-19", "time": "10:00", "duration_min": 60,  "timezone": "PST", "type": "technical",   "status": "confirmed", "platform": "Teams"},
    {"id": 22, "title": "Content Strategy Session",    "organizer": "Victor Lewis",    "attendees": ["Mkt1","Content1"],     "date": "2025-05-19", "time": "14:00", "duration_min": 60,  "timezone": "EST", "type": "planning",    "status": "pending",   "platform": "Google Meet"},
    {"id": 23, "title": "Sales Forecast Review",       "organizer": "Wendy Walker",    "attendees": ["Sales1","CFO","CEO"],  "date": "2025-05-20", "time": "09:00", "duration_min": 90,  "timezone": "CST", "type": "sales",       "status": "confirmed", "platform": "Zoom"},
    {"id": 24, "title": "Compliance Training",         "organizer": "Xander Hall",     "attendees": ["AllStaff"],            "date": "2025-05-20", "time": "14:00", "duration_min": 60,  "timezone": "EST", "type": "training",    "status": "confirmed", "platform": "Teams"},
    {"id": 25, "title": "API Integration Planning",    "organizer": "Yara Allen",      "attendees": ["Dev1","Partner2"],     "date": "2025-05-21", "time": "11:00", "duration_min": 60,  "timezone": "PST", "type": "technical",   "status": "pending",   "platform": "Google Meet"},
    {"id": 26, "title": "Expansion Market Research",   "organizer": "Zach Hill",       "attendees": ["BizDev1","Research1"], "date": "2025-05-21", "time": "14:00", "duration_min": 90,  "timezone": "EST", "type": "strategy",    "status": "confirmed", "platform": "Zoom"},
    {"id": 27, "title": "Remote Team Check-in",        "organizer": "Amy Green",       "attendees": ["Remote1","Remote2"],   "date": "2025-05-22", "time": "09:00", "duration_min": 30,  "timezone": "UTC", "type": "recurring",   "status": "confirmed", "platform": "Zoom"},
    {"id": 28, "title": "Launch Day War Room",         "organizer": "Brian Baker",     "attendees": ["CEO","CTO","Mkt1"],    "date": "2025-05-22", "time": "08:00", "duration_min": 180, "timezone": "PST", "type": "launch",      "status": "confirmed", "platform": "In-Person"},
    {"id": 29, "title": "Investor Update Call",        "organizer": "Cindy Carter",    "attendees": ["Investor1","Investor2"],"date": "2025-05-23","time": "10:00", "duration_min": 60,  "timezone": "EST", "type": "investor",    "status": "pending",   "platform": "Zoom"},
    {"id": 30, "title": "Retrospective — May Sprint",  "organizer": "Derek Mitchell",  "attendees": ["DevTeam"],             "date": "2025-05-23", "time": "15:00", "duration_min": 60,  "timezone": "CST", "type": "retrospective","status": "confirmed", "platform": "Teams"},
]

TIERS = {
    "FREE":       {"price_usd": 0,   "max_meetings": 5,    "calendar_sync": False, "reminders": False, "timezone_convert": False},
    "PRO":        {"price_usd": 29,  "max_meetings": 50,   "calendar_sync": True,  "reminders": True,  "timezone_convert": True},
    "ENTERPRISE": {"price_usd": 99,  "max_meetings": None, "calendar_sync": True,  "reminders": True,  "timezone_convert": True},
}


class MeetingSchedulerBot:
    """Automates meeting scheduling, availability checks, and confirmations.

    Competes with Calendly and Cal.com by providing team-aware scheduling,
    time zone conversion, and CRM-linked meeting records.
    Monetization: $29/month PRO or $99/month ENTERPRISE subscription.
    """

    def __init__(self, tier: str = "FREE"):
        if tier not in TIERS:
            raise ValueError(f"Invalid tier '{tier}'. Choose from {list(TIERS)}")
        self.tier = tier
        self._config = TIERS[tier]
        self._flow = GlobalAISourcesFlow(bot_name="MeetingSchedulerBot")
        self._scheduled: list[dict] = []

    def schedule_meeting(self, meeting_id: int, requested_by: str) -> dict:
        """Schedule a meeting from the template calendar."""
        max_m = self._config["max_meetings"]
        if max_m is not None and len(self._scheduled) >= max_m:
            raise PermissionError(
                f"Meeting limit of {max_m} reached on {self.tier} tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        meeting = next((m for m in EXAMPLES if m["id"] == meeting_id), None)
        if meeting is None:
            raise ValueError(f"Meeting ID {meeting_id} not found.")
        result = dict(meeting)
        result["requested_by"] = requested_by
        result["status"] = "scheduled"
        if self._config["calendar_sync"]:
            result["calendar_event_id"] = f"CAL-{meeting_id:04d}"
        if self._config["reminders"]:
            result["reminder_set"] = True
        self._scheduled.append(result)
        return result

    def get_meetings_by_type(self, meeting_type: str) -> list[dict]:
        """Return meetings of a specific type."""
        return [m for m in EXAMPLES if m["type"] == meeting_type]

    def get_meetings_by_date(self, date: str) -> list[dict]:
        """Return all meetings on a specific date."""
        return [m for m in EXAMPLES if m["date"] == date]

    def get_pending_confirmations(self) -> list[dict]:
        """Return meetings that are still pending confirmation."""
        return [m for m in EXAMPLES if m["status"] == "pending"]

    def get_upcoming_meetings(self, days: int = 7) -> list[dict]:
        """Return meetings scheduled within the next N days."""
        return EXAMPLES[:min(days * 2, len(EXAMPLES))]

    def convert_timezone(self, meeting_id: int, target_tz: str) -> dict:
        """Convert meeting time to a different timezone (PRO/ENTERPRISE)."""
        if not self._config["timezone_convert"]:
            raise PermissionError(
                "Timezone conversion requires PRO or ENTERPRISE tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        meeting = next((m for m in EXAMPLES if m["id"] == meeting_id), None)
        if meeting is None:
            raise ValueError(f"Meeting ID {meeting_id} not found.")
        tz_offsets = {"EST": -5, "PST": -8, "CST": -6, "UTC": 0, "GMT": 0, "IST": 5}
        offset = tz_offsets.get(target_tz, 0)
        return {
            "meeting_id": meeting_id,
            "original_time": f"{meeting['time']} {meeting['timezone']}",
            "converted_time": f"{meeting['time']} → {target_tz} (offset {offset:+d}h)",
            "target_timezone": target_tz,
        }

    def send_reminder(self, meeting_id: int) -> dict:
        """Send a meeting reminder (PRO/ENTERPRISE)."""
        if not self._config["reminders"]:
            raise PermissionError(
                "Meeting reminders require PRO or ENTERPRISE tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        meeting = next((m for m in EXAMPLES if m["id"] == meeting_id), None)
        if meeting is None:
            raise ValueError(f"Meeting ID {meeting_id} not found.")
        return {
            "sent": True,
            "meeting_id": meeting_id,
            "title": meeting["title"],
            "message": f"Reminder: '{meeting['title']}' is scheduled for {meeting['date']} at {meeting['time']} {meeting['timezone']} on {meeting['platform']}.",
        }

    def get_calendar_summary(self) -> dict:
        """Return a summary of all scheduled meetings."""
        by_type: dict[str, int] = {}
        by_platform: dict[str, int] = {}
        for m in EXAMPLES:
            by_type[m["type"]] = by_type.get(m["type"], 0) + 1
            by_platform[m["platform"]] = by_platform.get(m["platform"], 0) + 1
        return {
            "total_meetings": len(EXAMPLES),
            "by_type": by_type,
            "by_platform": by_platform,
            "pending": len(self.get_pending_confirmations()),
            "scheduled_this_session": len(self._scheduled),
            "tier": self.tier,
        }

    def describe_tier(self) -> str:
        cfg = self._config
        limit = cfg["max_meetings"] if cfg["max_meetings"] else "unlimited"
        lines = [
            f"=== MeetingSchedulerBot — {self.tier} Tier ===",
            f"  Monthly price    : ${cfg['price_usd']}/month",
            f"  Max meetings     : {limit}",
            f"  Calendar sync    : {'enabled' if cfg['calendar_sync'] else 'disabled'}",
            f"  Reminders        : {'enabled' if cfg['reminders'] else 'disabled'}",
            f"  Timezone convert : {'enabled' if cfg['timezone_convert'] else 'disabled'}",
        ]
        return "\n".join(lines)

    def run(self) -> dict:
        """Run the GLOBAL AI SOURCES FLOW pipeline."""
        result = self._flow.run_pipeline(
            raw_data={"domain": "meeting_scheduling", "meetings_count": len(EXAMPLES)},
            learning_method="supervised",
        )
        return {"pipeline_complete": result.get("pipeline_complete"), "summary": self.get_calendar_summary()}


if __name__ == "__main__":
    bot = MeetingSchedulerBot(tier="PRO")
    sales_meetings = bot.get_meetings_by_type("sales")
    print(f"Sales meetings: {len(sales_meetings)}")
    summary = bot.get_calendar_summary()
    print(f"Meetings by type: {summary['by_type']}")
    reminder = bot.send_reminder(1)
    print(f"Reminder: {reminder['message']}")
    print(bot.describe_tier())

# ---------------------------------------------------------------------------
# BusinessLaunchBot (from PR #142 — business launch planner)
# ---------------------------------------------------------------------------

import random as _random
from enum import Enum as _Enum
from typing import Optional as _Optional, List as _List, Dict as _Dict, Any as _Any


class _BizTier(_Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class BusinessLaunchBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class BusinessLaunchBot:
    """Tier-aware business launch planner."""

    RESULT_LIMITS: _Dict[str, int] = {"free": 5, "pro": 25, "enterprise": 100}

    MOCK_DATA: _List[_Dict[str, _Any]] = [
        {'id': f'BIZ{i:03d}', 'name': f'Biz {i}', 'sector': ['Tech', 'Service', 'Food', 'Retail'][i % 4],
         'revenue_potential': 8500 + i * 3500, 'startup_cost': 1800 + i * 800,
         'score': 47.6 + i * 2.6, 'roi_pct': 13.2 + i * 1.2}
        for i in range(1, 21)
    ]

    def __init__(self, tier: _Any = _BizTier.FREE) -> None:
        if isinstance(tier, str):
            self.tier = _BizTier(tier.lower())
        elif isinstance(tier, _BizTier):
            self.tier = tier
        else:
            self.tier = _BizTier(getattr(tier, "value", str(tier)))
        self._usage_count = 0

    def monthly_price(self) -> int:
        return {"free": 0, "pro": 29, "enterprise": 99}[self.tier.value]

    def get_tier_info(self) -> _Dict[str, _Any]:
        return {
            "tier": self.tier.value,
            "monthly_price_usd": self.monthly_price(),
            "result_limit": self.RESULT_LIMITS[self.tier.value],
            "usage_count": self._usage_count,
        }

    def _enforce_tier(self, required_value: str) -> None:
        order = ["free", "pro", "enterprise"]
        if order.index(self.tier.value) < order.index(required_value):
            raise BusinessLaunchBotTierError(
                f"{required_value.upper()} tier required; current: {self.tier.value}"
            )

    def list_items(self, limit: _Optional[int] = None) -> _List[_Dict[str, _Any]]:
        self._usage_count += 1
        cap = limit if limit else self.RESULT_LIMITS[self.tier.value]
        return _random.sample(self.MOCK_DATA, min(cap, len(self.MOCK_DATA)))

    def get_top_item(self) -> _Dict[str, _Any]:
        self._usage_count += 1
        return max(self.MOCK_DATA, key=lambda x: x.get("score", 0))

    def analyze(self) -> _Dict[str, _Any]:
        self._enforce_tier("pro")
        self._usage_count += 1
        values = [x.get("score", 0) for x in self.MOCK_DATA]
        return {"count": len(values), "max_score": max(values),
                "min_score": min(values), "avg_score": round(sum(values) / len(values), 2)}

    def filter_by_score(self, min_score: float) -> _List[_Dict[str, _Any]]:
        self._enforce_tier("pro")
        self._usage_count += 1
        return [x for x in self.MOCK_DATA if x.get("score", 0) >= min_score][:self.RESULT_LIMITS[self.tier.value]]

    def export_report(self) -> _Dict[str, _Any]:
        self._enforce_tier("enterprise")
        self._usage_count += 1
        return {"bot": "BusinessLaunchBot", "tier": self.tier.value,
                "total_items": len(self.MOCK_DATA), "items": self.MOCK_DATA}

# Expose Tier alias for test compatibility
Tier = _BizTier


# ---------------------------------------------------------------------------
# BuddyAI integration: bot_id, name, category, chat, end_session for MeetingSchedulerBot
# ---------------------------------------------------------------------------
import uuid as _uuid_biz1


def _meetingschedulerbot_init_buddy(self, tier: str = "FREE"):
    _orig_meeting_init(self, tier)
    if not hasattr(self, "bot_id"):
        self.bot_id = str(_uuid_biz1.uuid4())
    self.name = "Meeting Scheduler Bot"
    self.category = "business"
    self.domain = "meetings"


_orig_meeting_init = MeetingSchedulerBot.__init__
MeetingSchedulerBot.__init__ = _meetingschedulerbot_init_buddy


def _meetingschedulerbot_chat(self, user_input: str, user_id: str = "anonymous") -> str:
    q = user_input.lower()
    if any(w in q for w in ("meeting", "schedule", "appointment", "calendar")):
        return "I can help you schedule a meeting! What time works best?"
    return "I'm your Meeting Scheduler Bot. I can schedule meetings and manage your calendar."


def _meetingschedulerbot_end_session(self, user_id: str) -> None:
    pass


MeetingSchedulerBot.chat = _meetingschedulerbot_chat
MeetingSchedulerBot.end_session = _meetingschedulerbot_end_session

def _meetingschedulerbot_status(self) -> dict:
    return {
        "name": self.name,
        "category": self.category,
        "domain": self.domain,
        "revenue": {"total_revenue_usd": 0.0},
        "datasets": {"datasets_available": 0, "total_sales": 0},
        "top_intents": ["meeting", "schedule"],
    }


MeetingSchedulerBot.status = _meetingschedulerbot_status
