"""
DreamCo Platform — Policy-as-Code Engine
=========================================

The Policy-as-Code engine evaluates declarative ``PolicyRule`` instances
against an execution context at runtime, enforcing governance constraints
such as:

* ``action_cost > 1000  → require_human_approval``
* ``workflow_type == "financial"  → enforce_audit_logging``
* ``risk_score >= 0.8  → block_execution``

This is one of DreamCo's primary enterprise differentiators: very few AI
platforms solve policy enforcement at execution time.

Design
------
Rules are pure Python dataclasses — no YAML parser dependency in this layer.
A companion YAML loader (``load_rules_from_yaml``) is provided for
configuration-file-driven rule management.

Evaluation is always non-blocking: ``PolicyEngine.evaluate_all()`` returns
a list of ``PolicyResult`` records.  Callers decide what to do with the
results (block, escalate, log, allow with warning, etc.).

Rule conditions
---------------
A ``PolicyCondition`` is a ``(context: dict) -> bool`` callable.  The
helper constructors ``cost_exceeds``, ``workflow_type_is``, ``field_equals``,
``field_gte``, ``field_lte``, and ``custom`` make common patterns concise.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


# ---------------------------------------------------------------------------
# Policy action types
# ---------------------------------------------------------------------------

class PolicyAction(str, Enum):
    REQUIRE_HUMAN_APPROVAL = "require_human_approval"
    ENFORCE_AUDIT_LOGGING = "enforce_audit_logging"
    BLOCK_EXECUTION = "block_execution"
    ALERT = "alert"
    LOG_ONLY = "log_only"
    RATE_LIMIT = "rate_limit"
    NOTIFY = "notify"


# ---------------------------------------------------------------------------
# PolicyCondition — composable predicate
# ---------------------------------------------------------------------------

PolicyConditionFn = Callable[[Dict[str, Any]], bool]


@dataclass
class PolicyCondition:
    """
    A composable predicate that evaluates a context dict.

    Parameters
    ----------
    fn : callable
        ``(context: dict) -> bool`` — returns ``True`` if the condition is met.
    description : str
        Human-readable description of the condition (for audit logs and UI).
    """

    fn: PolicyConditionFn
    description: str = ""

    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate the condition against *context*."""
        return self.fn(context)

    def __repr__(self) -> str:
        return f"PolicyCondition({self.description!r})"

    # ------------------------------------------------------------------
    # Composition helpers
    # ------------------------------------------------------------------

    def __and__(self, other: "PolicyCondition") -> "PolicyCondition":
        return PolicyCondition(
            fn=lambda ctx: self.fn(ctx) and other.fn(ctx),
            description=f"({self.description}) AND ({other.description})",
        )

    def __or__(self, other: "PolicyCondition") -> "PolicyCondition":
        return PolicyCondition(
            fn=lambda ctx: self.fn(ctx) or other.fn(ctx),
            description=f"({self.description}) OR ({other.description})",
        )

    def __invert__(self) -> "PolicyCondition":
        return PolicyCondition(
            fn=lambda ctx: not self.fn(ctx),
            description=f"NOT ({self.description})",
        )


# ---------------------------------------------------------------------------
# Condition factory helpers
# ---------------------------------------------------------------------------

def cost_exceeds(threshold_usd: float) -> PolicyCondition:
    """``action_cost > threshold_usd``"""
    return PolicyCondition(
        fn=lambda ctx: float(ctx.get("action_cost", 0)) > threshold_usd,
        description=f"action_cost > {threshold_usd}",
    )


def workflow_type_is(wf_type: str) -> PolicyCondition:
    """``workflow_type == wf_type``"""
    return PolicyCondition(
        fn=lambda ctx: ctx.get("workflow_type") == wf_type,
        description=f'workflow_type == "{wf_type}"',
    )


def field_equals(key: str, value: Any) -> PolicyCondition:
    """``context[key] == value``"""
    return PolicyCondition(
        fn=lambda ctx: ctx.get(key) == value,
        description=f"{key} == {value!r}",
    )


def field_gte(key: str, value: float) -> PolicyCondition:
    """``context[key] >= value``"""
    return PolicyCondition(
        fn=lambda ctx: float(ctx.get(key, 0)) >= value,
        description=f"{key} >= {value}",
    )


def field_lte(key: str, value: float) -> PolicyCondition:
    """``context[key] <= value``"""
    return PolicyCondition(
        fn=lambda ctx: float(ctx.get(key, 0)) <= value,
        description=f"{key} <= {value}",
    )


def custom(fn: PolicyConditionFn, description: str = "") -> PolicyCondition:
    """Wrap an arbitrary callable as a ``PolicyCondition``."""
    return PolicyCondition(fn=fn, description=description or "custom condition")


# ---------------------------------------------------------------------------
# PolicyRule
# ---------------------------------------------------------------------------

@dataclass
class PolicyRule:
    """
    A single governance rule: condition → action.

    Attributes
    ----------
    rule_id : str
        Unique identifier.
    name : str
        Human-readable name.
    condition : PolicyCondition
        Predicate evaluated against the execution context.
    action : PolicyAction
        Enforcement action triggered when the condition is met.
    severity : str
        ``"low"`` | ``"medium"`` | ``"high"`` | ``"critical"``.
    description : str
        Full description for audit trails and UI.
    enabled : bool
        Whether this rule is active. Defaults to ``True``.
    tags : list[str]
        Searchable labels (e.g. ``["financial", "compliance"]``).
    metadata : dict
        Arbitrary extra metadata.
    """

    rule_id: str
    name: str
    condition: PolicyCondition
    action: PolicyAction
    severity: str = "medium"
    description: str = ""
    enabled: bool = True
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "condition": self.condition.description,
            "action": self.action.value,
            "severity": self.severity,
            "description": self.description,
            "enabled": self.enabled,
            "tags": list(self.tags),
            "metadata": dict(self.metadata),
        }

    def __repr__(self) -> str:
        return (
            f"PolicyRule(id={self.rule_id!r}, action={self.action.value!r}, "
            f"enabled={self.enabled})"
        )


# ---------------------------------------------------------------------------
# PolicyResult
# ---------------------------------------------------------------------------

@dataclass
class PolicyResult:
    """
    The outcome of evaluating a single ``PolicyRule`` against a context.

    Attributes
    ----------
    rule_id : str
    rule_name : str
    triggered : bool
        ``True`` if the condition was met.
    action : PolicyAction | None
        The action that should be taken, or ``None`` if not triggered.
    context_snapshot : dict
        A copy of the context at evaluation time (for audit purposes).
    timestamp : float
    message : str
        Human-readable explanation.
    """

    rule_id: str
    rule_name: str
    triggered: bool
    action: Optional[PolicyAction] = None
    context_snapshot: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "triggered": self.triggered,
            "action": self.action.value if self.action else None,
            "context_snapshot": self.context_snapshot,
            "timestamp": self.timestamp,
            "message": self.message,
        }

    def __repr__(self) -> str:
        return (
            f"PolicyResult(rule={self.rule_id!r}, triggered={self.triggered}, "
            f"action={self.action.value if self.action else None!r})"
        )


# ---------------------------------------------------------------------------
# Policy engine
# ---------------------------------------------------------------------------

class PolicyEngine:
    """
    Evaluates registered ``PolicyRule`` instances against an execution context.

    Usage
    -----
    ::

        engine = PolicyEngine()
        engine.add_rule(PolicyRule(
            rule_id="cost_gate",
            name="High-cost approval gate",
            condition=cost_exceeds(1000),
            action=PolicyAction.REQUIRE_HUMAN_APPROVAL,
            severity="high",
        ))

        results = engine.evaluate_all({"action_cost": 1500, "workflow_type": "financial"})
        triggered = [r for r in results if r.triggered]
    """

    def __init__(self) -> None:
        self._rules: Dict[str, PolicyRule] = {}
        self._audit_log: List[PolicyResult] = []

    # ------------------------------------------------------------------
    # Rule management
    # ------------------------------------------------------------------

    def add_rule(self, rule: PolicyRule) -> None:
        """Register *rule*. Replaces any existing rule with the same ``rule_id``."""
        self._rules[rule.rule_id] = rule

    def remove_rule(self, rule_id: str) -> Optional[PolicyRule]:
        """Remove and return the rule with *rule_id*, or ``None``."""
        return self._rules.pop(rule_id, None)

    def get_rule(self, rule_id: str) -> Optional[PolicyRule]:
        return self._rules.get(rule_id)

    def list_rules(self, enabled_only: bool = False) -> List[PolicyRule]:
        """Return all registered rules, optionally only the enabled ones."""
        rules = list(self._rules.values())
        if enabled_only:
            rules = [r for r in rules if r.enabled]
        return sorted(rules, key=lambda r: r.rule_id)

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def evaluate(
        self,
        rule_id: str,
        context: Dict[str, Any],
        *,
        record_audit: bool = True,
    ) -> PolicyResult:
        """
        Evaluate a single rule identified by *rule_id* against *context*.

        Parameters
        ----------
        rule_id : str
            The rule to evaluate.
        context : dict
            Execution context values (e.g. ``{"action_cost": 500, ...}``).
        record_audit : bool
            Whether to append the result to the internal audit log.

        Returns
        -------
        PolicyResult

        Raises
        ------
        KeyError
            If *rule_id* is not registered.
        """
        rule = self._rules.get(rule_id)
        if rule is None:
            raise KeyError(f"No rule registered with rule_id={rule_id!r}")

        triggered = rule.enabled and rule.condition.evaluate(context)
        result = PolicyResult(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            triggered=triggered,
            action=rule.action if triggered else None,
            context_snapshot=dict(context),
            message=(
                f"Rule '{rule.name}' triggered — action: {rule.action.value}"
                if triggered
                else f"Rule '{rule.name}' not triggered"
            ),
        )
        if record_audit:
            self._audit_log.append(result)
        return result

    def evaluate_all(
        self,
        context: Dict[str, Any],
        *,
        record_audit: bool = True,
    ) -> List[PolicyResult]:
        """
        Evaluate all registered (enabled) rules against *context*.

        Returns
        -------
        list[PolicyResult]
            One result per enabled rule.
        """
        return [
            self.evaluate(rule.rule_id, context, record_audit=record_audit)
            for rule in self.list_rules(enabled_only=True)
        ]

    def has_blocking_violation(self, context: Dict[str, Any]) -> bool:
        """
        Return ``True`` if any rule with ``BLOCK_EXECUTION`` action is triggered.
        """
        return any(
            r.triggered and r.action == PolicyAction.BLOCK_EXECUTION
            for r in self.evaluate_all(context, record_audit=False)
        )

    def requires_approval(self, context: Dict[str, Any]) -> bool:
        """
        Return ``True`` if any ``REQUIRE_HUMAN_APPROVAL`` rule is triggered.
        """
        return any(
            r.triggered and r.action == PolicyAction.REQUIRE_HUMAN_APPROVAL
            for r in self.evaluate_all(context, record_audit=False)
        )

    # ------------------------------------------------------------------
    # Audit
    # ------------------------------------------------------------------

    def audit_log(self, triggered_only: bool = False) -> List[PolicyResult]:
        """Return the audit log, optionally filtered to triggered results."""
        if triggered_only:
            return [r for r in self._audit_log if r.triggered]
        return list(self._audit_log)

    def clear_audit_log(self) -> None:
        self._audit_log.clear()

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._rules)

    def __repr__(self) -> str:
        return f"PolicyEngine({len(self._rules)} rules)"
