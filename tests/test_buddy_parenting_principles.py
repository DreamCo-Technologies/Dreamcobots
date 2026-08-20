import json
from pathlib import Path
import unittest

class BuddyParentingPrinciplesTests(unittest.TestCase):
    def test_actions_manifest_is_valid_and_has_core_guards(self):
        path = Path("website/data/buddy-parenting-principles-actions.json")
        data = json.loads(path.read_text())
        ids = {item["id"] for item in data["actions"]}
        for required in {"learn-from-failure", "protect-regressions", "specialist-routing", "sandbox-first", "human-approval", "audit-trail"}:
            self.assertIn(required, ids)

if __name__ == "__main__":
    unittest.main()
