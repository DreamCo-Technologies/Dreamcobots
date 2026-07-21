"""
DreamCo BaseBot — Strict execution contract for all DreamCo bots.

Every bot in the DreamCo ecosystem must extend ``BaseBot`` and implement
the ``run()`` method that accepts a task dict and returns a structured
result dict.

Usage
-----
    from core.base_bot import BaseBot

    class MyBot(BaseBot):
        bot_id = "my_bot"
        name = "My Bot"
        category = "custom"

        def run(self, task: dict) -> dict:
            ...
            return self._success(data={"result": "value"})
"""

from __future__ import annotations

import abc
import time
from typing import Any, Dict, List, Optional

from core.self_evolution import LLMProvider, SelfEvolutionEngine


# ---------------------------------------------------------------------------
# Required result shape
# ---------------------------------------------------------------------------

RESULT_STATUS_SUCCESS = "success"
RESULT_STATUS_FAILED = "failed"


class BaseBotError(Exception):
    """Raised when a bot violates its execution contract."""


# ---------------------------------------------------------------------------
# BaseBot abstract class
# ---------------------------------------------------------------------------


class BaseBot(abc.ABC):
    """
    Abstract base class that all DreamCo bots must extend.

    Subclasses **must** define the three class-level attributes and implement
    the ``run()`` method.

    Class attributes
    ----------------
    bot_id : str
        Unique machine-readable identifier (e.g. ``"real_estate_bot"``).
    name : str
        Human-readable display name (e.g. ``"Real Estate Bot"``).
    category : str
        Functional category (e.g. ``"real_estate"``, ``"finance"``, ``"ai"``).
    """

    # Subclasses MUST override these
    bot_id: str = ""
    name: str = ""
    category: str = ""

    def __init__(self, name: str = "", description: str = "", version: str = "1.0.0", **kwargs) -> None:
        if name:
            self.__class__.name = name
        self.description = description
        self.version = version
        self.revenue = 0.0
        self._logs: List[str] = []
        self._running = False
        # Every bot is a self-evolving system — wire up the evolution engine.
        self.self_evolution: SelfEvolutionEngine = SelfEvolutionEngine(
            bot_id=self.bot_id or self.__class__.__name__,
            category=self.category or "general",
        )

    def start(self) -> None:
        """Start the bot."""
        self._running = True
        print(f"[{self.__class__.__name__}] Starting...")

    def stop(self) -> None:
        """Stop the bot."""
        self._running = False

    def log(self, message: str) -> None:
        """Log a message."""
        self._logs.append(message)

    # ------------------------------------------------------------------
    # Execution contract
    # ------------------------------------------------------------------

    @abc.abstractmethod
    def run(self, task: dict) -> dict:
        """
        Execute the bot for the given *task*.

        Parameters
        ----------
        task : dict
            Arbitrary task payload supplied by the caller or orchestrator.

        Returns
        -------
        dict
            Must conform to the standard result shape::

                {
                    "status":     "success" | "failed",
                    "bot_id":     str,
                    "data":       dict,
                    "metrics":    dict,
                    "next_tasks": list,
                }

        Raises
        ------
        NotImplementedError
            If the subclass does not implement this method.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement run(task)"
        )

    # ------------------------------------------------------------------
    # Helpers for building compliant result dicts
    # ------------------------------------------------------------------

    def _success(
        self,
        data: Dict[str, Any] | None = None,
        metrics: Dict[str, Any] | None = None,
        next_tasks: List[dict] | None = None,
    ) -> dict:
        """Return a success-shaped result dict and record the run."""
        self.self_evolution.record_run(success=True, revenue=float(metrics.get("revenue", 0)) if metrics else 0.0)
        return {
            "status": RESULT_STATUS_SUCCESS,
            "bot_id": self.bot_id,
            "data": data or {},
            "metrics": metrics or {},
            "next_tasks": next_tasks or [],
        }

    def _failure(
        self,
        error: str,
        data: Dict[str, Any] | None = None,
        metrics: Dict[str, Any] | None = None,
        next_tasks: List[dict] | None = None,
    ) -> dict:
        """Return a failure-shaped result dict and record the run."""
        self.self_evolution.record_run(success=False)
        return {
            "status": RESULT_STATUS_FAILED,
            "bot_id": self.bot_id,
            "error": error,
            "data": data or {},
            "metrics": metrics or {},
            "next_tasks": next_tasks or [],
        }

    # ------------------------------------------------------------------
    # Self-evolution interface
    # ------------------------------------------------------------------

    def evolve(self) -> dict:
        """
        Trigger one evolution cycle on this bot.

        Analyses performance since the last cycle, mutates strategy
        parameters, and promotes the bot to the next LLM phase when
        readiness thresholds are met.

        Returns
        -------
        dict
            Serialisable summary of the evolution record produced.
        """
        from core.self_evolution import EvolutionRecord
        record: EvolutionRecord = self.self_evolution.evolve()
        return {
            "cycle": record.cycle,
            "phase": record.phase.value,
            "llm_provider": record.llm_provider.value,
            "fitness_improvement": record.fitness_improvement,
            "strategy_delta": record.strategy_delta,
            "metadata": record.metadata,
        }

    def evolution_status(self) -> dict:
        """
        Return a comprehensive, serialisable status of this bot's
        self-evolution state (phase, LLM provider, performance, strategy).
        """
        return self.self_evolution.evolution_status()

    def set_llm_provider(self, provider: LLMProvider) -> None:
        """
        Explicitly set the LLM provider for this bot.

        Parameters
        ----------
        provider : LLMProvider
            The desired LLM provider (e.g. ``LLMProvider.MISTRAL``).
        """
        self.self_evolution.llm_provider = provider

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @staticmethod
    def validate_result(result: dict) -> bool:
        """
        Return ``True`` if *result* conforms to the standard result shape.

        Parameters
        ----------
        result : dict
            The dict returned by ``run()``.

        Returns
        -------
        bool
        """
        required_keys = {"status", "bot_id", "data", "metrics", "next_tasks"}
        if not required_keys.issubset(result.keys()):
            return False
        if result["status"] not in (RESULT_STATUS_SUCCESS, RESULT_STATUS_FAILED):
            return False
        return True

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"{self.__class__.__name__}("
            f"bot_id={self.bot_id!r}, "
            f"name={self.name!r}, "
            f"category={self.category!r})"
        )
