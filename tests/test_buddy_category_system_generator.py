from __future__ import annotations

import unittest
from pathlib import Path

from tools.generate_buddy_category_system_registry import build


class BuddyCategorySystemGeneratorTests(unittest.TestCase):
    def test_study_catalogs_are_fully_represented(self):
        root = Path(__file__).resolve().parents[1]
        registry = build(root)
        import json
        mirror = json.loads((root / "website/data/category-system-registry.json").read_text(encoding="utf-8"))
        self.assertEqual(registry, mirror)
        expected = set()
        for path in sorted((root / "config").glob("buddy-study-resources-*.json")):
            import json
            payload = json.loads(path.read_text(encoding="utf-8"))
            expected.update(row[2] for row in payload["resources"])
        actual = {
            item["category"] for item in registry["systems"]
            if item.get("group") == "study"
        }
        self.assertEqual(actual, expected)
        self.assertEqual(registry["counts"]["study_categories"], len(expected))

    def test_study_records_retain_exact_source_ids_and_files(self):
        root = Path(__file__).resolve().parents[1]
        registry = build(root)
        for item in registry["systems"]:
            if item.get("group") != "study":
                continue
            self.assertEqual(item["source_item_count"], len(item["source_resource_ids"]))
            self.assertTrue(item["source_files"])
            self.assertEqual(item["lifecycle_status"], "catalogued")
            self.assertEqual(item["verification_status"], "not_verified")
            self.assertTrue(item["contract"]["mission"])

    def test_generator_does_not_claim_runtime_implementation(self):
        root = Path(__file__).resolve().parents[1]
        registry, _ = build(root)
        self.assertTrue(all(
            item["implementation_status"] == "not_implemented"
            for item in registry["systems"] if item.get("group") == "study"
        ))


if __name__ == "__main__":
    unittest.main()
