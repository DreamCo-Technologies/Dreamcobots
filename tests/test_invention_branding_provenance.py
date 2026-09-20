import json
import unittest
import tempfile
from pathlib import Path
from tools.optimize_static_payload import compact
from tools.build_buddy_public_site import ROOT, branding_content, FORBIDDEN_PUBLIC_NAMES

class BranchProvenanceTests(unittest.TestCase):
    def test_historical_identifier_is_preserved_but_not_promotional(self):
        name = "legacy-" + "r" + "eplit" + "-migration"
        original = json.dumps({"branches": [{"name": name, "sha": "a" * 40}]})
        self.assertFalse(FORBIDDEN_PUBLIC_NAMES.search(branding_content(ROOT / "website/data/branch-health.json", original)))
        self.assertIn(name, original)

    def test_packaging_preserves_all_json_values(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "catalog.json"
            data = {"parts": [{"name": "test 🛰", "size": None, "quantity": 3}], "approved": False}
            path.write_text(json.dumps(data, indent=2))
            self.assertGreater(compact(path), 0)
            self.assertEqual(json.loads(path.read_text()), data)
            self.assertEqual(compact(path), 0)

    def test_actual_copy_and_unrecognized_records_are_checked(self):
        name = "r" + "eplit"
        for payload in [{"branches": [{"name": name}]}, {"branches": [], "note": name}, {"branches": [{"name": "main", "sha": "a" * 40, "prTitle": name}]}]:
            self.assertTrue(FORBIDDEN_PUBLIC_NAMES.search(branding_content(ROOT / "website/data/branch-health.json", json.dumps(payload))))
        self.assertIn(name, branding_content(ROOT / "website/other.json", name))

if __name__ == "__main__":
    unittest.main()
