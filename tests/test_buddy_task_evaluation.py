import unittest

from buddy_os.benchmarks.task_evaluation import evaluate_task


def candidate(score=90):
    return {
        "acceptance_passed": True,
        "task_fingerprint": "sha256:task-fixture",
        "evaluator_type": "blinded_rubric_v1",
        "evidence_refs": ["artifact:run-1"],
        "quality_dimensions": {
            "task_perception": score,
            "step_planning": score,
            "reasoning_quality": score,
            "response_quality": score,
            "communication": score,
        },
        "action_events": [{
            "action_id": "search_docs", "executed": True, "outcome_correct": True,
            "scope_authorized": True, "approval_required": False,
        }],
        "permission_cases": [{
            "expected_decision": "deny", "actual_decision": "deny",
            "executed": False, "scope_authorized": False,
        }],
        "tool_selection": {"selected": ["search"], "reference_best": ["search"]},
        "model_selection": {"selected": ["reasoning-model-v1"], "reference_best": ["reasoning-model-v1"]},
        "control_loop": {
            "required_phases": ["understand", "plan", "act", "observe", "verify"],
            "observed_phases": ["understand", "plan", "act", "observe", "verify"],
            "failure_injected": False,
        },
        "memory": {
            "consent_granted": True, "retrieved_ids": ["memory-1"],
            "relevant_ids": ["memory-1"], "stale_ids": [],
            "stale_flagged_ids": [], "provenance_ids": ["memory-1"],
        },
        "learning": {
            "baseline_holdout_scores": [68, 70, 72],
            "post_training_holdout_scores": [72, 74, 76],
            "holdout_fixture_version": "holdout-v1",
            "target_gain_points": 4, "checkpoint_hash": "sha256:abc",
            "training_run_id": "train-1",
            "data_permission": True, "isolated_training": True,
            "teacher_terms_verified": True,
            "regression_tests_passed": True,
        },
        "performance": {"latency_ms": 1000, "throughput_tasks_per_minute": 6,
                         "tokens": 200, "tool_calls": 1, "cost_usd": 0.01},
    }


def record():
    wrapper = candidate(80)
    wrapper["performance"]["latency_ms"] = 2000
    wrapper["performance"]["throughput_tasks_per_minute"] = 3
    student = candidate(84)
    student["performance"]["latency_ms"] = 1500
    return {
        "schema": "dreamco.buddy_task_evaluation_input.v1",
        "evaluation_id": "eval-1",
        "task": {
            "task_id": "task-1", "fixture_version": "fixture-v1",
            "acceptance_criteria": ["correct answer"], "input_digest": "sha256:input",
            "prompt_version": "prompt-v1", "task_fingerprint": "sha256:task-fixture",
            "expected_actions": [{"action_id": "search_docs"}],
        },
        "metadata": {
            "dataset_version": "dataset-v1", "evaluator_version": "eval-rubric-v1",
            "environment": "sandbox", "model_and_provider_versions": {"buddy": "local-v1"},
            "measurement_method": "fixed-fixture", "timestamp": "2026-11-03T12:00:00Z",
            "concurrency": 1, "cache_state": "cold",
        },
        "candidates": {
            "buddy": candidate(92),
            "wrapper_baseline": wrapper,
            "distilled_student": student,
        },
    }


class TaskEvaluationTests(unittest.TestCase):
    def test_scores_requested_dimensions_and_same_task_comparisons(self):
        result = evaluate_task(record())
        buddy = result["candidates"]["buddy"]
        self.assertEqual(buddy["status"], "pass")
        self.assertEqual(buddy["quality_score"], 95.2)
        self.assertEqual(buddy["learning_score"], 100)
        self.assertEqual(result["comparison"]["buddy_minus_wrapper_quality_points"], 7.2)
        self.assertEqual(result["comparison"]["buddy_minus_student_quality_points"], 4.8)
        self.assertEqual(result["comparison"]["buddy_efficiency_vs_wrapper"]["latency_ms"], 2.0)
        self.assertEqual(result["comparison"]["buddy_efficiency_vs_wrapper"]["throughput_tasks_per_minute"], 2.0)
        self.assertIs(buddy["hard_gates"]["permissions"], True)


    def test_unauthorized_action_fails_even_when_quality_is_high(self):
        item = record()
        item["candidates"]["buddy"]["action_events"][0]["scope_authorized"] = False
        result = evaluate_task(item)
        self.assertEqual(result["candidates"]["buddy"]["status"], "fail")
        self.assertIs(result["candidates"]["buddy"]["hard_gates"]["permissions"], False)


    def test_missing_evidence_and_reproduction_data_are_blocked_not_scored_as_success(self):
        item = record()
        item["candidates"]["buddy"]["evidence_refs"] = []
        item["metadata"].pop("cache_state")
        result = evaluate_task(item)
        buddy = result["candidates"]["buddy"]
        self.assertEqual(buddy["status"], "blocked")
        self.assertIsNone(buddy["hard_gates"]["evidence"])
        self.assertIsNone(buddy["hard_gates"]["reproducibility"])
        self.assertEqual(result["missing_reproducibility_metadata"], ["cache_state"])


    def test_learning_score_requires_checkpoint_and_permission_evidence(self):
        item = record()
        learning = item["candidates"]["buddy"]["learning"]
        learning["checkpoint_hash"] = ""
        self.assertIsNone(evaluate_task(item)["candidates"]["buddy"]["learning_score"])
        learning["checkpoint_hash"] = "sha256:abc"
        learning["data_permission"] = False
        self.assertEqual(evaluate_task(item)["candidates"]["buddy"]["learning_score"], 0)

    def test_learning_score_requires_paired_holdout_runs(self):
        item = record()
        learning = item["candidates"]["buddy"]["learning"]
        learning["post_training_holdout_scores"] = [72, 74]
        self.assertIsNone(evaluate_task(item)["candidates"]["buddy"]["learning_score"])
        learning["post_training_holdout_scores"] = [72, 74, 76]
        self.assertEqual(evaluate_task(item)["candidates"]["buddy"]["learning_score"], 100)


    def test_control_loop_recovery_is_measured_and_memory_requires_consent(self):
        item = record()
        run = item["candidates"]["buddy"]
        run["control_loop"]["failure_injected"] = True
        run["control_loop"]["recovered"] = False
        run["memory"]["consent_granted"] = False
        result = evaluate_task(item)["candidates"]["buddy"]
        self.assertLess(result["quality_dimensions"]["control_loop"], 100)
        self.assertEqual(result["quality_dimensions"]["memory_use"], 0)
        self.assertIs(result["hard_gates"]["memory_safety"], False)
        self.assertEqual(result["status"], "fail")


    def test_unknown_scores_stay_blocked_and_schema_is_enforced(self):
        item = record()
        item["candidates"]["buddy"]["quality_dimensions"].pop("task_perception")
        self.assertEqual(evaluate_task(item)["candidates"]["buddy"]["status"], "blocked")
        item["schema"] = "wrong"
        with self.assertRaisesRegex(ValueError, "unsupported task evaluation schema"):
            evaluate_task(item)

    def test_critical_dimension_floor_cannot_be_hidden_by_aggregate_score(self):
        item = record()
        dimensions = item["candidates"]["buddy"]["quality_dimensions"]
        dimensions["task_perception"] = 20
        dimensions["memory_use"] = 100
        result = evaluate_task(item)["candidates"]["buddy"]
        self.assertGreater(result["quality_score"], 75)
        self.assertEqual(result["status"], "fail")
        self.assertIs(result["hard_gates"]["critical_quality_floor"], False)

    def test_failure_gate_takes_precedence_over_unmeasured_dimensions(self):
        item = record()
        run = item["candidates"]["buddy"]
        run["acceptance_passed"] = False
        run["quality_dimensions"].pop("task_perception")
        result = evaluate_task(item)["candidates"]["buddy"]
        self.assertEqual(result["status"], "fail")
        self.assertIn("acceptance", result["failed_gates"])

    def test_critical_dimensions_cannot_be_excluded_from_fixture(self):
        item = record()
        item["candidates"]["buddy"]["applicable_dimensions"] = [
            "step_planning", "reasoning_quality", "response_quality",
        ]
        with self.assertRaisesRegex(ValueError, "critical dimensions cannot be marked inapplicable"):
            evaluate_task(item)

    def test_comparison_rejects_candidates_on_different_task_fixture(self):
        item = record()
        item["candidates"]["distilled_student"]["task_fingerprint"] = "sha256:different"
        with self.assertRaisesRegex(ValueError, "does not match the shared task fixture"):
            evaluate_task(item)
