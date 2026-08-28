import pytest

from buddy_os.intelligence.world_model import Transition
from buddy_os.intelligence.world_model_confidence import PredictedState, WorldModelEvaluator


def test_transition_evaluation_preserves_model_confidence():
    transition = Transition("heat", (("temp", "high"),), .8, "learned transition")
    prediction = WorldModelEvaluator.evaluate_transition(transition)
    assert prediction.confidence == .8
    assert prediction.state == (("temp", "high"),)


def test_rollout_confidence_accumulates_uncertainty():
    predictions = (
        PredictedState((), .8, "a"),
        PredictedState((), .5, "b"),
    )
    assert WorldModelEvaluator.rollout_confidence(predictions) == pytest.approx(.4)
