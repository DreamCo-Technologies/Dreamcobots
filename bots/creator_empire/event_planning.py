"""
Event Planning module for the CreatorEmpire bot.

Supports creator-led events such as live shows, meet-and-greets, pop-up
experiences, virtual concerts, and community tournaments.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .tiers import (
    Tier,
    CREATOR_FEATURES_BY_TIER,
    FEATURE_EVENT_PLANNER,
)


class EventError(Exception):
    """Raised when an event planning operation cannot be completed."""


# Supported event types
EVENT_TYPES = [
    "live_show",
    "meet_and_greet",
    "pop_up_experience",
    "virtual_concert",
    "community_tournament",
    "masterclass",
    "product_launch",
    "charity_stream",
    "fan_convention",
    "workshop",
]

# Event status lifecycle
EVENT_STATUS_PLANNED = "planned"
EVENT_STATUS_PROMOTED = "promoted"
EVENT_STATUS_LIVE = "live"
EVENT_STATUS_COMPLETED = "completed"
EVENT_STATUS_CANCELLED = "cancelled"


@dataclass
class Event:
    """Represents a planned creator event.

    Attributes
    ----------
    event_id : str
        Unique identifier for the event.
    creator_name : str
        Organising creator's name.
    title : str
        Event title.
    event_type : str
        Type of event (e.g. 'live_show', 'masterclass').
    date : str
        ISO-format date string (YYYY-MM-DD).
    venue_or_platform : str
        Physical venue name or virtual platform (e.g. 'Zoom', 'Discord').
    capacity : int | None
        Maximum attendees.  ``None`` means unlimited.
    ticket_price_usd : float
        Ticket price; 0.0 for free events.
    status : str
        Current event lifecycle status.
    sponsors : list[str]
        Names of confirmed sponsors.
    tasks : list[str]
        Planning tasks with completion status encoded as 'done:...' or 'todo:...'.
    metadata : dict
        Arbitrary extra event data.
    """

    event_id: str
    creator_name: str
    title: str
    event_type: str
    date: str
    venue_or_platform: str
    capacity: Optional[int] = None
    ticket_price_usd: float = 0.0
    status: str = EVENT_STATUS_PLANNED
    sponsors: list[str] = field(default_factory=list)
    tasks: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "creator_name": self.creator_name,
            "title": self.title,
            "event_type": self.event_type,
            "date": self.date,
            "venue_or_platform": self.venue_or_platform,
            "capacity": self.capacity,
            "ticket_price_usd": self.ticket_price_usd,
            "status": self.status,
            "sponsors": self.sponsors,
            "tasks": self.tasks,
            "metadata": self.metadata,
        }


# Standard planning task templates per event type
_PLANNING_TASKS: dict[str, list[str]] = {
    "live_show": [
        "todo:Book venue and confirm date",
        "todo:Secure sound and lighting equipment",
        "todo:Design promotional artwork",
        "todo:Launch ticket sales",
        "todo:Promote across social media",
        "todo:Arrange merchandise table",
        "todo:Conduct sound check on day of show",
        "todo:Set up meet-and-greet slot after show",
    ],
    "meet_and_greet": [
        "todo:Select venue (record store, café, event space)",
        "todo:Set RSVP or ticket limit",
        "todo:Design branded backdrop for photos",
        "todo:Prepare signed merchandise for attendees",
        "todo:Announce via social media and email list",
        "todo:Arrange photographer/videographer",
    ],
    "virtual_concert": [
        "todo:Choose streaming platform (Twitch, YouTube, Veeps)",
        "todo:Set up virtual ticketing or donation goal",
        "todo:Rehearse full setlist",
        "todo:Design virtual stage or green-screen backdrop",
        "todo:Send reminder emails/DMs to registered attendees",
        "todo:Archive and monetise VOD after event",
    ],
    "masterclass": [
        "todo:Define syllabus and learning outcomes",
        "todo:Set up registration page or Eventbrite listing",
        "todo:Prepare slide deck and demo materials",
        "todo:Send confirmation and joining instructions to registrants",
        "todo:Record session for replay sales",
        "todo:Collect feedback survey after session",
    ],
    "community_tournament": [
        "todo:Define game/activity and ruleset",
        "todo:Open registration and set team/player cap",
        "todo:Create bracket and scheduling tool",
        "todo:Set up prize pool (cash, merchandise, shoutouts)",
        "todo:Stream tournament finals live",
        "todo:Announce winners on all channels",
    ],
}

_DEFAULT_TASKS = [
    "todo:Define event goals and target audience",
    "todo:Choose venue/platform and lock in date",
    "todo:Create promotional plan",
    "todo:Launch registration or ticket sales",
    "todo:Deliver event",
    "todo:Post-event follow-up and content publishing",
]


class EventPlanningEngine:
    """
    Manages event planning workflows for creators.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling available event features.
    """

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self._events: dict[str, Event] = {}
        self._id_counter: int = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_event(
        self,
        creator_name: str,
        title: str,
        event_type: str,
        date: str,
        venue_or_platform: str,
        capacity: Optional[int] = None,
        ticket_price_usd: float = 0.0,
    ) -> Event:
        """
        Create a new event for a creator.

        Parameters
        ----------
        creator_name : str
            Organising creator's name.
        title : str
            Event title.
        event_type : str
            Must be one of the supported event types.
        date : str
            ISO-format date string (YYYY-MM-DD).
        venue_or_platform : str
            Physical venue or virtual platform.
        capacity : int | None
            Maximum attendees; None for unlimited.
        ticket_price_usd : float
            Ticket price; 0.0 for free events.

        Returns
        -------
        Event
        """
        self._check_feature(FEATURE_EVENT_PLANNER)

        event_type = event_type.lower().strip()
        if event_type not in EVENT_TYPES:
            raise EventError(
                f"Unsupported event type '{event_type}'. "
                f"Valid types: {', '.join(EVENT_TYPES)}."
            )

        self._id_counter += 1
        event_id = f"evt_{self._id_counter:04d}"
        tasks = list(_PLANNING_TASKS.get(event_type, _DEFAULT_TASKS))

        event = Event(
            event_id=event_id,
            creator_name=creator_name,
            title=title,
            event_type=event_type,
            date=date,
            venue_or_platform=venue_or_platform,
            capacity=capacity,
            ticket_price_usd=ticket_price_usd,
            tasks=tasks,
        )
        self._events[event_id] = event
        return event

    def advance_status(self, event_id: str) -> Event:
        """
        Advance an event to the next lifecycle status.

        Lifecycle: planned → promoted → live → completed.
        """
        self._check_feature(FEATURE_EVENT_PLANNER)
        event = self._get_event(event_id)
        transitions = {
            EVENT_STATUS_PLANNED: EVENT_STATUS_PROMOTED,
            EVENT_STATUS_PROMOTED: EVENT_STATUS_LIVE,
            EVENT_STATUS_LIVE: EVENT_STATUS_COMPLETED,
        }
        if event.status not in transitions:
            raise EventError(
                f"Event '{event_id}' is in terminal status '{event.status}'."
            )
        event.status = transitions[event.status]
        return event

    def cancel_event(self, event_id: str) -> Event:
        """Cancel an event."""
        self._check_feature(FEATURE_EVENT_PLANNER)
        event = self._get_event(event_id)
        if event.status == EVENT_STATUS_COMPLETED:
            raise EventError("Cannot cancel a completed event.")
        event.status = EVENT_STATUS_CANCELLED
        return event

    def complete_task(self, event_id: str, task_index: int) -> Event:
        """Mark a planning task as done by its index."""
        self._check_feature(FEATURE_EVENT_PLANNER)
        event = self._get_event(event_id)
        if task_index < 0 or task_index >= len(event.tasks):
            raise EventError(f"Task index {task_index} is out of range.")
        task = event.tasks[task_index]
        if task.startswith("todo:"):
            event.tasks[task_index] = "done:" + task[5:]
        return event

    def add_sponsor(self, event_id: str, sponsor_name: str) -> Event:
        """Add a sponsor to an event."""
        self._check_feature(FEATURE_EVENT_PLANNER)
        event = self._get_event(event_id)
        if sponsor_name not in event.sponsors:
            event.sponsors.append(sponsor_name)
        return event

    def get_event(self, event_id: str) -> Event:
        """Return the Event for *event_id*."""
        return self._get_event(event_id)

    def list_events(self, creator_name: Optional[str] = None) -> list[dict]:
        """Return all events, optionally filtered by creator."""
        events = self._events.values()
        if creator_name:
            events = (e for e in events if e.creator_name == creator_name)
        return [e.to_dict() for e in events]

    def get_pending_tasks(self, event_id: str) -> list[str]:
        """Return all incomplete (todo) tasks for an event."""
        event = self._get_event(event_id)
        return [t[5:] for t in event.tasks if t.startswith("todo:")]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_event(self, event_id: str) -> Event:
        if event_id not in self._events:
            raise EventError(f"No event found with ID '{event_id}'.")
        return self._events[event_id]

    def _check_feature(self, feature: str) -> None:
        available = CREATOR_FEATURES_BY_TIER[self.tier.value]
        if feature not in available:
            raise EventError(
                f"Feature '{feature}' is not available on the "
                f"{self.tier.value.capitalize()} tier."
            )
