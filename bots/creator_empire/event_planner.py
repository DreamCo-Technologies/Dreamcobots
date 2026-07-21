"""
Event Planner Engine for CreatorEmpire.

Handles venue research, budget planning, and contract template generation
for events managed through the DreamCo platform.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from dataclasses import dataclass, field
from typing import Optional
from tiers import Tier


class EventPlannerError(Exception):
    """Raised when an event planning operation fails or exceeds tier limits."""


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

EVENT_TYPES = [
    "concert", "meet_and_greet", "pop_up_shop", "listening_party",
    "sports_showcase", "streaming_event", "charity_gala", "workshop",
    "launch_party", "tournament",
]

VENUE_TYPES = ["arena", "club", "outdoor", "studio", "online", "hotel_ballroom", "community_center"]

_FREE_EVENT_LIMIT = 2


@dataclass
class VenueOption:
    """A venue option returned by venue research."""
    name: str
    venue_type: str
    city: str
    capacity: int
    estimated_cost_usd: float
    contact_email: str = ""
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "venue_type": self.venue_type,
            "city": self.city,
            "capacity": self.capacity,
            "estimated_cost_usd": self.estimated_cost_usd,
            "contact_email": self.contact_email,
            "notes": self.notes,
        }


@dataclass
class BudgetPlan:
    """Detailed budget breakdown for an event."""
    venue_cost: float = 0.0
    production_cost: float = 0.0
    marketing_cost: float = 0.0
    staffing_cost: float = 0.0
    catering_cost: float = 0.0
    talent_fees: float = 0.0
    contingency_pct: float = 10.0  # % buffer on top of subtotal
    currency: str = "USD"

    def subtotal(self) -> float:
        return (
            self.venue_cost + self.production_cost + self.marketing_cost
            + self.staffing_cost + self.catering_cost + self.talent_fees
        )

    def contingency(self) -> float:
        return round(self.subtotal() * self.contingency_pct / 100, 2)

    def total(self) -> float:
        return round(self.subtotal() + self.contingency(), 2)

    def to_dict(self) -> dict:
        return {
            "venue_cost": self.venue_cost,
            "production_cost": self.production_cost,
            "marketing_cost": self.marketing_cost,
            "staffing_cost": self.staffing_cost,
            "catering_cost": self.catering_cost,
            "talent_fees": self.talent_fees,
            "contingency_pct": self.contingency_pct,
            "subtotal": self.subtotal(),
            "contingency_amount": self.contingency(),
            "total": self.total(),
            "currency": self.currency,
        }


@dataclass
class Event:
    """Represents a planned event."""
    event_id: str
    talent_id: str
    event_type: str
    title: str
    city: str
    expected_attendance: int
    venue: Optional[VenueOption] = None
    budget: Optional[BudgetPlan] = None
    contract_generated: bool = False
    status: str = "planning"  # "planning" | "confirmed" | "completed" | "cancelled"

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "talent_id": self.talent_id,
            "event_type": self.event_type,
            "title": self.title,
            "city": self.city,
            "expected_attendance": self.expected_attendance,
            "venue": self.venue.to_dict() if self.venue else None,
            "budget": self.budget.to_dict() if self.budget else None,
            "contract_generated": self.contract_generated,
            "status": self.status,
        }


# ---------------------------------------------------------------------------
# Simulated venue database
# ---------------------------------------------------------------------------

_VENUE_DB: list[dict] = [
    {"name": "The Marquee", "venue_type": "club", "city": "New York", "capacity": 500, "cost": 5000},
    {"name": "Madison Square Garden", "venue_type": "arena", "city": "New York", "capacity": 20000, "cost": 150000},
    {"name": "The Wiltern", "venue_type": "club", "city": "Los Angeles", "capacity": 1850, "cost": 12000},
    {"name": "Crypto.com Arena", "venue_type": "arena", "city": "Los Angeles", "capacity": 20000, "cost": 200000},
    {"name": "House of Blues", "venue_type": "club", "city": "Chicago", "capacity": 1400, "cost": 8000},
    {"name": "United Center", "venue_type": "arena", "city": "Chicago", "capacity": 23500, "cost": 180000},
    {"name": "Online Virtual Stage", "venue_type": "online", "city": "Virtual", "capacity": 999999, "cost": 2000},
    {"name": "Community Amphitheater", "venue_type": "outdoor", "city": "Atlanta", "capacity": 3000, "cost": 6000},
]

# Contract template (simplified)
_CONTRACT_TEMPLATE = """\
EVENT SERVICES AGREEMENT
========================
Event Title  : {title}
Event Type   : {event_type}
Talent       : {talent_id}
City         : {city}
Attendance   : ~{expected_attendance} guests
Venue        : {venue_name}

TERMS
-----
1. Performance obligations as agreed between talent and venue.
2. Payment schedule: 50% deposit upon signing, 50% day of event.
3. Cancellation policy: 30-day notice required; deposit non-refundable < 14 days.
4. Force majeure clause applies.
5. Both parties agree to mediation before litigation.

[SIGNATURE BLOCKS]
Talent Representative: ___________________  Date: ________
Venue Representative : ___________________  Date: ________

Generated by CreatorEmpire Event Planner
"""


class EventPlannerEngine:
    """
    Plans, budgets, and generates contracts for talent events.

    Parameters
    ----------
    tier : Tier
        Controls how many events can be planned per month and
        access to contract generation features.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self._events: dict[str, Event] = {}

    # ------------------------------------------------------------------
    # Event management
    # ------------------------------------------------------------------

    def create_event(
        self,
        event_id: str,
        talent_id: str,
        event_type: str,
        title: str,
        city: str,
        expected_attendance: int,
    ) -> Event:
        """
        Create a new event plan.

        FREE tier is limited to 2 events per planner instance.
        """
        if event_id in self._events:
            raise EventPlannerError(f"Event ID '{event_id}' already exists.")
        if self.tier == Tier.FREE and len(self._events) >= _FREE_EVENT_LIMIT:
            raise EventPlannerError(
                f"Free tier allows a maximum of {_FREE_EVENT_LIMIT} events. "
                "Upgrade to Pro for unlimited event planning."
            )
        event = Event(
            event_id=event_id,
            talent_id=talent_id,
            event_type=event_type.lower(),
            title=title,
            city=city,
            expected_attendance=expected_attendance,
        )
        self._events[event_id] = event
        return event

    def get_event(self, event_id: str) -> dict:
        return self._get_event(event_id).to_dict()

    def list_events(self, talent_id: Optional[str] = None) -> list[dict]:
        events = self._events.values()
        if talent_id:
            events = [e for e in events if e.talent_id == talent_id]
        return [e.to_dict() for e in events]

    def update_event_status(self, event_id: str, status: str) -> Event:
        valid = {"planning", "confirmed", "completed", "cancelled"}
        if status not in valid:
            raise EventPlannerError(f"Invalid status '{status}'. Choose from: {valid}.")
        event = self._get_event(event_id)
        event.status = status
        return event

    # ------------------------------------------------------------------
    # Venue research
    # ------------------------------------------------------------------

    def research_venues(
        self,
        city: str,
        min_capacity: int = 0,
        max_budget_usd: Optional[float] = None,
        venue_type: Optional[str] = None,
    ) -> list[dict]:
        """
        Search the venue database for options matching the criteria.
        """
        results = []
        for v in _VENUE_DB:
            if city.lower() not in v["city"].lower() and v["city"] != "Virtual":
                continue
            if v["capacity"] < min_capacity:
                continue
            if max_budget_usd is not None and v["cost"] > max_budget_usd:
                continue
            if venue_type and v["venue_type"] != venue_type.lower():
                continue
            results.append(VenueOption(
                name=v["name"],
                venue_type=v["venue_type"],
                city=v["city"],
                capacity=v["capacity"],
                estimated_cost_usd=v["cost"],
            ).to_dict())
        return results

    def assign_venue(self, event_id: str, venue_name: str) -> Event:
        """Assign a venue to an event by name."""
        event = self._get_event(event_id)
        venue_data = next((v for v in _VENUE_DB if v["name"] == venue_name), None)
        if venue_data is None:
            raise EventPlannerError(f"Venue '{venue_name}' not found.")
        event.venue = VenueOption(
            name=venue_data["name"],
            venue_type=venue_data["venue_type"],
            city=venue_data["city"],
            capacity=venue_data["capacity"],
            estimated_cost_usd=venue_data["cost"],
        )
        return event

    # ------------------------------------------------------------------
    # Budget planning
    # ------------------------------------------------------------------

    def create_budget(
        self,
        event_id: str,
        venue_cost: float = 0.0,
        production_cost: float = 0.0,
        marketing_cost: float = 0.0,
        staffing_cost: float = 0.0,
        catering_cost: float = 0.0,
        talent_fees: float = 0.0,
        contingency_pct: float = 10.0,
    ) -> BudgetPlan:
        """Attach a budget plan to an event."""
        event = self._get_event(event_id)
        budget = BudgetPlan(
            venue_cost=venue_cost,
            production_cost=production_cost,
            marketing_cost=marketing_cost,
            staffing_cost=staffing_cost,
            catering_cost=catering_cost,
            talent_fees=talent_fees,
            contingency_pct=contingency_pct,
        )
        event.budget = budget
        return budget

    # ------------------------------------------------------------------
    # Contract generation (PRO / ENTERPRISE)
    # ------------------------------------------------------------------

    def generate_contract(self, event_id: str) -> str:
        """
        Generate a contract template for an event.

        Requires PRO or ENTERPRISE tier.
        """
        if self.tier == Tier.FREE:
            raise EventPlannerError(
                "Contract generation requires the Pro tier or higher."
            )
        event = self._get_event(event_id)
        venue_name = event.venue.name if event.venue else "TBD"
        contract = _CONTRACT_TEMPLATE.format(
            title=event.title,
            event_type=event.event_type,
            talent_id=event.talent_id,
            city=event.city,
            expected_attendance=event.expected_attendance,
            venue_name=venue_name,
        )
        event.contract_generated = True
        return contract

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self) -> dict:
        return {
            "tier": self.tier.value,
            "total_events": len(self._events),
            "event_limit": _FREE_EVENT_LIMIT if self.tier == Tier.FREE else "unlimited",
            "statuses": {
                s: sum(1 for e in self._events.values() if e.status == s)
                for s in ("planning", "confirmed", "completed", "cancelled")
            },
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_event(self, event_id: str) -> Event:
        if event_id not in self._events:
            raise EventPlannerError(f"Event '{event_id}' not found.")
        return self._events[event_id]
