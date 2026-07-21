"""Adapter that projects legacy workflow payloads into canonical ontology contracts."""

from __future__ import annotations

from typing import Any, Dict

from ontology.registry.object_registry import canonical_id


class WorkflowOntologyAdapter:
    """Maps legacy workflow JSON to ontology-native workflow objects."""

    def project(self, workflow_json: Dict[str, Any]) -> Dict[str, Any]:
        workflow_id = workflow_json.get("id") or canonical_id("Workflow", workflow_json.get("name", "unknown"))
        bot_target = workflow_json.get("bot", "bot.unknown")
        return {
            "id": workflow_id if workflow_id.startswith("workflow.") else f"workflow.{workflow_id}",
            "type": "Workflow",
            "version": "1.0",
            "name": workflow_json.get("name", workflow_id),
            "state": workflow_json.get("status", "unknown"),
            "actions": list(workflow_json.get("steps", [])),
            "relationships": [{"type": "EXECUTES", "target": bot_target}],
            "metadata": {
                "source": "legacy_workflows_json",
                "legacy_id": workflow_json.get("id", ""),
            },
        }
