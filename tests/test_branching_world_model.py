import pytest

from buddy_os.intelligence.branching_world_model import BranchingWorldModel, FutureBranch


def test_branching_model_normalizes_and_scores_future_worlds():
    branches = [
        FutureBranch("a", (("status", "good"),), .2, 10),
        FutureBranch("b", (("status", "bad"),), .3, -4),
    ]
    normalized = BranchingWorldModel.normalize(branches)
    assert sum(b.probability for b in normalized) == pytest.approx(1.0)
    assert BranchingWorldModel.expected_utility(normalized) == pytest.approx(1.6)
    assert BranchingWorldModel.highest_probability(normalized).branch_id == "b"


def test_empty_or_zero_probability_cases_are_safe():
    assert BranchingWorldModel.normalize([]) == ()
    assert BranchingWorldModel.highest_probability([]) is None
    assert BranchingWorldModel.expected_utility([]) == 0
