import importlib.util
import json
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools/build_masterbot_division_crosswalk.py"
spec = importlib.util.spec_from_file_location("masterbot_crosswalk", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class MasterBotDivisionCrosswalkTests(unittest.TestCase):
    def test_authoritative_domain_taxonomy_contains_55_domains(self):
        source = module.DOMAIN_SOURCE.read_text(encoding="utf-8")
        names = module.load_domain_names(source)
        self.assertEqual(len(names), 55)
        self.assertIn("CommandCore", names)
        self.assertIn("DreamAffiliate", names)
        self.assertIn("DreamAgency", names)
        self.assertIn("DreamFoundry", names)
        self.assertNotIn("officialSources", names)
        self.assertNotIn("memberDirectory", names)

    def test_only_exact_identity_matches_are_proposed(self):
        bots = [{"id": i + 1, "name": name} for i, name in enumerate(
            ["DreamFinance"] + [f"Unmapped{i}" for i in range(64)]
        )]
        result = module.build_crosswalk({"canonical_count": 65, "divisions": bots},
                                        ["DreamFinance", "DreamHealth"])
        self.assertEqual(result["domains"][0]["mapping_status"], "proposed_exact_name_match")
        self.assertEqual(result["domains"][0]["masterbot_id"], 1)
        self.assertEqual(result["domains"][1]["mapping_status"], "unresolved")
        self.assertIsNone(result["domains"][1]["masterbot_id"])
        self.assertTrue(all(row["review_required"] for row in result["domains"]))

    def test_real_registry_crosswalk_never_claims_automatic_owner_approval(self):
        bots = json.loads(module.MASTERBOTS.read_text(encoding="utf-8"))
        domains = module.load_domain_names(module.DOMAIN_SOURCE.read_text(encoding="utf-8"))
        result = module.build_crosswalk(bots, domains)
        self.assertEqual(result["counts"]["masterbots"], 65)
        self.assertEqual(result["counts"]["domain_divisions"], 55)
        self.assertEqual(result["counts"]["unresolved_domain_divisions"], 10)
        self.assertTrue(all(row["owner_approval"] is None for row in result["domains"]))
        self.assertTrue(all(row["review_required"] for row in result["masterbots"]))


    def test_owner_review_preserves_core_supplemental_and_shared_service_boundaries(self):
        root = Path(__file__).resolve().parents[1]
        review = json.loads((root / "config/review/masterbot-domain-crosswalk-owner-review.json").read_text(encoding="utf-8"))
        reconciliation = json.loads((root / "config/generated/division-reconciliation.json").read_text(encoding="utf-8"))

        self.assertEqual(review["schema"], "dreamco.masterbot_domain_owner_review.v2")
        self.assertIn("config/generated/masterbot-45-domain-crosswalk.json", review["source_refs"])
        self.assertIn("config/generated/masterbot-55-domain-crosswalk.json", review["source_refs"])
        self.assertIn("config/generated/division-reconciliation.json", review["source_refs"])
        self.assertEqual(review["domain_taxonomy"]["original_core_divisions"], 45)
        self.assertEqual(review["domain_taxonomy"]["promoted_supplemental_divisions"], 10)
        self.assertEqual(review["domain_taxonomy"]["total_domain_divisions"], 55)
        self.assertEqual(review["domain_taxonomy"]["shared_platform_masterbot_ids"], {"first": 46, "last": 65, "count": 20})

        decisions = review["masterbot_domain_decisions"]
        self.assertEqual([row["masterbot_id"] for row in decisions], list(range(46, 66)))
        self.assertTrue(all(row["primary_domain_id"] is None for row in decisions))
        self.assertTrue(all(row["candidate_domain_ids"] == [] for row in decisions))
        self.assertTrue(all(row["owner_approval"] is None and row["review_required"] for row in decisions))

        supplemental = review["unassigned_domain_profiles"]
        expected = {row["name"].casefold() for row in reconciliation["promoted_supplemental_divisions"]}
        self.assertEqual({row["domain_name"].casefold() for row in supplemental}, expected)
        self.assertTrue(all(row["owner_approval"] is None and row["review_required"] for row in supplemental))
        self.assertEqual(reconciliation["counts"]["original_core_divisions"], 45)
        self.assertEqual(reconciliation["counts"]["promoted_supplemental_divisions"], 10)
        self.assertEqual(reconciliation["counts"]["total_domain_divisions"], 55)
        self.assertEqual(reconciliation["counts"]["shared_platform_masterbots"], 20)

    def test_owner_review_references_current_crosswalks_not_legacy_source_only(self):
        root = Path(__file__).resolve().parents[1]
        review = json.loads((root / "config/review/masterbot-domain-crosswalk-owner-review.json").read_text(encoding="utf-8"))
        self.assertNotIn("source", review)
        self.assertIn("config/generated/masterbot-45-domain-crosswalk.json", review["source_refs"])
        self.assertIn("config/generated/division-reconciliation.json", review["source_refs"])

if __name__ == "__main__":
    unittest.main()
