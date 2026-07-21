"""
DreamCo Platform — Canonical Event Type Registry
=================================================

Strict enumerations of every well-known event type, grouped by family.

RULE: No system component may emit an undeclared event type string. All
event_type values must come from one of the ``*Events`` enums below (or be
validated by ``EventTypeRegistry``).
"""

from __future__ import annotations

from enum import Enum


# ---------------------------------------------------------------------------
# Per-family event type enumerations
# ---------------------------------------------------------------------------

class SystemEvents(str, Enum):
    STARTUP = "system.startup"
    SHUTDOWN = "system.shutdown"
    HEARTBEAT = "system.heartbeat"
    HEALTH_CHECK = "system.health_check"
    CONFIG_CHANGED = "system.config_changed"
    ERROR = "system.error"


class WorkflowEvents(str, Enum):
    STARTED = "workflow.started"
    COMPLETED = "workflow.completed"
    FAILED = "workflow.failed"
    RETRIED = "workflow.retried"
    PAUSED = "workflow.paused"
    RESUMED = "workflow.resumed"
    CANCELLED = "workflow.cancelled"
    STEP_STARTED = "workflow.step_started"
    STEP_COMPLETED = "workflow.step_completed"


class BotEvents(str, Enum):
    REGISTERED = "bot.registered"
    STARTED = "bot.started"
    STOPPED = "bot.stopped"
    EXECUTED = "bot.executed"
    ERROR = "bot.error"
    LEARNING_UPDATED = "bot.learning_updated"
    HEALTH_CHANGED = "bot.health_changed"


class CapabilityEvents(str, Enum):
    INVOKED = "capability.invoked"
    COMPLETED = "capability.completed"
    FAILED = "capability.failed"
    COST_ACCRUED = "capability.cost_accrued"
    RETRIED = "capability.retried"
    TIMEOUT = "capability.timeout"


class BillingEvents(str, Enum):
    SUBSCRIPTION_CREATED = "billing.subscription_created"
    SUBSCRIPTION_CHANGED = "billing.subscription_changed"
    SUBSCRIPTION_CANCELLED = "billing.subscription_cancelled"
    INVOICE_ISSUED = "billing.invoice_issued"
    PAYMENT_SUCCEEDED = "billing.payment_succeeded"
    PAYMENT_FAILED = "billing.payment_failed"
    USAGE_THRESHOLD = "billing.usage_threshold"


class LearningEvents(str, Enum):
    CYCLE_STARTED = "learning.cycle_started"
    CYCLE_COMPLETED = "learning.cycle_completed"
    STAGE_COMPLETED = "learning.stage_completed"
    MODEL_UPDATED = "learning.model_updated"
    SCORE_IMPROVED = "learning.score_improved"
    SIGNAL_RECORDED = "learning.signal_recorded"


class MarketplaceEvents(str, Enum):
    LISTING_CREATED = "marketplace.listing_created"
    LISTING_UPDATED = "marketplace.listing_updated"
    LISTING_REMOVED = "marketplace.listing_removed"
    PURCHASE_INITIATED = "marketplace.purchase_initiated"
    PURCHASE_COMPLETED = "marketplace.purchase_completed"
    REVIEW_SUBMITTED = "marketplace.review_submitted"
    DEPLOYMENT_TRIGGERED = "marketplace.deployment_triggered"


class SecurityEvents(str, Enum):
    AUTH_SUCCEEDED = "security.auth_succeeded"
    AUTH_FAILED = "security.auth_failed"
    ACCESS_DENIED = "security.access_denied"
    TOKEN_ISSUED = "security.token_issued"
    TOKEN_REVOKED = "security.token_revoked"
    ANOMALY_DETECTED = "security.anomaly_detected"
    AUDIT_RECORDED = "security.audit_recorded"


class GovernanceEvents(str, Enum):
    POLICY_EVALUATED = "governance.policy_evaluated"
    POLICY_VIOLATED = "governance.policy_violated"
    APPROVAL_REQUESTED = "governance.approval_requested"
    APPROVAL_GRANTED = "governance.approval_granted"
    APPROVAL_DENIED = "governance.approval_denied"
    POLICY_CREATED = "governance.policy_created"
    POLICY_UPDATED = "governance.policy_updated"


class DeploymentEvents(str, Enum):
    RELEASE_STARTED = "deployment.release_started"
    RELEASE_COMPLETED = "deployment.release_completed"
    RELEASE_FAILED = "deployment.release_failed"
    ROLLBACK_STARTED = "deployment.rollback_started"
    ROLLBACK_COMPLETED = "deployment.rollback_completed"
    HEALTH_CHECK_PASSED = "deployment.health_check_passed"
    HEALTH_CHECK_FAILED = "deployment.health_check_failed"
    SCALED_UP = "deployment.scaled_up"
    SCALED_DOWN = "deployment.scaled_down"


# ---------------------------------------------------------------------------
# Unified registry mapping family prefix → enum class
# ---------------------------------------------------------------------------

_FAMILY_MAP: dict[str, type] = {
    "system": SystemEvents,
    "workflow": WorkflowEvents,
    "bot": BotEvents,
    "capability": CapabilityEvents,
    "billing": BillingEvents,
    "learning": LearningEvents,
    "marketplace": MarketplaceEvents,
    "security": SecurityEvents,
    "governance": GovernanceEvents,
    "deployment": DeploymentEvents,
}

# Flat set of every declared event type string for O(1) lookup
_ALL_EVENT_TYPES: frozenset[str] = frozenset(
    member.value
    for enum_cls in _FAMILY_MAP.values()
    for member in enum_cls  # type: ignore[call-overload]
)


class EventTypeRegistry:
    """Query helper for the canonical event type registry."""

    @staticmethod
    def is_known(event_type: str) -> bool:
        """Return True if *event_type* is a declared canonical event type."""
        return event_type in _ALL_EVENT_TYPES

    @staticmethod
    def all_types() -> frozenset[str]:
        """Return the full set of declared event type strings."""
        return _ALL_EVENT_TYPES

    @staticmethod
    def family_of(event_type: str) -> str | None:
        """Return the family prefix (e.g. ``'workflow'``) for *event_type*."""
        parts = event_type.split(".", 1)
        if len(parts) < 2:
            return None
        return parts[0] if parts[0] in _FAMILY_MAP else None

    @staticmethod
    def types_for_family(family: str) -> list[str]:
        """Return all declared event types for the given *family* prefix."""
        enum_cls = _FAMILY_MAP.get(family)
        if enum_cls is None:
            return []
        return [m.value for m in enum_cls]  # type: ignore[call-overload]
