import unittest
from tools.buddy_paired_inference import evaluate_pair
from tools.buddy_reverse_engineering import study_record

class BuddyInferenceTests(unittest.TestCase):
    def test_paired_correctness(self):
        cases = [{"id": "sample", "input": "x", "expected": "x", "authorized": True}]
        result = evaluate_pair(cases, lambda x: "wrong", lambda x: x)
        self.assertEqual(len(result["trials"]), 3)
        self.assertEqual(result["paired_accuracy_delta"], 1)
        self.assertFalse(result["independent_verification"])

    def test_reject_protected_holdout(self):
        with self.assertRaises(ValueError):
            evaluate_pair([{"id":"secret","input":"x","expected":"x","authorized":True,"protected_holdout":True}], lambda x:x, lambda x:x)

    def test_reject_unauthorized_target(self):
        with self.assertRaises(PermissionError):
            study_record("target", False, [{"claim":"a","evidence":"b","limitations":"c"}],
                         {"suite":"s","baseline":0,"metric":"accuracy","measurement":1,"cost":0,"safety":"review"})

    def test_evidence_required(self):
        with self.assertRaises(ValueError):
            study_record("target", True, [{"claim":"unsupported"}],
                         {"suite":"s","baseline":0,"metric":"accuracy","measurement":1,"cost":0,"safety":"review"})

if __name__ == "__main__":
    unittest.main()
