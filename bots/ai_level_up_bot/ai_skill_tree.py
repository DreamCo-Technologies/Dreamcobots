"""
AI Skill Tree — gamified learning progression for the DreamCo AI Level-Up Bot.

Users advance through nodes by completing course modules, earning badges,
token discounts, and unlocking higher levels.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import copy
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from framework import GlobalAISourcesFlow  # noqa: F401


class NodeStatus(Enum):
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@dataclass
class SkillNode:
    """A single node in the AI Skill Tree."""

    node_id: str
    level: int
    title: str
    skills: List[str]
    badge: str
    reward_description: str
    token_discount_pct: float = 0.0
    status: NodeStatus = NodeStatus.LOCKED

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "level": self.level,
            "title": self.title,
            "skills": self.skills,
            "badge": self.badge,
            "reward_description": self.reward_description,
            "token_discount_pct": self.token_discount_pct,
            "status": self.status.value,
        }


# ---------------------------------------------------------------------------
# Skill tree seed data
# ---------------------------------------------------------------------------

_SKILL_NODES: List[SkillNode] = [
    SkillNode(
        node_id="L1-FOUNDATIONS",
        level=1,
        title="AI Foundations",
        skills=["AI fundamentals", "Ethics of AI", "AI tools overview"],
        badge="🤖 AI Explorer",
        reward_description="Unlock Level 2 and earn the AI Explorer badge.",
        token_discount_pct=0.0,
    ),
    SkillNode(
        node_id="L2-PROMPTS",
        level=2,
        title="Prompt Master",
        skills=["Prompt fundamentals", "Chain-of-thought prompting", "Few-shot prompting"],
        badge="⚡ Prompt Master",
        reward_description="+5% token discount on all LLM services.",
        token_discount_pct=5.0,
    ),
    SkillNode(
        node_id="L3-CONTENT",
        level=3,
        title="Content Creator",
        skills=["AI writing", "Image generation", "Video creation", "Voice synthesis"],
        badge="🎨 AI Content Creator",
        reward_description="+5% token discount on image and video generation.",
        token_discount_pct=5.0,
    ),
    SkillNode(
        node_id="L4-AUTOMATION",
        level=4,
        title="Automation Architect",
        skills=["Workflow automation", "No-code tools", "Marketing automation"],
        badge="⚙️ Automation Architect",
        reward_description="+10% token discount on automation services.",
        token_discount_pct=10.0,
    ),
    SkillNode(
        node_id="L5-BUSINESS",
        level=5,
        title="AI Business Builder",
        skills=["AI business models", "MVP development", "Go-to-market strategy"],
        badge="💼 AI Entrepreneur",
        reward_description="+10% token discount and access to business templates.",
        token_discount_pct=10.0,
    ),
    SkillNode(
        node_id="L6-AGENTS",
        level=6,
        title="Agent Developer",
        skills=["AI agent architecture", "LangChain", "Multi-agent systems"],
        badge="🦾 Agent Builder",
        reward_description="+15% token discount on agent services.",
        token_discount_pct=15.0,
    ),
    SkillNode(
        node_id="L7-INFRA",
        level=7,
        title="AI Infrastructure Engineer",
        skills=["Cloud AI platforms", "Model serving", "MLOps"],
        badge="🏗️ Infrastructure Engineer",
        reward_description="+15% token discount on infrastructure services.",
        token_discount_pct=15.0,
    ),
    SkillNode(
        node_id="L8-RESEARCH",
        level=8,
        title="AI Researcher",
        skills=["Fine-tuning", "RLHF", "Evaluation frameworks", "Benchmarking"],
        badge="🔬 AI Researcher",
        reward_description="+20% token discount on compute-heavy services.",
        token_discount_pct=20.0,
    ),
    SkillNode(
        node_id="L9-FOUNDER",
        level=9,
        title="AI Founder",
        skills=["Company strategy", "Fundraising", "Team building", "Scaling"],
        badge="🚀 AI Founder",
        reward_description="+20% token discount and DreamCo AI Founder Certificate.",
        token_discount_pct=20.0,
    ),
    SkillNode(
        node_id="L10-MASTER",
        level=10,
        title="AI Superintelligence Architect",
        skills=["Advanced architectures", "Multimodal systems", "AI safety", "Future of AI"],
        badge="🌟 AI Master",
        reward_description="+25% lifetime token discount and DreamCo AI Master Certification.",
        token_discount_pct=25.0,
    ),
]


class AISkillTree:
    """Manages user progression through the gamified AI Skill Tree.

    Parameters
    ----------
    max_level : int
        Maximum level unlockable on the current tier.
    """

    def __init__(self, max_level: int = 10) -> None:
        self._max_level = max(1, min(max_level, 10))
        # Deep-copy so that each instance has its own mutable node objects.
        self._nodes: dict = {n.node_id: copy.copy(n) for n in _SKILL_NODES}
        # Unlock the first node by default
        first = self._nodes.get("L1-FOUNDATIONS")
        if first:
            first.status = NodeStatus.UNLOCKED

    # ------------------------------------------------------------------
    # Node access
    # ------------------------------------------------------------------

    def get_node(self, node_id: str) -> Optional[SkillNode]:
        """Return a skill node by its ID."""
        return self._nodes.get(node_id)

    def get_node_by_level(self, level: int) -> Optional[SkillNode]:
        """Return the skill node for a given level."""
        for node in self._nodes.values():
            if node.level == level:
                return node
        return None

    def list_all_nodes(self) -> List[SkillNode]:
        """Return all nodes sorted by level."""
        return sorted(self._nodes.values(), key=lambda n: n.level)

    def list_accessible_nodes(self) -> List[SkillNode]:
        """Return nodes accessible on the current tier."""
        return [n for n in self.list_all_nodes() if n.level <= self._max_level]

    # ------------------------------------------------------------------
    # Progression
    # ------------------------------------------------------------------

    def complete_node(self, node_id: str) -> dict:
        """Mark a node as completed and unlock the next one.

        Returns a result dict with badge, reward, and next node info.
        """
        node = self._nodes.get(node_id)
        if node is None:
            return {"error": f"Node '{node_id}' not found."}
        if node.status == NodeStatus.LOCKED:
            return {"error": f"Node '{node_id}' is locked.  Complete prior levels first."}

        node.status = NodeStatus.COMPLETED

        # Unlock next node if within tier limits
        next_node = self.get_node_by_level(node.level + 1)
        next_unlocked = False
        if next_node and next_node.level <= self._max_level:
            next_node.status = NodeStatus.UNLOCKED
            next_unlocked = True

        return {
            "completed_node": node_id,
            "badge_earned": node.badge,
            "reward": node.reward_description,
            "token_discount_pct": node.token_discount_pct,
            "next_node_unlocked": next_unlocked,
            "next_node_id": next_node.node_id if next_node else None,
        }

    def start_node(self, node_id: str) -> dict:
        """Mark a node as in-progress."""
        node = self._nodes.get(node_id)
        if node is None:
            return {"error": f"Node '{node_id}' not found."}
        if node.status == NodeStatus.LOCKED:
            return {"error": f"Node '{node_id}' is locked."}
        node.status = NodeStatus.IN_PROGRESS
        return {"node_id": node_id, "status": node.status.value}

    def get_current_discount(self) -> float:
        """Return the highest token discount earned from completed nodes."""
        completed = [
            n.token_discount_pct
            for n in self._nodes.values()
            if n.status == NodeStatus.COMPLETED
        ]
        return max(completed, default=0.0)

    def get_progress_summary(self) -> dict:
        """Return a summary of skill tree progress."""
        nodes = self.list_all_nodes()
        completed = [n for n in nodes if n.status == NodeStatus.COMPLETED]
        in_progress = [n for n in nodes if n.status == NodeStatus.IN_PROGRESS]
        unlocked = [n for n in nodes if n.status == NodeStatus.UNLOCKED]
        return {
            "total_nodes": len(nodes),
            "completed": len(completed),
            "in_progress": len(in_progress),
            "unlocked_ready": len(unlocked),
            "locked": len(nodes) - len(completed) - len(in_progress) - len(unlocked),
            "current_discount_pct": self.get_current_discount(),
            "badges_earned": [n.badge for n in completed],
        }
