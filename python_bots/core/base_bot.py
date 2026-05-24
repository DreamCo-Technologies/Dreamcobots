"""
DreamCo OS — DreamCoBot Base Class
=====================================

``DreamCoBot`` is the single base class every bot in the DreamCo ecosystem
must inherit from.  It wires together:

* Lifecycle state machine (IDLE → RUNNING → IDLE / QUARANTINED / STOPPED)
* Async-first execution via ``asyncio``
* Four-tier memory (Redis, vector DB, Postgres, behavioral graph)
* OpenTelemetry tracing
* Structured logging with ``structlog``
* Four canonical methods: ``run()``, ``analyze()``, ``monetize()``, ``report()``
* ``health_check()`` and auto-registration with the orchestrator

Usage::

    from python_bots.core import DreamCoBot

    class MyBot(DreamCoBot):
        async def run(self) -> dict:
            self.log.info("running")
            result = await self.analyze()
            await self.memory.event("task_completed", result)
            return result

        async def analyze(self) -> dict:
            return {"status": "ok"}

        async def monetize(self) -> dict:
            return {"revenue_usd": 0.0}

        async def report(self) -> dict:
            return {"summary": "all good"}
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
import uuid
from abc import ABC, abstractmethod
from typing import Any

try:
    import structlog  # type: ignore

    _logger_factory = structlog.get_logger
except ImportError:
    _logger_factory = logging.getLogger  # type: ignore

from python_bots.core.lifecycle import BotState, assert_transition, IllegalStateTransitionError
from python_bots.core.memory.client import MemoryClient

try:
    from opentelemetry import trace  # type: ignore

    _tracer = trace.get_tracer("dreamco.bots")
    _OTEL_AVAILABLE = True
except ImportError:
    _tracer = None
    _OTEL_AVAILABLE = False


class DreamCoBot(ABC):
    """Abstract base class for every DreamCo OS bot.

    Parameters
    ----------
    name:
        Human-readable bot identifier used in logs, metrics, and the registry.
    config:
        Arbitrary configuration dict injected at construction time.
    memory_client:
        Pre-built ``MemoryClient`` instance.  When *None*, a default client
        keyed to *name* is created automatically.
    event_bus:
        Optional external event bus (must expose ``publish(topic, data)``).
        Uses an in-process no-op bus when *None*.
    capabilities:
        Whitelist of tool names this bot is allowed to use.  Empty means
        all tools are permitted.
    max_retries:
        Number of consecutive failures before the circuit breaker fires.
    execution_timeout:
        Maximum wall-clock seconds allowed for a single ``run()`` call.
    """

    def __init__(
        self,
        name: str,
        config: dict[str, Any] | None = None,
        memory_client: MemoryClient | None = None,
        event_bus: Any = None,
        capabilities: list[str] | None = None,
        max_retries: int = 3,
        execution_timeout: float = 300.0,
    ) -> None:
        self.name = name
        self.bot_id = f"{name}_{uuid.uuid4().hex[:8]}"
        self.config: dict[str, Any] = config or {}
        self.memory = memory_client or MemoryClient(bot_id=self.bot_id)
        self.event_bus = event_bus
        self.capabilities: list[str] = capabilities or []
        self.max_retries = max_retries
        self.execution_timeout = execution_timeout

        self._state = BotState.IDLE
        self._error_count = 0
        self._total_runs = 0
        self._last_run_at: float | None = None

        self.log = _logger_factory(self.__class__.__name__)
        self._tracer = _tracer

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    @property
    def state(self) -> BotState:
        return self._state

    def _transition(self, next_state: BotState) -> None:
        assert_transition(self._state, next_state)
        self._state = next_state

    def stop(self) -> None:
        """Gracefully stop the bot (IDLE or RUNNING → STOPPED)."""
        if self._state not in (BotState.STOPPED,):
            try:
                self._transition(BotState.STOPPED)
            except IllegalStateTransitionError:
                self._state = BotState.STOPPED

    def release_quarantine(self) -> None:
        """Release the bot from quarantine back to IDLE (operator action)."""
        if self._state == BotState.QUARANTINED:
            self._state = BotState.IDLE
            self._error_count = 0

    def restart(self) -> None:
        """Restart a STOPPED bot (STOPPED → IDLE)."""
        self._transition(BotState.IDLE)
        self._error_count = 0

    # ------------------------------------------------------------------
    # Canonical methods (must be implemented by every subclass)
    # ------------------------------------------------------------------

    @abstractmethod
    async def run(self) -> dict[str, Any]:
        """Execute the bot's primary task.  Must be async."""

    @abstractmethod
    async def analyze(self) -> dict[str, Any]:
        """Analyse the current environment / inputs and return structured findings."""

    @abstractmethod
    async def monetize(self) -> dict[str, Any]:
        """Return monetization outcome (revenue, leads, conversions, etc.)."""

    @abstractmethod
    async def report(self) -> dict[str, Any]:
        """Return a human/machine-readable summary of the last run."""

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------

    def health_check(self) -> dict[str, Any]:
        """Return JSON-serialisable health status for monitoring endpoints."""
        return {
            "bot_id": self.bot_id,
            "name": self.name,
            "state": self._state.value,
            "error_count": self._error_count,
            "total_runs": self._total_runs,
            "last_run_at": self._last_run_at,
            "memory_stats": self.memory.stats(),
            "capabilities": self.capabilities,
        }

    # ------------------------------------------------------------------
    # Orchestrator registration
    # ------------------------------------------------------------------

    def register(self, orchestrator: Any) -> None:
        """Auto-register this bot with *orchestrator* on startup."""
        if hasattr(orchestrator, "register"):
            orchestrator.register(self)

    # ------------------------------------------------------------------
    # Managed execution (called by the orchestrator)
    # ------------------------------------------------------------------

    async def execute(self) -> dict[str, Any]:
        """Lifecycle-managed wrapper around ``run()``.

        Handles: state transitions, circuit breaker, timeout, tracing,
        memory recording, event bus publishing.
        """
        if self._state == BotState.STOPPED:
            return {"success": False, "error": "Bot is STOPPED", "bot_id": self.bot_id}
        if self._state == BotState.QUARANTINED:
            return {"success": False, "error": "Bot is QUARANTINED", "bot_id": self.bot_id}

        self._transition(BotState.RUNNING)
        started = time.time()
        self._last_run_at = started
        self._total_runs += 1
        error_msg = ""
        result: dict[str, Any] = {}

        # Emit start event
        self._publish("bot.run.started", {"bot_id": self.bot_id, "name": self.name})
        self.memory.event("bot.run.started", {"bot_id": self.bot_id})

        try:
            result = await asyncio.wait_for(self.run(), timeout=self.execution_timeout)
            self._error_count = 0  # reset on success
        except asyncio.TimeoutError:
            error_msg = f"Execution timed out after {self.execution_timeout}s"
            self._error_count += 1
        except Exception as exc:  # noqa: BLE001
            error_msg = str(exc)
            self._error_count += 1

        duration = time.time() - started
        success = not error_msg

        # Circuit breaker
        if self._error_count >= self.max_retries:
            self._state = BotState.QUARANTINED
            self._publish(
                "bot.quarantined",
                {"bot_id": self.bot_id, "reason": error_msg, "error_count": self._error_count},
            )
        elif success:
            self._transition(BotState.IDLE)
        else:
            self._transition(BotState.IDLE)

        # Persist run to structured memory
        try:
            self.memory.record_run(
                success=success,
                duration_s=duration,
                metadata={"error": error_msg} if error_msg else {},
            )
        except Exception:  # noqa: BLE001
            pass

        event_data = {
            "bot_id": self.bot_id,
            "name": self.name,
            "success": success,
            "error": error_msg,
            "duration_s": round(duration, 3),
        }
        self._publish("bot.run.completed", event_data)
        self.memory.event("bot.run.completed", event_data)

        return {
            "bot_id": self.bot_id,
            "name": self.name,
            "success": success,
            "error": error_msg,
            "result": result,
            "duration_s": round(duration, 3),
        }

    # ------------------------------------------------------------------
    # Tool capability check
    # ------------------------------------------------------------------

    def can_use(self, tool_name: str) -> bool:
        """Return True if this bot is allowed to use *tool_name*."""
        if not self.capabilities:
            return True  # empty whitelist = all tools allowed
        return tool_name in self.capabilities

    def assert_can_use(self, tool_name: str) -> None:
        """Raise PermissionError if this bot is not allowed to use *tool_name*."""
        if not self.can_use(tool_name):
            raise PermissionError(
                f"Bot '{self.name}' does not have capability '{tool_name}'. "
                f"Declared capabilities: {self.capabilities}"
            )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _publish(self, topic: str, data: Any = None) -> None:
        if self.event_bus is not None and hasattr(self.event_bus, "publish"):
            try:
                self.event_bus.publish(topic, data)
            except Exception:  # noqa: BLE001
                pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, state={self._state.value})"
