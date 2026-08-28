from framework.custom_page.superbot_selector import build_custom_page_routes
from framework.dynamic_fleet.action_control_plane import DynamicRegistry, Health, Module, Superbot


def test_selector_only_marks_healthy_routes_verified():
    registry = DynamicRegistry()
    module = Module("geometry-module", {"geometric_reasoning"})
    module.register()
    module.health = Health.VERIFIED
    registry.discover_modules([module])
    bot = Superbot("reasoning-superbot", {"geometry-module"}, {"reasoning"})
    bot.register()
    bot.health = Health.VERIFIED
    registry.superbots[bot.superbot_id] = bot

    result = build_custom_page_routes({"reasoning": "geometry"}, registry)
    geometry = next(x for x in result["capabilities"] if x["capability"] == "geometric_reasoning")
    assert geometry["status"] == "VERIFIED_ROUTE_AVAILABLE"
    assert geometry["eligible_routes"] == [{"superbot_id": "reasoning-superbot", "module_id": "geometry-module"}]


def test_selector_does_not_promote_registered_route_to_verified():
    registry = DynamicRegistry()
    module = Module("geometry-module", {"geometric_reasoning"})
    module.register()
    registry.discover_modules([module])
    bot = Superbot("reasoning-superbot", {"geometry-module"}, {"reasoning"})
    bot.register()
    registry.superbots[bot.superbot_id] = bot

    result = build_custom_page_routes({"reasoning": "geometry"}, registry)
    geometry = next(x for x in result["capabilities"] if x["capability"] == "geometric_reasoning")
    assert geometry["status"] == "ROUTE_REQUIRES_VERIFICATION"
