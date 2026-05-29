"""
BuddyAI — Bot Settings

Provides :class:`BotSettings`, a self-contained settings store that any bot
can embed to:

* Manage persistent key/value configuration.
* Register and invoke custom navigation buttons beyond the 25 standard ones.
* Expose a settings summary for the dashboard.

Usage::

    from BuddyAI.settings import BotSettings

    class MyBot(BaseBot, NavigationMixin):
        def __init__(self):
            super().__init__()
            self.settings = BotSettings(bot_name=self.name)
            self.settings.set("theme", "dark")
            self.settings.add_custom_button(
                button_id="my_report",
                label="My Report",
                handler=lambda ctx: {"report": "..."},
                icon="📄",
            )

    bot = MyBot()
    bot.settings.get("theme")               # → "dark"
    bot.settings.invoke_button("my_report") # → {"report": "..."}
    bot.settings.list_custom_buttons()      # → [{"id": ..., "label": ..., "icon": ...}]
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable


class BotSettings:
    """Per-bot settings store with custom button registry.

    Parameters
    ----------
    bot_name : str
        Name of the owning bot (used in log/error messages).
    defaults : dict, optional
        Initial key/value settings to pre-populate.
    """

    def __init__(self, bot_name: str = "UnknownBot", defaults: dict | None = None) -> None:
        self._bot_name = bot_name
        self._settings: dict[str, Any] = dict(defaults or {})
        self._custom_buttons: dict[str, dict] = {}
        self._change_log: list[dict] = []

    # ------------------------------------------------------------------
    # Settings CRUD
    # ------------------------------------------------------------------

    def set(self, key: str, value: Any) -> None:
        """Store *value* under *key*.

        Parameters
        ----------
        key : str
            Setting name (e.g. ``"theme"``).
        value : Any
            Setting value.
        """
        old = self._settings.get(key)
        self._settings[key] = value
        self._change_log.append({
            "key": key,
            "old": old,
            "new": value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def get(self, key: str, default: Any = None) -> Any:
        """Return the value for *key*, or *default* if not set.

        Parameters
        ----------
        key : str
            Setting name.
        default : Any
            Fallback value when the key is absent.
        """
        return self._settings.get(key, default)

    def delete(self, key: str) -> bool:
        """Remove *key* from the settings store.

        Returns
        -------
        bool
            ``True`` if the key existed and was removed, ``False`` otherwise.
        """
        if key in self._settings:
            del self._settings[key]
            self._change_log.append({
                "key": key,
                "old": None,
                "new": None,
                "action": "delete",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            return True
        return False

    def all_settings(self) -> dict:
        """Return a copy of all current key/value settings."""
        return dict(self._settings)

    def change_log(self) -> list[dict]:
        """Return the full history of setting changes."""
        return list(self._change_log)

    # ------------------------------------------------------------------
    # Custom button registry
    # ------------------------------------------------------------------

    def add_custom_button(
        self,
        button_id: str,
        label: str,
        handler: Callable[[dict], Any],
        icon: str = "🔧",
        description: str = "",
    ) -> None:
        """Register a custom navigation button with an action handler.

        Parameters
        ----------
        button_id : str
            Unique identifier for this button (must not clash with standard
            nav buttons).
        label : str
            Human-readable button label shown in the UI.
        handler : callable
            ``handler(context: dict) -> Any`` called when the button is
            invoked.
        icon : str
            Emoji or icon string for the button.
        description : str
            Optional description shown in tooltips / help.
        """
        self._custom_buttons[button_id] = {
            "id": button_id,
            "label": label,
            "icon": icon,
            "description": description,
            "handler": handler,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def remove_custom_button(self, button_id: str) -> bool:
        """Remove a previously registered custom button.

        Returns
        -------
        bool
            ``True`` if the button existed and was removed.
        """
        if button_id in self._custom_buttons:
            del self._custom_buttons[button_id]
            return True
        return False

    def list_custom_buttons(self) -> list[dict]:
        """Return metadata for all custom buttons (without handlers)."""
        return [
            {k: v for k, v in btn.items() if k != "handler"}
            for btn in self._custom_buttons.values()
        ]

    def invoke_button(self, button_id: str, context: dict | None = None) -> Any:
        """Invoke the handler for a custom button.

        Parameters
        ----------
        button_id : str
            Id of the custom button to invoke.
        context : dict, optional
            Payload forwarded to the handler.

        Returns
        -------
        Any
            Whatever the handler returns.

        Raises
        ------
        KeyError
            If *button_id* is not registered.
        """
        if button_id not in self._custom_buttons:
            raise KeyError(
                f"[{self._bot_name}] Custom button '{button_id}' is not registered. "
                f"Available: {sorted(self._custom_buttons.keys())}"
            )
        handler = self._custom_buttons[button_id]["handler"]
        return handler(context or {})

    # ------------------------------------------------------------------
    # Summary / serialisation
    # ------------------------------------------------------------------

    def summary(self) -> dict:
        """Return a full settings and button summary dict."""
        return {
            "bot": self._bot_name,
            "settings": self.all_settings(),
            "custom_buttons": self.list_custom_buttons(),
            "total_changes": len(self._change_log),
            "snapshot_at": datetime.now(timezone.utc).isoformat(),
        }
