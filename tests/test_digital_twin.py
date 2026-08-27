from buddy_os.intelligence.digital_twin import DigitalTwin, TwinAction


def test_twin_simulation_is_side_effect_free_until_applied():
    twin = DigitalTwin({"status": "ready"})
    result = twin.simulate(TwinAction("deploy", {"status": "deployed"}, cost=2.5, risk=0.2))
    assert twin.snapshot() == {"status": "ready"}
    assert result.after["status"] == "deployed"
    twin.apply_simulated(result)
    assert twin.snapshot()["status"] == "deployed"
