"""Turn questionnaire capability recommendations into routable page plans."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.dynamic_fleet.action_control_plane import DynamicRegistry
from .capability_questionnaire import recommend_capabilities


@dataclass(frozen=True, slots=True)
class PageCapability:
    capability: str
    score: int
    routes: tuple[tuple[str, str], ...]
    status: str


def build_page_plan(answers: dict[str, str | list[str]], registry: DynamicRegistry) -> dict[str, Any]:
    recommendations = recommend_capabilities(answers)
    plan: list[PageCapability] = []
    for item in recommendations["capabilities"]:
        capability = item["capability"]
        routes = tuple(registry.route("run_capability_batch", capability))
        status = "ROUTABLE" if routes else "NEEDS_CAPABILITY_PROVIDER"
        plan.append(PageCapability(capability, item["score"], routes, status))

    return {
        "capabilities": [
            {"capability": x.capability, "score": x.score, "routes": list(x.routes), "status": x.status}
            for x in plan
        ],
        "actions": ["run_capability_batch", "benchmark_buddy", "production_readiness"],
        "unroutable": [x.capability for x in plan if x.status != "ROUTABLE"],
    }
