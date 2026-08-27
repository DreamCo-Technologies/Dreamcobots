from buddy_os.learning.math_intelligence import (
    HiddenMarkovModel, KalmanState, bayesian_update, entropy,
    information_gain, kalman_update, normalize, pareto_front,
)


def test_normalize_and_entropy():
    p = normalize({"a": 1, "b": 3})
    assert abs(sum(p.values()) - 1) < 1e-9
    assert entropy(p) > 0


def test_bayesian_update():
    result = bayesian_update({"good": .5, "bad": .5}, {"good": .9, "bad": .1})
    assert result.posterior["good"] > result.posterior["bad"]


def test_hmm_inference():
    model = HiddenMarkovModel(
        {"idle": .5, "busy": .5},
        {"idle": {"idle": .8, "busy": .2}, "busy": {"idle": .1, "busy": .9}},
        {"idle": {"quiet": .9}, "busy": {"quiet": .1}},
    )
    assert model.infer(["quiet"])["idle"] > model.infer(["quiet"])["busy"]


def test_information_gain_and_kalman():
    assert information_gain([.5, .5], [.9, .1]) > 0
    result = kalman_update(KalmanState(0, 1), 10, 1)
    assert result.estimate == 5
    assert result.variance == .5


def test_pareto_front():
    points = [{"utility": 1, "cost": 3}, {"utility": 2, "cost": 2}, {"utility": 1, "cost": 4}]
    front = pareto_front(points, maximize=["utility"], minimize=["cost"])
    assert points[1] in front
    assert points[2] not in front
