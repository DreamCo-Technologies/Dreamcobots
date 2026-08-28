from framework.custom_page.capability_planner import build_page_plan
from framework.dynamic_fleet.action_control_plane import DynamicRegistry, Module, Superbot


def test_questionnaire_plan_routes_available_capabilities():
    registry = DynamicRegistry()
    module = Module("geometry-module", {"geometric_reasoning"})
    module.register()
    registry.discover_modules([module])
    registry.register_superbot(Superbot("reasoning-superbot", {"geometry-module"}, {"reasoning"}))

    plan = build_page_plan({"reasoning": "geometry"}, registry)
    geometry = next(x for x in plan["capabilities"] if x["capability"] == "geometric_reasoning")
    assert geometry["status"] == "ROUTABLE"
    assert geometry["routes"] == [["reasoning-superbot", "geometry-module"]]


def test_questionnaire_plan_identifies_missing_providers():
    plan = build_page_plan({"reasoning": "causal"}, DynamicRegistry())
    causal = next(x for x in plan["capabilities"] if x["capability"] == "causal_reasoning")
    assert causal["status"] == "NEEDS_CAPABILITY_PROVIDER"
    assert "causal_reasoning" in plan["unroutable"]
