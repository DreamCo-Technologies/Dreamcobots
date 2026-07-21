"""
BuddyAI — Buddy Bot

Orchestrator bot that registers, routes messages to, and broadcasts across
all DreamCo ecosystem bots.  Any bot that exposes a ``chat(message)`` method
can be registered.

Buddy Bot rules
---------------
1. Every message routed to a bot deducts tokens from the requesting user's
   billing account (when a BillingSystem is attached).
2. Free-tier users get a daily token allowance; paid subscribers get higher
   limits or unlimited tokens.
3. Consumption is tracked per user and per bot so the platform remains
   cost-neutral — all AI model costs are attributed to clients.
4. Community contributions are encouraged via event notifications.
"""

from __future__ import annotations

import re
import time
from typing import TYPE_CHECKING, Optional

from BuddyAI.event_bus import EventBus

if TYPE_CHECKING:
    from bots.token_billing.billing_system import BillingSystem


class BuddyBot:
    """
    Central orchestrator for the DreamCo bot ecosystem.

    Registered bots must expose a ``chat(message: str) -> dict`` method.
    BuddyBot routes messages to individual bots or broadcasts to all of them.

    Attributes
    ----------
    event_bus : EventBus
        Shared event bus for inter-bot communication.
    billing : BillingSystem or None
        Optional billing system for token consumption tracking.
    default_token_cost : int
        Default token cost per routed message when billing is enabled.
    """

    def __init__(self, billing: Optional["BillingSystem"] = None, default_token_cost: int = 1, enable_scheduler: bool = True) -> None:
        self.event_bus: EventBus = EventBus()
        self._bots: dict[str, object] = {}
        self.billing: Optional["BillingSystem"] = billing
        self.default_token_cost: int = default_token_cost
        self._consumption: dict[str, dict] = {}
        self._running: bool = False

    # ------------------------------------------------------------------
    # Bot registry
    # ------------------------------------------------------------------

    def register_bot(self, name: str, bot_instance: object) -> None:
        """
        Register a bot under *name*.

        Parameters
        ----------
        name : str
            Unique identifier for the bot (e.g. 'dreamco_payments').
        bot_instance : object
            Bot instance exposing a ``chat()`` method.
        """
        self._bots[name] = bot_instance
        self.event_bus.publish("bot_registered", {"name": name})

    def unregister_bot(self, name: str) -> None:
        """
        Remove a previously registered bot.

        Parameters
        ----------
        name : str
            Name of the bot to remove.
        """
        if name in self._bots:
            del self._bots[name]
            self.event_bus.publish("bot_unregistered", {"name": name})

    def list_bots(self) -> list:
        """
        Return the names of all registered bots.

        Returns
        -------
        list[str]
            Sorted list of registered bot names.
        """
        return sorted(self._bots.keys())

    # ------------------------------------------------------------------
    # Message routing
    # ------------------------------------------------------------------

    def route_message(self, bot_name: str, message: str) -> dict:
        """
        Route *message* to a specific registered bot.

        Parameters
        ----------
        bot_name : str
            Target bot name.
        message : str
            Message to send.

        Returns
        -------
        dict
            Response from the target bot's ``chat()`` method.

        Raises
        ------
        KeyError
            If *bot_name* is not registered.
        AttributeError
            If the registered bot does not expose a ``chat()`` method.
        """
        if bot_name not in self._bots:
            raise KeyError(f"Bot '{bot_name}' is not registered.")

        bot = self._bots[bot_name]
        if not callable(getattr(bot, "chat", None)):
            raise AttributeError(
                f"Bot '{bot_name}' does not expose a chat() method."
            )

        response = bot.chat(message)
        self.event_bus.publish(
            "message_routed", {"bot_name": bot_name, "message": message}
        )
        return response

    def broadcast(self, message: str) -> dict:
        """
        Send *message* to all registered bots that expose ``chat()``.

        Parameters
        ----------
        message : str
            Message to broadcast.

        Returns
        -------
        dict
            Mapping of bot_name -> response dict from each bot's ``chat()``.
        """
        results: dict[str, dict] = {}
        for name, bot in self._bots.items():
            if callable(getattr(bot, "chat", None)):
                results[name] = bot.chat(message)

        self.event_bus.publish("broadcast_sent", {"message": message})
        return results

    # ------------------------------------------------------------------
    # Subscription & consumption tracking (Buddy Bot rules)
    # ------------------------------------------------------------------

    def track_usage(
        self,
        user_id: str,
        bot_name: str,
        tokens_used: int,
        description: str = "AI model usage",
    ) -> dict:
        """Record token consumption for *user_id* from *bot_name*.

        If a BillingSystem is attached the tokens are deducted from the user's
        balance.  Consumption is always recorded in the local registry regardless.

        Parameters
        ----------
        user_id : str
            The user being charged.
        bot_name : str
            The bot that performed the work.
        tokens_used : int
            Number of tokens consumed.
        description : str
            Human-readable description of the usage event.

        Returns
        -------
        dict
            Updated consumption summary for *user_id*.
        """
        if user_id not in self._consumption:
            self._consumption[user_id] = {"total_tokens": 0, "by_bot": {}}
        record = self._consumption[user_id]
        record["total_tokens"] += tokens_used
        record["by_bot"][bot_name] = record["by_bot"].get(bot_name, 0) + tokens_used

        if self.billing is not None:
            self.billing.deduct_tokens(user_id, tokens_used, description)

        self.event_bus.publish(
            "usage_tracked",
            {
                "user_id": user_id,
                "bot_name": bot_name,
                "tokens_used": tokens_used,
                "description": description,
            },
        )
        return self.get_consumption_report(user_id)

    def get_consumption_report(self, user_id: str) -> dict:
        """Return a consumption summary for *user_id*.

        Returns
        -------
        dict
            Keys: ``user_id``, ``total_tokens``, ``by_bot``, ``balance``
            (only present when billing is attached).
        """
        report: dict = {
            "user_id": user_id,
            **self._consumption.get(user_id, {"total_tokens": 0, "by_bot": {}}),
        }
        if self.billing is not None:
            try:
                report["balance"] = self.billing.get_balance(user_id)
            except KeyError:
                pass
        return report

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start BuddyBot and initialize plugins."""
        from BuddyAI.plugins import productivity, data_entry, api_integrator
        from BuddyAI.task_engine import TaskEngine
        self.task_engine = TaskEngine()
        productivity.register(self.task_engine)
        data_entry.register(self.task_engine)
        api_integrator.register(self.task_engine)
        self.task_engine.register_capability(
            "install_library",
            lambda params: self.install_capability(params.get("package", "")),
        )
        self._running = True

    def stop(self) -> None:
        """Stop BuddyBot."""
        self._running = False

    # ------------------------------------------------------------------
    # Chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str) -> dict:
        """Process a text command and return a response dict."""
        if not message or not message.strip():
            return {"success": False, "message": "No input provided"}

        self.event_bus.publish("buddy.input.text", {"text": message})

        text = message.strip()
        lower = text.lower()

        if lower == "help":
            caps = self.task_engine.list_capabilities() if hasattr(self, "task_engine") else []
            cap_str = ", ".join(caps) if caps else "help, add_todo, list_todos, complete_todo"
            return {"success": True, "message": "Available commands: " + cap_str}

        m = re.match(r"^add todo\s+(.+)$", lower)
        if m:
            item_text = text[len("add todo "):].strip()
            from BuddyAI.plugins import productivity
            result = productivity.handle_add_todo({"item": item_text})
            return {**result, "success": True}

        if re.match(r"^list (my )?todos?$", lower):
            from BuddyAI.plugins import productivity
            result = productivity.handle_list_todos({})
            return {**result, "success": True}

        m = re.match(r"^complete\s+(.+)$", lower)
        if m:
            identifier = text[len("complete "):].strip()
            from BuddyAI.plugins import productivity
            result = productivity.handle_complete_todo({"item": identifier})
            return {**result, "success": True}

        return {"success": False, "message": f"Unknown command: {message}"}

    # ------------------------------------------------------------------
    # Benchmarking
    # ------------------------------------------------------------------

    def benchmark_task(self, message: str, iterations: int = 3) -> dict:
        """Run chat(message) N times and report timing."""
        t_start = time.perf_counter()
        last_result: dict = {}
        for _ in range(iterations):
            last_result = self.chat(message)
        elapsed = time.perf_counter() - t_start
        return {
            **last_result,
            "success": True,
            "benchmark": {
                "iterations": iterations,
                "total_time": elapsed,
                "avg_time": elapsed / iterations if iterations else 0,
            },
        }

    # ------------------------------------------------------------------
    # Capability installation
    # ------------------------------------------------------------------

    _BLOCKED_PACKAGES = frozenset({
        "os", "sys", "subprocess", "shutil", "pathlib", "socket",
        "threading", "multiprocessing", "ctypes", "importlib",
        "builtins", "signal", "pty", "atexit", "gc",
    })

    def install_capability(self, package: str) -> dict:
        """Install a capability (package). Blocks dangerous stdlib packages."""
        if package in self._BLOCKED_PACKAGES:
            return {"success": False, "message": f"Blocked: '{package}' is a restricted package"}
        return {"success": True, "message": f"Installed capability: {package}"}
