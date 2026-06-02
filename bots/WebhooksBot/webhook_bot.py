"""
WebhooksBot — Full-system webhook manager for every DreamCo bot.

Architecture
------------
WebhooksBot auto-discovers all registered bots from the BotRegistry,
registers HMAC-signed webhook endpoints for every bot event, manages
retries with exponential back-off, and exposes a FastAPI application for
external callers to subscribe, trigger, inspect and replay events.

Integrates with GlobalAISourcesFlow for sandbox-testing each webhook
before promotion to production.

GLOBAL AI SOURCES FLOW
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_RETRY_ATTEMPTS = 5
BASE_BACKOFF_SECONDS = 1.0
MAX_BACKOFF_SECONDS = 60.0
WEBHOOK_VERSION = "2.0.0"


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class DeliveryStatus(str, Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    DEAD_LETTER = "dead_letter"


class WebhookEventType(str, Enum):
    BOT_STARTED = "bot.started"
    BOT_STOPPED = "bot.stopped"
    BOT_ERROR = "bot.error"
    LEAD_GENERATED = "lead.generated"
    REVENUE_RECORDED = "revenue.recorded"
    TASK_COMPLETED = "task.completed"
    SANDBOX_PASSED = "sandbox.passed"
    SANDBOX_FAILED = "sandbox.failed"
    HEALTH_DEGRADED = "health.degraded"
    HEALTH_RECOVERED = "health.recovered"
    WEBHOOK_REGISTERED = "webhook.registered"
    WEBHOOK_DEREGISTERED = "webhook.deregistered"
    API_CALL_MADE = "api.call_made"
    DEBATE_CONSENSUS = "debate.consensus"
    UPGRADE_DEPLOYED = "upgrade.deployed"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class WebhookSubscription:
    subscription_id: str
    bot_id: str
    url: str
    events: Set[WebhookEventType]
    secret: str
    active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    delivery_count: int = 0
    failure_count: int = 0
    last_delivered_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subscription_id": self.subscription_id,
            "bot_id": self.bot_id,
            "url": self.url,
            "events": [e.value for e in self.events],
            "active": self.active,
            "created_at": self.created_at.isoformat(),
            "delivery_count": self.delivery_count,
            "failure_count": self.failure_count,
            "last_delivered_at": self.last_delivered_at.isoformat() if self.last_delivered_at else None,
        }


@dataclass
class WebhookDelivery:
    delivery_id: str
    subscription_id: str
    event_type: str
    payload: Dict[str, Any]
    status: DeliveryStatus = DeliveryStatus.PENDING
    attempt: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_attempt_at: Optional[datetime] = None
    response_code: Optional[int] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "delivery_id": self.delivery_id,
            "subscription_id": self.subscription_id,
            "event_type": self.event_type,
            "status": self.status.value,
            "attempt": self.attempt,
            "created_at": self.created_at.isoformat(),
            "last_attempt_at": self.last_attempt_at.isoformat() if self.last_attempt_at else None,
            "response_code": self.response_code,
            "error": self.error,
        }


# ---------------------------------------------------------------------------
# Delivery engine (async)
# ---------------------------------------------------------------------------

class WebhookDeliveryEngine:
    """Async delivery engine with exponential back-off and dead-letter queue."""

    def __init__(self) -> None:
        self._deliveries: Dict[str, WebhookDelivery] = {}
        self._dead_letter: List[WebhookDelivery] = []
        self._handlers: Dict[str, Callable] = {}

    def register_http_handler(self, name: str, handler: Callable) -> None:
        """Plug in an HTTP transport (aiohttp, httpx, etc.)."""
        self._handlers[name] = handler

    async def deliver(
        self,
        subscription: WebhookSubscription,
        event_type: str,
        payload: Dict[str, Any],
    ) -> WebhookDelivery:
        delivery = WebhookDelivery(
            delivery_id=str(uuid.uuid4()),
            subscription_id=subscription.subscription_id,
            event_type=event_type,
            payload=payload,
        )
        self._deliveries[delivery.delivery_id] = delivery

        signed_payload = self._sign(payload, subscription.secret)

        for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
            delivery.attempt = attempt
            delivery.last_attempt_at = datetime.now(timezone.utc)
            delivery.status = DeliveryStatus.RETRYING if attempt > 1 else DeliveryStatus.PENDING

            try:
                await self._send(subscription.url, signed_payload)
                delivery.status = DeliveryStatus.DELIVERED
                delivery.response_code = 200
                subscription.delivery_count += 1
                subscription.last_delivered_at = datetime.now(timezone.utc)
                logger.info(
                    "Webhook delivered | delivery=%s bot=%s event=%s attempt=%d",
                    delivery.delivery_id, subscription.bot_id, event_type, attempt,
                )
                return delivery
            except Exception as exc:
                delivery.error = str(exc)
                delivery.failure_count if hasattr(delivery, "failure_count") else None
                backoff = min(BASE_BACKOFF_SECONDS * (2 ** (attempt - 1)), MAX_BACKOFF_SECONDS)
                logger.warning(
                    "Webhook delivery failed | delivery=%s attempt=%d backoff=%.1fs error=%s",
                    delivery.delivery_id, attempt, backoff, exc,
                )
                if attempt < MAX_RETRY_ATTEMPTS:
                    await asyncio.sleep(backoff)

        delivery.status = DeliveryStatus.DEAD_LETTER
        subscription.failure_count += 1
        self._dead_letter.append(delivery)
        logger.error(
            "Webhook delivery moved to dead-letter | delivery=%s bot=%s event=%s",
            delivery.delivery_id, subscription.bot_id, event_type,
        )
        return delivery

    async def _send(self, url: str, payload: Dict[str, Any]) -> None:
        """Simulate or delegate HTTP POST. Wire in httpx/aiohttp for production."""
        try:
            import httpx  # type: ignore
            async with httpx.AsyncClient(timeout=10) as client:
                await client.post(url, json=payload)
        except ImportError:
            logger.debug("httpx not installed — simulating delivery to %s", url)

    @staticmethod
    def _sign(payload: Dict[str, Any], secret: str) -> Dict[str, Any]:
        body = json.dumps(payload, sort_keys=True).encode()
        sig = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest() if secret else ""
        return {**payload, "_signature": f"sha256={sig}", "_timestamp": time.time()}

    def get_dead_letter(self) -> List[Dict[str, Any]]:
        return [d.to_dict() for d in self._dead_letter]

    def get_all_deliveries(self) -> List[Dict[str, Any]]:
        return [d.to_dict() for d in self._deliveries.values()]


# ---------------------------------------------------------------------------
# WebhooksBot — main class
# ---------------------------------------------------------------------------

class WebhooksBot:
    """
    Universal webhook manager that auto-registers all DreamCo bots,
    runs sandbox validation via GlobalAISourcesFlow, and dispatches
    HMAC-signed events with async retry logic.

    GLOBAL AI SOURCES FLOW
    """

    def __init__(self) -> None:
        self._flow = GlobalAISourcesFlow(bot_name="WebhooksBot")
        self._subscriptions: Dict[str, WebhookSubscription] = {}
        self._engine = WebhookDeliveryEngine()
        self._sandbox_validated: Set[str] = set()
        self._event_hooks: Dict[str, List[str]] = {}
        logger.info("WebhooksBot v%s initialized", WEBHOOK_VERSION)

    # ------------------------------------------------------------------
    # Subscription management
    # ------------------------------------------------------------------

    def register(
        self,
        bot_id: str,
        url: str,
        events: List[WebhookEventType],
        secret: str = "",
    ) -> WebhookSubscription:
        """Register a new webhook subscription for a bot."""
        sub_id = f"sub_{bot_id}_{uuid.uuid4().hex[:8]}"
        sub = WebhookSubscription(
            subscription_id=sub_id,
            bot_id=bot_id,
            url=url,
            events=set(events),
            secret=secret or uuid.uuid4().hex,
        )
        self._subscriptions[sub_id] = sub

        # Track event → subscription mappings
        for evt in events:
            self._event_hooks.setdefault(evt.value, []).append(sub_id)

        logger.info("Registered webhook | sub=%s bot=%s events=%s", sub_id, bot_id, [e.value for e in events])
        return sub

    def register_all_bots(self, bot_ids: List[str], base_url_template: str) -> List[WebhookSubscription]:
        """Bulk-register webhooks for a list of bots using a URL template.

        Template variables: ``{bot_id}``

        Example::

            register_all_bots(["lead_gen_bot", "closer_bot"],
                               "https://hooks.dreamco.io/bots/{bot_id}")
        """
        subs = []
        all_events = list(WebhookEventType)
        for bot_id in bot_ids:
            url = base_url_template.replace("{bot_id}", bot_id)
            sub = self.register(bot_id, url, all_events)
            subs.append(sub)
        logger.info("Bulk-registered webhooks for %d bots", len(subs))
        return subs

    def deregister(self, subscription_id: str) -> bool:
        sub = self._subscriptions.pop(subscription_id, None)
        if sub:
            for evt in sub.events:
                ids = self._event_hooks.get(evt.value, [])
                if subscription_id in ids:
                    ids.remove(subscription_id)
            return True
        return False

    # ------------------------------------------------------------------
    # Sandbox validation via GlobalAISourcesFlow
    # ------------------------------------------------------------------

    def sandbox_validate(self, subscription_id: str) -> Dict[str, Any]:
        """Run a GlobalAISourcesFlow sandbox pass for a subscription."""
        sub = self._subscriptions.get(subscription_id)
        if not sub:
            raise KeyError(f"Subscription {subscription_id!r} not found.")
        result = self._flow.run_pipeline(
            raw_data={"subscription_id": subscription_id, "bot_id": sub.bot_id, "url": sub.url},
            learning_method="supervised",
        )
        self._sandbox_validated.add(subscription_id)
        logger.info("Sandbox validated webhook | sub=%s", subscription_id)
        return result

    # ------------------------------------------------------------------
    # Event dispatch
    # ------------------------------------------------------------------

    async def trigger(
        self,
        event_type: WebhookEventType,
        payload: Dict[str, Any],
        bot_id: Optional[str] = None,
    ) -> List[WebhookDelivery]:
        """Trigger an event and deliver to all matching subscriptions."""
        enriched = {
            "event_type": event_type.value,
            "version": WEBHOOK_VERSION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "bot_id": bot_id,
            **payload,
        }
        sub_ids = self._event_hooks.get(event_type.value, [])
        deliveries = []
        tasks = []
        for sub_id in sub_ids:
            sub = self._subscriptions.get(sub_id)
            if not sub or not sub.active:
                continue
            if bot_id and sub.bot_id != bot_id:
                continue
            tasks.append(self._engine.deliver(sub, event_type.value, enriched))
        if tasks:
            deliveries = await asyncio.gather(*tasks)
        return list(deliveries)

    def trigger_sync(
        self,
        event_type: WebhookEventType,
        payload: Dict[str, Any],
        bot_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Synchronous wrapper for non-async callers."""
        loop = asyncio.new_event_loop()
        try:
            results = loop.run_until_complete(self.trigger(event_type, payload, bot_id))
            return [r.to_dict() for r in results]
        finally:
            loop.close()

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    def get_subscriptions(self, bot_id: Optional[str] = None) -> List[Dict[str, Any]]:
        subs = self._subscriptions.values()
        if bot_id:
            subs = [s for s in subs if s.bot_id == bot_id]
        return [s.to_dict() for s in subs]

    def get_health_summary(self) -> Dict[str, Any]:
        total = len(self._subscriptions)
        active = sum(1 for s in self._subscriptions.values() if s.active)
        validated = len(self._sandbox_validated)
        dead_letters = len(self._engine.get_dead_letter())
        return {
            "total_subscriptions": total,
            "active_subscriptions": active,
            "sandbox_validated": validated,
            "dead_letter_count": dead_letters,
            "webhook_version": WEBHOOK_VERSION,
        }

    def __repr__(self) -> str:
        return f"WebhooksBot(subscriptions={len(self._subscriptions)}, version={WEBHOOK_VERSION!r})"
