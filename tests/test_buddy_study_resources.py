import glob
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BuddyStudyResourcesTests(unittest.TestCase):
    def test_resources_are_unique_and_meet_operational_floor(self) -> None:
        policy = json.loads((ROOT / "config" / "buddy-study-resource-policy.json").read_text(encoding="utf-8"))
        files = sorted(glob.glob(str(ROOT / "config" / "buddy-study-resources-*.json")))
        self.assertTrue(files, "No Buddy study-resource catalogs found")
        ids = set()
        urls = set()
        total = 0
        for file_path in files:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            self.assertIsInstance(payload.get("resources"), list, f"Invalid resources list: {file_path}")
            for row in payload["resources"]:
                self.assertGreaterEqual(len(row), 6)
                self.assertIsInstance(row[0], int)
                self.assertTrue(row[3].startswith(("https://", "http://")))
                canonical = row[3].strip().rstrip("/").lower()
                self.assertNotIn(row[0], ids, f"Duplicate study resource ID: {row[0]}")
                self.assertNotIn(canonical, urls, f"Duplicate study resource URL: {row[3]}")
                ids.add(row[0])
                urls.add(canonical)
                total += 1
        minimum = int(policy.get("minimum_operational_count", policy.get("target_count", 0)))
        target = int(policy.get("target_count", minimum))
        self.assertGreaterEqual(total, minimum)
        self.assertLessEqual(total, target)


if __name__ == "__main__":
    unittest.main()
