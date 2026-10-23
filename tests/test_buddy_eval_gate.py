"""Contract tests for Buddy offline model evaluation; no model inference."""
import copy
import unittest
from buddy.eval_gate import evaluate


def fixtures():
    cases = [
        {"id": "h1", "source_id": "source-a", "expected": "4",
         "license": "owner_created", "provenance": "synthetic fixture",
         "split": "holdout", "consent": True, "privacy_safe": True,
         "division": "DreamEducation", "task": "math"},
        {"id": "h2", "source_id": "source-b", "expected": "yes",
         "license": "owner_created", "provenance": "synthetic fixture",
         "split": "holdout", "consent": True, "privacy_safe": True,
         "division": "DreamEducation", "task": "math"},
    ]
    return cases, {"h1": "4", "h2": "no"}, {"h1": "4", "h2": "yes"}


def run(cases=None, baseline=None, candidate=None, **options):
    a, b, c = fixtures()
    return evaluate(a if cases is None else cases,
                    b if baseline is None else baseline,
                    c if candidate is None else candidate,
                    division="DreamEducation", task="math",
                    model_id="synthetic-fixture", **options)


class EvaluationGateTests(unittest.TestCase):
    def test_candidate_improvement_passes(self):
        receipt = run(min_accuracy=0.75)
        self.assertTrue(receipt["gate_passed"])
        self.assertEqual(receipt["candidate_accuracy"], 1.0)
        self.assertFalse(receipt["production_verified"])

    def test_regression_fails(self):
        self.assertFalse(run(candidate={"h1": "no", "h2": "no"}, min_accuracy=0.0)["gate_passed"])

    def test_missing_prediction_rejected(self):
        with self.assertRaises(ValueError):
            run(candidate={"h1": "4"})

    def test_train_split_rejected(self):
        cases, _, _ = fixtures()
        cases[0]["split"] = "train"
        with self.assertRaises(ValueError):
            run(cases=cases)

    def test_missing_consent_rejected(self):
        cases, _, _ = fixtures()
        cases[0]["consent"] = False
        with self.assertRaises(ValueError):
            run(cases=cases)

    def test_duplicate_source_rejected(self):
        cases, _, _ = fixtures()
        cases[1]["source_id"] = cases[0]["source_id"]
        with self.assertRaises(ValueError):
            run(cases=cases)

    def test_unreviewed_license_rejected(self):
        cases, _, _ = fixtures()
        cases[0]["license"] = "unknown"
        with self.assertRaises(ValueError):
            run(cases=cases)

    def test_deterministic_receipt(self):
        self.assertEqual(run(), run())


if __name__ == "__main__":
    unittest.main()
