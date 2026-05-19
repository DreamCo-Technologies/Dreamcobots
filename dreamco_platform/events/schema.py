"""
DreamCo Platform — Canonical Event Schema
==========================================

This module defines the **language of DreamCo**: every workflow, bot, and
orchestrator communicates through typed events that belong to one of ten
standardised families.

Event Families
--------------
system.*       — platform health, startup, shutdown, heartbeat
workflow.*     — workflow lifecycle (started, completed, failed, retried)
bot.*          — bot registration, execution, learning, error
capability.*   — capability invocation, completion, cost accrual
billing.*      — subscription changes, invoices, payment events
learning.*     — training cycles, model updates, score improvements
marketplace.*  — listing, purchase, review, deployment events
security.*     — auth, access control, audit, anomaly detection
governance.*   — policy evaluation, approval requests, violations
deployment.*   — release, rollback, health-check, scale events

Every event carries a ``correlation_id`` for end-to-end tracing and a
``causation_id`` pointing to the event that triggered it (enabling
full causal chains for Dream Brain ingestion and replay).
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Event family constants
# ---------------------------------------------------------------------------

class EventFamily(str, Enum):
    SYSTEM = "system"
    WORKFLOW = "workflow"
    BOT = "bot"
    CAPABILITY = "capability"
    BILLING = "billing"
    LEARNING = "learning"
    MARKETPLACE = "marketplace"
    SECURITY = "security"
    GOVERNANCE = "governance"
    DEPLOYMENT = "deployment"


EVENT_FAMILIES: tuple[str, ...] = tuple(f.value for f in EventFamily)

# Mapping family → allowed sub-event names (non-exhaustive; used for docs and validation hints)
_FAMILY_SUBTYPES: dict[str, tuple[str, ...]] = {
    EventFamily.SYSTEM: ("heartbeat", "startup", "shutdown", "error", "warning"),
    EventFamily.WORKFLOW: ("started", "completed", "failed", "retried", "paused", "resumed", "cancelled"),
    EventFamily.BOT: ("registered", "started", "completed", "failed", "learning_tick", "unregistered"),
    EventFamily.CAPABILITY: ("invoked", "completed", "failed", "cost_accrued", "timeout"),
    EventFamily.BILLING: ("subscription_created", "subscription_updated", "invoice_paid",
                          "invoice_failed", "payment_method_updated", "refund_issued"),
    EventFamily.LEARNING: ("cycle_started", "cycle_completed", "model_updated",
                           "score_improved", "score_degraded", "dataset_ingested"),
    EventFamily.MARKETPLACE: ("listing_created", "listing_updated", "listing_removed",
                              "purchase_completed", "review_submitted", "deployed"),
    EventFamily.SECURITY: ("login_success", "login_failure", "token_revoked",
                           "anomaly_detected", "access_denied", "audit_entry"),
    EventFamily.GOVERNANCE: ("policy_evaluated", "policy_violated", "approval_requested",
                             "approval_granted", "approval_denied"),
    EventFamily.DEPLOYMENT: ("release_started", "release_completed", "rollback_triggered",
                             "health_check_passed", "health_check_failed", "scaled"),
}


# ---------------------------------------------------------------------------
# Core event dataclass
# ---------------------------------------------------------------------------

@dataclass
class DreamCoEvent:
    """
    A single typed event in the DreamCo platform.

    Parameters
    ----------
    event_type : str
        Dot-namespaced type following the pattern ``<family>.<subtype>``,
        e.g. ``workflow.started`` or ``capability.invoked``.
    source : str
        Identifier of the component that emitted the event
        (bot_id, orchestrator name, service name, etc.).
    payload : dict
        Arbitrary structured data relevant to this event.
    correlation_id : str
        Groups all events belonging to a single logical operation/trace.
        Defaults to a new UUID if not supplied.
    causation_id : str | None
        The ``event_id`` of the event that directly caused this one.
        ``None`` for root events.
    version : str
        Schema version of this event type. Default ``"1.0"``.
    """

    event_type: str
    source: str
    payload: dict[str, Any] = field(default_factory=dict)
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    causation_id: Optional[str] = None
    version: str = "1.0"
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)

    # ------------------------------------------------------------------
    # Derived properties
    # ------------------------------------------------------------------

    @property
    def family(self) -> str:
        """Return the family prefix of this event (the part before the first dot)."""
        return self.event_type.split(".")[0]

    @property
    def subtype(self) -> str:
        """Return the subtype (the part after the first dot), or empty string."""
        parts = self.event_type.split(".", 1)
        return parts[1] if len(parts) > 1 else ""

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dict (suitable for JSON encoding)."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "family": self.family,
            "subtype": self.subtype,
            "source": self.source,
            "version": self.version,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DreamCoEvent":
        """Reconstruct a ``DreamCoEvent`` from a serialised dict."""
        return cls(
            event_type=data["event_type"],
            source=data["source"],
            payload=data.get("payload", {}),
            correlation_id=data.get("correlation_id", str(uuid.uuid4())),
            causation_id=data.get("causation_id"),
            version=data.get("version", "1.0"),
            event_id=data.get("event_id", str(uuid.uuid4())),
            timestamp=data.get("timestamp", time.time()),
        )

    def __repr__(self) -> str:
        return (
            f"DreamCoEvent(type={self.event_type!r}, source={self.source!r}, "
            f"id={self.event_id[:8]}...)"
        )


# ---------------------------------------------------------------------------
# Factory helper
# ---------------------------------------------------------------------------

def make_event(
    family: EventFamily | str,
    subtype: str,
    source: str,
    payload: dict[str, Any] | None = None,
    *,
    correlation_id: str | None = None,
    causation_id: str | None = None,
    version: str = "1.0",
) -> DreamCoEvent:
    """
    Convenience factory for creating a ``DreamCoEvent``.

    Parameters
    ----------
    family : EventFamily | str
        The event family (e.g. ``EventFamily.BOT`` or ``"bot"``).
    subtype : str
        The sub-event name (e.g. ``"started"``).
    source : str
        Emitting component identifier.
    payload : dict | None
        Optional event payload.
    correlation_id : str | None
        Override the auto-generated correlation ID.
    causation_id : str | None
        ID of the causing event.

    Returns
    -------
    DreamCoEvent
    """
    family_str = family.value if isinstance(family, EventFamily) else str(family)
    event_type = f"{family_str}.{subtype}"
    kwargs: dict[str, Any] = {
        "event_type": event_type,
        "source": source,
        "payload": payload or {},
        "version": version,
    }
    if correlation_id is not None:
        kwargs["correlation_id"] = correlation_id
    if causation_id is not None:
        kwargs["causation_id"] = causation_id
    return DreamCoEvent(**kwargs)


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

class EventValidator:
    """
    Validates ``DreamCoEvent`` instances against the canonical schema.

    Raises
    ------
    ValueError
        If the event type is malformed or the family is unrecognised.
    """

    @staticmethod
    def validate(event: DreamCoEvent) -> bool:
        """
        Validate *event* against the canonical schema rules.

        Rules
        -----
        1. ``event_type`` must be non-empty and contain at least one dot.
        2. The family prefix must be one of the ten canonical families.
        3. ``source`` must be non-empty.
        4. ``event_id`` must be a non-empty string.
        5. ``timestamp`` must be a positive number.

        Returns
        -------
        bool
            ``True`` on success.

        Raises
        ------
        ValueError
            With a descriptive message on the first violation found.
        """
        if not event.event_type or "." not in event.event_type:
            raise ValueError(
                f"event_type must follow '<family>.<subtype>' format; "
                f"got {event.event_type!r}"
            )
        if event.family not in EVENT_FAMILIES:
            raise ValueError(
                f"Unknown event family {event.family!r}. "
                f"Recognised families: {EVENT_FAMILIES}"
            )
        if not event.source:
            raise ValueError("Event 'source' must be non-empty.")
        if not event.event_id:
            raise ValueError("Event 'event_id' must be non-empty.")
        if not event.timestamp or event.timestamp <= 0:
            raise ValueError("Event 'timestamp' must be a positive number.")
        return True

    @staticmethod
    def validate_family(family: str) -> bool:
        """Return ``True`` if *family* is a recognised event family."""
        if family not in EVENT_FAMILIES:
            raise ValueError(
                f"Unknown family {family!r}. Valid: {EVENT_FAMILIES}"
            )
        return True
