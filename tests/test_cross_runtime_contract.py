import json
import unittest
from pathlib import Path

from tools.validate_cross_runtime_contract import CONTRACT, validate


class CrossRuntimeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_three_candidate_contract_is_valid(self):
        self.assertEqual(validate(self.data), [])

    def test_requires_python_c_and_swift(self):
        data = json.loads(json.dumps(self.data))
        data["implementations"] = data["implementations"][:2]
        self.assertTrue(any("must map to" in error or "all three runtime" in error for error in validate(data)))

    def test_candidate_paths_are_explicit_and_complete(self):
        data = json.loads(json.dumps(self.data))
        data["implementations"][1]["tracked_paths"].remove("core-c/CMakeLists.txt")
        self.assertTrue(any("apple-c is missing required tracked paths" in error for error in validate(data)))

    def test_competition_includes_all_three_candidates(self):
        data = json.loads(json.dumps(self.data))
        data["competition"]["runtime_candidates"].remove("apple-swift")
        self.assertTrue(any("include Python, C, and Swift" in error for error in validate(data)))

    def test_competition_requires_parity_and_eligibility_gates(self):
        data = json.loads(json.dumps(self.data))
        data["competition"]["parity_requirements"].remove("same_task_packets")
        data["competition"]["hard_gates"].remove("privacy_and_security")
        errors = validate(data)
        self.assertTrue(any("parity requirements" in error for error in errors))
        self.assertTrue(any("eligibility hard gates" in error for error in errors))

    def test_python_first_order_is_enforced(self):
        data = json.loads(json.dumps(self.data))
        data["completion_order"].reverse()
        self.assertTrue(any("out of order" in error for error in validate(data)))

    def test_c_and_swift_must_follow_contract_freeze(self):
        data = json.loads(json.dumps(self.data))
        data["completion_order"].remove("freeze_versioned_shared_contracts")
        self.assertTrue(any("missing one or more" in error for error in validate(data)))

    def test_competition_follows_both_apple_candidates(self):
        data = json.loads(json.dumps(self.data))
        data["completion_order"].remove("preserve_and_adapt_apple_swift_runtime_to_shared_contract_after_python_completion")
        self.assertTrue(any("missing one or more" in error for error in validate(data)))

    def test_planning_is_not_training(self):
        data = json.loads(json.dumps(self.data))
        data["training"]["scheduled_planning_is_not_training"] = False
        self.assertTrue(any("planning must remain" in error for error in validate(data)))

    def test_private_chat_and_credentials_are_excluded(self):
        data = json.loads(json.dumps(self.data))
        data["integration"]["no_credentials_or_private_chat_transcripts_in_git"] = False
        self.assertTrue(any("private chat" in error for error in validate(data)))

    def test_native_language_is_not_a_performance_claim(self):
        data = json.loads(json.dumps(self.data))
        data["truth_rules"]["native_language_does_not_imply_better_performance"] = False
        self.assertTrue(any("native language" in error for error in validate(data)))

    def test_incomparable_hardware_is_not_ranked_directly(self):
        data = json.loads(json.dumps(self.data))
        data["truth_rules"]["incomparable_hardware_results_must_not_be_ranked_as_direct_wins"] = False
        self.assertTrue(any("incomparable hardware" in error for error in validate(data)))


if __name__ == "__main__":
    unittest.main()
