import json
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from generate_division_model_manifest import build_manifest  # noqa: E402

class DivisionModelManifestTests(unittest.TestCase):
    def setUp(self):
        self.source_text = (ROOT / "config" / "masterbot-65-registry.json").read_text(encoding="utf-8")
        self.registry = json.loads(self.source_text)

    def test_manifest_covers_each_canonical_division_once(self):
        manifest = build_manifest(self.registry, self.source_text)
        self.assertEqual(manifest["division_count"], len(self.registry["divisions"]))
        self.assertEqual([r["division_id"] for r in manifest["records"]], [r["id"] for r in self.registry["divisions"]])
        self.assertEqual(len({r["model_id"] for r in manifest["records"]}), len(manifest["records"]))

    def test_inventory_never_claims_training_or_deployment(self):
        manifest = build_manifest(self.registry, self.source_text)
        self.assertEqual(manifest["status"], "inventory_only_not_trained")
        for row in manifest["records"]:
            self.assertEqual(row["lifecycle_state"], "planned")
            self.assertIsNone(row["training"]["checkpoint"])
            self.assertIsNone(row["serving"]["endpoint"])
            self.assertIsNone(row["release_evidence"]["license_review"])

    def test_registry_count_mismatch_is_rejected(self):
        bad = dict(self.registry)
        bad["canonical_count"] += 1
        with self.assertRaises(ValueError):
            build_manifest(bad, json.dumps(bad))

if __name__ == "__main__":
    unittest.main()
