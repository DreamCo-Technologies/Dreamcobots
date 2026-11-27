import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "config/dreamco-verified-goals-2027.json"

class VerifiedGoalsContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(FILE.read_text(encoding="utf-8"))

    def test_unique_100_capability_targets(self):
        tracks = self.data["tracks"]
        self.assertEqual(len(tracks), 10)
        ids = [item["id"] for track in tracks for item in track["capabilities"]]
        self.assertEqual(len(ids), 100)
        self.assertEqual(len(set(ids)), 100)

    def test_no_target_falsely_marked_verified(self):
        for track in self.data["tracks"]:
            for item in track["capabilities"]:
                self.assertEqual(item["state"], "planned_target")
                self.assertFalse(item["verified"])
                self.assertEqual(item["evidence"], [])

    def test_milestones_and_sources(self):
        self.assertEqual([m["day"] for m in self.data["milestones"]], [30, 60, 90, 120, 180, 270, 365])
        self.assertGreaterEqual(len(self.data["sources"]), 7)
        self.assertEqual(self.data["target_summary"]["verified_capabilities"], 100)

if __name__ == "__main__":
    unittest.main()
