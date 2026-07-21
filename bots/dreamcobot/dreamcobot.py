"""
DreamCobot – integrated with the BuddyAI framework
----------------------------------------------------
DreamCobot is the primary user-facing bot in the DreamCobots ecosystem.
It connects to a :class:`~BuddyAI.buddy_bot.BuddyBot` instance and
leverages its shared authentication, event bus, knowledge base, and task
queue to deliver a cohesive collaboration experience.

Integration overview
~~~~~~~~~~~~~~~~~~~~
1. DreamCobot registers itself with BuddyBot on startup.
2. It subscribes to relevant ecosystem events (e.g. ``user.joined``).
3. It reads/writes the shared knowledge base to exchange data with peer bots.
4. It pushes and pulls tasks through the shared task queue.
5. It provides user-facing interaction methods that internally dispatch
   BuddyBot events so other bots can react.

Example::

    buddy = BuddyBot()
    dream = DreamCobot(buddy)
    dream.start()

    dream.handle_user_message("Hello!")
    dream.assign_task({"type": "goal_setting", "user": "Alex"})
"""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py

from __future__ import annotations

from typing import Any, Dict, List, Optional

from BuddyAI.buddy_bot import BuddyBot, BuddyBotError
from BuddyAI.auth import AuthError


class DreamCobotError(Exception):
    """Raised when DreamCobot encounters an unrecoverable error."""


class DreamCobot:
    """User-facing bot that integrates with the BuddyAI framework.

    Parameters
    ----------
    buddy:
        The :class:`~BuddyAI.buddy_bot.BuddyBot` hub this bot should
        connect to.
    bot_id:
        Unique identifier for this DreamCobot instance.
    """

    # Permissions requested from BuddyBot on registration.
    PERMISSIONS: List[str] = [
        "task:run",
        "task:push",
        "knowledge:read",
        "knowledge:write",
        "event:publish",
    ]

    def __init__(self, buddy: BuddyBot, bot_id: str = "dreamcobot") -> None:
        if not isinstance(buddy, BuddyBot):
            raise DreamCobotError("buddy must be a BuddyBot instance")
        self._buddy = buddy
        self._bot_id = bot_id
        self._token: Optional[str] = None
        self._running = False
        self._message_log: List[str] = []

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Register with BuddyBot and subscribe to ecosystem events.

        Raises
        ------
        DreamCobotError
            If registration fails (e.g. bot_id already in use).
        """
        if self._running:
            return
        try:
            self._token = self._buddy.register_bot(self._bot_id)
        except BuddyBotError as exc:
            raise DreamCobotError(
                f"DreamCobot could not register with BuddyBot: {exc}"
            ) from exc

        # Subscribe to events we care about.
        self._buddy.subscribe_event("user.joined", self._on_user_joined)
        self._buddy.subscribe_event("task.queued", self._on_task_queued)
        self._buddy.subscribe_event("bot.registered", self._on_bot_registered)

        self._running = True
        print(f"[{self._bot_id}] Started and connected to {self._buddy.hub_id}")

    def stop(self) -> None:
        """Unregister from BuddyBot and release resources."""
        if not self._running:
            return
        self._buddy.event_bus.unsubscribe("user.joined", self._on_user_joined)
        self._buddy.event_bus.unsubscribe("task.queued", self._on_task_queued)
        self._buddy.event_bus.unsubscribe("bot.registered", self._on_bot_registered)
        self._buddy.unregister_bot(self._bot_id)
        self._running = False
        print(f"[{self._bot_id}] Stopped")

    @property
    def is_running(self) -> bool:
        """``True`` when the bot is active and registered."""
        return self._running

    # ------------------------------------------------------------------
    # User interaction
    # ------------------------------------------------------------------

    def handle_user_message(self, message: str) -> str:
        """Process a user message and return a response.

        The message is logged and a ``user.message`` event is published
        on the shared event bus so peer bots can react.

        Parameters
        ----------
        message:
            The text message sent by the user.

        Returns
        -------
        str
            A response string.
        """
        self._require_running()
        self._message_log.append(message)
        self._buddy.publish_event("user.message", {"bot": self._bot_id, "text": message})
        response = f"[{self._bot_id}] Received: {message}"
        return response

    # ------------------------------------------------------------------
    # Task management
    # ------------------------------------------------------------------

    def assign_task(self, task: Dict[str, Any]) -> None:
        """Push *task* onto the shared BuddyBot task queue.

        Parameters
        ----------
        task:
            A dict describing the task to assign, e.g.
            ``{"type": "onboard", "user_id": 7}``.
        """
        self._require_running()
        self._buddy.push_task(task)

    def process_next_task(self) -> Optional[Dict[str, Any]]:
        """Pull and process the next task from the shared queue.

        Returns
        -------
        dict or None
            The task that was processed, or ``None`` if the queue was empty.
        """
        self._require_running()
        task = self._buddy.pop_task()
        if task is not None:
            self._buddy.publish_event(
                "task.started", {"bot": self._bot_id, "task": task}
            )
        return task

    # ------------------------------------------------------------------
    # Knowledge base helpers
    # ------------------------------------------------------------------

    def store_knowledge(self, key: str, value: Any) -> None:
        """Write *value* to the shared knowledge base under *key*."""
        self._require_running()
        self._buddy.set_knowledge(key, value)

    def retrieve_knowledge(self, key: str, default: Any = None) -> Any:
        """Read a value from the shared knowledge base."""
        self._require_running()
        return self._buddy.get_knowledge(key, default)

    # ------------------------------------------------------------------
    # Authentication helper
    # ------------------------------------------------------------------

    def verify_identity(self) -> bool:
        """Verify this bot's own token against BuddyBot.

        Returns
        -------
        bool
            ``True`` if the token is valid.

        Raises
        ------
        DreamCobotError
            If the bot is not running or token verification fails.
        """
        self._require_running()
        try:
            return self._buddy.authenticate(self._bot_id, self._token)
        except AuthError as exc:
            raise DreamCobotError(f"Identity verification failed: {exc}") from exc

    # ------------------------------------------------------------------
    # Event handlers (private)
    # ------------------------------------------------------------------

    def _on_user_joined(self, payload: Any) -> None:
        user_id = payload.get("user_id") if isinstance(payload, dict) else payload
        print(f"[{self._bot_id}] New user joined: {user_id}")

    def _on_task_queued(self, payload: Any) -> None:
        task_type = payload.get("type", "unknown") if isinstance(payload, dict) else payload
        print(f"[{self._bot_id}] Task queued: {task_type}")

    def _on_bot_registered(self, payload: Any) -> None:
        other_id = payload.get("bot_id") if isinstance(payload, dict) else payload
        if other_id != self._bot_id:
            print(f"[{self._bot_id}] Peer bot registered: {other_id}")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_running(self) -> None:
        if not self._running:
            raise DreamCobotError(
                "DreamCobot is not running. Call start() first."
            )

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    @classmethod
    def create_and_start(cls, buddy: BuddyBot, bot_id: str = "dreamcobot") -> "DreamCobot":
        """Convenience factory: create a DreamCobot, start it, and return it."""
        bot = cls(buddy, bot_id=bot_id)
        bot.start()
        return bot
