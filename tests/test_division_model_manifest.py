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
        self.assertEqual(manifest["status"], "inventory_and_lifecycle_plan_only_not_trained")
        for row in manifest["records"]:
            self.assertEqual(row["lifecycle_state"], "planned")
            self.assertIsNone(row["training"]["checkpoint"])
            self.assertIsNone(row["serving"]["endpoint"])
            self.assertIsNone(row["release_evidence"]["license_review"])

    def test_every_division_has_independent_model_and_training_plan(self):
        manifest = build_manifest(self.registry, self.source_text)
        for row in manifest["records"]:
            self.assertTrue(row["model_id"].startswith("dreamco.division."))
            self.assertEqual(row["planned_model_version"], "0.1.0")
            self.assertEqual(row["tokenizer"]["mode"], "shared_per_base_model")
            self.assertEqual(row["training"]["schedule"]["planner_cron"], "*/5 * * * *")
            self.assertFalse(row["training"]["weights_trained"])
            self.assertIsNone(row["training"]["checkpoint"])
            self.assertIn("private_evaluation_only_holdout", row["evaluation"]["suite"])
            self.assertIn("safety_and_policy", row["evaluation"]["suite"])
            self.assertTrue(row["independence_contract"]["division_owned_trainable_weights_or_adapter"])
            self.assertTrue(row["independence_contract"]["division_owned_checkpoint_and_optimizer_state"])
            self.assertIsNone(row["serving"]["endpoint"])
            self.assertEqual(row["teacher_plan"]["status"], "TEACHER_SELECTION_PENDING_LICENSE_AND_DOMAIN_EVALUATION")
            self.assertEqual(row["resource_bundle_id"], f"division-resource-{row['division_id']:03d}")
            self.assertEqual(row["resource_bundle_status"], "requirements_defined_not_provisioned")
            self.assertIn("rights-cleared-dataset-ingestion", row["required_resource_services"])
            self.assertIn("sandboxed-workflow-reconstruction", row["reverse_engineering_plan"]["allowed_practices"])
            self.assertIn("credential-or-access-control-bypass", row["reverse_engineering_plan"]["blocked_practices"])

    def test_registry_count_mismatch_is_rejected(self):
        bad = dict(self.registry)
        bad["canonical_count"] += 1
        with self.assertRaises(ValueError):
            build_manifest(bad, json.dumps(bad))

if __name__ == "__main__":
    unittest.main()
