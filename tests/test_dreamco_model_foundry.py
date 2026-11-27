import json
import tempfile
import unittest
from pathlib import Path

from scripts.dreamco_model_foundry import (
    MODEL_BLUEPRINTS,
    estimate_llama_parameters,
    build_catalog,
    build_buyer_foundry_kit,
    build_business_profile_foundry_kit,
    load_divisions,
    load_business_profiles,
)
from scripts.train_my_agent import preflight


class ModelFoundryCommercialKitTests(unittest.TestCase):
    def test_catalog_has_250_unique_untrained_skus(self):
        catalog = build_catalog()
        self.assertEqual(catalog["masterbot_division_count"], 65)
        self.assertEqual(catalog["business_profile_count"], 55)
        self.assertEqual(catalog["masterbot_kit_count"], 195)
        self.assertEqual(catalog["business_profile_kit_count"], 55)
        self.assertEqual(catalog["kit_count"], 250)
        skus = [item["sku"] for item in catalog["kits"]]
        self.assertEqual(len(set(skus)), 250)
        self.assertTrue(all(item["weights_included"] is False for item in catalog["kits"]))
        self.assertTrue(all(item["weights_status"] == "UNTRAINED_BLUEPRINT_READY_FOR_TRAINING" for item in catalog["kits"]))
        domain = [item for item in catalog["kits"] if item["catalog_family"] == "business_profile_domain_model"]
        self.assertEqual(len(domain), 55)
        self.assertTrue(all(item["tier"] == "45m-edge" and item["domain_weights_status"] == "NOT_TRAINED" for item in domain))

    def test_canonical_divisions_and_business_profiles_are_both_complete(self):
        self.assertEqual(len(load_divisions()), 65)
        self.assertEqual(len(load_business_profiles()), 55)
        self.assertEqual(set(MODEL_BLUEPRINTS), {"45m-edge", "350m-workstation", "1b-sovereign"})
        for spec in MODEL_BLUEPRINTS.values():
            self.assertEqual(estimate_llama_parameters(spec["config"]), spec["parameter_target"])

    def test_business_profile_blueprint_uses_45m_template_and_own_curriculum(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile = load_business_profiles()[0]
            kit = build_business_profile_foundry_kit(profile, Path(tmp))
            manifest = json.loads((kit / "BUYER_MANIFEST.json").read_text(encoding="utf-8"))
            config = json.loads((kit / "blueprint/config.json").read_text(encoding="utf-8"))
            curriculum = json.loads((kit / "curriculum/LEARNING_PATH.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["business_profile_id"], profile["division_id"])
            self.assertEqual(manifest["business_profile"], profile["division_name"])
            self.assertEqual(manifest["parameter_target"], 45040128)
            self.assertEqual(config["computed_parameter_count"], 45040128)
            self.assertFalse(manifest["weights_included"])
            self.assertEqual(manifest["weights_status"], "UNTRAINED_BLUEPRINT_READY_FOR_TRAINING")
            self.assertEqual(manifest["domain_weights_status"], "NOT_TRAINED")
            self.assertEqual(len(curriculum["modules"]), len(profile["ordered_units"]))
            self.assertEqual(len(manifest["kit_seal_sha256"]), 64)

    def test_all_55_business_profile_names_have_individual_45m_skus(self):
        catalog = build_catalog()
        expected = {p["division_name"] for p in load_business_profiles()}
        actual = {x["business_profile"] for x in catalog["kits"] if x["catalog_family"] == "business_profile_domain_model"}
        self.assertEqual(actual, expected)

    def test_masterbot_buyer_kit_manifest_and_seal(self):
        with tempfile.TemporaryDirectory() as tmp:
            kit = build_buyer_foundry_kit("45m-edge", load_divisions()[0], Path(tmp))
            manifest = json.loads((kit / "BUYER_MANIFEST.json").read_text(encoding="utf-8"))
            self.assertFalse(manifest["weights_included"])
            self.assertEqual(manifest["weights_status"], "UNTRAINED_BLUEPRINT_READY_FOR_TRAINING")
            self.assertEqual(len(manifest["kit_seal_sha256"]), 64)

    def test_launcher_fails_closed_without_rights_or_backend(self):
        with tempfile.TemporaryDirectory() as tmp:
            kit = build_buyer_foundry_kit("45m-edge", load_divisions()[0], Path(tmp))
            result = preflight(kit, True)
            self.assertEqual(result["status"], "BLOCKED")
            self.assertFalse(result["training_started"])
            self.assertFalse(result["paid_compute_requested"])
            self.assertTrue(result["blockers"])


if __name__ == "__main__":
    unittest.main()
