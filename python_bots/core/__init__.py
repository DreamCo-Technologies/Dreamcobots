"""
DreamCo OS — Core package.

Exports the primary public API so callers can simply::

    from python_bots.core import DreamCoBot, BotState, MemoryClient, EventBus
"""

from python_bots.core.base_bot import DreamCoBot
from python_bots.core.lifecycle import BotState
from python_bots.core.memory import MemoryClient
from python_bots.core.model_router import ModelRouter

__all__ = ["DreamCoBot", "BotState", "MemoryClient", "ModelRouter"]
