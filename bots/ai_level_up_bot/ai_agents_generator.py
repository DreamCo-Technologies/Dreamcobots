"""
AI Agents Generator — custom bot builder for the DreamCo AI Level-Up Bot.

Users define a purpose for their agent and select AI tools from the database.
The generator assembles a structured agent specification.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from framework import GlobalAISourcesFlow  # noqa: F401


class AgentStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


@dataclass
class AgentSpec:
    """Specification for a user-created custom AI agent."""

    agent_id: str
    name: str
    purpose: str
    tools: List[str]
    automation_hooks: List[str]
    created_by: str
    status: AgentStatus = AgentStatus.DRAFT
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "purpose": self.purpose,
            "tools": self.tools,
            "automation_hooks": self.automation_hooks,
            "created_by": self.created_by,
            "status": self.status.value,
            "description": self.description,
        }


# ---------------------------------------------------------------------------
# Pre-built agent templates
# ---------------------------------------------------------------------------

_AGENT_TEMPLATES: dict = {
    "real_estate_marketing": {
        "name": "Real Estate Marketing Agent",
        "purpose": "Automate real estate marketing using AI tools",
        "tools": ["ChatGPT", "DALL-E", "ElevenLabs", "HubSpot CRM"],
        "automation_hooks": ["Email drip campaigns", "Social media scheduling", "Lead scoring"],
        "description": "Generates listings, creates ad images, records voiceovers, and manages leads.",
    },
    "content_creator": {
        "name": "Content Creator Agent",
        "purpose": "Produce blog posts, social content, and videos at scale",
        "tools": ["Jasper AI", "Midjourney", "Runway", "ElevenLabs"],
        "automation_hooks": ["Blog scheduling", "Social posting", "Newsletter generation"],
        "description": "Writes, illustrates, and publishes content across all channels.",
    },
    "customer_support": {
        "name": "Customer Support Agent",
        "purpose": "Handle customer inquiries using AI chatbots",
        "tools": ["ChatGPT", "Zendesk AI", "Speechify"],
        "automation_hooks": ["Ticket routing", "FAQ answering", "Escalation alerts"],
        "description": "24/7 AI-powered support agent with escalation to human agents.",
    },
    "sales_automation": {
        "name": "Sales Automation Agent",
        "purpose": "Qualify leads and automate sales outreach",
        "tools": ["Conversica", "ChatGPT", "Zapier", "Salesforce"],
        "automation_hooks": ["Lead qualification", "Email outreach", "CRM updates"],
        "description": "AI agent that engages prospects, qualifies leads, and books demos.",
    },
    "ai_research_assistant": {
        "name": "AI Research Assistant",
        "purpose": "Gather, summarise, and report on AI research papers",
        "tools": ["Elicit", "ChatGPT", "Notion AI", "Otter.ai"],
        "automation_hooks": ["Literature search", "Summarisation", "Report generation"],
        "description": "Continuously monitors new research and delivers structured summaries.",
    },
}


class AIAgentsGenerator:
    """Generates and manages custom AI agent specifications.

    Parameters
    ----------
    max_agents : int | None
        Maximum number of agents the current tier allows (None = unlimited).
    created_by : str
        Identifier for the user or system creating agents.
    """

    def __init__(
        self,
        max_agents: Optional[int] = None,
        created_by: str = "user",
    ) -> None:
        self._max_agents = max_agents
        self._created_by = created_by
        self._agents: dict = {}
        self._counter: int = 0

    # ------------------------------------------------------------------
    # Template access
    # ------------------------------------------------------------------

    def list_templates(self) -> List[str]:
        """Return names of available agent templates."""
        return list(_AGENT_TEMPLATES.keys())

    def get_template(self, template_key: str) -> Optional[dict]:
        """Return a template spec dict by key."""
        return _AGENT_TEMPLATES.get(template_key)

    # ------------------------------------------------------------------
    # Agent creation
    # ------------------------------------------------------------------

    def create_agent(
        self,
        name: str,
        purpose: str,
        tools: List[str],
        automation_hooks: Optional[List[str]] = None,
        description: str = "",
    ) -> dict:
        """Create a new custom agent specification.

        Returns the serialised AgentSpec dict or an error dict if the
        tier limit has been reached.
        """
        if self._max_agents is not None and len(self._agents) >= self._max_agents:
            return {
                "error": "Agent limit reached for current tier.",
                "max_agents": self._max_agents,
            }

        self._counter += 1
        agent_id = f"AGENT-{self._counter:04d}"
        spec = AgentSpec(
            agent_id=agent_id,
            name=name,
            purpose=purpose,
            tools=tools,
            automation_hooks=automation_hooks or [],
            created_by=self._created_by,
            description=description,
        )
        self._agents[agent_id] = spec
        return spec.to_dict()

    def create_from_template(self, template_key: str) -> dict:
        """Create an agent from a pre-built template."""
        template = _AGENT_TEMPLATES.get(template_key)
        if template is None:
            return {"error": f"Template '{template_key}' not found."}
        return self.create_agent(
            name=template["name"],
            purpose=template["purpose"],
            tools=template["tools"],
            automation_hooks=template.get("automation_hooks", []),
            description=template.get("description", ""),
        )

    # ------------------------------------------------------------------
    # Agent management
    # ------------------------------------------------------------------

    def get_agent(self, agent_id: str) -> Optional[AgentSpec]:
        """Return an agent by ID."""
        return self._agents.get(agent_id)

    def list_agents(self) -> List[dict]:
        """Return all agent specs as dicts."""
        return [a.to_dict() for a in self._agents.values()]

    def activate_agent(self, agent_id: str) -> dict:
        """Set an agent's status to ACTIVE."""
        agent = self._agents.get(agent_id)
        if agent is None:
            return {"error": f"Agent '{agent_id}' not found."}
        agent.status = AgentStatus.ACTIVE
        return {"agent_id": agent_id, "status": agent.status.value}

    def pause_agent(self, agent_id: str) -> dict:
        """Set an agent's status to PAUSED."""
        agent = self._agents.get(agent_id)
        if agent is None:
            return {"error": f"Agent '{agent_id}' not found."}
        agent.status = AgentStatus.PAUSED
        return {"agent_id": agent_id, "status": agent.status.value}

    def count_agents(self) -> int:
        """Return the total number of agents created."""
        return len(self._agents)
