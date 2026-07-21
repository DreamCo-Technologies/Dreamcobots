"""
Drag-Drop Builder — visual, no-code bot builder for the DreamCo Bot Wars Bot.

Enables non-developers to compose bots from reusable components without
writing code.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import uuid
from enum import Enum

from framework import GlobalAISourcesFlow  # noqa: F401


class ComponentType(Enum):
    TRIGGER = "trigger"
    ACTION = "action"
    CONDITION = "condition"
    OUTPUT = "output"
    API_CALL = "api_call"
    DATA_FETCH = "data_fetch"
    TRANSFORMER = "transformer"
    SCHEDULER = "scheduler"


BOT_COMPONENT_TYPES = [ct.value for ct in ComponentType]


class DragDropBuilderError(Exception):
    """Raised for invalid operations within the DragDropBuilder."""


class DragDropBuilder:
    """Visual, no-code bot builder that lets users compose bots from components.

    All data is stored in-memory; intended for integration with a persistence
    layer in production.
    """

    def __init__(self) -> None:
        self._projects: dict = {}
        self._components: dict = {}
        self._connections: dict = {}

    # ------------------------------------------------------------------
    # Project management
    # ------------------------------------------------------------------

    def create_bot_project(
        self,
        user_id: str,
        bot_name: str,
        description: str,
    ) -> dict:
        """Create a new bot-builder project.

        Returns
        -------
        dict  Project record.
        """
        if not bot_name or not bot_name.strip():
            raise DragDropBuilderError("Bot name must not be empty.")

        project_id = str(uuid.uuid4())
        record = {
            "id": project_id,
            "user_id": user_id,
            "bot_name": bot_name.strip(),
            "description": description,
            "components": [],
            "connections": [],
            "status": "draft",
        }
        self._projects[project_id] = record
        return record

    # ------------------------------------------------------------------
    # Component management
    # ------------------------------------------------------------------

    def add_component(
        self,
        project_id: str,
        component_type: str,
        config: dict,
    ) -> dict:
        """Add a component to a bot project.

        Parameters
        ----------
        component_type: One of BOT_COMPONENT_TYPES.
        config:         Component-specific configuration dictionary.

        Returns
        -------
        dict  Component record.
        """
        project = self._get_project(project_id)
        if component_type not in BOT_COMPONENT_TYPES:
            raise DragDropBuilderError(
                f"Invalid component type '{component_type}'. "
                f"Valid types: {BOT_COMPONENT_TYPES}"
            )

        component_id = str(uuid.uuid4())
        record = {
            "id": component_id,
            "project_id": project_id,
            "component_type": component_type,
            "config": config,
        }
        self._components[component_id] = record
        project["components"].append(component_id)
        return record

    def list_components(self, project_id: str) -> list:
        """Return all components belonging to a project."""
        project = self._get_project(project_id)
        return [
            self._components[cid]
            for cid in project["components"]
            if cid in self._components
        ]

    # ------------------------------------------------------------------
    # Connections
    # ------------------------------------------------------------------

    def connect_components(
        self,
        project_id: str,
        from_component_id: str,
        to_component_id: str,
    ) -> dict:
        """Connect two components within a project (directed edge).

        Returns
        -------
        dict  Connection record.
        """
        project = self._get_project(project_id)

        if from_component_id not in project["components"]:
            raise DragDropBuilderError(
                f"Component '{from_component_id}' not found in project '{project_id}'."
            )
        if to_component_id not in project["components"]:
            raise DragDropBuilderError(
                f"Component '{to_component_id}' not found in project '{project_id}'."
            )
        if from_component_id == to_component_id:
            raise DragDropBuilderError("Cannot connect a component to itself.")

        connection_id = str(uuid.uuid4())
        record = {
            "id": connection_id,
            "project_id": project_id,
            "from_component_id": from_component_id,
            "to_component_id": to_component_id,
        }
        self._connections[connection_id] = record
        project["connections"].append(connection_id)
        return record

    # ------------------------------------------------------------------
    # Validation & export
    # ------------------------------------------------------------------

    def validate_bot(self, project_id: str) -> dict:
        """Validate a bot project for completeness and correctness.

        Returns
        -------
        dict  ``{"valid": bool, "issues": list[str]}``
        """
        project = self._get_project(project_id)
        issues: list = []

        components = self.list_components(project_id)
        if not components:
            issues.append("Bot has no components. Add at least one component.")

        types_present = {c["component_type"] for c in components}
        if ComponentType.TRIGGER.value not in types_present:
            issues.append(
                "Bot is missing a TRIGGER component. "
                "Every bot needs at least one trigger."
            )

        has_action = ComponentType.ACTION.value in types_present
        has_output = ComponentType.OUTPUT.value in types_present
        if not has_action and not has_output:
            issues.append(
                "Bot should have at least one ACTION or OUTPUT component."
            )

        return {"valid": len(issues) == 0, "issues": issues}

    def export_bot(self, project_id: str) -> dict:
        """Export the bot project as a marketplace-ready definition.

        Returns
        -------
        dict  Bot definition including components and wiring.
        """
        project = self._get_project(project_id)
        validation = self.validate_bot(project_id)
        return {
            "project_id": project_id,
            "bot_name": project["bot_name"],
            "description": project["description"],
            "user_id": project["user_id"],
            "components": self.list_components(project_id),
            "connections": [
                self._connections[cid]
                for cid in project["connections"]
                if cid in self._connections
            ],
            "valid": validation["valid"],
            "validation_issues": validation["issues"],
            "status": "exported" if validation["valid"] else "draft",
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_project(self, project_id: str) -> dict:
        if project_id not in self._projects:
            raise DragDropBuilderError(
                f"Project '{project_id}' not found."
            )
        return self._projects[project_id]
