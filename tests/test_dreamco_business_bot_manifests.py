import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"config/dreamco-business-bot-swarm.json"
class BusinessBotManifestTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=json.loads(CATALOG.read_text(encoding="utf-8"))
 def test_roster_has_55_unique_business_bots(self):
  bots=self.data["bots"]
  self.assertEqual(len(bots),55)
  self.assertEqual(len({b["bot_id"] for b in bots}),55)
  self.assertEqual([b["bot_number"] for b in bots],list(range(1,56)))
 def test_parameter_counts_are_config_derived_and_aggregate_is_not_dense(self):
  self.assertEqual(self.data["micro_model_computed_parameters"],18543104)
  self.assertEqual(self.data["upgrade_model_computed_parameters"],45003264)
  self.assertEqual(self.data["aggregate_micro_model_parameters"],18543104*55)
  self.assertFalse(self.data["aggregate_is_one_dense_model"])
  self.assertFalse(self.data["micro_model_config"]["tie_word_embeddings"] is False)
 def test_each_generated_manifest_has_100_blocked_slots(self):
  from scripts.generate_dreamco_business_bot_manifests import build_manifest
  targets={"micro_model_parameters":self.data["micro_model_computed_parameters"],
           "upgrade_model_parameters":self.data["upgrade_model_computed_parameters"],
           "collective_55_bot_target_parameters":self.data["aggregate_micro_model_parameters"],
           "weights_included":False,
           "weights_status":"UNTRAINED_BLUEPRINT_READY_FOR_TRAINING"}
  for bot in self.data["bots"]:
   m=build_manifest(bot,targets)
   self.assertEqual(len(m["curriculum"]),100)
   self.assertEqual([x["resource_slots"] for x in m["curriculum_allocation"]],[25,30,25,20])
   self.assertTrue(all(x["training_permission"]=="UNKNOWN_BLOCKED" for x in m["curriculum"]))
   self.assertTrue(all(x["resource_ref"] is None for x in m["curriculum"]))
if __name__=="__main__": unittest.main()
