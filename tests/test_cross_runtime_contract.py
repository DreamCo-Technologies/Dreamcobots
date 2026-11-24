import json
import unittest
from pathlib import Path

from tools.validate_cross_runtime_contract import CONTRACT, validate


class CrossRuntimeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_canonical_contract_is_valid(self):
        self.assertEqual(validate(self.data), [])

    def test_requires_both_implementations(self):
        data = json.loads(json.dumps(self.data))
        data["implementations"] = [data["implementations"][0]]
        self.assertTrue(any("both canonical" in error for error in validate(data)))

    def test_cannot_start_c_before_contract_freeze(self):
        data = json.loads(json.dumps(self.data))
        data["completion_order"].remove("freeze_versioned_shared_contracts")
        self.assertTrue(any("C runtime work" in error for error in validate(data)))

    def test_planning_is_not_training(self):
        data = json.loads(json.dumps(self.data))
        data["training"]["scheduled_planning_is_not_training"] = False
        self.assertTrue(any("planning must remain" in error for error in validate(data)))

    def test_private_chat_and_credentials_are_excluded(self):
        data = json.loads(json.dumps(self.data))
        data["integration"]["no_credentials_or_private_chat_transcripts_in_git"] = False
        self.assertTrue(any("private chat" in error for error in validate(data)))


if __name__ == "__main__":
    unittest.main()
