"""Select healthy, routable Superbot/module paths for custom pages."""
from __future__ import annotations

from typing import Any

from framework.dynamic_fleet.action_control_plane import DynamicRegistry, Health
from .capability_planner import build_page_plan


def build_custom_page_routes(answers: dict[str, str | list[str]], registry: DynamicRegistry) -> dict[str, Any]:
    plan = build_page_plan(answers, registry)
    selected: list[dict[str, Any]] = []
    for item in plan["capabilities"]:
        if item["status"] != "ROUTABLE":
            continue
        eligible = []
        for superbot_id, module_id in item["routes"]:
            bot = registry.superbots.get(superbot_id)
            module = registry.modules.get(module_id)
            if bot and module and bot.health in {Health.REGISTERED, Health.ROUTABLE, Health.TESTABLE, Health.OBSERVABLE, Health.VERIFIED, Health.PROMOTED} and module.health in {Health.REGISTERED, Health.ROUTABLE, Health.TESTABLE, Health.OBSERVABLE, Health.VERIFIED, Health.PROMOTED}:
                eligible.append({"superbot_id": superbot_id, "module_id": module_id})
        selected.append({**item, "eligible_routes": eligible, "status": "VERIFIED_ROUTE_AVAILABLE" if eligible else "ROUTE_REQUIRES_VERIFICATION"})

    return {"capabilities": selected, "unroutable": plan["unroutable"]}
