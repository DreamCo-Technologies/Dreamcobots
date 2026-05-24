"""
DreamCo OS — Code Graph Agent
================================

Builds a knowledge graph of the entire repository:
files → classes → functions → imports → dependencies.
Used by the self-healing pipeline to diagnose CI failures.
"""

from __future__ import annotations

import ast
import os
from pathlib import Path
from typing import Any

from python_bots.core.base_bot import DreamCoBot


class CodeGraphAgent(DreamCoBot):
    """Builds a structural knowledge graph of the codebase."""

    async def run(self) -> dict[str, Any]:
        graph = await self._build_graph()
        await self.memory.store_doc("code_graph", str(graph)[:10000])
        await self.memory.event("code_graph_built", {"files": graph["stats"]["files"]})
        return graph

    async def analyze(self) -> dict[str, Any]:
        return {"agent": "code_graph"}

    async def monetize(self) -> dict[str, Any]:
        return {"value": "code_intelligence"}

    async def report(self) -> dict[str, Any]:
        return {"agent": "code_graph"}

    async def _build_graph(self) -> dict[str, Any]:
        repo_root = Path(os.getenv("GITHUB_WORKSPACE", "."))
        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, str]] = []
        file_count = 0

        for py_file in repo_root.rglob("*.py"):
            if ".git" in py_file.parts or "__pycache__" in py_file.parts:
                continue
            try:
                source = py_file.read_text(errors="replace")
                tree = ast.parse(source)
                rel_path = str(py_file.relative_to(repo_root))
                nodes.append({"id": rel_path, "type": "file"})
                file_count += 1

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_id = f"{rel_path}::{node.name}"
                        nodes.append({"id": class_id, "type": "class", "name": node.name})
                        edges.append({"from": rel_path, "to": class_id, "rel": "defines"})
                    elif isinstance(node, (ast.Import, ast.ImportFrom)):
                        mod = getattr(node, "module", None) or (node.names[0].name if node.names else "")
                        if mod:
                            edges.append({"from": rel_path, "to": mod, "rel": "imports"})
            except Exception:  # noqa: BLE001
                continue

        return {
            "nodes": nodes[:500],
            "edges": edges[:1000],
            "stats": {"files": file_count, "nodes": len(nodes), "edges": len(edges)},
        }
