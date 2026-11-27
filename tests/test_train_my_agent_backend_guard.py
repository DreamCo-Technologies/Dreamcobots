import tempfile
import unittest
from pathlib import Path

from scripts.dreamco_model_foundry import build_buyer_foundry_kit, load_divisions
from scripts.train_my_agent import preflight


class TrainMyAgentBackendGuardTests(unittest.TestCase):
    def test_preflight_reports_disabled_backend_without_starting_training(self):
        with tempfile.TemporaryDirectory() as tmp:
            kit = build_buyer_foundry_kit("45m-edge", load_divisions()[0], Path(tmp))
            result = preflight(kit, execute=True)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["training_started"])
        self.assertFalse(result["paid_compute_requested"])
        self.assertFalse(result["customer_data_uploaded"])
        self.assertTrue(any("backend adapter" in blocker.lower() for blocker in result["blockers"]))


if __name__ == "__main__":
    unittest.main()
