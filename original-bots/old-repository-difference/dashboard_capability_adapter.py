from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


FEATURE_GROUPS = {
    "operations": {"operations", "bot_control", "deployment", "runtime", "queue"},
    "governance": {"governance", "rbac", "policy", "audit", "admin"},
    "monetization": {"monetization", "revenue", "billing", "pricing", "payments"},
    "growth_analytics": {"analytics", "telemetry", "growth", "reporting", "insights"},
}


@dataclass(slots=True)
class DashboardCapabilityProfile:
    dashboard_id: str
    capabilities: list[str] = field(default_factory=list)
    buttons_actions: list[str] = field(default_factory=list)
    api_endpoints: list[str] = field(default_factory=list)
    bot_controls: list[str] = field(default_factory=list)
    governance_features: list[str] = field(default_factory=list)
    revenue_controls: list[str] = field(default_factory=list)
    auth_model: str = "unknown"
    deployment_readiness: str = "unknown"
    security_findings: list[str] = field(default_factory=list)
    duplicate_mappings: list[str] = field(default_factory=list)


def _to_unique_strings(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    deduped = {str(v).strip() for v in values if str(v).strip()}
    return sorted(deduped)


def normalize_dashboard_schema(dashboard_id: str, raw: dict[str, Any]) -> dict[str, Any]:
    profile = DashboardCapabilityProfile(
        dashboard_id=dashboard_id,
        capabilities=_to_unique_strings(raw.get("capabilities")),
        buttons_actions=_to_unique_strings(raw.get("buttons_actions") or raw.get("buttons/actions")),
        api_endpoints=_to_unique_strings(raw.get("api_endpoints")),
        bot_controls=_to_unique_strings(raw.get("bot_controls")),
        governance_features=_to_unique_strings(raw.get("governance_features")),
        revenue_controls=_to_unique_strings(raw.get("revenue_controls")),
        auth_model=str(raw.get("auth_model") or "unknown"),
        deployment_readiness=str(raw.get("deployment_readiness") or "unknown"),
        security_findings=_to_unique_strings(raw.get("security_findings")),
        duplicate_mappings=_to_unique_strings(raw.get("duplicate_mappings")),
    )
    return {
        "dashboard_id": profile.dashboard_id,
        "capabilities": profile.capabilities,
        "buttons/actions": profile.buttons_actions,
        "api_endpoints": profile.api_endpoints,
        "bot_controls": profile.bot_controls,
        "governance_features": profile.governance_features,
        "revenue_controls": profile.revenue_controls,
        "auth_model": profile.auth_model,
        "deployment_readiness": profile.deployment_readiness,
        "security_findings": profile.security_findings,
        "duplicate_mappings": profile.duplicate_mappings,
        "feature_groups": map_feature_groups(profile.capabilities),
    }


def map_feature_groups(capabilities: list[str]) -> dict[str, bool]:
    lowered = {c.strip().lower() for c in capabilities}
    return {
        group: any(token in lowered for token in tokens)
        for group, tokens in FEATURE_GROUPS.items()
    }


def deployment_readiness_score(value: str) -> int:
    normalized = (value or "").strip().lower()
    if normalized in {"production", "ready", "high"}:
        return 90
    if normalized in {"staging", "medium", "partial"}:
        return 60
    if normalized in {"experimental", "low"}:
        return 30
    return 10
