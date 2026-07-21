"""
StripeWebhookHandler — Secure Stripe webhook event processor.

Verifies the ``Stripe-Signature`` header using the webhook signing secret
and dispatches events to registered handlers.

Environment variables
---------------------
STRIPE_WEBHOOK_SECRET   Endpoint signing secret (whsec_...) from the
                        Stripe Dashboard → Developers → Webhooks.

Usage
-----
    from bots.stripe_integration import StripeWebhookHandler, WebhookEvent

    handler = StripeWebhookHandler()

    @handler.on("payment_intent.succeeded")
    def handle_payment(event: WebhookEvent) -> None:
        print("Payment succeeded:", event.data)

    # In your Flask/FastAPI route:
    result = handler.process(request_body, stripe_signature_header)
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
import uuid
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from framework import GlobalAISourcesFlow  # noqa: F401


class WebhookSignatureError(Exception):
    """Raised when the Stripe-Signature header cannot be verified."""


@dataclass
class WebhookEvent:
    """Represents a verified Stripe webhook event."""

    event_id: str
    event_type: str
    data: dict
    created: int = field(default_factory=lambda: int(time.time()))
    api_version: str = "2023-10-16"
    livemode: bool = False


class StripeWebhookHandler:
    """
    Secure Stripe webhook event processor.

    Parameters
    ----------
    webhook_secret : str | None
        The endpoint signing secret (``whsec_...``).  Defaults to
        ``STRIPE_WEBHOOK_SECRET`` from the environment.  When absent or a
        placeholder, signature verification is skipped (mock/test mode).
    tolerance_seconds : int
        Maximum age (in seconds) of a webhook payload before rejection.
        Defaults to 300 (5 minutes), matching Stripe's recommendation.
    """

    _PLACEHOLDER = "whsec_your_webhook_secret_here"

    def __init__(
        self,
        webhook_secret: Optional[str] = None,
        tolerance_seconds: int = 300,
        client=None,
        verify_signatures: bool = True,
    ) -> None:
        self._secret: str = (
            webhook_secret
            or os.environ.get("STRIPE_WEBHOOK_SECRET", "")
        )
        self._tolerance = tolerance_seconds
        self._handlers: Dict[str, List[Callable[[WebhookEvent], None]]] = {}
        self._event_log: List[WebhookEvent] = []
        self._mock = not self._secret or self._secret == self._PLACEHOLDER

        # Register default no-op handlers for the three critical events
        for evt in (
            "payment_intent.succeeded",
            "checkout.session.completed",
            "customer.subscription.updated",
            "customer.subscription.deleted",
            "invoice.payment_failed",
        ):
            self._handlers.setdefault(evt, [])

    # ------------------------------------------------------------------
    # Handler registration
    # ------------------------------------------------------------------

    def on(self, event_type: str) -> Callable:
        """Decorator to register a handler for *event_type*."""
        def decorator(fn: Callable[[WebhookEvent], None]) -> Callable:
            self._handlers.setdefault(event_type, []).append(fn)
            return fn
        return decorator

    def register(self, event_type: str, fn: Callable[[WebhookEvent], None]) -> None:
        """Register *fn* as a handler for *event_type*."""
        self._handlers.setdefault(event_type, []).append(fn)

    # ------------------------------------------------------------------
    # Signature verification
    # ------------------------------------------------------------------

    def _verify_signature(self, payload: bytes, sig_header: str) -> None:
        """
        Verify the ``Stripe-Signature`` header using HMAC-SHA256.

        Raises WebhookSignatureError on failure.
        """
        parts: dict = {}
        for part in sig_header.split(","):
            if "=" in part:
                k, v = part.split("=", 1)
                parts[k.strip()] = v.strip()

        timestamp = parts.get("t")
        signature = parts.get("v1")
        if not timestamp or not signature:
            raise WebhookSignatureError(
                "Invalid Stripe-Signature header: missing 't' or 'v1'."
            )

        # Reject stale payloads
        age = int(time.time()) - int(timestamp)
        if age > self._tolerance:
            raise WebhookSignatureError(
                f"Webhook timestamp too old ({age}s > {self._tolerance}s tolerance)."
            )

        signed_payload = f"{timestamp}.".encode() + payload
        expected = hmac.new(
            self._secret.encode("utf-8"),
            signed_payload,
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(expected, signature):
            raise WebhookSignatureError(
                "Stripe-Signature verification failed. Possible replay attack."
            )

    # ------------------------------------------------------------------
    # Event processing
    # ------------------------------------------------------------------

    def process(
        self,
        payload: bytes,
        sig_header: Optional[str] = None,
    ) -> WebhookEvent:
        """
        Parse, optionally verify, and dispatch a Stripe webhook event.

        Parameters
        ----------
        payload     Raw request body bytes.
        sig_header  Value of the ``Stripe-Signature`` HTTP header.  When
                    provided and not in mock mode, the signature is verified.

        Returns
        -------
        The dispatched WebhookEvent.

        Raises
        ------
        WebhookSignatureError  If signature verification fails.
        ValueError             If the payload is not valid JSON.
        """
        if not self._mock and sig_header:
            self._verify_signature(payload, sig_header)

        try:
            body = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON webhook payload: {exc}") from exc

        event = WebhookEvent(
            event_id=body.get("id", f"evt_{uuid.uuid4().hex[:24]}"),
            event_type=body.get("type", "unknown"),
            data=body.get("data", {}).get("object", body.get("data", {})),
            created=body.get("created", int(time.time())),
            api_version=body.get("api_version", "2023-10-16"),
            livemode=body.get("livemode", False),
        )

        self._event_log.append(event)
        for handler in self._handlers.get(event.event_type, []):
            handler(event)

        return event

    # ------------------------------------------------------------------
    # Mock helpers (for testing)
    # ------------------------------------------------------------------

    def simulate(self, event_type: str, data: dict) -> WebhookEvent:
        """
        Simulate a webhook event without HTTP or signature overhead.

        Useful in tests and local development.
        """
        payload = json.dumps(
            {
                "id": f"evt_{uuid.uuid4().hex[:24]}",
                "type": event_type,
                "data": {"object": data},
                "created": int(time.time()),
                "livemode": False,
            }
        ).encode()
        return self.process(payload)

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def is_mock(self) -> bool:
        """Return True when operating without signature verification."""
        return self._mock

    def get_event_log(self) -> list:
        """Return list of all processed WebhookEvent objects."""
        return list(self._event_log)

    def get_registered_events(self) -> list:
        """Return event types that have at least one registered handler."""
        return [k for k, v in self._handlers.items() if v]


import time as _time_wh
import json as _json_wh


@staticmethod
def _build_event_payload(event_type: str, data: dict) -> bytes:
    """Build a raw webhook JSON payload for testing."""
    payload = {
        "id": f"evt_{_time_wh.time_ns()}",
        "type": event_type,
        "data": {"object": data},
        "created": int(_time_wh.time()),
        "livemode": False,
    }
    return _json_wh.dumps(payload).encode()


StripeWebhookHandler.build_event_payload = _build_event_payload


def _dispatch(self, payload: bytes, sig_header=None, skip_verify: bool = False) -> "WebhookEvent":
    """Dispatch a webhook event. Alias for process() with skip_verify support."""
    if skip_verify:
        old_mock = self._mock
        self._mock = True
        try:
            return self.process(payload, sig_header)
        finally:
            self._mock = old_mock
    return self.process(payload, sig_header)


StripeWebhookHandler.dispatch = _dispatch
