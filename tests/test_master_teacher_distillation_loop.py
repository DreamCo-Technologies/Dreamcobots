import unittest
from tools.master_teacher_distillation_loop import distill

class DistillationTests(unittest.TestCase):
    def setUp(self):
        self.row = {"authorized": True, "privacy_reviewed": True, "holdout": False,
                    "contains_answer_key": False, "sensitive": False,
                    "capability": "debugging", "failure_mode": "missing dependency",
                    "repair": "declare dependencies", "regression_test": "import check",
                    "source_ref": "approved-run-1"}

    def test_deduplicates(self):
        self.assertEqual(len(distill([self.row, dict(self.row)])["candidate_lessons"]), 1)

    def test_rejects_unreviewed(self):
        self.assertEqual(distill([{**self.row, "privacy_reviewed": False}])["rejected_records"], 1)

    def test_rejects_holdouts(self):
        self.assertEqual(distill([{**self.row, "holdout": True}])["rejected_records"], 1)

    def test_rejects_unknown_sensitivity(self):
        row = dict(self.row)
        del row["sensitive"]
        self.assertEqual(distill([row])["rejected_records"], 1)

    def test_no_training_claim(self):
        result = distill([self.row])
        self.assertFalse(result["model_training_executed"])
        self.assertFalse(result["mastery_claimed"])

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            distill({})

if __name__ == "__main__":
    unittest.main()
