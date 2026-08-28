import pytest

from buddy_os.intelligence.information_gain import EvidenceAction, InformationGainPlanner


def test_information_gain_prefers_more_informative_lower_cost_action():
    planner = InformationGainPlanner()
    actions = [
        EvidenceAction("a", "cheap binary test", (("yes", .5), ("no", .5)), cost=1),
        EvidenceAction("b", "expensive binary test", (("yes", .5), ("no", .5)), cost=4),
    ]
    assert planner.rank(actions)[0].action_id == "a"


def test_information_action_validates_probabilities_and_risk():
    with pytest.raises(ValueError):
        EvidenceAction("x", "bad", (("a", .7), ("b", .7)))
    with pytest.raises(ValueError):
        EvidenceAction("y", "bad risk", (), risk=1.2)
