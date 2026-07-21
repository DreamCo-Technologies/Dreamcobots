"""
Buddy Core System — Public API.

    from bots.buddy_core import BuddyCore, Tier, BuddyCoreError
    from bots.buddy_core import ToolScraper, ToolReplicationEngine
"""

from __future__ import annotations

from bots.buddy_core.buddy_core import BuddyCore, BuddyCoreError, BuddyCoreTierError
from bots.buddy_core.tiers import Tier
from bots.buddy_core.tool_scraper import ToolScraper, ToolProfile, ToolScraperError
from bots.buddy_core.tool_replication import (
    ToolReplicationEngine,
    ReplicatedTool,
    ToolReplicationError,
)

__all__ = [
    "BuddyCore",
    "Tier",
    "BuddyCoreError",
    "BuddyCoreTierError",
    "ToolScraper",
    "ToolProfile",
    "ToolScraperError",
    "ToolReplicationEngine",
    "ReplicatedTool",
    "ToolReplicationError",
]
