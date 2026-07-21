"""
DreamCo Core — Bot Registry

Tracks all bots that have been approved and registered within the DreamCo OS
runtime so they can be discovered, scheduled, and wired to the event bus.
"""

from __future__ import annotations

from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# In-process registry (global singleton list)
# ---------------------------------------------------------------------------

REGISTERED_BOTS: List[Dict[str, Any]] = []


def register_bot(bot_info: Dict[str, Any]) -> None:
    """
    Add *bot_info* to the global bot registry.

    Parameters
    ----------
    bot_info : dict
        Arbitrary metadata dict describing the bot.  Recommended keys:
        ``name``, ``path``, ``type``, ``status``.
    """
    REGISTERED_BOTS.append(bot_info)


def get_registered_bots() -> List[Dict[str, Any]]:
    """Return a copy of the current registry."""
    return list(REGISTERED_BOTS)


def clear_registry() -> None:
    """Clear all entries from the registry (useful for testing)."""
    REGISTERED_BOTS.clear()
