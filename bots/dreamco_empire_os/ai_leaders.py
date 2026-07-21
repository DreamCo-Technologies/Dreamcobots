"""
DreamCo Empire OS — AI Leaders Module

Tracks AI-driven decision makers, lead recommendation bots, revenue
forecasters, and strategic AI agents operating across the empire.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from framework import GlobalAISourcesFlow  # noqa: F401


class LeaderRole(Enum):
    REVENUE_FORECASTER = "revenue_forecaster"
    LEAD_RECOMMENDER = "lead_recommender"
    STRATEGY_ADVISOR = "strategy_advisor"
    OPERATIONS_MANAGER = "operations_manager"
    RISK_ANALYST = "risk_analyst"
    GROWTH_HACKER = "growth_hacker"
    CONTENT_DIRECTOR = "content_director"


class LeaderStatus(Enum):
    ACTIVE = "active"
    STANDBY = "standby"
    TRAINING = "training"
    RETIRED = "retired"


@dataclass
class AILeader:
    """Represents a high-level AI decision-making agent."""
    leader_id: str
    name: str
    role: LeaderRole
    status: LeaderStatus = LeaderStatus.ACTIVE
    performance_score: float = 0.0
    decisions_made: int = 0
    revenue_influenced_usd: float = 0.0
    specialties: list = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_active: Optional[str] = None


class AILeaders:
    """
    AI Leaders — track and manage the empire's strategic AI agents.

    Each AI Leader owns a domain of decision-making and influences
    revenue outcomes, risk assessments, or operational efficiency.
    """

    def __init__(self) -> None:
        self._leaders: dict[str, AILeader] = {}
        self._decision_log: list = []

    # ------------------------------------------------------------------
    # Leader management
    # ------------------------------------------------------------------

    def add_leader(
        self,
        leader_id: str,
        name: str,
        role: LeaderRole,
        specialties: Optional[list] = None,
    ) -> dict:
        """Register a new AI leader."""
        leader = AILeader(
            leader_id=leader_id,
            name=name,
            role=role,
            specialties=specialties or [],
        )
        self._leaders[leader_id] = leader
        return _leader_to_dict(leader)

    def update_status(self, leader_id: str, status: LeaderStatus) -> dict:
        """Update the operational status of an AI leader."""
        leader = self._get(leader_id)
        leader.status = status
        leader.last_active = datetime.now(timezone.utc).isoformat()
        return {"leader_id": leader_id, "status": status.value}

    # ------------------------------------------------------------------
    # Decision tracking
    # ------------------------------------------------------------------

    def record_decision(
        self,
        leader_id: str,
        decision: str,
        outcome: str,
        revenue_impact_usd: float = 0.0,
        success: bool = True,
    ) -> dict:
        """Log a decision made by an AI leader and update their performance."""
        leader = self._get(leader_id)
        leader.decisions_made += 1
        leader.revenue_influenced_usd += revenue_impact_usd
        leader.last_active = datetime.now(timezone.utc).isoformat()

        # Update performance score (rolling weighted average)
        increment = 10.0 if success else -5.0
        leader.performance_score = round(
            (leader.performance_score * (leader.decisions_made - 1) + increment) / leader.decisions_made, 2
        )

        entry = {
            "leader_id": leader_id,
            "leader_name": leader.name,
            "decision": decision,
            "outcome": outcome,
            "revenue_impact_usd": round(revenue_impact_usd, 2),
            "success": success,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._decision_log.append(entry)
        return entry

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def get_leader(self, leader_id: str) -> dict:
        return _leader_to_dict(self._get(leader_id))

    def list_leaders(self, status: Optional[LeaderStatus] = None) -> list:
        leaders = list(self._leaders.values())
        if status:
            leaders = [l for l in leaders if l.status == status]
        leaders.sort(key=lambda l: l.performance_score, reverse=True)
        return [_leader_to_dict(l) for l in leaders]

    def get_leaderboard(self) -> list:
        """Return AI leaders ranked by performance score."""
        return self.list_leaders()

    def get_summary(self) -> dict:
        leaders = list(self._leaders.values())
        active = [l for l in leaders if l.status == LeaderStatus.ACTIVE]
        total_revenue = sum(l.revenue_influenced_usd for l in leaders)
        return {
            "total_leaders": len(leaders),
            "active_leaders": len(active),
            "total_decisions": sum(l.decisions_made for l in leaders),
            "total_revenue_influenced_usd": round(total_revenue, 2),
            "avg_performance_score": round(
                sum(l.performance_score for l in leaders) / len(leaders), 2
            ) if leaders else 0.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_decision_log(self, limit: int = 20) -> list:
        return self._decision_log[-limit:]

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get(self, leader_id: str) -> AILeader:
        if leader_id not in self._leaders:
            raise KeyError(f"AI Leader '{leader_id}' not found.")
        return self._leaders[leader_id]


def _leader_to_dict(l: AILeader) -> dict:
    return {
        "leader_id": l.leader_id,
        "name": l.name,
        "role": l.role.value,
        "status": l.status.value,
        "performance_score": l.performance_score,
        "decisions_made": l.decisions_made,
        "revenue_influenced_usd": round(l.revenue_influenced_usd, 2),
        "specialties": l.specialties,
        "created_at": l.created_at,
        "last_active": l.last_active,
    }
