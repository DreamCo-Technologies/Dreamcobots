import unittest

from continuous_learning_controller import EventType, LearningEvent, evaluate_event


class ContinuousLearningControllerTest(unittest.TestCase):
    def make_event(self, **overrides):
        values = {
            "event_id": "event-1",
            "event_type": EventType.BENCHMARK,
            "capability": "coding",
            "success": True,
            "verified": True,
            "regression_passed": True,
            "safety_passed": True,
            "external_assistance": False,
            "evidence_refs": ("artifact://runs/run-1/evidence.json",),
            "run_id": "run-1",
            "commit_sha": "a" * 40,
            "baseline_ref": "artifact://runs/run-1/baseline.json",
            "holdout_ref": "artifact://runs/run-1/holdout.json",
            "regression_ref": "artifact://runs/run-1/regression.json",
            "safety_ref": "artifact://runs/run-1/safety.json",
        }
        values.update(overrides)
        return LearningEvent(**values)

    def test_verified_success_with_complete_provenance_can_promote(self):
        decision = evaluate_event(self.make_event())
        self.assertTrue(decision.learn)
        self.assertTrue(decision.promote)

    def test_missing_artifact_provenance_blocks_promotion(self):
        decision = evaluate_event(self.make_event(evidence_refs=()))
        self.assertTrue(decision.learn)
        self.assertFalse(decision.promote)
        self.assertIn("evidence_refs", decision.reason)

    def test_missing_independent_holdout_blocks_promotion(self):
        decision = evaluate_event(self.make_event(holdout_ref=""))
        self.assertFalse(decision.promote)
        self.assertIn("holdout_ref", decision.reason)

    def test_invalid_commit_sha_blocks_promotion(self):
        decision = evaluate_event(self.make_event(commit_sha="main"))
        self.assertFalse(decision.promote)
        self.assertIn("commit_sha", decision.reason)

    def test_unverified_success_cannot_promote(self):
        decision = evaluate_event(self.make_event(verified=False))
        self.assertTrue(decision.learn)
        self.assertFalse(decision.promote)

    def test_verified_failure_cannot_promote(self):
        decision = evaluate_event(self.make_event(success=False))
        self.assertFalse(decision.promote)
        self.assertIn("verified failure", decision.reason)

    def test_regression_failure_blocks_promotion(self):
        decision = evaluate_event(self.make_event(regression_passed=False))
        self.assertFalse(decision.promote)
        self.assertIn("regression failure", decision.reason)

    def test_safety_failure_blocks_promotion(self):
        decision = evaluate_event(self.make_event(safety_passed=False))
        self.assertFalse(decision.promote)
        self.assertIn("safety failure", decision.reason)

    def test_external_assistance_still_requires_independent_evidence(self):
        assisted = evaluate_event(self.make_event(external_assistance=True))
        self.assertTrue(assisted.promote)
        unproven = evaluate_event(self.make_event(external_assistance=True, holdout_ref=""))
        self.assertFalse(unproven.promote)


if __name__ == "__main__":
    unittest.main()
