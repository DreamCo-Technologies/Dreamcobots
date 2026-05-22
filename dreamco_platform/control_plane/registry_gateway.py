"""
DreamCo Control Plane — Registry Gateway
==========================================

Exposes bot-catalog and category health for the dashboard Marketplace /
Bot Network sections.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from dreamco_platform.registry.bot_registry import (
    BotLifecycleState,
    BotRegistry,
    HealthStatus,
)


class RegistryGateway:
    """
    Dashboard gateway for the canonical bot registry.

    Parameters
    ----------
    registry : BotRegistry | None
        The canonical bot registry.  A fresh empty registry is created if
        ``None`` is supplied.
    """

    def __init__(self, registry: Optional[BotRegistry] = None) -> None:
        self._registry = registry if registry is not None else BotRegistry()

    @property
    def registry(self) -> BotRegistry:
        return self._registry

    # ------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------

    def snapshot(self) -> Dict[str, Any]:
        """Return a registry / marketplace snapshot for the dashboard."""
        bots = self._registry.list_all()

        tier_counts: Dict[str, int] = {}
        category_counts: Dict[str, int] = {}
        lifecycle_counts: Dict[str, int] = {s.value: 0 for s in BotLifecycleState}

        for bot in bots:
            tier_counts[bot.pricing_tier] = tier_counts.get(bot.pricing_tier, 0) + 1
            if bot.category:
                category_counts[bot.category] = category_counts.get(bot.category, 0) + 1
            lifecycle_counts[bot.lifecycle_state.value] += 1

        catalog: List[Dict[str, Any]] = [
            {
                "bot_id": b.bot_id,
                "display_name": b.display_name,
                "category": b.category,
                "pricing_tier": b.pricing_tier,
                "version": b.version,
                "health": b.health.value,
                "lifecycle_state": b.lifecycle_state.value,
                "learning_enabled": b.learning_enabled,
                "tags": list(b.tags),
            }
            for b in bots
        ]

        return {
            "total_bots": len(bots),
            "tier_breakdown": tier_counts,
            "category_breakdown": category_counts,
            "lifecycle_breakdown": lifecycle_counts,
            "catalog": catalog,
            "snapshot_at": time.time(),
        }
