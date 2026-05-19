"""
DreamCo Platform — Policy Loader (YAML)
=========================================

``PolicyLoader`` loads policy rules from YAML files or strings.

YAML format (one or more policies in a document):

.. code-block:: yaml

    policies:
      - id: cost_gate
        description: Block expensive operations without approval
        severity: high
        condition:
          field: action_cost
          op: gte
          value: 1000
        action: require_human_approval

      - id: financial_audit
        description: All financial workflows must audit-log
        severity: medium
        condition:
          field: workflow_type
          op: eq
          value: "financial"
        action: enforce_audit_logging

Supported ``op`` values: ``eq``, ``ne``, ``gt``, ``gte``, ``lt``, ``lte``,
``contains``, ``in``.

Supported ``action`` values map to ``PolicyAction`` enum names (case-insensitive).
"""

from __future__ import annotations

import json
from typing import Any

try:
    import yaml  # type: ignore[import-untyped]
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

from dreamco_platform.governance.policy_engine import (
    PolicyAction,
    PolicyCondition,
    PolicyEngine,
    PolicyRule,
)


# ---------------------------------------------------------------------------
# Condition factory
# ---------------------------------------------------------------------------

def _build_condition(cond_dict: dict[str, Any]) -> PolicyCondition:
    """Build a ``PolicyCondition`` from a dict with keys: field, op, value."""
    field_name = cond_dict["field"]
    op = cond_dict.get("op", "eq").lower()
    value = cond_dict.get("value")

    _OPS = {
        "eq": lambda ctx, f, v: ctx.get(f) == v,
        "ne": lambda ctx, f, v: ctx.get(f) != v,
        "gt": lambda ctx, f, v: (ctx.get(f) or 0) > v,
        "gte": lambda ctx, f, v: (ctx.get(f) or 0) >= v,
        "lt": lambda ctx, f, v: (ctx.get(f) or 0) < v,
        "lte": lambda ctx, f, v: (ctx.get(f) or 0) <= v,
        "contains": lambda ctx, f, v: v in (ctx.get(f) or ""),
        "in": lambda ctx, f, v: (ctx.get(f)) in v,
    }

    if op not in _OPS:
        raise ValueError(f"Unknown condition operator: '{op}'")

    op_fn = _OPS[op]
    _field = field_name
    _value = value

    def _fn(context: dict[str, Any]) -> bool:
        return op_fn(context, _field, _value)

    return PolicyCondition(
        fn=_fn,
        description=f"{field_name} {op} {value}",
    )


def _build_rule(rule_dict: dict[str, Any]) -> PolicyRule:
    condition = _build_condition(rule_dict["condition"])
    action_str = rule_dict.get("action", "allow").upper().replace(" ", "_")
    try:
        action = PolicyAction[action_str]
    except KeyError:
        # Try common aliases
        _aliases = {
            "REQUIRE_HUMAN_APPROVAL": PolicyAction.REQUIRE_HUMAN_APPROVAL,
            "ENFORCE_AUDIT_LOGGING": PolicyAction.ENFORCE_AUDIT_LOGGING,
            "DENY": PolicyAction.BLOCK_EXECUTION,
            "BLOCK": PolicyAction.BLOCK_EXECUTION,
            "BLOCK_EXECUTION": PolicyAction.BLOCK_EXECUTION,
            "ALLOW": PolicyAction.LOG_ONLY,
            "ALERT": PolicyAction.ALERT,
        }
        action = _aliases.get(action_str, PolicyAction.ALLOW)

    rule_id = rule_dict.get("id", "unnamed")
    return PolicyRule(
        rule_id=rule_id,
        name=rule_dict.get("name", rule_id),
        condition=condition,
        action=action,
        severity=rule_dict.get("severity", "info"),
        description=rule_dict.get("description", ""),
    )


# ---------------------------------------------------------------------------
# PolicyLoader
# ---------------------------------------------------------------------------

class PolicyLoader:
    """Load ``PolicyRule`` objects from YAML or JSON."""

    @staticmethod
    def from_yaml(yaml_string: str) -> list[PolicyRule]:
        """Parse *yaml_string* and return a list of ``PolicyRule`` objects.

        Requires the ``pyyaml`` package.  Raises ``ImportError`` if not
        available.
        """
        if not _HAS_YAML:
            raise ImportError(
                "pyyaml is required for YAML policy loading. "
                "Install with: pip install pyyaml"
            )
        data = yaml.safe_load(yaml_string)
        return PolicyLoader._from_dict(data)

    @staticmethod
    def from_json(json_string: str) -> list[PolicyRule]:
        """Parse *json_string* and return a list of ``PolicyRule`` objects."""
        data = json.loads(json_string)
        return PolicyLoader._from_dict(data)

    @staticmethod
    def _from_dict(data: Any) -> list[PolicyRule]:
        if isinstance(data, dict):
            rule_dicts = data.get("policies", [])
        elif isinstance(data, list):
            rule_dicts = data
        else:
            raise ValueError(f"Unexpected policy data format: {type(data)}")
        return [_build_rule(r) for r in rule_dicts]

    @staticmethod
    def load_into_engine(
        policy_source: str,
        engine: PolicyEngine,
        fmt: str = "yaml",
    ) -> int:
        """Parse *policy_source* and register all rules into *engine*.

        Returns the number of rules loaded.
        """
        if fmt.lower() == "json":
            rules = PolicyLoader.from_json(policy_source)
        else:
            rules = PolicyLoader.from_yaml(policy_source)
        for rule in rules:
            engine.add_rule(rule)
        return len(rules)
