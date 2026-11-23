import importlib.util
import json
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools/build_masterbot_division_crosswalk.py"
spec = importlib.util.spec_from_file_location("masterbot_crosswalk", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class MasterBotDivisionCrosswalkTests(unittest.TestCase):
    def test_authoritative_domain_taxonomy_contains_exactly_45_domains(self):
        source = module.DOMAIN_SOURCE.read_text(encoding="utf-8")
        names = module.load_domain_names(source)
        self.assertEqual(len(names), 45)
        self.assertIn("CommandCore", names)
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
        self.assertEqual(result["counts"]["domain_divisions"], 45)
        self.assertTrue(all(row["owner_approval"] is None for row in result["domains"]))
        self.assertTrue(all(row["review_required"] for row in result["masterbots"]))


if __name__ == "__main__":
    unittest.main()
