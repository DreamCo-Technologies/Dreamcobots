"""Dependency-free local-first Buddy routing for user-owned workflows."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class LocalRoute:
    workflow: str
    external_data_required: bool
    reason: str

def route(text: str) -> LocalRoute:
    value = text.lower().strip()
    if any(word in value for word in ("note", "remember", "mark", "waypoint")):
        return LocalRoute("local_notes_and_waypoints", False, "Stores user-provided notes and coordinates locally.")
    if any(word in value for word in ("food", "rent help", "utility", "childcare", "transportation help")):
        return LocalRoute("local_need_triage", False, "Classifies the need locally; current service availability needs an authorized source.")
    if any(word in value for word in ("property history", "listing", "rental", "homes for sale")):
        return LocalRoute("property_provider_request", True, "Current listing and public-record data require an authorized provider or licensed dataset.")
    if any(word in value for word in ("weather", "earthquake", "flight", "traffic", "map")):
        return LocalRoute("public_world_source_request", True, "Current world signals require a selected source or a self-hosted data mirror.")
    return LocalRoute("local_buddy_planning", False, "Creates a local plan from user-provided context without claiming external facts.")
