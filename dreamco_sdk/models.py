"""DreamCo SDK — Pydantic models."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel


class RunRequest(BaseModel):
    bot_name: str
    payload: dict[str, Any] = {}
    priority: int = 5
    requires_approval: bool = False


class BotStatus(BaseModel):
    bot_id: str
    name: str
    state: str
    error_count: int = 0
    total_runs: int = 0
    last_run_at: float | None = None


class BotResult(BaseModel):
    bot_id: str
    name: str
    success: bool
    error: str = ""
    result: dict[str, Any] = {}
    duration_s: float = 0.0
