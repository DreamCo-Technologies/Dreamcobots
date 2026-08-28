from buddy_os.intelligence.adaptive_verification import AdaptiveVerification
from buddy_os.intelligence.planner_arbitration import Arbitration, PlannerResult
from buddy_os.intelligence.verification_selector import VerificationOption


def test_adaptive_verification_selects_when_planners_disagree():
    arbitration = Arbitration(
        PlannerResult("tree", "a", .8, .8),
        .5,
        ("a", "b"),
        True,
    )
    options = [
        VerificationOption("test_a", .8, cost=1),
        VerificationOption("test_b", .9, cost=3),
    ]
    request = AdaptiveVerification().build_request(arbitration, options)
    assert request.reason == "planner disagreement"
    assert request.selected_option_id == "test_a"


def test_no_disagreement_does_not_select_verification():
    arbitration = Arbitration(None, 1.0, ("a",), False)
    request = AdaptiveVerification().build_request(arbitration, [VerificationOption("test", .9)])
    assert request.selected_option_id is None
