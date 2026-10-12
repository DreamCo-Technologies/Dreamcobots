"""Shared runtime for compiled Markdown bots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BotResult:
    status: str
    bot_id: str
    data: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    next_tasks: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None

    def as_dict(self) -> dict[str, Any]:
        payload = {
            "status": self.status,
            "bot_id": self.bot_id,
            "data": self.data,
            "metrics": self.metrics,
            "next_tasks": self.next_tasks,
        }
        if self.error:
            payload["error"] = self.error
        return payload


class CompiledBot:
    slug = "compiled-bot"
    display_name = "Compiled Bot"
    division = "CommandCore"
    tier = "free"
    mission = "Sandbox compiled bot"
    capabilities: list[str] = []
    autonomy_ceiling = "plan_only"
    source = ""

    def success(self, data: dict[str, Any] | None = None, metrics: dict[str, Any] | None = None, next_tasks: list | None = None) -> BotResult:
        return BotResult(
            status="success",
            bot_id=self.slug,
            data=data or {},
            metrics=metrics or {},
            next_tasks=next_tasks or [],
        )

    def execute(self, task: dict | None = None) -> BotResult:
        raise NotImplementedError

    def run(self, task: dict | None = None) -> dict[str, Any]:
        result = self.execute(task)
        return result.as_dict()
