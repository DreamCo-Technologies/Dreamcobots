"""
DreamCo OS — BaseTool
========================

Every shared tool in ``python_bots/tools/`` must inherit from ``BaseTool``
and implement ``schema()`` so it can be auto-registered as an MCP tool.
"""

from __future__ import annotations

import abc
from typing import Any


class BaseTool(abc.ABC):
    """Abstract base for all DreamCo shared tools."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Unique tool identifier (snake_case)."""

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """One-sentence description for MCP/LLM tool registration."""

    @abc.abstractmethod
    def schema(self) -> dict[str, Any]:
        """Return a JSON-schema-compatible dict describing the tool's inputs."""

    @abc.abstractmethod
    async def execute(self, **kwargs: Any) -> Any:
        """Execute the tool with the supplied keyword arguments."""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"
