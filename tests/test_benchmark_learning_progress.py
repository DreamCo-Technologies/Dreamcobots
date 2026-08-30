from buddy.learning.benchmark_progress import BenchmarkResult, mastery_ready, progress


def test_progress_distinguishes_external_and_native_passes():
    results = [
        BenchmarkResult("coding", True, external_dependency=True),
        BenchmarkResult("coding", True, external_dependency=False),
        BenchmarkResult("coding", False, external_dependency=False),
    ]
    metrics = progress(results)
    assert metrics["attempts"] == 3.0
    assert metrics["pass_rate"] == 2 / 3
    assert metrics["native_pass_rate"] == 1 / 3


def test_mastery_requires_three_native_passes():
    results = [
        BenchmarkResult("coding", True),
        BenchmarkResult("coding", True),
        BenchmarkResult("coding", True),
    ]
    assert mastery_ready(results)


def test_external_passes_do_not_count_as_mastery():
    results = [
        BenchmarkResult("coding", True, external_dependency=True),
        BenchmarkResult("coding", True, external_dependency=True),
        BenchmarkResult("coding", True, external_dependency=True),
    ]
    assert not mastery_ready(results)
