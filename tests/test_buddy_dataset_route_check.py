import json
import unittest

from tools.build_buddy_dataset_routes import matches_existing, build


class DatasetRouteCheckTests(unittest.TestCase):
    def test_generation_timestamp_does_not_make_artifact_stale(self):
        payload = {"generated_at": "new-run-time", "masterbot_count": 65, "routes": []}
        existing = {"generated_at": "previous-run-time", "masterbot_count": 65, "routes": []}
        encoded = json.dumps(existing, indent=2, ensure_ascii=False) + "\n"
        self.assertTrue(matches_existing(payload, encoded))

    def test_real_content_drift_is_still_detected(self):
        payload = {"generated_at": "new-run-time", "masterbot_count": 65, "routes": []}
        existing = {"generated_at": "previous-run-time", "masterbot_count": 64, "routes": []}
        encoded = json.dumps(existing, indent=2, ensure_ascii=False) + "\n"
        self.assertFalse(matches_existing(payload, encoded))

    def test_malformed_existing_artifact_is_stale(self):
        self.assertFalse(matches_existing({"generated_at": "now"}, "not json"))

    def test_catalog_train_hint_never_becomes_training_eligibility(self):
        payload = build()
        self.assertEqual(payload["masterbot_count"], 65)
        for route in payload["routes"]:
            for candidate in route["candidates"]:
                self.assertIn("source_catalog_train_hint", candidate)
                self.assertFalse(candidate["training_eligible"])
                self.assertEqual(candidate["training_status"], "DISCOVERY_ONLY_NOT_TRAINING_APPROVED")
                self.assertEqual(candidate["rights_status"], "UNVERIFIED_DATASET_CARD_AND_TERMS_REQUIRED")


if __name__ == "__main__":
    unittest.main()
