"""CommandCore smoke tests for its internal Bootcamp route and scheduler."""
import unittest

from tools.smoke_commandcore_bootcamp import run_smoke


class CommandCoreBootcampSmokeTests(unittest.TestCase):
    def test_commandcore_routes_to_its_dreamco_bootcamp_course(self):
        report = run_smoke()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["course_track_id"], "dreamco-division-specialist")
        self.assertEqual(report["course_lesson_count"], 6)
        self.assertEqual(report["runtime_queue_lesson_count"], 6)
        self.assertEqual(report["runtime_queue_track_ids"], ["dreamco-division-specialist"])
        self.assertTrue(report["exercise_ids"])
        self.assertTrue(report["project_ids"])
        self.assertTrue(report["assessment_ids"])
        self.assertTrue(report["retraining_policy_id"])
        self.assertFalse(report["learner_external_routing"])
        self.assertFalse(report["model_fallback_used"])

    def test_smoke_does_not_claim_model_training_or_full_capability_mastery(self):
        report = run_smoke()
        self.assertFalse(report["model_weight_training_authorized"])
        self.assertEqual(report["capability_runtime_status"], "not_verified")
        self.assertEqual(report["mastery_status"], "not_claimed")
        self.assertEqual(report["certification_status"], "not_certified")


if __name__ == "__main__":
    unittest.main()
