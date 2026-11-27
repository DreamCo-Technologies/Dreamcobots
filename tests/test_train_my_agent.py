import json
import tempfile
import unittest
from pathlib import Path
from scripts.dreamco_model_foundry import build_buyer_foundry_kit, load_divisions
from scripts.train_my_agent import preflight

class TrainMyAgentTests(unittest.TestCase):
    def test_preflight_never_starts_training_without_approved_data_and_backend(self):
        with tempfile.TemporaryDirectory() as tmp:
            kit = build_buyer_foundry_kit("45m-edge", load_divisions()[0], Path(tmp))
            result = preflight(kit, execute=True)
            self.assertEqual(result["status"], "BLOCKED")
            self.assertFalse(result["training_started"])
            self.assertFalse(result["paid_compute_requested"])
            self.assertFalse(result["customer_data_uploaded"])
            self.assertTrue(result["blockers"])

    def test_manifest_must_explicitly_exclude_pretrained_weights(self):
        with tempfile.TemporaryDirectory() as tmp:
            kit = build_buyer_foundry_kit("45m-edge", load_divisions()[0], Path(tmp))
            path = kit / "BUYER_MANIFEST.json"
            manifest = json.loads(path.read_text())
            manifest["weights_included"] = True
            path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "weights"):
                preflight(kit)

if __name__ == "__main__":
    unittest.main()
