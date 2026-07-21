"""
Big Bro AI — Bot Prospectus System

Generates, manages, and evaluates structured prospectus documents for
every bot in the ecosystem.  Includes ROI bridges, external growth node
analysis, readiness scores, and study path automation.

GLOBAL AI SOURCES FLOW: participates via big_bro_ai.py pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Prospectus status
# ---------------------------------------------------------------------------

class ProspectusStatus(Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    DEPLOYED = "deployed"
    ARCHIVED = "archived"


# ---------------------------------------------------------------------------
# ROI Bridge
# ---------------------------------------------------------------------------

@dataclass
class ROIBridge:
    """
    Describes how a bot or system generates return on investment.

    Attributes
    ----------
    revenue_model : str
        Description of the revenue model (e.g. subscription, one-time, ads).
    monthly_revenue_target : float
        Expected monthly revenue in USD.
    break_even_months : int
        Estimated months to recoup development cost.
    scale_multiplier : float
        How much revenue scales per additional user/unit.
    automation_saving_hrs_per_month : float
        Hours saved per month via automation.
    notes : str
        Any additional context.
    """

    revenue_model: str
    monthly_revenue_target: float = 0.0
    break_even_months: int = 0
    scale_multiplier: float = 1.0
    automation_saving_hrs_per_month: float = 0.0
    notes: str = ""

    def annual_revenue_projection(self) -> float:
        """Project annual revenue based on monthly target and scale."""
        return round(self.monthly_revenue_target * 12 * self.scale_multiplier, 2)

    def to_dict(self) -> dict:
        return {
            "revenue_model": self.revenue_model,
            "monthly_revenue_target": self.monthly_revenue_target,
            "break_even_months": self.break_even_months,
            "scale_multiplier": self.scale_multiplier,
            "automation_saving_hrs_per_month": self.automation_saving_hrs_per_month,
            "notes": self.notes,
            "annual_revenue_projection": self.annual_revenue_projection(),
        }


# ---------------------------------------------------------------------------
# Study path
# ---------------------------------------------------------------------------

@dataclass
class StudyPathItem:
    """A single item in a bot's required study path."""
    order: int
    topic: str
    domain: str
    status: str = "pending"  # pending / in_progress / complete
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "order": self.order,
            "topic": self.topic,
            "domain": self.domain,
            "status": self.status,
            "notes": self.notes,
        }


# ---------------------------------------------------------------------------
# Full Prospectus document
# ---------------------------------------------------------------------------

@dataclass
class Prospectus:
    """
    Complete prospectus document for a bot or system.

    Attributes
    ----------
    prospectus_id : str
        Unique identifier.
    bot_name : str
        Name of the bot this prospectus describes.
    status : ProspectusStatus
        Current review stage.
    executive_summary : str
        Plain-language overview.
    core_skills : list[str]
        Key capabilities.
    objectives : list[str]
        Measurable goals.
    target_market : str
        Who this bot serves.
    roi_bridge : ROIBridge
        Financial projection and ROI analysis.
    study_path : list[StudyPathItem]
        Learning / build path for the bot's creator.
    external_growth_nodes : list[str]
        External integrations or expansion opportunities.
    readiness_score : int
        0-100 deployment readiness score.
    checklist : list[dict]
        Pre-deployment checklist items.
    created_at : str
        ISO creation timestamp.
    updated_at : str
        ISO last-update timestamp.
    """

    prospectus_id: str
    bot_name: str
    status: ProspectusStatus = ProspectusStatus.DRAFT
    executive_summary: str = ""
    core_skills: list[str] = field(default_factory=list)
    objectives: list[str] = field(default_factory=list)
    target_market: str = ""
    roi_bridge: ROIBridge = field(
        default_factory=lambda: ROIBridge(revenue_model="subscription")
    )
    study_path: list[StudyPathItem] = field(default_factory=list)
    external_growth_nodes: list[str] = field(default_factory=list)
    readiness_score: int = 0
    checklist: list[dict] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    # ------------------------------------------------------------------
    # Readiness score calculation
    # ------------------------------------------------------------------

    def recalculate_readiness(self) -> int:
        """
        Recompute the readiness score from:
        - executive_summary present: +10
        - core_skills count (5 pts each, max 25)
        - objectives count (5 pts each, max 25)
        - study_path items complete (5 pts each, max 20)
        - checklist items complete (2 pts each, max 20)
        """
        score = 0
        if self.executive_summary:
            score += 10
        score += min(len(self.core_skills) * 5, 25)
        score += min(len(self.objectives) * 5, 25)
        completed_study = sum(
            1 for s in self.study_path if s.status == "complete"
        )
        score += min(completed_study * 5, 20)
        completed_checks = sum(
            1 for c in self.checklist if c.get("done", False)
        )
        score += min(completed_checks * 2, 20)
        self.readiness_score = min(score, 100)
        self._touch()
        return self.readiness_score

    # ------------------------------------------------------------------
    # Study path management
    # ------------------------------------------------------------------

    def add_study_item(self, topic: str, domain: str, notes: str = "") -> StudyPathItem:
        """Append a study item to the learning path."""
        item = StudyPathItem(
            order=len(self.study_path) + 1,
            topic=topic,
            domain=domain,
            notes=notes,
        )
        self.study_path.append(item)
        self._touch()
        return item

    def complete_study_item(self, order: int) -> Optional[StudyPathItem]:
        """Mark a study item as complete by its order number."""
        for item in self.study_path:
            if item.order == order:
                item.status = "complete"
                self._touch()
                return item
        return None

    # ------------------------------------------------------------------
    # Checklist management
    # ------------------------------------------------------------------

    def add_checklist_item(self, label: str) -> dict:
        """Add a pre-deployment checklist item."""
        item = {"label": label, "done": False}
        self.checklist.append(item)
        self._touch()
        return item

    def complete_checklist_item(self, label: str) -> bool:
        """Mark a checklist item complete by label.  Returns True if found."""
        for item in self.checklist:
            if item["label"] == label:
                item["done"] = True
                self._touch()
                return True
        return False

    # ------------------------------------------------------------------
    # Status progression
    # ------------------------------------------------------------------

    def advance_status(self) -> ProspectusStatus:
        """Move to the next review stage."""
        order = [
            ProspectusStatus.DRAFT,
            ProspectusStatus.REVIEW,
            ProspectusStatus.APPROVED,
            ProspectusStatus.DEPLOYED,
        ]
        if self.status in order:
            idx = order.index(self.status)
            if idx + 1 < len(order):
                self.status = order[idx + 1]
                self._touch()
        return self.status

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "prospectus_id": self.prospectus_id,
            "bot_name": self.bot_name,
            "status": self.status.value,
            "executive_summary": self.executive_summary,
            "core_skills": self.core_skills,
            "objectives": self.objectives,
            "target_market": self.target_market,
            "roi_bridge": self.roi_bridge.to_dict(),
            "study_path": [s.to_dict() for s in self.study_path],
            "external_growth_nodes": self.external_growth_nodes,
            "readiness_score": self.readiness_score,
            "checklist": self.checklist,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Prospectus System
# ---------------------------------------------------------------------------

class ProspectusSystemError(Exception):
    """Raised when a prospectus operation fails."""


class ProspectusSystem:
    """
    Manages the full lifecycle of bot prospectus documents.
    """

    def __init__(self) -> None:
        self._prospectuses: dict[str, Prospectus] = {}
        self._id_counter: int = 0

    def create(
        self,
        bot_name: str,
        executive_summary: str = "",
        core_skills: Optional[list[str]] = None,
        objectives: Optional[list[str]] = None,
        target_market: str = "",
        roi_bridge: Optional[ROIBridge] = None,
    ) -> Prospectus:
        """Create a new prospectus for *bot_name*."""
        self._id_counter += 1
        p_id = f"prs_{self._id_counter:04d}"
        prospectus = Prospectus(
            prospectus_id=p_id,
            bot_name=bot_name,
            executive_summary=executive_summary,
            core_skills=core_skills or [],
            objectives=objectives or [],
            target_market=target_market,
            roi_bridge=roi_bridge or ROIBridge(revenue_model="subscription"),
        )
        prospectus.recalculate_readiness()
        self._prospectuses[p_id] = prospectus
        return prospectus

    def get(self, prospectus_id: str) -> Optional[Prospectus]:
        """Return a prospectus by ID, or None."""
        return self._prospectuses.get(prospectus_id)

    def list_all(
        self, status: Optional[ProspectusStatus] = None
    ) -> list[Prospectus]:
        """Return all prospectuses, optionally filtered by status."""
        items = list(self._prospectuses.values())
        if status is not None:
            items = [p for p in items if p.status == status]
        return sorted(items, key=lambda p: p.created_at)

    def count(self) -> int:
        """Return total prospectus count."""
        return len(self._prospectuses)

    def system_report(self) -> dict:
        """Return an overview of all prospectuses."""
        items = list(self._prospectuses.values())
        by_status: dict[str, int] = {}
        for p in items:
            by_status[p.status.value] = by_status.get(p.status.value, 0) + 1
        avg_readiness = (
            sum(p.readiness_score for p in items) / len(items) if items else 0
        )
        return {
            "total": len(items),
            "by_status": by_status,
            "average_readiness_score": round(avg_readiness, 1),
        }
