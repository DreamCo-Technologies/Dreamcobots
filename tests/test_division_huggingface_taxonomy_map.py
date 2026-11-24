import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.build_division_huggingface_taxonomy_map import build_map  # noqa: E402

class DivisionHuggingFaceTaxonomyMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.masterbots = json.loads((ROOT / "config/masterbot-65-registry.json").read_text())
        cls.crosswalk = json.loads((ROOT / "config/generated/masterbot-55-domain-crosswalk.json").read_text())
        cls.packs = json.loads((ROOT / "config/hf-capability-download-map.json").read_text())
        cls.taxonomy = json.loads((ROOT / "config/huggingface-task-taxonomy.json").read_text())
        cls.policy = json.loads((ROOT / "config/buddy-dataset-routing-policy.json").read_text())

    def build(self):
        return build_map(self.masterbots, self.crosswalk, self.packs, self.taxonomy,
                         self.policy, {"fixture": "0" * 40})

    def test_every_masterbot_has_one_unique_discovery_lane(self):
        result = self.build()
        self.assertEqual(result["counts"]["masterbots"], 65)
        self.assertEqual(len(result["routes"]), 65)
        self.assertEqual(len({row["lane_id"] for row in result["routes"]}), 65)
        self.assertEqual({row["masterbot_id"] for row in result["routes"]},
                         {row["id"] for row in self.masterbots["divisions"]})

    def test_unresolved_domain_crosswalk_is_not_filled_by_guessing(self):
        result = self.build()
        unresolved = [row for row in result["routes"]
                      if row["domain_crosswalk"]["mapping_status"] == "unresolved"]
        self.assertEqual(len(unresolved), self.crosswalk["counts"]["unresolved_masterbots"])
        self.assertTrue(all(row["domain_crosswalk"]["domain_id"] is None for row in unresolved))
        self.assertTrue(all(row["domain_crosswalk"]["owner_review_required"] for row in result["routes"]))

    def test_candidate_tags_are_known_and_training_never_auto_approved(self):
        result = self.build()
        task_ids = {task["id"] for task in self.taxonomy["task_families"]}
        pack_ids = {pack["id"] for pack in self.packs["packs"]}
        for row in result["routes"]:
            self.assertTrue(set(row["capability_pack_ids"]).issubset(pack_ids))
            self.assertTrue(set(row["candidate_pipeline_tags"]).issubset(task_ids))
            self.assertFalse(row["training_approved"])
            self.assertEqual(row["rights_status"], "UNVERIFIED_DISCOVERY_ONLY")

    def test_shared_foundation_packs_cover_all_lanes(self):
        result = self.build()
        required = {"pack.instruct", "pack.reason", "pack.safety"}
        self.assertTrue(all(required.issubset(row["capability_pack_ids"]) for row in result["routes"]))

if __name__ == "__main__":
    unittest.main()
