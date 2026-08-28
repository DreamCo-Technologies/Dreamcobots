from buddy_os.intelligence.reasoning_fabric import ReasoningFabric


def test_reasoning_fabric_routes_by_domain_and_keeps_metacognition():
    fabric = ReasoningFabric()
    plan = fabric.route("diagnosis", ["causal", "uncertainty"])
    names = {method.name for method in plan.methods}
    assert "causal" in names
    assert "probabilistic" in names
    assert "metacognitive" in names
    assert fabric.history[-1] == plan
