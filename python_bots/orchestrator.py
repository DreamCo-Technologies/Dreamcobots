"""
DreamCo Python Bots — Orchestrator
====================================

Coordinates a collection of ``BaseBot`` sub-bots, running them in sequence
against a shared in-process event bus and aggregating their results.

The ``PythonBotOrchestrator`` is intentionally lightweight: it does **not**
depend on Redis or any external service, making it easy to unit-test and to
embed in larger workflows.

Usage
-----
    from python_bots.orchestrator import PythonBotOrchestrator
    from python_bots.base_bot import BaseBot

    class MyBot(BaseBot):
        def run(self, event_bus):
            event_bus.publish("my_bot.done", {"revenue": 42.0})

    orch = PythonBotOrchestrator()
    orch.register(MyBot("my_bot"))
    summary = orch.run_all()
    print(summary)
"""

from __future__ import annotations

import sys
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# Ensure the repo root is on sys.path so that sibling packages are importable
# when this file is run as a script.
# ---------------------------------------------------------------------------
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from python_bots.base_bot import BaseBot  # noqa: E402

# ---------------------------------------------------------------------------
# Minimal in-process event bus (no Redis dependency)
# ---------------------------------------------------------------------------


class _InProcessEventBus:
    """Simple synchronous event bus backed by a plain list."""

    def __init__(self) -> None:
        self._events: List[Dict[str, Any]] = []

    def publish(self, topic: str, data: Any = None) -> None:
        self._events.append(
            {
                "topic": topic,
                "data": data,
                "ts": datetime.now(tz=timezone.utc).isoformat(),
            }
        )

    @property
    def events(self) -> List[Dict[str, Any]]:
        return list(self._events)


# ---------------------------------------------------------------------------
# PythonBotOrchestrator
# ---------------------------------------------------------------------------


class PythonBotOrchestrator:
    """Orchestrates a collection of ``BaseBot`` sub-bots.

    Parameters
    ----------
    learning_loop : object, optional
        An optional learning-loop integration that receives ``record_run``
        calls after each bot run.  Any object that exposes
        ``record_run(bot_name, success, revenue)`` is accepted.
    """

    def __init__(self, learning_loop: Any = None) -> None:
        self._bots: Dict[str, BaseBot] = {}
        self._run_history: List[Dict[str, Any]] = []
        self._learning_loop = learning_loop

    # ------------------------------------------------------------------
    # Bot registration
    # ------------------------------------------------------------------

    def register(self, bot: BaseBot) -> None:
        """Register *bot* with the orchestrator.

        Parameters
        ----------
        bot : BaseBot
            The bot instance to register.  Its ``name`` attribute is used
            as the unique key; registering two bots with the same name
            replaces the earlier entry.
        """
        self._bots[bot.name] = bot

    def unregister(self, bot_name: str) -> None:
        """Remove the bot identified by *bot_name*.

        Parameters
        ----------
        bot_name : str
            Name of the bot to remove.  Silently ignored if not found.
        """
        self._bots.pop(bot_name, None)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def run_bot(self, bot_name: str) -> Dict[str, Any]:
        """Run a single bot by name.

        Parameters
        ----------
        bot_name : str
            Name of the registered bot to run.

        Returns
        -------
        dict
            Result record with keys ``bot_name``, ``success``, ``error``,
            ``events``, and ``started_at`` / ``finished_at`` timestamps.
        """
        if bot_name not in self._bots:
            return {
                "bot_name": bot_name,
                "success": False,
                "error": f"Bot '{bot_name}' not found",
                "events": [],
                "started_at": datetime.now(tz=timezone.utc).isoformat(),
                "finished_at": datetime.now(tz=timezone.utc).isoformat(),
            }

        bot = self._bots[bot_name]
        event_bus = _InProcessEventBus()
        started_at = datetime.now(tz=timezone.utc).isoformat()
        error_msg: str = ""
        success = True

        try:
            bot.run(event_bus)
        except Exception as exc:  # noqa: BLE001
            success = False
            error_msg = str(exc)

        finished_at = datetime.now(tz=timezone.utc).isoformat()

        result: Dict[str, Any] = {
            "bot_name": bot_name,
            "success": success,
            "error": error_msg,
            "events": event_bus.events,
            "started_at": started_at,
            "finished_at": finished_at,
        }
        self._run_history.append(result)

        if self._learning_loop is not None:
            revenue = sum(
                e.get("data", {}).get("revenue", 0.0)
                for e in event_bus.events
                if isinstance(e.get("data"), dict)
            )
            try:
                self._learning_loop.record_run(bot_name, success, revenue)
            except Exception:  # noqa: BLE001
                pass

        return result

    def run_all(self) -> Dict[str, Any]:
        """Run all registered bots sequentially.

        Returns
        -------
        dict
            Aggregated summary with keys ``total``, ``succeeded``,
            ``failed``, ``results``, and ``ran_at``.
        """
        results: List[Dict[str, Any]] = [
            self.run_bot(name) for name in list(self._bots)
        ]
        succeeded = sum(1 for r in results if r["success"])
        return {
            "total": len(results),
            "succeeded": succeeded,
            "failed": len(results) - succeeded,
            "results": results,
            "ran_at": datetime.now(tz=timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def run_history(self) -> List[Dict[str, Any]]:
        """Return a copy of the full run history."""
        return list(self._run_history)

    def summary(self) -> Dict[str, Any]:
        """Return a snapshot summary of the orchestrator state.

        Returns
        -------
        dict
            Keys: ``registered_bots``, ``total_runs``, ``total_succeeded``,
            ``total_failed``.
        """
        total = len(self._run_history)
        succeeded = sum(1 for r in self._run_history if r["success"])
        return {
            "registered_bots": list(self._bots.keys()),
            "total_runs": total,
            "total_succeeded": succeeded,
            "total_failed": total - succeeded,
        }
