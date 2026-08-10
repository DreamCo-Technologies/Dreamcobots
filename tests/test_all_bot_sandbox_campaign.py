import unittest

from tools.run_all_bot_sandbox_campaign import load, main, OUT, CURRICULUM


class AllBotSandboxCampaignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        main()
        cls.campaign = load(OUT, {})
        cls.curriculum = load(CURRICULUM, {})

    def test_all_canonical_bots_have_sandbox_records(self):
        self.assertEqual(self.campaign["canonical_bot_count"], 1051)
        self.assertTrue(self.campaign["all_bots_have_active_sandbox_record"])
        self.assertEqual(len(self.campaign["bots"]), 1051)

    def test_every_declared_capability_has_campaign_state(self):
        expected = self.curriculum["declared_capability_count"]
        actual = sum(len(bot["capabilities"]) for bot in self.campaign["bots"])
        self.assertEqual(actual, expected)
        for bot in self.campaign["bots"]:
            for capability in bot["capabilities"]:
                self.assertIn(capability["state"], {"passing", "fixture_ready", "gap_found"})

    def test_nonpassing_capabilities_receive_gap_workers(self):
        indexed = {gap["gap_id"]: gap for gap in self.campaign["gaps"]}
        for bot in self.campaign["bots"]:
            for capability in bot["capabilities"]:
                if capability["state"] == "passing":
                    self.assertIsNone(capability["gap_id"])
                    continue
                self.assertIn(capability["gap_id"], indexed)
                gap = indexed[capability["gap_id"]]
                self.assertEqual(gap["status"], "active_gap_worker_assigned")
                self.assertEqual(gap["worker"]["execution_mode"], "sandbox")
                self.assertFalse(gap["worker"]["live_external_actions"])

    def test_campaign_is_cost_and_side_effect_bounded(self):
        self.assertEqual(self.campaign["maximum_parallel_gap_workers"], 32)
        self.assertEqual(self.campaign["live_external_actions_executed"], 0)
        self.assertEqual(self.campaign["paid_model_calls_executed"], 0)
        self.assertTrue(self.campaign["shared_fix_first"])


if __name__ == "__main__":
    unittest.main()
