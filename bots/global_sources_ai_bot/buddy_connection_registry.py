"""
Buddy connection registry for Global Sources modules.
"""

from __future__ import annotations

from datetime import datetime, timezone

_REGISTRY: dict[str, dict[str, str]] = {}


def register_buddy_connection(module_name: str, buddy_channel: str = "buddy_global_sources") -> None:
    """Register a module as directly connected to Buddy orchestration."""
    _REGISTRY[module_name] = {
        "module": module_name,
        "buddy_channel": buddy_channel,
        "status": "connected",
        "registered_at": datetime.now(timezone.utc).isoformat(),
    }


def buddy_connection_checklist() -> dict[str, object]:
    """Return a checklist summary for all registered Global Sources modules."""
    modules = sorted(_REGISTRY.values(), key=lambda item: item["module"])
    return {
        "buddy_channel": "buddy_global_sources",
        "total_modules": len(modules),
        "connected_modules": len([m for m in modules if m["status"] == "connected"]),
        "all_connected": all(m["status"] == "connected" for m in modules) if modules else False,
        "modules": modules,
    }
