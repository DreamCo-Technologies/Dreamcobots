import json
import unittest
from pathlib import Path

from tools.build_division_reconciliation import build_reconciliation, load_domain_names

ROOT = Path(__file__).resolve().parents[1]


class DivisionReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = build_reconciliation()

    def test_45_original_and_10_additional_domains_are_first_class(self):
        names = load_domain_names((ROOT / "shared/division-production-contract.ts").read_text(encoding="utf-8"))
        self.assertEqual(len(names), 55)
        self.assertEqual(len(self.result["domain_divisions"]), 55)
        self.assertEqual(self.result["counts"]["original_core_divisions"], 45)
        self.assertEqual(self.result["counts"]["promoted_supplemental_divisions"], 10)
        self.assertEqual(self.result["counts"]["total_domain_divisions"], 55)
        self.assertEqual(len({row["id"] for row in self.result["domain_divisions"]}), 55)

    def test_all_ten_additional_divisions_keep_their_own_five_bot_portfolios(self):
        rows = self.result["promoted_supplemental_divisions"]
        expected = {
            "DreamAffiliate", "DreamAgency", "DreamFoundry", "DreamFranchise",
            "DreamIntegrations", "DreamLicensing", "DreamRobotics", "DreamSaaS",
            "DreamStreaming", "DreamTravel",
        }
        self.assertEqual({row["name"] for row in rows}, expected)
        self.assertEqual(sum(row["bot_profile_count"] for row in rows), 50)
        for row in rows:
            self.assertEqual(row["kind"], "first_class_domain_division")
            self.assertGreaterEqual(row["bot_profile_count"], 5)
            self.assertTrue((ROOT / row["source_portfolio"]).is_file())
            self.assertTrue((ROOT / row["fleet_manifest"]).is_file())
            self.assertTrue((ROOT / row["capability_test_manifest"]).is_file())
            self.assertEqual(row["masterbot_link_status"], "proposed_requires_owner_review")
            self.assertFalse(row["production_ready"])


    def test_generated_fleet_and_test_manifests_use_their_actual_envelopes(self):
        name = "DreamAffiliate"
        fleet = json.loads((ROOT / "website/data/bot-fleet/DreamAffiliate.json").read_text(encoding="utf-8"))
        tests = json.loads((ROOT / "website/data/bot-capability-tests/DreamAffiliate.json").read_text(encoding="utf-8"))
        self.assertEqual(fleet["division"], name)
        self.assertTrue(fleet["bots"])
        self.assertEqual({bot["identity"]["division"] for bot in fleet["bots"]}, {name})
        self.assertEqual(tests["division"], name)
        self.assertTrue(tests["profiles"])
        self.assertEqual({profile["division"] for profile in tests["profiles"]}, {name})

    def test_every_division_inherits_the_same_ten_operating_capabilities(self):
        expected = ["discover", "intake", "research", "design", "build", "simulate", "evaluate", "integrate", "operate", "improve"]
        for row in self.result["domain_divisions"]:
            self.assertEqual(row["capability_operations"], expected)
            self.assertEqual(row["shared_platform_masterbot_ids"], list(range(46, 66)))

    def test_all_20_platform_masterbots_remain_shared_services(self):
        rows = self.result["shared_platform_masterbots"]
        self.assertEqual([row["id"] for row in rows], list(range(46, 66)))
        self.assertTrue(all(row["kind"] == "shared_platform_service" for row in rows))
        self.assertTrue(all(row["available_to_all_domain_divisions"] for row in rows))
        self.assertTrue(all(row["primary_domain_owner"] is None for row in rows))
        names = {row["name"] for row in self.result["domain_divisions"]}
        self.assertTrue(names.isdisjoint({row["name"] for row in rows}))

    def test_generated_artifact_is_deterministic_and_current(self):
        import tools.build_division_reconciliation as builder
        rendered = json.dumps(self.result, indent=2, ensure_ascii=False) + "\n"
        self.assertEqual(builder.OUTPUT.read_text(encoding="utf-8"), rendered)


if __name__ == "__main__":
    unittest.main()
