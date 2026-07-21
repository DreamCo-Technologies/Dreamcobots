"""
Automated Task Delegation AI for DreamOps.

Provides skill-capacity matching, workload balancing,
and delegation confidence scoring.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))

from framework import GlobalAISourcesFlow  # noqa: F401

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set


@dataclass
class Agent:
    agent_id: str
    name: str
    skills: Set[str]
    current_load: float    # hours currently assigned
    capacity: float        # max hours available
    success_rate: float    # 0.0 - 1.0


@dataclass
class Task:
    task_id: str
    required_skills: Set[str]
    priority: int          # 1 (highest) - 5 (lowest)
    estimated_hours: float
    deadline: Optional[datetime] = None


class TaskDelegationAI:
    """Matches tasks to agents using skill-capacity scoring."""

    def __init__(self) -> None:
        self._agents: Dict[str, Agent] = {}
        self._task_assignments: Dict[str, str] = {}   # task_id -> agent_id
        self._delegation_log: List[dict] = []

    def register_agent(self, agent_id: str, skills: Set[str], capacity: float) -> Agent:
        """Register a new agent with given skills and capacity."""
        agent = Agent(
            agent_id=agent_id,
            name=agent_id,
            skills=set(skills),
            current_load=0.0,
            capacity=capacity,
            success_rate=1.0,
        )
        self._agents[agent_id] = agent
        return agent

    def delegate_task(self, task: Task) -> Optional[dict]:
        """Assign a task to the best available agent."""
        best_agent = None
        best_score = -1.0
        for agent in self._agents.values():
            score = self.score_confidence(task, agent.agent_id)
            if score > best_score:
                best_score = score
                best_agent = agent
        if not best_agent or best_score <= 0:
            return {"status": "unassigned", "reason": "No suitable agent found."}
        best_agent.current_load += task.estimated_hours
        self._task_assignments[task.task_id] = best_agent.agent_id
        log_entry = {
            "task_id": task.task_id,
            "agent_id": best_agent.agent_id,
            "confidence_score": round(best_score, 4),
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._delegation_log.append(log_entry)
        return {"status": "assigned", "agent_id": best_agent.agent_id, "confidence": round(best_score, 4)}

    def score_confidence(self, task: Task, agent_id: str) -> float:
        """Score the confidence of assigning a task to an agent."""
        agent = self._agents.get(agent_id)
        if not agent:
            return 0.0
        # Skill match
        required = set(task.required_skills)
        matched = required & agent.skills
        skill_score = len(matched) / max(len(required), 1)
        # Capacity headroom; use 0.1 as minimum divisor to avoid division by zero
        available = max(agent.capacity - agent.current_load, 0.0)
        capacity_score = min(available / max(task.estimated_hours, 0.1), 1.0)
        # Success rate
        confidence = (skill_score * 0.5 + capacity_score * 0.3 + agent.success_rate * 0.2)
        return confidence

    def rebalance_workload(self) -> dict:
        """Redistribute load to reduce imbalance across agents."""
        if not self._agents:
            return {"status": "no_agents"}
        loads = {aid: a.current_load / max(a.capacity, 1e-9) for aid, a in self._agents.items()}
        avg_utilization = sum(loads.values()) / len(loads)
        overloaded = [aid for aid, u in loads.items() if u > 0.9]
        underloaded = [aid for aid, u in loads.items() if u < 0.3]
        return {
            "avg_utilization": round(avg_utilization, 4),
            "overloaded_agents": overloaded,
            "underloaded_agents": underloaded,
            "rebalanced": True,
        }

    def get_delegation_report(self) -> dict:
        """Return a summary of delegation activity."""
        return {
            "total_agents": len(self._agents),
            "total_tasks_delegated": len(self._task_assignments),
            "delegation_log": self._delegation_log[-10:],
            "agent_loads": {
                aid: round(a.current_load / max(a.capacity, 1e-9) * 100, 2)
                for aid, a in self._agents.items()
            },
        }

    def update_agent_success_rate(self, agent_id: str, completed: int, attempted: int) -> None:
        """Update an agent's success rate based on outcomes."""
        agent = self._agents.get(agent_id)
        if agent and attempted > 0:
            agent.success_rate = round(completed / attempted, 4)
