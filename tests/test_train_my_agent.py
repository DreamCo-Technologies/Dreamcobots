"""Direct regression coverage for the buyer training preflight entry point."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.dreamco_model_foundry import build_buyer_foundry_kit, load_divisions
from scripts.train_my_agent import preflight


class TrainMyAgentPreflightTests(unittest.TestCase):
    def test_execute_request_fails_closed_without_backend(self):
        with tempfile.TemporaryDirectory() as tmp:
            kit = build_buyer_foundry_kit("45m-edge", load_divisions()[0], Path(tmp))
            result = preflight(kit, execute=True)
            self.assertEqual(result["status"], "BLOCKED")
            self.assertFalse(result["training_started"])
            self.assertFalse(result["paid_compute_requested"])
            self.assertFalse(result["customer_data_uploaded"])
            self.assertTrue(any("backend" in item.lower() for item in result["blockers"]))

    def test_manifest_with_included_weights_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            kit = build_buyer_foundry_kit("45m-edge", load_divisions()[0], Path(tmp))
            manifest_path = kit / "BUYER_MANIFEST.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["weights_included"] = True
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "weight status"):
                preflight(kit, execute=True)

    def test_preflight_never_claims_training_or_customer_data_upload(self):
        with tempfile.TemporaryDirectory() as tmp:
            kit = build_buyer_foundry_kit("45m-edge", load_divisions()[0], Path(tmp))
            result = preflight(kit, execute=False)
            self.assertFalse(result["training_started"])
            self.assertFalse(result["paid_compute_requested"])
            self.assertFalse(result["customer_data_uploaded"])

    def test_incomplete_kit_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "Incomplete buyer kit"):
                preflight(Path(tmp), execute=True)


if __name__ == "__main__":
    unittest.main()
