"""
Auto-Scaler Bot — monitors bot revenue and automatically clones profitable bots
into new niches to create a self-growing DreamCo bot ecosystem.

Revenue threshold (default $100) triggers a clone+deploy operation.
"""

from __future__ import annotations

import os
import shutil
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_REVENUE_THRESHOLD = 100.0  # USD


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class BotMetrics:
    bot_id: str
    bot_name: str
    revenue_usd: float = 0.0
    clone_count: int = 0
    last_updated: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "bot_id": self.bot_id,
            "bot_name": self.bot_name,
            "revenue_usd": round(self.revenue_usd, 2),
            "clone_count": self.clone_count,
            "last_updated": self.last_updated,
        }


@dataclass
class CloneRecord:
    clone_id: str
    source_bot: str
    target_niche: str
    deployed_path: str
    status: str  # "pending", "deployed", "failed"
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "clone_id": self.clone_id,
            "source_bot": self.source_bot,
            "target_niche": self.target_niche,
            "deployed_path": self.deployed_path,
            "status": self.status,
            "created_at": self.created_at,
        }


class AutoScalerError(Exception):
    """Raised when an auto-scaling operation fails."""


# ---------------------------------------------------------------------------
# AutoScalerBot
# ---------------------------------------------------------------------------


class AutoScalerBot:
    """
    Monitors bot revenue metrics and clones profitable bots into new niches.

    Usage
    -----
    scaler = AutoScalerBot(bots_root="/path/to/bots")
    scaler.register_bot("home_buyer_bot", "HomeBuyerBot")
    scaler.record_revenue("home_buyer_bot", 150.0)
    scaler.check_and_scale()   # triggers clone if revenue > threshold
    """

    def __init__(
        self,
        bots_root: str = "bots",
        revenue_threshold: float = DEFAULT_REVENUE_THRESHOLD,
        dry_run: bool = False,
    ):
        self.bots_root = os.path.abspath(bots_root)
        self.revenue_threshold = revenue_threshold
        self.dry_run = dry_run
        self._metrics: Dict[str, BotMetrics] = {}
        self._clones: Dict[str, CloneRecord] = {}
        self._scale_log: List[dict] = []

    # ------------------------------------------------------------------
    # Bot registration and revenue tracking
    # ------------------------------------------------------------------

    def register_bot(self, bot_id: str, bot_name: str) -> BotMetrics:
        """Register a bot for revenue monitoring."""
        metrics = BotMetrics(bot_id=bot_id, bot_name=bot_name)
        self._metrics[bot_id] = metrics
        return metrics

    def record_revenue(self, bot_id: str, amount: float) -> BotMetrics:
        """Add revenue to a bot's running total."""
        if bot_id not in self._metrics:
            raise AutoScalerError(f"Bot '{bot_id}' is not registered.")
        self._metrics[bot_id].revenue_usd += amount
        self._metrics[bot_id].last_updated = datetime.now(timezone.utc).isoformat()
        return self._metrics[bot_id]

    def get_metrics(self, bot_id: str) -> BotMetrics:
        if bot_id not in self._metrics:
            raise AutoScalerError(f"Bot '{bot_id}' is not registered.")
        return self._metrics[bot_id]

    def list_metrics(self) -> List[dict]:
        return [m.to_dict() for m in self._metrics.values()]

    # ------------------------------------------------------------------
    # Auto-scaling
    # ------------------------------------------------------------------

    def check_and_scale(self) -> List[CloneRecord]:
        """
        Evaluate all registered bots.  Clone any bot whose revenue has
        exceeded the threshold and has not yet been cloned for that niche.
        Returns the list of new CloneRecords created in this pass.
        """
        new_clones: List[CloneRecord] = []
        for bot_id, metrics in self._metrics.items():
            if metrics.revenue_usd >= self.revenue_threshold:
                niche = self._next_niche(bot_id, metrics.clone_count)
                record = self._clone_bot(bot_id, metrics.bot_name, niche)
                if record:
                    new_clones.append(record)
                    metrics.clone_count += 1
        return new_clones

    def clone_bot(self, bot_id: str, target_niche: str) -> CloneRecord:
        """Manually trigger a clone of *bot_id* into *target_niche*."""
        if bot_id not in self._metrics:
            raise AutoScalerError(f"Bot '{bot_id}' is not registered.")
        metrics = self._metrics[bot_id]
        record = self._clone_bot(bot_id, metrics.bot_name, target_niche)
        if record is None:
            raise AutoScalerError(f"Clone of '{bot_id}' into '{target_niche}' failed.")
        metrics.clone_count += 1
        return record

    def get_clone(self, clone_id: str) -> CloneRecord:
        if clone_id not in self._clones:
            raise AutoScalerError(f"Clone '{clone_id}' not found.")
        return self._clones[clone_id]

    def list_clones(self) -> List[dict]:
        return [c.to_dict() for c in self._clones.values()]

    def scale_summary(self) -> dict:
        total_revenue = sum(m.revenue_usd for m in self._metrics.values())
        profitable = [m for m in self._metrics.values() if m.revenue_usd >= self.revenue_threshold]
        return {
            "registered_bots": len(self._metrics),
            "profitable_bots": len(profitable),
            "total_clones": len(self._clones),
            "total_revenue_usd": round(total_revenue, 2),
            "revenue_threshold_usd": self.revenue_threshold,
            "dry_run": self.dry_run,
        }

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _next_niche(self, bot_id: str, clone_count: int) -> str:
        """Generate a niche name for the next clone."""
        niches = [
            "miami",
            "atlanta",
            "dallas",
            "los_angeles",
            "new_york",
            "houston",
            "phoenix",
            "seattle",
            "denver",
            "boston",
        ]
        idx = clone_count % len(niches)
        return f"{bot_id}_{niches[idx]}"

    def _clone_bot(
        self, source_bot_id: str, bot_name: str, target_niche: str
    ) -> Optional[CloneRecord]:
        """Copy the bot directory to a new niche directory."""
        source_path = os.path.join(self.bots_root, source_bot_id)
        target_name = target_niche.replace("/", "_")
        target_path = os.path.join(self.bots_root, target_name)

        clone_id = f"clone-{uuid.uuid4().hex[:8]}"
        status = "pending"

        if not self.dry_run:
            if not os.path.isdir(source_path):
                record = CloneRecord(
                    clone_id=clone_id,
                    source_bot=source_bot_id,
                    target_niche=target_niche,
                    deployed_path=target_path,
                    status="failed",
                )
                self._clones[clone_id] = record
                self._log("clone_failed", record.to_dict())
                return record
            try:
                if not os.path.exists(target_path):
                    shutil.copytree(source_path, target_path)
                status = "deployed"
            except Exception as exc:  # pragma: no cover
                status = "failed"

        record = CloneRecord(
            clone_id=clone_id,
            source_bot=source_bot_id,
            target_niche=target_niche,
            deployed_path=target_path,
            status=status if not self.dry_run else "dry_run",
        )
        self._clones[clone_id] = record
        self._log("bot_cloned", record.to_dict())
        return record

    def _log(self, event: str, data: dict) -> None:
        self._scale_log.append(
            {
                "event": event,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": data,
            }
        )

    def get_scale_log(self) -> List[dict]:
        return list(self._scale_log)
