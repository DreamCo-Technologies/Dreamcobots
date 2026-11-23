"""Policy-only database routing decisions for Buddy.

This module never opens a connection or executes SQL. It selects only sources
whose registry evidence says they are connected, healthy, tested, and permitted.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "config" / "buddy-database-source-registry.json"
LIFECYCLE_STATES = {
    "DISCOVERED", "DOCUMENTED", "CONFIGURED", "AUTHENTICATED",
    "CONNECTED", "TESTED", "PRODUCTION", "BLOCKED",
}
DEFAULT_POLICY = {
    "routable_lifecycle_states": ["CONNECTED", "TESTED", "PRODUCTION"],
    "classification_order": ["public", "internal", "confidential", "restricted"],
    "cost_order": ["free", "low", "medium", "high"],
    "consistency_order": ["eventual", "strong"],
    "require_connected_connector": True,
    "require_healthy_source": True,
    "write_requires_approval_id": True,
    "write_requires_idempotency_key": True,
    "write_requires_transaction_support": True,
    "automatic_write_failover": False,
}
FORBIDDEN_KEY = re.compile(
    r"^(?:password|secret|token|api[_-]?key|connection[_-]?string|credential[_-]?value|dsn)$",
    re.IGNORECASE,
)


class DatabaseRouteError(ValueError):
    """Invalid routing request or unsafe source registry."""


def _contains_credential_value_key(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            FORBIDDEN_KEY.fullmatch(str(key)) or _contains_credential_value_key(child)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return any(_contains_credential_value_key(item) for item in value)
    return False


def validate_source_registry(sources: list[dict[str, Any]]) -> None:
    if not isinstance(sources, list):
        raise DatabaseRouteError("Database sources must be a list")
    seen: set[str] = set()
    required = {
        "source_id", "engine", "lifecycle_state", "connector_status", "health",
        "permitted_operations", "data_types", "query_capabilities",
        "max_data_classification", "freshness_seconds", "consistency",
        "latency_ms", "cost_tier", "residency_regions", "write_enabled",
        "supports_idempotency", "transaction_support", "write_approval_refs",
    }
    for source in sources:
        if not isinstance(source, dict):
            raise DatabaseRouteError("Every database source must be an object")
        if _contains_credential_value_key(source):
            raise DatabaseRouteError("Source registry must contain credential status only, never credential values")
        missing = sorted(required - set(source))
        if missing:
            raise DatabaseRouteError(f"Source record is missing required fields: {', '.join(missing)}")
        source_id = str(source.get("source_id") or "").strip()
        if not source_id or source_id in seen:
            raise DatabaseRouteError("Source IDs must be present and unique")
        seen.add(source_id)
        if source.get("lifecycle_state") not in LIFECYCLE_STATES:
            raise DatabaseRouteError(f"{source_id}: invalid lifecycle state")
        if not isinstance(source.get("permitted_operations"), list):
            raise DatabaseRouteError(f"{source_id}: permitted_operations must be a list")
        if not set(source["permitted_operations"]).issubset({"read", "write"}):
            raise DatabaseRouteError(f"{source_id}: unsupported permitted operation")
        for field in ("data_types", "query_capabilities", "residency_regions", "write_approval_refs"):
            if not isinstance(source.get(field), list):
                raise DatabaseRouteError(f"{source_id}: {field} must be a list")


def load_source_registry(path: str | Path = REGISTRY_PATH) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema") != "dreamco.database_source_registry.v1":
        raise DatabaseRouteError("Unsupported database source registry schema")
    policy = data.get("policy") or DEFAULT_POLICY
    sources = data.get("sources")
    validate_source_registry(sources)
    return {"policy": policy, "sources": sources, "schema": data["schema"]}


def _rank(value: Any, order: list[str]) -> int | None:
    try:
        return order.index(str(value).lower())
    except ValueError:
        return None


def _request_error(request: dict[str, Any], policy: dict[str, Any]) -> str | None:
    if not isinstance(request, dict):
        return "request_must_be_an_object"
    required = (
        "operation", "data_type", "data_classification", "query_capability",
        "max_staleness_seconds", "consistency", "max_latency_ms",
        "max_cost_tier", "region",
    )
    if any(key not in request for key in required):
        return "request_missing_required_routing_constraints"
    if request["operation"] not in {"read", "write"}:
        return "unsupported_operation"
    if _rank(request["data_classification"], policy["classification_order"]) is None:
        return "unknown_data_classification"
    if _rank(request["max_cost_tier"], policy["cost_order"]) is None:
        return "unknown_max_cost_tier"
    if request["consistency"] not in policy["consistency_order"]:
        return "unknown_consistency_requirement"
    if not isinstance(request["max_staleness_seconds"], int) or request["max_staleness_seconds"] < 0:
        return "invalid_max_staleness_seconds"
    if not isinstance(request["max_latency_ms"], int) or request["max_latency_ms"] < 1:
        return "invalid_max_latency_ms"
    if not str(request["region"]).strip():
        return "region_required"
    priority = request.get("routing_priority", ["cost", "latency", "freshness"])
    if not isinstance(priority, list) or not priority or not set(priority).issubset({"cost", "latency", "freshness"}):
        return "invalid_routing_priority"
    return None


def route_database_request(
    request: dict[str, Any],
    sources: list[dict[str, Any]] | None = None,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a deterministic route decision; never connect, query, or write."""
    if sources is None:
        registry = load_source_registry()
        sources = registry["sources"]
        policy = policy or registry["policy"]
    policy = {**DEFAULT_POLICY, **(policy or {})}
    validate_source_registry(sources)

    error = _request_error(request, policy)
    if error:
        raise DatabaseRouteError(error)

    operation = request["operation"]
    if operation == "write":
        if policy["write_requires_approval_id"] and not str(request.get("write_approval_id") or "").strip():
            return {"status": "BLOCKED", "reason": "write_approval_id_required", "selected_source_id": None, "rejected_sources": []}
        if policy["write_requires_idempotency_key"] and not str(request.get("idempotency_key") or "").strip():
            return {"status": "BLOCKED", "reason": "idempotency_key_required", "selected_source_id": None, "rejected_sources": []}

    classification_rank = _rank(request["data_classification"], policy["classification_order"])
    max_cost_rank = _rank(request["max_cost_tier"], policy["cost_order"])
    required_consistency_rank = _rank(request["consistency"], policy["consistency_order"])
    routable = set(policy["routable_lifecycle_states"])
    rejected: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []

    for source in sources:
        reasons: list[str] = []
        source_id = source["source_id"]
        if source["lifecycle_state"] not in routable:
            reasons.append("lifecycle_state_not_routable")
        if policy["require_connected_connector"] and source["connector_status"] != "CONNECTED":
            reasons.append("connector_not_connected")
        if policy["require_healthy_source"] and source["health"] != "HEALTHY":
            reasons.append("source_not_healthy")
        if operation not in source["permitted_operations"]:
            reasons.append("operation_not_permitted")
        if request["data_type"] not in source["data_types"] and "*" not in source["data_types"]:
            reasons.append("data_type_not_supported")
        source_class_rank = _rank(source["max_data_classification"], policy["classification_order"])
        if source_class_rank is None or source_class_rank < classification_rank:
            reasons.append("insufficient_data_classification")
        if not isinstance(source["freshness_seconds"], int) or source["freshness_seconds"] < 0:
            reasons.append("freshness_unknown")
        elif source["freshness_seconds"] > request["max_staleness_seconds"]:
            reasons.append("freshness_exceeds_limit")
        if source["consistency"] not in policy["consistency_order"]:
            reasons.append("consistency_unknown")
        elif _rank(source["consistency"], policy["consistency_order"]) < required_consistency_rank:
            reasons.append("consistency_below_requirement")
        if not isinstance(source["latency_ms"], int) or source["latency_ms"] < 0:
            reasons.append("latency_unknown")
        elif source["latency_ms"] > request["max_latency_ms"]:
            reasons.append("latency_exceeds_limit")
        source_cost_rank = _rank(source["cost_tier"], policy["cost_order"])
        if source_cost_rank is None:
            reasons.append("cost_tier_unknown")
        elif source_cost_rank > max_cost_rank:
            reasons.append("cost_exceeds_limit")
        if request["query_capability"] not in source["query_capabilities"]:
            reasons.append("query_capability_not_supported")
        if request["region"] not in source["residency_regions"] and "*" not in source["residency_regions"]:
            reasons.append("residency_region_not_allowed")

        if operation == "write":
            if source["write_enabled"] is not True:
                reasons.append("writes_disabled")
            if source["supports_idempotency"] is not True:
                reasons.append("idempotency_not_supported")
            if policy["write_requires_transaction_support"] and source["transaction_support"] is not True:
                reasons.append("transaction_support_required")
            approval = str(request.get("write_approval_id") or "")
            if approval not in source["write_approval_refs"]:
                reasons.append("write_approval_not_allowlisted")

        if reasons:
            rejected.append({"source_id": source_id, "reasons": sorted(set(reasons))})
        else:
            candidates.append(source)

    if not candidates:
        return {
            "status": "BLOCKED",
            "reason": "no_eligible_source",
            "selected_source_id": None,
            "rejected_sources": rejected,
            "alternatives": [],
            "failover_allowed": False,
        }

    priority = request.get("routing_priority", ["cost", "latency", "freshness"])
    def sort_key(source: dict[str, Any]) -> tuple[Any, ...]:
        values = []
        for dimension in priority:
            if dimension == "cost":
                values.append(_rank(source["cost_tier"], policy["cost_order"]))
            elif dimension == "latency":
                values.append(source["latency_ms"])
            else:
                values.append(source["freshness_seconds"])
        return (*values, source["source_id"])

    candidates.sort(key=sort_key)
    selected = candidates[0]
    failover_allowed = (
        operation == "read"
        and request.get("allow_failover") is True
        and request.get("idempotent") is True
    )
    alternatives = [item["source_id"] for item in candidates[1:]] if failover_allowed else []
    return {
        "status": "ROUTED",
        "reason": "eligible_source_selected_by_declared_priority",
        "selected_source_id": selected["source_id"],
        "engine": selected["engine"],
        "lifecycle_state": selected["lifecycle_state"],
        "alternatives": alternatives,
        "failover_allowed": failover_allowed,
        "rejected_sources": rejected,
        "audit_record": {
            "operation": operation,
            "data_type": request["data_type"],
            "data_classification": request["data_classification"],
            "query_capability": request["query_capability"],
            "region": request["region"],
            "selected_source_id": selected["source_id"],
            "routing_priority": priority,
        },
    }
