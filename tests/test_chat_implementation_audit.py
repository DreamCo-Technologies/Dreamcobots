import copy
import unittest

from tools.chat_implementation_audit import archive_eligibility


class ChatArchiveEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.conversation = {
            "id": "chat-a", "source": {"complete": True,
                "semantic_review_complete": True, "attachments_complete": True},
            "messages": [{"id": "message-a", "sha256": "a" * 64,
                "reviewed": True, "requirement_ids": ["R1"]}],
            "requirements": [{"id": "R1", "status": "implemented",
                "requires_real_execution": True,
                "evidence": {"code_refs": ["example.py:10"], "commit": "b" * 40,
                    "deployed_commit": "b" * 40, "acceptance_verified": True,
                    "reviewed": True, "test_result": "passed", "test_artifact": "test.json",
                    "live_verified": True, "live_artifact": "live.json", "execution_mode": "real"}}]}

    def test_complete_contract_is_candidate_without_action_or_mutation(self):
        original = copy.deepcopy(self.conversation)
        result = archive_eligibility(self.conversation)
        self.assertTrue(result["archive_candidate"])
        self.assertEqual(result["action_taken"], "none")
        self.assertEqual(original, self.conversation)

    def test_incomplete_source_blocks_even_passing_implementation(self):
        self.conversation["source"]["attachments_complete"] = False
        self.assertIn("source_attachments_complete_unverified", archive_eligibility(self.conversation)["blockers"])

    def test_undocumented_short_approval_is_not_silently_discarded(self):
        self.conversation["messages"][0]["requirement_ids"] = []
        self.assertFalse(archive_eligibility(self.conversation)["archive_candidate"])

    def test_catalog_or_plan_does_not_prove_implementation(self):
        self.conversation["requirements"][0]["status"] = "source_present"
        self.assertFalse(archive_eligibility(self.conversation)["archive_candidate"])

    def test_pass_on_different_commit_does_not_prove_live_revision(self):
        self.conversation["requirements"][0]["evidence"]["deployed_commit"] = "c" * 40
        self.assertFalse(archive_eligibility(self.conversation)["archive_candidate"])

    def test_simulation_does_not_prove_real_bot_execution(self):
        self.conversation["requirements"][0]["evidence"]["execution_mode"] = "simulation"
        self.assertFalse(archive_eligibility(self.conversation)["archive_candidate"])

    def test_missing_inventory_and_unreviewed_test_block(self):
        self.assertFalse(archive_eligibility({})["archive_candidate"])
        self.conversation["requirements"][0]["evidence"]["reviewed"] = False
        self.assertFalse(archive_eligibility(self.conversation)["archive_candidate"])


if __name__ == "__main__":
    unittest.main()
