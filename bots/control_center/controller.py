"""
DreamCo Control Center — Controller

Wraps and extends ControlCenter with dynamic bot discovery, task queue,
inter-bot messaging, and a real-time automation execution loop.

GLOBAL AI SOURCES FLOW compliant.
"""

from __future__ import annotations

import importlib
import logging
import os
import pkgutil
import sys
import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)
from bots.control_center.control_center import ControlCenter

logger = logging.getLogger(__name__)


class TaskMessage:
    """Lightweight message passed between bots via the Controller."""

    def __init__(self, sender: str, recipient: str, action: str, payload: dict | None = None) -> None:
        self.sender = sender
        self.recipient = recipient
        self.action = action
        self.payload: dict = payload or {}
        self.created_at: str = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "action": self.action,
            "payload": self.payload,
            "created_at": self.created_at,
        }


class Controller:
    """
    DreamCo Mission Control — orchestrates every registered bot.

    Features
    --------
    * Dynamic bot discovery and registration from the ``bots/`` package.
    * Task queue with routing to individual bots or broadcast to all.
    * Inter-bot messaging via :meth:`send_message`.
    * Automation loop: runs registered bots on a configurable interval.
    """

    def __init__(self) -> None:
        self._cc = ControlCenter()
        self._task_queue: List[TaskMessage] = []
        self._message_log: List[dict] = []
        self._running: bool = False
        self._loop_count: int = 0
        self._auto_registered: List[str] = []

    # ------------------------------------------------------------------
    # Bot registration
    # ------------------------------------------------------------------

    def register_bot(self, name: str, bot_instance: Any) -> None:
        """Register *bot_instance* under *name* with the control center."""
        self._cc.register_bot(name, bot_instance)
        logger.info("Registered bot: %s", name)

    def auto_discover_bots(self, bots_package_path: str | None = None) -> List[str]:
        """
        Walk the ``bots/`` directory and register any bot instance found.

        For each sub-package that exposes a ``run()`` method on its main
        class (or exposes a ``BotGeneratorBot``, ``AILearningSystem``, etc.),
        the instance is registered automatically.

        Parameters
        ----------
        bots_package_path : str, optional
            Filesystem path to the ``bots/`` directory.  Defaults to the
            sibling ``bots/`` directory relative to this file.

        Returns
        -------
        List[str]
            Names of bots successfully auto-registered.
        """
        if bots_package_path is None:
            bots_package_path = os.path.join(os.path.dirname(__file__), "..")

        registered: List[str] = []

        # Ensure repo root is on sys.path so relative imports resolve.
        repo_root = os.path.abspath(os.path.join(bots_package_path, ".."))
        if repo_root not in sys.path:
            sys.path.insert(0, repo_root)

        for entry in sorted(os.listdir(bots_package_path)):
            full_path = os.path.join(bots_package_path, entry)
            if not os.path.isdir(full_path):
                continue
            if entry.startswith(("_", ".")):
                continue
            # Look for a Python module inside the sub-package with the same name
            candidate_module = os.path.join(full_path, f"{entry}.py")
            if not os.path.isfile(candidate_module):
                continue
            try:
                mod = importlib.import_module(f"bots.{entry}.{entry}")
            except Exception:
                continue
            # Find the first class in the module that has a run() method
            for attr_name in dir(mod):
                cls = getattr(mod, attr_name)
                if not isinstance(cls, type):
                    continue
                if not hasattr(cls, "run"):
                    continue
                try:
                    instance = cls()
                    self._cc.register_bot(entry, instance)
                    registered.append(entry)
                    logger.info("Auto-registered bot: %s (%s)", entry, attr_name)
                except Exception:
                    pass
                break  # only register one class per sub-package

        self._auto_registered = registered
        return registered

    # ------------------------------------------------------------------
    # Task management
    # ------------------------------------------------------------------

    def assign_task(self, recipient: str, action: str, payload: dict | None = None, sender: str = "controller") -> TaskMessage:
        """Create a task message and add it to the queue."""
        msg = TaskMessage(sender=sender, recipient=recipient, action=action, payload=payload)
        self._task_queue.append(msg)
        logger.debug("Task queued: %s → %s [%s]", sender, recipient, action)
        return msg

    def broadcast_task(self, action: str, payload: dict | None = None) -> List[TaskMessage]:
        """Broadcast a task to ALL registered bots."""
        msgs = []
        status = self._cc.get_status()
        for bot_name in status.get("bots", {}):
            msgs.append(self.assign_task(recipient=bot_name, action=action, payload=payload))
        return msgs

    def process_tasks(self) -> List[dict]:
        """
        Drain the task queue, dispatching each message to its target bot.

        Returns
        -------
        List[dict]
            Results for each processed task.
        """
        results = []
        while self._task_queue:
            msg = self._task_queue.pop(0)
            result = self._dispatch(msg)
            self._message_log.append({**msg.to_dict(), "result": result})
            results.append(result)
        return results

    def _dispatch(self, msg: TaskMessage) -> dict:
        """Route a :class:`TaskMessage` to the target bot."""
        status = self._cc.get_status()
        bots_meta = status.get("bots", {})
        if msg.recipient not in bots_meta:
            return {"task": msg.to_dict(), "status": "error", "error": f"Bot '{msg.recipient}' not registered"}
        # Access the internal bot registry
        bot_entry = self._cc._bots.get(msg.recipient, {})
        bot = bot_entry.get("instance")
        if bot is None:
            return {"task": msg.to_dict(), "status": "error", "error": "Bot instance missing"}
        try:
            if msg.action == "run" and hasattr(bot, "run"):
                output = bot.run()
            elif msg.action == "status" and hasattr(bot, "get_status"):
                output = bot.get_status()
            elif hasattr(bot, msg.action):
                fn = getattr(bot, msg.action)
                output = fn(**msg.payload) if callable(fn) else fn
            else:
                output = f"Action '{msg.action}' not supported"
            return {"task": msg.to_dict(), "status": "ok", "output": output}
        except Exception as exc:
            return {"task": msg.to_dict(), "status": "error", "error": str(exc)}

    # ------------------------------------------------------------------
    # Inter-bot messaging
    # ------------------------------------------------------------------

    def send_message(self, sender: str, recipient: str, action: str, payload: dict | None = None) -> dict:
        """
        Send a message from one bot to another, executing immediately.

        Returns
        -------
        dict
            Dispatch result.
        """
        msg = TaskMessage(sender=sender, recipient=recipient, action=action, payload=payload)
        result = self._dispatch(msg)
        self._message_log.append({**msg.to_dict(), "result": result})
        return result

    def get_message_log(self) -> List[dict]:
        """Return a copy of the full inter-bot message log."""
        return list(self._message_log)

    # ------------------------------------------------------------------
    # Automation loop
    # ------------------------------------------------------------------

    def run_loop(self, iterations: int = 1, interval_seconds: float = 0.0) -> List[dict]:
        """
        Execute the automation loop *iterations* times.

        Each iteration:
        1. Runs all registered bots via :meth:`ControlCenter.run_all`.
        2. Processes any pending tasks.

        Parameters
        ----------
        iterations : int
            Number of loop cycles to execute.  ``0`` means run indefinitely
            (stop by calling :meth:`stop`).
        interval_seconds : float
            Seconds to sleep between iterations (0 = as fast as possible).

        Returns
        -------
        List[dict]
            Aggregated results from every iteration.
        """
        self._running = True
        all_results: List[dict] = []
        cycle = 0
        try:
            while self._running:
                self._loop_count += 1
                bot_results = self._cc.run_all()
                task_results = self.process_tasks()
                all_results.append({
                    "cycle": self._loop_count,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "bot_results": bot_results,
                    "task_results": task_results,
                })
                cycle += 1
                if iterations > 0 and cycle >= iterations:
                    break
                if interval_seconds > 0:
                    time.sleep(interval_seconds)
        finally:
            self._running = False
        return all_results

    def stop(self) -> None:
        """Signal the automation loop to stop after the current iteration."""
        self._running = False

    # ------------------------------------------------------------------
    # Status & dashboard
    # ------------------------------------------------------------------

    def get_status(self) -> dict:
        """Return combined Controller + ControlCenter status."""
        cc_status = self._cc.get_status()
        return {
            "controller": {
                "loop_count": self._loop_count,
                "running": self._running,
                "pending_tasks": len(self._task_queue),
                "messages_logged": len(self._message_log),
                "auto_registered_bots": self._auto_registered,
            },
            "control_center": cc_status,
        }

    def get_dashboard(self) -> dict:
        """Return the full monitoring dashboard."""
        return self._cc.get_monitoring_dashboard()
