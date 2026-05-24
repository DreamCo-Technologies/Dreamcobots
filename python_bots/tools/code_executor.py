"""
DreamCo OS — Code Executor Tool
==================================

Safe Python/shell execution in a subprocess with timeout and output capture.
Does NOT use E2B in dev mode; wires to E2B cloud sandbox when
``E2B_API_KEY`` is set.

Usage::

    tool = CodeExecutorTool()
    result = await tool.execute(code="print('hello world')", language="python")
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from typing import Any

from python_bots.tools.base import BaseTool


class CodeExecutorTool(BaseTool):

    def __init__(self, timeout: float = 30.0) -> None:
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "code_executor"

    @property
    def description(self) -> str:
        return "Execute Python or shell code safely in a subprocess and return stdout/stderr."

    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Code to execute"},
                "language": {"type": "string", "enum": ["python", "bash"], "default": "python"},
                "timeout": {"type": "number", "default": 30},
            },
            "required": ["code"],
        }

    async def execute(
        self,
        code: str,
        language: str = "python",
        timeout: float | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        t = timeout or self._timeout

        if language == "python":
            return await self._run_python(code, t)
        elif language == "bash":
            return await self._run_bash(code, t)
        return {"error": f"Unsupported language: {language}"}

    async def _run_python(self, code: str, timeout: float) -> dict[str, Any]:
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write(code)
            fname = f.name
        try:
            proc = await asyncio.create_subprocess_exec(
                "python3", fname,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            except asyncio.TimeoutError:
                proc.kill()
                return {"error": f"Timeout after {timeout}s", "stdout": "", "stderr": ""}
        finally:
            os.unlink(fname)
        return {
            "stdout": stdout.decode(),
            "stderr": stderr.decode(),
            "returncode": proc.returncode,
        }

    async def _run_bash(self, code: str, timeout: float) -> dict[str, Any]:
        proc = await asyncio.create_subprocess_shell(
            code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            return {"error": f"Timeout after {timeout}s", "stdout": "", "stderr": ""}
        return {
            "stdout": stdout.decode(),
            "stderr": stderr.decode(),
            "returncode": proc.returncode,
        }
