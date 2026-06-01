"""
TaskEngine - Core task execution engine for Buddy.

Maps parsed intents to registered capability handlers and executes them.
New capabilities are registered dynamically, enabling a modular,
extensible architecture.
"""

from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
import time
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

from BuddyAI.event_bus import EventBus
from BuddyAI.master_registry import MasterRegistryAdapter
from BuddyAI.text_handler import ParsedCommand, TextHandler

logger = logging.getLogger(__name__)


class UnknownIntentError(ValueError):
    """Raised when no capability is registered for a given intent."""


@dataclass(frozen=True)
class CapabilityDefinition:
    """Structured metadata for a capability handler."""

    intent: str
    handler_ref: Callable[[Dict[str, Any]], Any]
    risk_level: str = "low"
    approval_required: bool = False
    division: str = "DreamBuddy"
    revenue_generating: bool = False
    spends_money: bool = False
    enabled: bool = True
    bot_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def with_overrides(self, overrides: Optional[Dict[str, Any]]) -> "CapabilityDefinition":
        """Return a copy with registry-driven overrides."""
        if not overrides:
            return self
        merged_metadata = dict(self.metadata)
        merged_metadata.update({k: v for k, v in overrides.items() if k not in {
            "intent",
            "handler_ref",
            "risk_level",
            "approval_required",
            "division",
            "revenue_generating",
            "spends_money",
            "enabled",
            "bot_id",
        }})
        return CapabilityDefinition(
            intent=self.intent,
            handler_ref=self.handler_ref,
            risk_level=str(overrides.get("risk_level", self.risk_level)).lower(),
            approval_required=bool(overrides.get("approval_required", self.approval_required)),
            division=str(overrides.get("division", self.division)),
            revenue_generating=bool(overrides.get("revenue_generating", self.revenue_generating)),
            spends_money=bool(overrides.get("spends_money", self.spends_money)),
            enabled=bool(overrides.get("enabled", self.enabled)),
            bot_id=overrides.get("bot_id", self.bot_id),
            metadata=merged_metadata,
        )


@dataclass(frozen=True)
class GateDecision:
    """Decision produced by policy or permission gate."""

    allowed: bool
    reason: str
    code: str = "ok"


class PolicyEngine:
    """Policy checks for risk, monetization, rate limits, and spend guards."""

    def __init__(self, max_requests_per_minute: int = 120, max_spend_amount: float = 10000.0) -> None:
        self.max_requests_per_minute = max_requests_per_minute
        self.max_spend_amount = max_spend_amount
        self._rate_history: dict[tuple[str, str], deque[float]] = defaultdict(deque)

    def validate(
        self, capability: CapabilityDefinition, params: Dict[str, Any], user_id: str
    ) -> GateDecision:
        if not capability.enabled:
            return GateDecision(False, "Capability disabled by master registry.", "capability_disabled")

        now = time.time()
        key = (user_id, capability.intent)
        history = self._rate_history[key]
        while history and now - history[0] > 60:
            history.popleft()
        per_minute_limit = int(params.get("_rate_limit_per_minute", self.max_requests_per_minute))
        if per_minute_limit > 0 and len(history) >= per_minute_limit:
            return GateDecision(False, "Rate limit exceeded.", "rate_limited")
        history.append(now)

        if capability.risk_level in {"critical"} and not bool(params.get("_compliance_checked", False)):
            return GateDecision(False, "Compliance check required for critical capability.", "compliance_required")

        if capability.revenue_generating and not bool(params.get("_policy_acknowledged", False)):
            return GateDecision(False, "Policy acknowledgement required for revenue capability.", "policy_ack_required")

        if capability.spends_money:
            spend_amount = float(params.get("_spend_amount", 0) or 0)
            if spend_amount > 0 and not bool(params.get("_spending_guard", False)):
                return GateDecision(False, "Spending guard approval required.", "spending_guard_required")
            max_spend = float(params.get("_max_spend_amount", self.max_spend_amount))
            if spend_amount > max_spend:
                return GateDecision(False, "Spend amount exceeds policy limit.", "spend_limit_exceeded")

        return GateDecision(True, "Policy checks passed.")


class PermissionEngine:
    """Permission checks for approvals and role-based restrictions."""

    @staticmethod
    def _has_approval(intent: str, params: Dict[str, Any]) -> bool:
        if bool(params.get("_approved", False)):
            return True
        approved_intents = params.get("_approved_intents", [])
        return isinstance(approved_intents, list) and intent in approved_intents

    def check(self, capability: CapabilityDefinition, params: Dict[str, Any]) -> GateDecision:
        roles = {str(role).lower() for role in params.get("_roles", []) if isinstance(role, str)}
        if capability.approval_required and not self._has_approval(capability.intent, params):
            return GateDecision(False, "Approval required for this capability.", "approval_required")

        if capability.risk_level in {"high", "critical"} and not ({"admin", "owner"} & roles):
            return GateDecision(False, "Admin or owner role required for high-risk capability.", "role_required")

        if capability.risk_level == "critical" and not bool(params.get("_dual_approval", False)):
            return GateDecision(False, "Dual approval required for critical capability.", "dual_approval_required")

        return GateDecision(True, "Permission checks passed.")


class TaskEngine:
    """Dispatches parsed commands to registered capability handlers.

    Capabilities are plain callables that accept a ``params`` dict and
    return a result dict.

    Example::

        engine = TaskEngine()
        engine.register_capability("greet", lambda p: {"message": "Hello!"})
        result = engine.execute("greet", {})
        # {"message": "Hello!"}
    """

    def __init__(
        self,
        registry_adapter: Optional[MasterRegistryAdapter] = None,
        event_bus: Optional[EventBus] = None,
        policy_engine: Optional[PolicyEngine] = None,
        permission_engine: Optional[PermissionEngine] = None,
    ) -> None:
        self._capabilities: Dict[str, CapabilityDefinition] = {}
        self._text_handler = TextHandler()
        self._registry_adapter = registry_adapter or MasterRegistryAdapter()
        self.event_bus = event_bus or EventBus()
        self._policy_engine = policy_engine or PolicyEngine()
        self._permission_engine = permission_engine or PermissionEngine()
        self._audit_log: list[dict[str, Any]] = []
        self._telemetry: dict[str, Any] = {
            "executions": 0,
            "successes": 0,
            "failures": 0,
            "denials": 0,
            "total_latency_ms": 0.0,
        }

    # ------------------------------------------------------------------
    # Capability management
    # ------------------------------------------------------------------

    def register_capability(self, intent: str, handler: Callable, **metadata: Any) -> None:
        """Register *handler* for *intent*.

        Args:
            intent: Intent label string (e.g. ``"add_todo"``).
            handler: Callable that accepts ``params: dict`` and returns a dict.
        """
        self._capabilities[intent] = CapabilityDefinition(
            intent=intent,
            handler_ref=handler,
            risk_level=str(metadata.get("risk_level", "low")).lower(),
            approval_required=bool(metadata.get("approval_required", False)),
            division=str(metadata.get("division", "DreamBuddy")),
            revenue_generating=bool(metadata.get("revenue_generating", False)),
            spends_money=bool(metadata.get("spends_money", False)),
            enabled=bool(metadata.get("enabled", True)),
            bot_id=metadata.get("bot_id"),
            metadata={k: v for k, v in metadata.items() if k not in {
                "risk_level",
                "approval_required",
                "division",
                "revenue_generating",
                "spends_money",
                "enabled",
                "bot_id",
            }},
        )
        logger.debug("Registered capability for intent '%s'.", intent)

    def unregister_capability(self, intent: str) -> bool:
        """Remove the handler for *intent*.

        Returns:
            ``True`` if the capability existed and was removed.
        """
        if intent in self._capabilities:
            del self._capabilities[intent]
            logger.debug("Unregistered capability for intent '%s'.", intent)
            return True
        return False

    def list_capabilities(self) -> List[str]:
        """Return a sorted list of all registered intent names."""
        return sorted(self._capabilities.keys())

    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Return execution audit records."""
        return list(self._audit_log)

    def get_telemetry(self) -> Dict[str, Any]:
        """Return aggregate telemetry metrics."""
        executions = self._telemetry["executions"]
        average_latency = (
            self._telemetry["total_latency_ms"] / executions if executions else 0.0
        )
        success_rate = (
            self._telemetry["successes"] / executions if executions else 0.0
        )
        return {
            **self._telemetry,
            "average_latency_ms": average_latency,
            "success_rate": success_rate,
        }

    def _resolve_capability(self, intent: str) -> Optional[CapabilityDefinition]:
        base_capability = self._capabilities.get(intent)
        if base_capability is None:
            return None
        registry_metadata = self._registry_adapter.get_capability(intent)
        return base_capability.with_overrides(registry_metadata)

    def _event_payload(
        self,
        correlation_id: str,
        intent: str,
        user_id: str,
        outcome: Optional[str] = None,
        detail: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "correlation_id": correlation_id,
            "intent": intent,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if outcome:
            payload["outcome"] = outcome
        if detail:
            payload["detail"] = detail
        return payload

    def _record_audit(self, record: Dict[str, Any]) -> None:
        self._audit_log.append(record)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(self, intent: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the capability registered for *intent*.

        Args:
            intent: Intent label string.
            params: Parameters to pass to the handler.

        Returns:
            Result dict from the handler.

        Raises:
            UnknownIntentError: If no capability is registered for *intent*.
        """
        params = params or {}
        capability = self._resolve_capability(intent)
        if capability is None:
            raise UnknownIntentError(
                f"No capability registered for intent '{intent}'. "
                f"Available: {self.list_capabilities()}"
            )

        user_id = str(params.get("_user_id", "anonymous"))
        correlation_id = str(uuid4())
        started_at = time.perf_counter()
        self.event_bus.publish(
            "capability.requested",
            self._event_payload(correlation_id, intent, user_id, outcome="requested"),
        )

        policy = self._policy_engine.validate(capability, params, user_id)
        if not policy.allowed:
            latency_ms = (time.perf_counter() - started_at) * 1000
            denial_payload = self._event_payload(
                correlation_id, intent, user_id, outcome="denied", detail=policy.reason
            )
            self.event_bus.publish("capability.denied", denial_payload)
            self._telemetry["executions"] += 1
            self._telemetry["denials"] += 1
            self._telemetry["total_latency_ms"] += latency_ms
            self._record_audit(
                {
                    **denial_payload,
                    "stage": "policy",
                    "policy": {"allowed": policy.allowed, "reason": policy.reason, "code": policy.code},
                    "permission": None,
                    "result": {"success": False, "error": policy.reason},
                }
            )
            return {
                "success": False,
                "error": policy.reason,
                "denied": True,
                "stage": "policy",
                "_execution": {"correlation_id": correlation_id},
            }

        permission = self._permission_engine.check(capability, params)
        if not permission.allowed:
            latency_ms = (time.perf_counter() - started_at) * 1000
            denial_payload = self._event_payload(
                correlation_id, intent, user_id, outcome="denied", detail=permission.reason
            )
            self.event_bus.publish("capability.denied", denial_payload)
            self._telemetry["executions"] += 1
            self._telemetry["denials"] += 1
            self._telemetry["total_latency_ms"] += latency_ms
            self._record_audit(
                {
                    **denial_payload,
                    "stage": "permission",
                    "policy": {"allowed": policy.allowed, "reason": policy.reason, "code": policy.code},
                    "permission": {"allowed": permission.allowed, "reason": permission.reason, "code": permission.code},
                    "result": {"success": False, "error": permission.reason},
                }
            )
            return {
                "success": False,
                "error": permission.reason,
                "denied": True,
                "stage": "permission",
                "_execution": {"correlation_id": correlation_id},
            }

        self.event_bus.publish(
            "capability.approved",
            self._event_payload(correlation_id, intent, user_id, outcome="approved"),
        )
        self.event_bus.publish(
            "capability.started",
            self._event_payload(correlation_id, intent, user_id, outcome="started"),
        )
        logger.debug("Executing intent '%s' with params: %s", intent, params)
        try:
            result = capability.handler_ref(params)
            normalized_result = result if isinstance(result, dict) else {"result": result}
            latency_ms = (time.perf_counter() - started_at) * 1000
            self.event_bus.publish(
                "capability.succeeded",
                self._event_payload(correlation_id, intent, user_id, outcome="succeeded"),
            )
            self._telemetry["executions"] += 1
            self._telemetry["successes"] += 1
            self._telemetry["total_latency_ms"] += latency_ms
            self._record_audit(
                {
                    **self._event_payload(correlation_id, intent, user_id, outcome="succeeded"),
                    "stage": "handler",
                    "policy": {"allowed": policy.allowed, "reason": policy.reason, "code": policy.code},
                    "permission": {"allowed": permission.allowed, "reason": permission.reason, "code": permission.code},
                    "result": normalized_result,
                    "latency_ms": latency_ms,
                    "capability": {
                        "division": capability.division,
                        "risk_level": capability.risk_level,
                        "approval_required": capability.approval_required,
                        "revenue_generating": capability.revenue_generating,
                        "spends_money": capability.spends_money,
                        "enabled": capability.enabled,
                    },
                }
            )
            return {
                **normalized_result,
                "_execution": {
                    "correlation_id": correlation_id,
                    "policy": policy.reason,
                    "permission": permission.reason,
                },
            }
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Handler for '%s' raised: %s", intent, exc)
            latency_ms = (time.perf_counter() - started_at) * 1000
            self.event_bus.publish(
                "capability.failed",
                self._event_payload(correlation_id, intent, user_id, outcome="failed", detail=str(exc)),
            )
            self._telemetry["executions"] += 1
            self._telemetry["failures"] += 1
            self._telemetry["total_latency_ms"] += latency_ms
            self._record_audit(
                {
                    **self._event_payload(correlation_id, intent, user_id, outcome="failed", detail=str(exc)),
                    "stage": "handler",
                    "policy": {"allowed": policy.allowed, "reason": policy.reason, "code": policy.code},
                    "permission": {"allowed": permission.allowed, "reason": permission.reason, "code": permission.code},
                    "result": {"success": False, "error": str(exc)},
                    "latency_ms": latency_ms,
                }
            )
            return {
                "success": False,
                "error": str(exc),
                "_execution": {"correlation_id": correlation_id},
            }

    def process_text(self, text: str) -> Dict[str, Any]:
        """Parse *text* and execute the matched capability.

        This is the high-level entry point that combines text parsing and
        task execution in a single call.

        Args:
            text: Free-form user command string.

        Returns:
            Result dict from the matching capability handler,
            or an error dict when the intent is unknown or text is empty.
        """
        if not text or not text.strip():
            return {"success": False, "message": "Empty input received."}

        command: ParsedCommand = self._text_handler.parse(text)
        logger.info(
            "Parsed command: intent='%s' params=%s", command.intent, command.params
        )

        if command.intent == "unknown":
            return {
                "success": False,
                "message": (
                    f"Sorry, I didn't understand: \"{text}\". "
                    "Type 'help' to see what I can do."
                ),
            }

        if command.intent not in self._capabilities:
            return {
                "success": False,
                "message": (
                    f"I understood '{command.intent}' but don't have that "
                    "capability yet.  You can install a library or plugin to "
                    "add it."
                ),
            }

        return self.execute(command.intent, command.params)
