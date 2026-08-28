import pytest

from buddy_os.intelligence.experiment_results import ExperimentResults, Observation


def test_results_classify_support_and_contradiction():
    results = ExperimentResults()
    results.record(Observation("o1", "e1", "yes", supports=("h1",)))
    results.record(Observation("o2", "e1", "no", contradicts=("h1",)))
    update = results.update_for("h1")
    assert update.direction == "mixed"
    assert update.supporting_observations == ("o1",)
    assert update.contradicting_observations == ("o2",)


def test_results_reject_duplicate_observations():
    results = ExperimentResults()
    observation = Observation("o1", "e1", "yes")
    results.record(observation)
    with pytest.raises(ValueError):
        results.record(observation)
