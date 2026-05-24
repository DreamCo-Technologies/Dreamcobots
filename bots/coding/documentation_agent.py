"""
DreamCo OS — Documentation Agent
====================================

Keeps README, ARCHITECTURE.md, and inline docstrings in sync with code.
Scans for undocumented public symbols and generates draft documentation.
"""

from __future__ import annotations

import ast
import os
from pathlib import Path
from typing import Any

from python_bots.core.base_bot import DreamCoBot


class DocumentationAgent(DreamCoBot):
    """Audits and improves repository documentation."""

    async def run(self) -> dict[str, Any]:
        gaps = await self._find_documentation_gaps()
        await self.memory.event("docs_audited", {"gaps": len(gaps)})
        return {"documentation_gaps": gaps, "total_gaps": len(gaps)}

    async def analyze(self) -> dict[str, Any]:
        return {"agent": "documentation"}

    async def monetize(self) -> dict[str, Any]:
        return {"value": "documentation_quality"}

    async def report(self) -> dict[str, Any]:
        return {"agent": "documentation"}

    async def _find_documentation_gaps(self) -> list[dict[str, Any]]:
        gaps: list[dict[str, Any]] = []
        repo_root = Path(os.getenv("GITHUB_WORKSPACE", "."))

        for py_file in list(repo_root.rglob("*.py"))[:100]:
            if ".git" in py_file.parts or "__pycache__" in py_file.parts:
                continue
            try:
                source = py_file.read_text(errors="replace")
                tree = ast.parse(source)
                rel_path = str(py_file.relative_to(repo_root))
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        if not (ast.get_docstring(node) or node.name.startswith("_")):
                            gaps.append({
                                "file": rel_path,
                                "type": type(node).__name__,
                                "name": node.name,
                                "line": node.lineno,
                            })
            except Exception:  # noqa: BLE001
                continue
        return gaps[:50]
