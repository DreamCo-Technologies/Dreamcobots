import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config/dreamco-universal-division-mastery-contract.json"


class UniversalDivisionMasteryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_canonical_registry_counts_and_shared_services(self):
        c = self.contract
        self.assertEqual(c["inventory_contract"]["masterbot_learning_lanes_expected"], 65)
        self.assertEqual(c["inventory_contract"]["domain_divisions_expected"], 55)
        self.assertEqual(c["inventory_contract"]["shared_platform_masterbots"]["count"], 20)
        self.assertEqual(c["inventory_contract"]["lane_model_kits_expected"], 195)
        self.assertEqual(c["inventory_contract"]["lane_model_kits_expected"],
                         c["inventory_contract"]["masterbot_learning_lanes_expected"] * 3)

    def test_four_stages_are_ordered_and_distinct(self):
        stages = self.contract["universal_mastery_loop"]
        self.assertEqual([s["stage"] for s in stages], [1, 2, 3, 4])
        self.assertEqual(
            [s["id"] for s in stages],
            ["curriculum_ingestion", "clean_room_blueprint_distillation",
             "three_tier_model_foundry", "365_day_capability_certification"],
        )
        self.assertTrue(all(s.get("gate") for s in stages))

    def test_model_tiers_are_blueprints_not_claimed_weights(self):
        kits = self.contract["universal_mastery_loop"][2]["kits"]
        self.assertEqual([k["id"] for k in kits], ["nano_18m", "core_120m", "master_teacher"])
        self.assertEqual(kits[0]["target_parameters"], 18_000_000)
        self.assertEqual(kits[1]["target_parameters"], 120_000_000)
        self.assertIsNone(kits[2]["target_parameters"])
        self.assertIn("NOT_INSTANTIATED", kits[0]["status"])
        self.assertIn("NOT_INSTANTIATED", kits[1]["status"])

    def test_certification_has_365_day_expiry_and_rechecks(self):
        cert = self.contract["certification"]
        self.assertEqual(cert["validity_days"], 365)
        self.assertEqual(cert["evidence_history_days"], 365)
        self.assertEqual(len(cert["scheduled_rechecks"]), 4)
        self.assertEqual(cert["promotion"], "human_approval_required")

    def test_rights_and_execution_are_fail_closed(self):
        rules = self.contract["fail_closed_rules"]
        self.assertTrue(any("Unknown rights block" in x for x in rules))
        self.assertTrue(any("Missing evidence never" in x for x in rules))
        self.assertTrue(any("No automatic model-weight" in x for x in rules))
        discovery = self.contract["source_discovery"]
        self.assertIn("No arbitrary repository code execution", discovery["execution_policy"])

    def test_commercial_model_families_are_not_overwritten(self):
        policy = self.contract["model_tier_separation"]
        self.assertIn("not silently overwritten", policy["commercial_foundry"])

    def test_canonical_registry_files_exist(self):
        for path in (
            "config/masterbot-65-registry.json",
            "config/generated/division-reconciliation.json",
            "config/generated/masterbot-55-domain-crosswalk.json",
            "config/dreamco-business-bot-55-roster.json",
        ):
            self.assertTrue((ROOT / path).is_file(), path)


if __name__ == "__main__":
    unittest.main()
