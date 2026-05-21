"""
DreamCo Platform — Policy Evaluator
=====================================

``PolicyEvaluator`` is the runtime evaluation engine that applies a set of
``PolicyRule`` objects (from ``governance/policy_engine.py``) to an execution
context dict.

It is deliberately stateless: it receives rules + context, returns
``EvaluationResult``.  This makes it trivially testable and composable.

Usage::

    evaluator = PolicyEvaluator()
    result = evaluator.evaluate(rules, context={"action_cost": 500})
    result.blocked          # False
    result.requires_approval  # False
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dreamco_platform.governance.policy_engine import (
    PolicyAction,
    PolicyRule,
)


# ---------------------------------------------------------------------------
# EvaluationResult
# ---------------------------------------------------------------------------

@dataclass
class EvaluationResult:
    blocked: bool = False
    requires_approval: bool = False
    audit_required: bool = False
    triggered_rules: list[PolicyRule] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "blocked": self.blocked,
            "requires_approval": self.requires_approval,
            "audit_required": self.audit_required,
            "triggered_rules": [r.rule_id for r in self.triggered_rules],
        }


# ---------------------------------------------------------------------------
# PolicyEvaluator
# ---------------------------------------------------------------------------

class PolicyEvaluator:
    """Stateless policy evaluation engine."""

    def evaluate(
        self,
        rules: list[PolicyRule],
        context: dict[str, Any],
    ) -> EvaluationResult:
        """Evaluate all *rules* against *context* and return a combined result."""
        result = EvaluationResult()

        for rule in rules:
            if not rule.enabled:
                continue

            triggered = rule.condition.evaluate(context)
            if not triggered:
                continue

            result.triggered_rules.append(rule)

            if rule.action == PolicyAction.BLOCK_EXECUTION:
                result.blocked = True
            elif rule.action == PolicyAction.REQUIRE_HUMAN_APPROVAL:
                result.requires_approval = True
            elif rule.action == PolicyAction.ENFORCE_AUDIT_LOGGING:
                result.audit_required = True
            elif rule.action in (PolicyAction.ALERT, PolicyAction.LOG_ONLY,
                                  PolicyAction.NOTIFY, PolicyAction.RATE_LIMIT):
                pass  # informational — surfaced via triggered_rules

        return result

    def is_allowed(
        self,
        rules: list[PolicyRule],
        context: dict[str, Any],
    ) -> bool:
        """Return True iff execution is not blocked by any rule."""
        return not self.evaluate(rules, context).blocked

    def requires_approval(
        self,
        rules: list[PolicyRule],
        context: dict[str, Any],
    ) -> bool:
        return self.evaluate(rules, context).requires_approval
