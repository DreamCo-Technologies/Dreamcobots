from framework.dynamic_fleet.action_control_plane import ACTIONS, DynamicRegistry, Health, Module, Superbot


def test_exactly_ten_stable_actions():
    assert len(ACTIONS) == 10
    assert len(set(ACTIONS)) == 10


def test_modules_scale_without_fixed_count():
    registry = DynamicRegistry()
    modules = [Module(f"module-{i}", {f"capability-{i}"}) for i in range(250)]
    assert registry.discover_modules(modules) == 250
    assert registry.snapshot()["module_count"] == 250


def test_superbot_routes_through_actions_to_module():
    registry = DynamicRegistry()
    module = Module("geometry-module", {"geometric_reasoning"})
    module.register()
    registry.discover_modules([module])
    bot = Superbot("reasoning-superbot", {module.module_id}, {"reasoning", "geometry"})
    registry.register_superbot(bot)
    routes = registry.route("reasoning_health_check", "geometric_reasoning")
    assert routes == [("reasoning-superbot", "geometry-module")]


def test_unknown_action_is_rejected():
    registry = DynamicRegistry()
    try:
        registry.route("not-an-action")
    except ValueError as exc:
        assert "unknown action" in str(exc)
    else:
        raise AssertionError("unknown action was accepted")


def test_unknown_superbot_module_is_rejected():
    registry = DynamicRegistry()
    bot = Superbot("broken-superbot", {"missing-module"})
    try:
        registry.register_superbot(bot)
    except ValueError as exc:
        assert "unknown modules" in str(exc)
    else:
        raise AssertionError("unknown module was accepted")


def test_health_is_explicit_not_implied_by_registration():
    module = Module("new-module")
    assert module.health is Health.DISCOVERED
    module.register()
    assert module.health is Health.REGISTERED
