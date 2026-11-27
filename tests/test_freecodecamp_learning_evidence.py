import unittest
from tools.validate_freecodecamp_learning_evidence import evaluate_learning_record

class FreeCodeCampLearningEvidenceTests(unittest.TestCase):
    def evaluate(self, record):
        catalog = {
            "schema": "dreamco.freecodecamp_catalog.v1",
            "source": {"channel_id": "UC8butISFwT-Wl7EV0hUK0BQ"},
            "videos": [{
                "video_id": "video-123",
                "url": "https://www.youtube.com/watch?v=video-123",
            }],
        }
        return evaluate_learning_record(record, catalog=catalog)

    def record(self):
        return {
            "schema": "dreamco.freecodecamp_learning_evidence.v1",
            "video_id": "video-123",
            "source_url": "https://www.youtube.com/watch?v=video-123",
            "division_id": 1,
            "rights": {"verified": True, "evidence_ref": "owner-review-123"},
            "study": {"completed": True, "minutes": 45, "attestation_ref": "study-session-123", "original_notes_sha256": "a" * 64},
            "sandbox": {"passed": True, "exercise_id": "exercise-1", "result_sha256": "b" * 64},
            "benchmark": {"target_passed": True, "holdout_passed": True, "regression_passed": True,
                          "target_run_id": "run-1", "holdout_run_id": "run-2", "regression_run_id": "run-3"},
        }

    def test_complete_evidence_can_mark_division_capability_mastered(self):
        result = self.evaluate(self.record())
        self.assertEqual(result["status"], "mastered")
        self.assertTrue(all(result["gates"].values()))
        self.assertFalse(result["model_training_authorized"])

    def test_public_catalog_entry_alone_is_not_studied(self):
        record = self.record()
        record["rights"] = {}
        record["study"] = {}
        result = self.evaluate(record)
        self.assertEqual(result["status"], "rights_pending")

    def test_study_without_sandbox_and_benchmarks_is_not_mastery(self):
        record = self.record()
        record["sandbox"] = {}
        record["benchmark"] = {}
        result = self.evaluate(record)
        self.assertEqual(result["status"], "studied_unverified")

    def test_study_evidence_requires_original_notes_hash_and_attestation(self):
        record = self.record()
        record["study"]["original_notes_sha256"] = "not-a-hash"
        self.assertEqual(self.evaluate(record)["status"], "study_pending")

    def test_mismatched_catalog_video_or_url_cannot_be_mastered(self):
        record = self.record()
        record["source_url"] = "https://www.youtube.com/watch?v=not-video-123"
        result = self.evaluate(record)
        self.assertEqual(result["status"], "source_unverified")
        self.assertFalse(result["gates"]["source_catalog_match"])

        record = self.record()
        record["video_id"] = "not-video-123"
        result = self.evaluate(record)
        self.assertEqual(result["status"], "source_unverified")

    def test_rejects_invalid_division_id_and_schema(self):
        record = self.record()
        record["division_id"] = 66
        with self.assertRaisesRegex(ValueError, "65 canonical"):
            evaluate_learning_record(record)
        record = self.record()
        record["schema"] = "unknown"
        with self.assertRaisesRegex(ValueError, "schema"):
            evaluate_learning_record(record)

if __name__ == "__main__":
    unittest.main()
