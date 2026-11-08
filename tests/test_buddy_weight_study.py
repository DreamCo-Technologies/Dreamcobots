import unittest
from buddy.certification.weight_study import study_models

class WeightStudyTests(unittest.TestCase):
    def test_requires_permission_even_with_permissive_license(self):
        report = study_models([{"model_id": "org/model", "revision": "abc123", "license": "apache-2.0", "parameters": 1000000000}])
        self.assertTrue(report["models"][0]["license_review_required"])
        self.assertFalse(report["models"][0]["local_training_approved"])
        self.assertFalse(report["training_executed"])

    def test_memory_estimate_and_permission(self):
        entry = {"model_id": "org/model", "revision": "abc", "license": "mit", "parameters": 1000000000, "derivative_training_permitted": True}
        report = study_models([entry])
        self.assertEqual(report["models"][0]["estimated_weight_memory_gb"]["4"], 0.65)
        self.assertFalse(report["models"][0]["license_review_required"])
        self.assertTrue(report["models"][0]["local_inference_candidate_4bit"])

    def test_invalid_records_skipped(self):
        self.assertEqual(study_models([{"model_id": "bad"}])["count"], 0)

    def test_deterministic(self):
        data = [{"model_id": "org/model", "revision": "v1", "license": "unknown", "parameters": 500000000}]
        self.assertEqual(study_models(data), study_models(data))

    def test_invalid_memory_budget(self):
        with self.assertRaises(ValueError):
            study_models([], memory_gb=0)

if __name__ == "__main__":
    unittest.main()
