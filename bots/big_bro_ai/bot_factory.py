"""
Big Bro AI — Bot Factory

Automates the creation, tracking, and management of bots with defined
missions, memory tracking, tools integration, prospectuses, and
readiness scores.

Each manufactured bot includes:
- Mission statement
- Core skills & objectives
- Revenue goal
- Tool integrations
- Prospectus (structured spec)
- Readiness score (0-100)

GLOBAL AI SOURCES FLOW: participates via big_bro_ai.py pipeline.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Bot status
# ---------------------------------------------------------------------------

class BotStatus(Enum):
    BLUEPRINT = "blueprint"    # Design phase
    IN_PROGRESS = "in_progress"  # Being built
    READY = "ready"            # Deployed and operational
    PAUSED = "paused"          # Temporarily halted
    RETIRED = "retired"        # No longer active


# ---------------------------------------------------------------------------
# Bot categories
# ---------------------------------------------------------------------------

class BotCategory(Enum):
    MENTOR = "mentor"
    MONEY = "money"
    AUTOMATION = "automation"
    EDUCATION = "education"
    SALES = "sales"
    ANALYTICS = "analytics"
    COMMUNITY = "community"
    SECURITY = "security"
    CUSTOM = "custom"


# ---------------------------------------------------------------------------
# Prospectus (bot specification)
# ---------------------------------------------------------------------------

@dataclass
class BotProspectus:
    """
    Full specification document for a manufactured bot.

    Attributes
    ----------
    mission : str
        One-sentence mission statement.
    core_skills : list[str]
        Key capabilities the bot possesses.
    objectives : list[str]
        Measurable outcomes the bot targets.
    revenue_goal_usd : float
        Target monthly revenue the bot is expected to generate or support.
    tools : list[str]
        Integrations and APIs the bot uses.
    target_users : str
        Description of the intended user base.
    roi_bridge : str
        Explanation of how this bot generates return on investment.
    """

    mission: str
    core_skills: list[str] = field(default_factory=list)
    objectives: list[str] = field(default_factory=list)
    revenue_goal_usd: float = 0.0
    tools: list[str] = field(default_factory=list)
    target_users: str = ""
    roi_bridge: str = ""

    def to_dict(self) -> dict:
        return {
            "mission": self.mission,
            "core_skills": self.core_skills,
            "objectives": self.objectives,
            "revenue_goal_usd": self.revenue_goal_usd,
            "tools": self.tools,
            "target_users": self.target_users,
            "roi_bridge": self.roi_bridge,
        }


# ---------------------------------------------------------------------------
# Manufactured bot record
# ---------------------------------------------------------------------------

@dataclass
class ManufacturedBot:
    """
    A bot created by the Bot Factory.

    Attributes
    ----------
    bot_id : str
        Unique identifier.
    name : str
        Display name.
    category : BotCategory
        Domain category.
    prospectus : BotProspectus
        Full specification document.
    status : BotStatus
        Current lifecycle state.
    readiness_score : int
        0-100 score indicating deployment readiness.
    tasks_completed : list[str]
        Log of completed tasks.
    errors_log : list[dict]
        Error log with timestamps.
    revenue_earned_usd : float
        Cumulative revenue tracked.
    created_at : str
        ISO timestamp of creation.
    updated_at : str
        ISO timestamp of last update.
    """

    bot_id: str
    name: str
    category: BotCategory
    prospectus: BotProspectus
    status: BotStatus = BotStatus.BLUEPRINT
    readiness_score: int = 0
    tasks_completed: list[str] = field(default_factory=list)
    errors_log: list[dict] = field(default_factory=list)
    revenue_earned_usd: float = 0.0
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    # ------------------------------------------------------------------
    # Operations
    # ------------------------------------------------------------------

    def complete_task(self, task: str) -> None:
        """Mark a task as completed and recalculate readiness."""
        self.tasks_completed.append(task)
        self._recalculate_readiness()
        self._touch()

    def log_error(self, error: str, context: str = "") -> None:
        """Append an error to the error log."""
        self.errors_log.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": error,
                "context": context,
            }
        )
        self._touch()

    def record_revenue(self, amount: float) -> None:
        """Record revenue earned by this bot."""
        self.revenue_earned_usd += amount
        self._touch()

    def advance_status(self) -> BotStatus:
        """Move to the next lifecycle status."""
        order = [
            BotStatus.BLUEPRINT,
            BotStatus.IN_PROGRESS,
            BotStatus.READY,
        ]
        if self.status in order:
            idx = order.index(self.status)
            if idx + 1 < len(order):
                self.status = order[idx + 1]
                self._touch()
        return self.status

    def _recalculate_readiness(self) -> None:
        """
        Readiness score = f(tasks completed, skills defined,
        objectives defined, tools integrated).
        Capped at 100.
        """
        task_pts = min(len(self.tasks_completed) * 10, 40)
        skill_pts = min(len(self.prospectus.core_skills) * 5, 20)
        obj_pts = min(len(self.prospectus.objectives) * 5, 20)
        tool_pts = min(len(self.prospectus.tools) * 5, 20)
        self.readiness_score = int(min(task_pts + skill_pts + obj_pts + tool_pts, 100))

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "bot_id": self.bot_id,
            "name": self.name,
            "category": self.category.value,
            "prospectus": self.prospectus.to_dict(),
            "status": self.status.value,
            "readiness_score": self.readiness_score,
            "tasks_completed": self.tasks_completed,
            "errors_log": self.errors_log,
            "revenue_earned_usd": self.revenue_earned_usd,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# ---------------------------------------------------------------------------
# Bot Factory
# ---------------------------------------------------------------------------

class BotFactoryError(Exception):
    """Raised when a Bot Factory operation fails."""


class BotFactory:
    """
    Automated bot creation and lifecycle management system.

    Parameters
    ----------
    max_bots : int | None
        Maximum bots that can be created.  None = unlimited.
    """

    def __init__(self, max_bots: Optional[int] = None) -> None:
        self.max_bots = max_bots
        self._bots: dict[str, ManufacturedBot] = {}
        self._id_counter: int = 0

    # ------------------------------------------------------------------
    # Creation
    # ------------------------------------------------------------------

    def create_bot(
        self,
        name: str,
        category: BotCategory,
        mission: str,
        core_skills: Optional[list[str]] = None,
        objectives: Optional[list[str]] = None,
        revenue_goal_usd: float = 0.0,
        tools: Optional[list[str]] = None,
        target_users: str = "",
        roi_bridge: str = "",
    ) -> ManufacturedBot:
        """
        Design and register a new bot.

        Parameters
        ----------
        name : str
            Display name for the bot.
        category : BotCategory
            Domain category.
        mission : str
            One-sentence mission statement.
        core_skills : list[str] | None
            Core capabilities.
        objectives : list[str] | None
            Measurable objectives.
        revenue_goal_usd : float
            Target monthly revenue.
        tools : list[str] | None
            Tool/API integrations.
        target_users : str
            Intended user base description.
        roi_bridge : str
            How this bot generates ROI.

        Returns
        -------
        ManufacturedBot
        """
        if self.max_bots is not None and len(self._bots) >= self.max_bots:
            raise BotFactoryError(
                f"Bot limit ({self.max_bots}) reached. Upgrade your tier to create more bots."
            )
        self._id_counter += 1
        bot_id = f"bot_{self._id_counter:04d}"
        prospectus = BotProspectus(
            mission=mission,
            core_skills=core_skills or [],
            objectives=objectives or [],
            revenue_goal_usd=revenue_goal_usd,
            tools=tools or [],
            target_users=target_users,
            roi_bridge=roi_bridge,
        )
        bot = ManufacturedBot(
            bot_id=bot_id,
            name=name,
            category=category,
            prospectus=prospectus,
        )
        bot._recalculate_readiness()
        self._bots[bot_id] = bot
        return bot

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get_bot(self, bot_id: str) -> Optional[ManufacturedBot]:
        """Return the bot with *bot_id*, or None."""
        return self._bots.get(bot_id)

    def list_bots(
        self,
        category: Optional[BotCategory] = None,
        status: Optional[BotStatus] = None,
    ) -> list[ManufacturedBot]:
        """
        Return all manufactured bots, optionally filtered.

        Parameters
        ----------
        category : BotCategory | None
            If provided, only bots in this category are returned.
        status : BotStatus | None
            If provided, only bots with this status are returned.
        """
        bots = list(self._bots.values())
        if category is not None:
            bots = [b for b in bots if b.category == category]
        if status is not None:
            bots = [b for b in bots if b.status == status]
        return sorted(bots, key=lambda b: b.created_at)

    def bot_count(self) -> int:
        """Return total number of bots."""
        return len(self._bots)

    # ------------------------------------------------------------------
    # Lifecycle management
    # ------------------------------------------------------------------

    def advance_bot(self, bot_id: str) -> ManufacturedBot:
        """Advance *bot_id* to the next lifecycle status."""
        bot = self._require_bot(bot_id)
        bot.advance_status()
        return bot

    def retire_bot(self, bot_id: str) -> ManufacturedBot:
        """Mark *bot_id* as retired."""
        bot = self._require_bot(bot_id)
        bot.status = BotStatus.RETIRED
        bot._touch()
        return bot

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def factory_report(self) -> dict:
        """Return a summary of all bots created by this factory."""
        bots = list(self._bots.values())
        total_revenue = sum(b.revenue_earned_usd for b in bots)
        avg_readiness = (
            sum(b.readiness_score for b in bots) / len(bots) if bots else 0
        )
        by_status: dict[str, int] = {}
        for b in bots:
            by_status[b.status.value] = by_status.get(b.status.value, 0) + 1
        return {
            "total_bots": len(bots),
            "total_revenue_usd": round(total_revenue, 2),
            "average_readiness_score": round(avg_readiness, 1),
            "by_status": by_status,
            "bot_limit": self.max_bots,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _require_bot(self, bot_id: str) -> ManufacturedBot:
        bot = self._bots.get(bot_id)
        if bot is None:
            raise BotFactoryError(f"No bot found with id '{bot_id}'.")
        return bot
