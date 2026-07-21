"""
DreamCo Resource Manager — Tool execution layer for AI agents.

Provides the action tools that DreamCo agents use to take real-world actions
after the AI model produces a response.  Each tool is a callable that
accepts a payload dict and returns a result.

Built-in tools
--------------
  email    — Send transactional email (SMTP stub; replace with SendGrid etc.)
  crm      — Persist a lead or contact record to CRM
  payment  — Process a subscription or one-time payment
  data     — Fetch external data from a configured source

Usage
-----
    from tools.resource_manager import ResourceManager

    resources = ResourceManager()
    resources.use("email", {"email": "client@example.com", "subject": "Hello"})

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# ResourceManager
# ---------------------------------------------------------------------------

class ResourceManager:
    """Tool execution layer — performs real-world actions on behalf of agents.

    Parameters
    ----------
    extra_tools : dict[str, callable] | None
        Additional tools to register beyond the built-in set.  Each value
        must be callable with a single ``payload`` dict argument.
    """

    def __init__(self, extra_tools: dict | None = None) -> None:
        self.tools: dict[str, object] = {
            "email":   self.send_email,
            "crm":     self.save_crm,
            "payment": self.process_payment,
            "data":    self.fetch_data,
        }
        if extra_tools:
            self.tools.update(extra_tools)

    # ------------------------------------------------------------------
    # Dispatcher
    # ------------------------------------------------------------------

    def use(self, tool: str, payload: dict) -> object:
        """Execute *tool* with *payload*.

        Parameters
        ----------
        tool : str
            Tool name key (e.g. ``"email"``).
        payload : dict
            Arbitrary parameters for the tool.

        Returns
        -------
        object
            Tool result, or ``None`` if the tool is not found.
        """
        action = self.tools.get(tool)
        if action is None:
            return None
        return action(payload)  # type: ignore[operator]

    # ------------------------------------------------------------------
    # Built-in tools (stubs — replace with real integrations)
    # ------------------------------------------------------------------

    def send_email(self, payload: dict) -> dict:
        """Send a transactional email.

        Expected payload keys: ``email``, ``subject`` (optional), ``body`` (optional).

        Returns
        -------
        dict
            ``{"tool": "email", "status": "sent", "recipient": str}``
        """
        recipient = payload.get("email", "unknown")
        subject = payload.get("subject", "(no subject)")
        return {"tool": "email", "status": "sent", "recipient": recipient, "subject": subject}

    def save_crm(self, payload: dict) -> dict:
        """Persist a contact or lead record to CRM.

        Expected payload keys: any contact/lead fields.

        Returns
        -------
        dict
            ``{"tool": "crm", "status": "saved", "record": dict}``
        """
        return {"tool": "crm", "status": "saved", "record": payload}

    def process_payment(self, payload: dict) -> dict:
        """Process a payment or subscription charge.

        Expected payload keys: ``email``, ``amount`` (optional), ``plan`` (optional).

        Returns
        -------
        dict
            ``{"tool": "payment", "status": "processed", "email": str, "amount": float}``
        """
        email = payload.get("email", "unknown")
        amount = float(payload.get("amount", 0.0))
        return {"tool": "payment", "status": "processed", "email": email, "amount": amount}

    def fetch_data(self, payload: dict) -> dict:
        """Fetch external data from a configured source.

        Expected payload keys: ``source`` (optional), ``query`` (optional).

        Returns
        -------
        dict
            ``{"tool": "data", "status": "fetched", "source": str, "data": dict}``
        """
        source = payload.get("source", "default")
        query = payload.get("query", "")
        return {
            "tool": "data",
            "status": "fetched",
            "source": source,
            "query": query,
            "data": {"result": "sample_data"},
        }

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def list_tools(self) -> list[str]:
        """Return the names of all registered tools."""
        return list(self.tools.keys())

    def register_tool(self, name: str, handler: object) -> None:
        """Register a new tool at runtime.

        Parameters
        ----------
        name : str
            Tool key used in :meth:`use`.
        handler : callable
            Callable accepting a single payload dict.
        """
        self.tools[name] = handler

    def get_summary(self) -> dict:
        """Return a summary of registered tools."""
        return {"total_tools": len(self.tools), "tools": self.list_tools()}
