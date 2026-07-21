"""
Webhook Manager for DreamCobots ConnectionsControl.

Manages webhook registrations and event dispatching.

GLOBAL AI SOURCES FLOW
"""

from __future__ import annotations

# GLOBAL AI SOURCES FLOW

import hashlib
import hmac
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set


@dataclass
class Webhook:
    name: str
    url: str
    events: Set[str]
    secret: str = ""
    active: bool = True


@dataclass
class WebhookEvent:
    event_id: str
    name: str
    payload: dict
    timestamp: datetime = field(default_factory=datetime.utcnow)


class WebhookManager:
    """Registers webhooks and dispatches events to registered endpoints."""

    def __init__(self) -> None:
        self._webhooks: Dict[str, Webhook] = {}
        self._event_log: List[WebhookEvent] = []

    def register_webhook(
        self,
        name: str,
        url: str,
        events: List[str],
        secret: str = "",
    ) -> Webhook:
        """Register a new webhook endpoint."""
        webhook = Webhook(name=name, url=url, events=set(events), secret=secret)
        self._webhooks[name] = webhook
        return webhook

    def unregister_webhook(self, name: str) -> bool:
        """Remove a webhook by name. Returns True if found and removed."""
        if name in self._webhooks:
            del self._webhooks[name]
            return True
        return False

    def trigger_event(self, event_name: str, payload: dict) -> List[dict]:
        """Dispatch an event to all matching active webhooks."""
        event = WebhookEvent(
            event_id=str(uuid.uuid4()),
            name=event_name,
            payload=payload,
        )
        self._event_log.append(event)
        results = []
        for webhook in self._webhooks.values():
            if not webhook.active:
                continue
            if event_name not in webhook.events and "*" not in webhook.events:
                continue
            signature = self._sign_payload(payload, webhook.secret)
            results.append({
                "webhook": webhook.name,
                "url": webhook.url,
                "status": "dispatched",
                "signature": signature,
                "event_id": event.event_id,
            })
        return results

    def _sign_payload(self, payload: dict, secret: str) -> str:
        """Compute an HMAC-SHA256 signature for the payload."""
        if not secret:
            return ""
        body = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()

    def get_webhooks(self) -> List[Webhook]:
        """Return all registered webhooks."""
        return list(self._webhooks.values())

    def get_event_log(self) -> List[WebhookEvent]:
        """Return all dispatched events."""
        return list(self._event_log)

    def deactivate_webhook(self, name: str) -> bool:
        """Deactivate a webhook without removing it."""
        webhook = self._webhooks.get(name)
        if webhook:
            webhook.active = False
            return True
        return False

    def get_status(self) -> dict:
        """Return a summary of registered webhooks and events dispatched."""
        return {
            "total_webhooks": len(self._webhooks),
            "active_webhooks": sum(1 for w in self._webhooks.values() if w.active),
            "total_events_dispatched": len(self._event_log),
        }
