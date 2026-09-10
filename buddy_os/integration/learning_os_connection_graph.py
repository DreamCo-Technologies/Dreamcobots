"""Runtime discovery and routing over Buddy's generated connection graph."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class BuddyConnectionGraph:
    def __init__(self, payload: dict[str, Any], repository_root: Path | None = None):
        self.payload = payload
        self.repository_root = repository_root
        self.nodes = {node["id"]: node for node in payload.get("nodes", [])}
        self.edges = payload.get("edges", [])
        if payload.get("root_node") not in self.nodes:
            raise ValueError("Connection graph is missing its Buddy root node")

    @classmethod
    def load(cls, path: Path, repository_root: Path | None = None) -> "BuddyConnectionGraph":
        return cls(json.loads(path.read_text(encoding="utf-8")), repository_root)

    def discover(self, category: str, *, runtime_only: bool = False) -> list[dict[str, Any]]:
        rows = [node for node in self.nodes.values() if category in node.get("categories", [])]
        if runtime_only:
            rows = [node for node in rows if node.get("readiness") == "runtime_verified"]
        return sorted(rows, key=lambda node: (node["kind"], node["name"], node["id"]))

    def route(self, category: str, *, require_runtime: bool = False) -> dict[str, Any]:
        candidates = self.discover(category, runtime_only=require_runtime)
        if not candidates:
            qualifier = " runtime-verified" if require_runtime else ""
            raise LookupError(f"No{qualifier} Buddy connection for category: {category}")
        priority = {"repository_verified": 0, "runtime_verified": 0, "source_verified": 1, "credentials_required": 2}
        return min(candidates, key=lambda node: (priority.get(node["readiness"], 9), node["name"]))

    def validate(self) -> list[str]:
        errors: list[str] = []
        linked = {edge["to"] for edge in self.edges if edge.get("from") == self.payload["root_node"]}
        for node_id, node in self.nodes.items():
            if node_id != self.payload["root_node"] and node_id not in linked:
                errors.append(f"unlinked node: {node_id}")
            source = node.get("source_path")
            if self.repository_root and node.get("kind") != "external_resource" and source:
                if not (self.repository_root / source).exists():
                    errors.append(f"missing source: {source}")
            if node.get("kind") == "external_resource" and node.get("status") == "connected":
                if node.get("readiness") != "runtime_verified" or not node.get("evidence"):
                    errors.append(f"external connection lacks runtime evidence: {node_id}")
        return errors
