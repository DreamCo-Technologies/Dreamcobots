"""
DreamCo Empire OS — Core Bot Module
=====================================

Lightweight Bot-protocol wrapper around DreamCoEmpireOS so that the
ControlCenter's automation loop can discover and invoke it via the
standard ``run()`` interface.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

from bots.dreamco_empire_os.empire_os import DreamCoEmpireOS
from bots.dreamco_empire_os.tiers import Tier


class Bot:
    """
    Bot-protocol adapter for DreamCoEmpireOS.

    Exposes a ``run()`` method so the ControlCenter can invoke the Empire OS
    in every automation cycle without needing to know its internal API.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.name = "DreamCo Empire OS"
        self._os = DreamCoEmpireOS(tier=tier)
        self._cycle: int = 0

    def run(self) -> str:
        """Execute one Empire OS automation cycle."""
        self._cycle += 1
        dashboard = self._os.dashboard()
        total_bots = dashboard.get("bot_fleet", {}).get("total_registered", 0)
        return (
            f"Empire OS cycle #{self._cycle} complete — "
            f"{total_bots} bots in fleet, system status: operational"
        )

    def get_status(self) -> dict:
        """Return the Empire OS dashboard as a status dict."""
        return self._os.dashboard()
