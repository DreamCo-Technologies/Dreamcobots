import pytest

from buddy_os.intelligence.world_model import Transition, WorldModel


def test_world_model_normalizes_states_and_rolls_out_known_actions():
    model = WorldModel()
    start = {"power": "off", "temp": "low"}
    middle = model.normalize({"power": "on", "temp": "low"})
    model.learn_transition(start, Transition("power_on", middle, 1.0, "switch turned on"))
    end = model.normalize({"power": "on", "temp": "high"})
    model.learn_transition(dict(middle), Transition("heat", end, .8, "heater raises temperature"))
    assert model.predict(start, "power_on").next_state == middle
    assert model.rollout(start, ("power_on", "heat")) == (model.normalize(start), middle, end)
    assert len(model.rollout(start, ("unknown",))) == 1


def test_transition_probability_is_bounded():
    with pytest.raises(ValueError):
        Transition("x", (), 1.1)
