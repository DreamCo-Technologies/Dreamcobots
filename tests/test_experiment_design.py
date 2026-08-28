import pytest

from buddy_os.intelligence.experiment_design import Experiment, ExperimentDesigner


def test_experiment_requires_hypothesis_and_variable():
    with pytest.raises(ValueError):
        Experiment("x", "objective", (), ("temperature",))
    with pytest.raises(ValueError):
        Experiment("y", "objective", ("h",), ())


def test_experiment_reports_readiness_gaps_and_reproducibility_key():
    experiment = Experiment("x", "test cause", ("h1",), ("input",))
    designer = ExperimentDesigner()
    assert designer.readiness_gaps(experiment) == (
        "control_definition", "expected_outcomes", "stopping_criteria", "safety_constraints"
    )
    assert designer.reproducibility_key(experiment)[0] == "x"
    designer.register(experiment)
    with pytest.raises(ValueError):
        designer.register(experiment)
