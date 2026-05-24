"""
DreamCo OS — Sandboxed File System Tool
==========================================

Safe file read/write with path validation.  All paths are resolved relative
to a configurable root directory; traversal attacks are blocked.

Usage::

    tool = FileSystemTool(root="/tmp/dreamco_workspace")
    await tool.execute(operation="write", path="output.txt", content="hello")
    content = await tool.execute(operation="read", path="output.txt")
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from python_bots.tools.base import BaseTool


class FileSystemTool(BaseTool):

    def __init__(self, root: str = "/tmp/dreamco_workspace") -> None:
        self._root = Path(root).resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    @property
    def name(self) -> str:
        return "file_system"

    @property
    def description(self) -> str:
        return "Read or write files in the sandboxed workspace directory."

    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "enum": ["read", "write", "list", "delete"]},
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["operation", "path"],
        }

    async def execute(
        self,
        operation: str,
        path: str,
        content: str = "",
        **kwargs: Any,
    ) -> Any:
        safe_path = self._safe_path(path)
        if operation == "read":
            return safe_path.read_text() if safe_path.exists() else None
        elif operation == "write":
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            safe_path.write_text(content)
            return {"written": str(safe_path), "bytes": len(content)}
        elif operation == "list":
            target = self._safe_path(path) if path else self._root
            return [str(p.relative_to(self._root)) for p in target.iterdir()] if target.is_dir() else []
        elif operation == "delete":
            if safe_path.exists():
                safe_path.unlink()
                return {"deleted": str(safe_path)}
            return {"error": "File not found"}
        raise ValueError(f"Unknown operation: {operation}")

    def _safe_path(self, path: str) -> Path:
        resolved = (self._root / path).resolve()
        if not str(resolved).startswith(str(self._root)):
            raise PermissionError(f"Path traversal blocked: {path}")
        return resolved
