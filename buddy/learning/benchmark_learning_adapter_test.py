from benchmark_learning_adapter import benchmark_to_event


def test_benchmark_outcome_becomes_learning_event():
    event = benchmark_to_event({
        "benchmark_id": "coding-1",
        "division": "coding",
        "passed": True,
        "verified": True,
        "regression_passed": True,
        "safety_passed": True,
        "native_success": True,
    })
    assert event["event_type"] == "benchmark"
    assert event["success"] is True
    assert event["native_success"] is True
