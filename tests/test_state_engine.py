from buddy_os.intelligence.state_engine import StateEngine


def test_state_engine_records_lifecycle():
    engine = StateEngine()
    engine.set_state("goal:1", "planned", "planner created plan")
    engine.set_state("goal:1", "simulated", "digital twin preflight")
    assert engine.get_state("goal:1") == "simulated"
    assert [e.current for e in engine.history("goal:1")] == ["planned", "simulated"]
