import unittest

from tools.dreamco_10pillar_orchestrator import run


class DreamCo10PillarOrchestratorTests(unittest.TestCase):
    def test_curriculum_command_dispatches_to_practice_scheduler(self):
        result = run("curriculum", {
            "scope_type": "domain_division",
            "scope_id": "dreamcodelab",
            "pass_rate": 0.96,
        })
        self.assertEqual(result["scope_id"], "dreamcodelab")
        self.assertEqual(result["difficulty"], 1.1)

    def test_500_model_command_does_not_invent_models_or_execute(self):
        inventory = {
            "schema": "dreamco.verified_model_inventory.v1",
            "status": "EMPTY_PENDING_MODEL_AND_RIGHTS_REVIEW",
            "expected_model_count": 500,
            "models": [],
        }
        result = run("plan-500", inventory)
        self.assertEqual(result["status"], "BLOCKED_NO_VERIFIED_500_MODEL_INVENTORY")
        self.assertEqual(result["verified_model_records"], 0)
        self.assertFalse(result["execution_started"])
        self.assertEqual(result["provider_calls"], 0)


if __name__ == "__main__":
    unittest.main()
