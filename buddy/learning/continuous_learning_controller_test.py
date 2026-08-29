from continuous_learning_controller import EventType, LearningEvent, evaluate_event


def test_verified_success_can_promote():
    decision = evaluate_event(LearningEvent("e1", EventType.BENCHMARK, "coding", True, True, True, True))
    assert decision.learn and decision.promote


def test_unverified_success_cannot_promote():
    decision = evaluate_event(LearningEvent("e2", EventType.BENCHMARK, "coding", True, False, True, True))
    assert decision.learn and not decision.promote


def test_external_assistance_is_recorded_without_blocking_learning():
    decision = evaluate_event(LearningEvent("e3", EventType.EXTERNAL_ASSISTANCE, "coding", True, True, True, True, True))
    assert decision.learn and decision.promote
