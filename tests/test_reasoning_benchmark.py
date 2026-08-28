from buddy_os.intelligence.reasoning_benchmark import BenchmarkCase, ReasoningBenchmark


def test_benchmark_records_correctness_and_exceptions():
    benchmark = ReasoningBenchmark([
        BenchmarkCase("a", "logic", "2+2", 4),
        BenchmarkCase("b", "logic", "bad", 4),
    ])
    results = benchmark.run("deductive", lambda prompt: 4 if prompt == "2+2" else (_ for _ in ()).throw(ValueError("invalid")))
    assert ReasoningBenchmark.accuracy(results) == 0.5
    assert ReasoningBenchmark.failure_modes(results) == {"ValueError": 1}
