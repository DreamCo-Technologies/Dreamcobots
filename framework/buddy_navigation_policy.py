"""Provider-neutral navigation policy primitives.

This layer does not drive a vehicle. It selects route preferences and controls
which nonessential interactions should be deferred while motion is detected.
"""
from dataclasses import dataclass, field

@dataclass(frozen=True)
class NavigationPreferences:
    avoid_highways: bool = False
    avoid_backroads: bool = False
    avoid_tolls: bool = False
    avoid_ferries: bool = False
    vehicle_type: str = "car"
    fastest: bool = True
    safest: bool = True

@dataclass
class NavigationState:
    destination: str | None = None
    moving: bool = False
    voice_mode: bool = True
    microphone_enabled: bool = True
    queued_requests: list[str] = field(default_factory=list)
    spoken_context: list[str] = field(default_factory=list)

class BuddyNavigationPolicy:
    def __init__(self, preferences: NavigationPreferences | None = None):
        self.preferences = preferences or NavigationPreferences()

    def route_constraints(self) -> dict:
        return {
            "avoid_highways": self.preferences.avoid_highways,
            "avoid_backroads": self.preferences.avoid_backroads,
            "avoid_tolls": self.preferences.avoid_tolls,
            "avoid_ferries": self.preferences.avoid_ferries,
            "vehicle_type": self.preferences.vehicle_type,
            "rank_for": ["safety", "travel_time"] if self.preferences.safest else ["travel_time"],
        }

    def handle_request(self, state: NavigationState, request: str, safety_critical: bool = False) -> str:
        if state.moving and not safety_critical:
            state.queued_requests.append(request)
            return "queued_for_safe_interaction"
        return "handle_now"

    def navigation_priority(self, state: NavigationState) -> list[str]:
        if state.moving:
            return ["turn_instructions", "hazards", "route_changes", "emergency", "queued_conversation"]
        return ["navigation", "conversation", "creative", "commerce"]
