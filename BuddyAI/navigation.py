"""
BuddyAI — Universal Navigation System

Every DreamCo bot inherits NavigationMixin, which exposes all 25 standard
navigation actions as callable methods.  Each action returns a structured
navigation response that the dashboard and chat interface can render.

Standard navigation buttons (all bots):
    Chat · Empire HQ · Divisions · Bot Fleet · Deal Analyzer ·
    Formula Vault · Learning Matrix · AI Leaders · AI Models Hub ·
    AI Ecosystem · Orchestration · Marketplace · Crypto · Payments ·
    Biz Launch · Code Lab · Loans & Deals · Debug Intel · Revenue ·
    Pricing · Connections · Time Capsule · Cost Tracking · Autonomy ·
    Recent Chats
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# Navigation action registry
# ---------------------------------------------------------------------------

NAV_BUTTONS: list[dict] = [
    {"id": "chat",           "label": "Chat",           "icon": "💬", "route": "/chat"},
    {"id": "empire_hq",      "label": "Empire HQ",      "icon": "🏰", "route": "/empire-hq"},
    {"id": "divisions",      "label": "Divisions",      "icon": "🏢", "route": "/divisions"},
    {"id": "bot_fleet",      "label": "Bot Fleet",      "icon": "🤖", "route": "/bot-fleet"},
    {"id": "deal_analyzer",  "label": "Deal Analyzer",  "icon": "📊", "route": "/deal-analyzer"},
    {"id": "formula_vault",  "label": "Formula Vault",  "icon": "🔮", "route": "/formula-vault"},
    {"id": "learning_matrix","label": "Learning Matrix","icon": "🧠", "route": "/learning-matrix"},
    {"id": "ai_leaders",     "label": "AI Leaders",     "icon": "👑", "route": "/ai-leaders"},
    {"id": "ai_models_hub",  "label": "AI Models Hub",  "icon": "🌐", "route": "/ai-models-hub"},
    {"id": "ai_ecosystem",   "label": "AI Ecosystem",   "icon": "🌿", "route": "/ai-ecosystem"},
    {"id": "orchestration",  "label": "Orchestration",  "icon": "🎼", "route": "/orchestration"},
    {"id": "marketplace",    "label": "Marketplace",    "icon": "🛒", "route": "/marketplace"},
    {"id": "crypto",         "label": "Crypto",         "icon": "₿",  "route": "/crypto"},
    {"id": "payments",       "label": "Payments",       "icon": "💳", "route": "/payments"},
    {"id": "biz_launch",     "label": "Biz Launch",     "icon": "🚀", "route": "/biz-launch"},
    {"id": "code_lab",       "label": "Code Lab",       "icon": "🧪", "route": "/code-lab"},
    {"id": "loans_deals",    "label": "Loans & Deals",  "icon": "🤝", "route": "/loans-deals"},
    {"id": "debug_intel",    "label": "Debug Intel",    "icon": "🔍", "route": "/debug-intel"},
    {"id": "revenue",        "label": "Revenue",        "icon": "💰", "route": "/revenue"},
    {"id": "pricing",        "label": "Pricing",        "icon": "🏷️", "route": "/pricing"},
    {"id": "connections",    "label": "Connections",    "icon": "🔗", "route": "/connections"},
    {"id": "time_capsule",   "label": "Time Capsule",   "icon": "⏳", "route": "/time-capsule"},
    {"id": "cost_tracking",  "label": "Cost Tracking",  "icon": "📉", "route": "/cost-tracking"},
    {"id": "autonomy",       "label": "Autonomy",       "icon": "⚡", "route": "/autonomy"},
    {"id": "recent_chats",   "label": "Recent Chats",   "icon": "🕐", "route": "/recent-chats"},
]

_NAV_BY_ID: dict[str, dict] = {btn["id"]: btn for btn in NAV_BUTTONS}


def _make_nav_response(button_id: str, context: dict | None = None) -> dict:
    """Return a standard navigation action response."""
    btn = _NAV_BY_ID.get(button_id, {})
    return {
        "nav_action": button_id,
        "label": btn.get("label", button_id),
        "route": btn.get("route", f"/{button_id}"),
        "icon": btn.get("icon", ""),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": context or {},
        "success": True,
    }


# ---------------------------------------------------------------------------
# Mixin
# ---------------------------------------------------------------------------

class NavigationMixin:
    """Adds all 25 universal navigation button actions to any bot class.

    Mix into any bot that inherits :class:`~BuddyAI.base_bot.BaseBot` to gain
    every standard navigation action as a method and the ``nav_buttons()``
    introspection helper.

    Usage::

        class MyBot(BaseBot, NavigationMixin):
            ...

        bot = MyBot()
        bot.nav_chat()          # → navigation response dict
        bot.nav_buttons()       # → list of all button definitions
        bot.navigate("crypto")  # → navigation response dict (by id)
    """

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def nav_buttons(self) -> list[dict]:
        """Return all registered navigation button definitions."""
        return list(NAV_BUTTONS)

    def navigate(self, button_id: str, context: dict | None = None) -> dict:
        """Dispatch a navigation action by *button_id*.

        Parameters
        ----------
        button_id : str
            One of the standard nav button ids (e.g. ``"chat"``, ``"crypto"``).
        context : dict, optional
            Extra payload to attach to the navigation response.

        Returns
        -------
        dict
            Navigation response including route, label, icon and timestamp.
        """
        if button_id not in _NAV_BY_ID:
            return {
                "nav_action": button_id,
                "success": False,
                "error": f"Unknown navigation button: '{button_id}'. "
                         f"Valid ids: {sorted(_NAV_BY_ID.keys())}",
            }
        return _make_nav_response(button_id, context)

    # ------------------------------------------------------------------
    # Per-button shortcut methods
    # ------------------------------------------------------------------

    def nav_chat(self, context: dict | None = None) -> dict:
        """Navigate to the Chat view."""
        return _make_nav_response("chat", context)

    def nav_empire_hq(self, context: dict | None = None) -> dict:
        """Navigate to Empire HQ."""
        return _make_nav_response("empire_hq", context)

    def nav_divisions(self, context: dict | None = None) -> dict:
        """Navigate to the Divisions dashboard."""
        return _make_nav_response("divisions", context)

    def nav_bot_fleet(self, context: dict | None = None) -> dict:
        """Navigate to the Bot Fleet manager."""
        return _make_nav_response("bot_fleet", context)

    def nav_deal_analyzer(self, context: dict | None = None) -> dict:
        """Navigate to the Deal Analyzer."""
        return _make_nav_response("deal_analyzer", context)

    def nav_formula_vault(self, context: dict | None = None) -> dict:
        """Navigate to the Formula Vault."""
        return _make_nav_response("formula_vault", context)

    def nav_learning_matrix(self, context: dict | None = None) -> dict:
        """Navigate to the Learning Matrix."""
        return _make_nav_response("learning_matrix", context)

    def nav_ai_leaders(self, context: dict | None = None) -> dict:
        """Navigate to the AI Leaders board."""
        return _make_nav_response("ai_leaders", context)

    def nav_ai_models_hub(self, context: dict | None = None) -> dict:
        """Navigate to the AI Models Hub."""
        return _make_nav_response("ai_models_hub", context)

    def nav_ai_ecosystem(self, context: dict | None = None) -> dict:
        """Navigate to the AI Ecosystem view."""
        return _make_nav_response("ai_ecosystem", context)

    def nav_orchestration(self, context: dict | None = None) -> dict:
        """Navigate to the Orchestration panel."""
        return _make_nav_response("orchestration", context)

    def nav_marketplace(self, context: dict | None = None) -> dict:
        """Navigate to the Marketplace."""
        return _make_nav_response("marketplace", context)

    def nav_crypto(self, context: dict | None = None) -> dict:
        """Navigate to the Crypto panel."""
        return _make_nav_response("crypto", context)

    def nav_payments(self, context: dict | None = None) -> dict:
        """Navigate to the Payments panel."""
        return _make_nav_response("payments", context)

    def nav_biz_launch(self, context: dict | None = None) -> dict:
        """Navigate to the Biz Launch wizard."""
        return _make_nav_response("biz_launch", context)

    def nav_code_lab(self, context: dict | None = None) -> dict:
        """Navigate to the Code Lab."""
        return _make_nav_response("code_lab", context)

    def nav_loans_deals(self, context: dict | None = None) -> dict:
        """Navigate to the Loans & Deals board."""
        return _make_nav_response("loans_deals", context)

    def nav_debug_intel(self, context: dict | None = None) -> dict:
        """Navigate to the Debug Intel panel."""
        return _make_nav_response("debug_intel", context)

    def nav_revenue(self, context: dict | None = None) -> dict:
        """Navigate to the Revenue dashboard."""
        return _make_nav_response("revenue", context)

    def nav_pricing(self, context: dict | None = None) -> dict:
        """Navigate to the Pricing panel."""
        return _make_nav_response("pricing", context)

    def nav_connections(self, context: dict | None = None) -> dict:
        """Navigate to the Connections manager."""
        return _make_nav_response("connections", context)

    def nav_time_capsule(self, context: dict | None = None) -> dict:
        """Navigate to the Time Capsule archive."""
        return _make_nav_response("time_capsule", context)

    def nav_cost_tracking(self, context: dict | None = None) -> dict:
        """Navigate to the Cost Tracking panel."""
        return _make_nav_response("cost_tracking", context)

    def nav_autonomy(self, context: dict | None = None) -> dict:
        """Navigate to the Autonomy controls."""
        return _make_nav_response("autonomy", context)

    def nav_recent_chats(self, context: dict | None = None) -> dict:
        """Navigate to Recent Chats."""
        return _make_nav_response("recent_chats", context)
