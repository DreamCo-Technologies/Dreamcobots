import json
import unittest

from tools.build_buddy_dataset_routes import matches_existing


class DatasetRouteCheckTests(unittest.TestCase):
    def test_generation_timestamp_does_not_make_artifact_stale(self):
        payload = {"generated_at": "new-run-time", "masterbot_count": 65, "routes": []}
        existing = {"generated_at": "previous-run-time", "masterbot_count": 65, "routes": []}
        self.assertTrue(matches_existing(payload, json.dumps(existing, indent=2, ensure_ascii=False) + "\n"))

    def test_real_content_drift_is_still_detected(self):
        payload = {"generated_at": "new-run-time", "masterbot_count": 65, "routes": []}
        existing = {"generated_at": "previous-run-time", "masterbot_count": 64, "routes": []}
        self.assertFalse(matches_existing(payload, json.dumps(existing, indent=2, ensure_ascii=False) + "\n"))

    def test_malformed_existing_artifact_is_stale(self):
        self.assertFalse(matches_existing({"generated_at": "now"}, "not json"))


if __name__ == "__main__":
    unittest.main()
