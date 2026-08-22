from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]


class UserTestingCatalogTests(unittest.TestCase):
    def test_catalog_exists_and_distinguishes_live_testing(self):
        text = (ROOT / "docs/BUDDY_USER_TESTING_CATALOG.md").read_text(encoding="utf-8")
        self.assertIn("PASS-SANDBOX", text)
        self.assertIn("NEEDS-LIVE", text)
        self.assertIn("MASTERED", text)
        self.assertIn("Buddy Actions end-to-end user journey", text)
        self.assertIn("Canary deployment + rollback", text)

    def test_user_result_schema_requires_evidence(self):
        payload = json.loads((ROOT / "buddy_os/benchmarks/user_test_result.schema.json").read_text(encoding="utf-8"))
        self.assertIn("passed", payload["required"])
        self.assertIn("evidence", payload["required"])
        self.assertIn("environment", payload["required"])


if __name__ == "__main__":
    unittest.main()
