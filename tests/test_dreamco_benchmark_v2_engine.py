import tempfile
import unittest
from pathlib import Path

from tools.dreamco_benchmark_v2_engine import (
    BenchmarkTask, RunnerResult, append_failure_replay, evaluate,
    select_failure_replay, update_elo_pair, self_debug_with_reviewed_patch,
)

TASK = BenchmarkTask(
    task_id="task-001", division_id="DCO-001", model_id="buddy-nano",
    model_revision="rev-a", dataset_revision="dataset-v1", split="validation",
    seed=17, test_sha256="a" * 64, hardware_profile="cpu-4c-16gb",
)


class BenchmarkV2EngineTests(unittest.TestCase):
    def test_evidence_pass_requires_complete_provenance_and_resource_compliance(self):
        evidence = evaluate(TASK, lambda _: RunnerResult(True, 0, 12, "ok", "", 100),
                            max_duration_ms=100, max_memory_mb=512)
        self.assertEqual(evidence["gate"], "PASS")
        self.assertEqual(len(evidence["evidence_sha256"]), 64)

    def test_missing_memory_and_timeout_fail_closed(self):
        for result in (
            RunnerResult(True, 0, 10, peak_memory_mb=None),
            RunnerResult(True, 0, 10, peak_memory_mb=10, timeout=True),
            RunnerResult(True, 0, 10, peak_memory_mb=10, security_findings=("secret",)),
        ):
            evidence = evaluate(TASK, lambda _, r=result: r,
                                max_duration_ms=100, max_memory_mb=512)
            self.assertEqual(evidence["gate"], "FAIL_CLOSED")

    def test_training_split_is_rejected(self):
        task = BenchmarkTask(**{**TASK.__dict__, "split": "train"})
        with self.assertRaises(ValueError):
            evaluate(task, lambda _: RunnerResult(True, 0, 1, peak_memory_mb=1),
                     max_duration_ms=10, max_memory_mb=10)

    def test_failure_replay_is_redacted_and_not_training_eligible(self):
        failed = evaluate(TASK, lambda _: RunnerResult(False, 1, 10, stderr="API_KEY=abc123 failed", peak_memory_mb=1),
                          max_duration_ms=100, max_memory_mb=512)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "replay.jsonl"
            append_failure_replay(path, failed)
            line = path.read_text(encoding="utf-8")
            self.assertNotIn("abc123", line)
            self.assertIn('"training_eligible":false', line)
            self.assertEqual(len(select_failure_replay([__import__("json").loads(line)], 1)), 1)

    def test_elo_is_head_to_head_and_zero_sum(self):
        a, b = update_elo_pair(1200, 1200, 1.0)
        self.assertGreater(a, 1200)
        self.assertLess(b, 1200)
        self.assertAlmostEqual((a - 1200) + (b - 1200), 0, places=2)

    def test_three_strike_loop_requires_reviewed_patch_and_new_task_hash(self):
        calls = {"runner": 0, "review": 0}
        def runner(_):
            calls["runner"] += 1
            return RunnerResult(calls["runner"] == 2, 0 if calls["runner"] == 2 else 1,
                                10, peak_memory_mb=20)
        def proposer(task, evidence, attempt):
            return {"revalidated_task": task}
        def reviewer(_):
            calls["review"] += 1
            return True
        result = self_debug_with_reviewed_patch(TASK, runner, proposer, reviewer, max_attempts=3)
        self.assertEqual(result["status"], "PASS_WITH_EVIDENCE")
        self.assertEqual(result["attempts"], 2)

    def test_patch_loop_never_exceeds_three_attempts(self):
        calls = {"runner": 0}
        def runner(_):
            calls["runner"] += 1
            return RunnerResult(False, 1, 1, stderr="failed", peak_memory_mb=1)
        result = self_debug_with_reviewed_patch(
            TASK, runner, lambda *_: {"revalidated_task": TASK}, lambda _: True,
            max_attempts=3, max_duration_ms=10, max_memory_mb=10,
        )
        self.assertEqual(result["status"], "FAIL_CLOSED")
        self.assertEqual(calls["runner"], 3)

    def test_missing_revalidated_task_blocks(self):
        result = self_debug_with_reviewed_patch(
            TASK, lambda _: RunnerResult(False, 1, 1, peak_memory_mb=1),
            lambda *_: {"patch": "not a task"}, lambda _: True,
            max_attempts=3, max_duration_ms=10, max_memory_mb=10,
        )
        self.assertEqual(result["status"], "BLOCKED_MISSING_REVALIDATED_TASK")


if __name__ == "__main__":
    unittest.main()
