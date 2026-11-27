import json, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.build_dreamco_universal_bot_learning_manifests import build, make_slots, build_bot_manifest

class UniversalBotLearningFoundryTests(unittest.TestCase):
 def test_each_bot_gets_exactly_100_personalized_slots(self):
  slots=make_slots("BOT_TEST","Test Bot","DreamTest",["testing"],["tests/fixture.md"])
  self.assertEqual(len(slots),100)
  self.assertEqual([x["resource_id"] for x in slots],[f"BOT_TEST_R{i:03d}" for i in range(1,101)])
  self.assertEqual([sum(x["stage"]==stage for x in slots) for stage in ("01_task_taxonomy","02_domain_playbooks","03_synthetic_scenarios","04_evaluation_harnesses")],[25,30,25,20])
 def test_rights_fail_closed_and_training_not_claimed(self):
  m=build_bot_manifest({"bot_id":"BOT_TEST","name":"Test","division":"DreamTest","capability_count":3,"focus_tags":["test"],"source_refs":["test.md"]},"test")
  self.assertTrue(all(x["third_party_rights"]=="UNKNOWN_BLOCKED" for x in m["resources"]))
  self.assertTrue(all(x["training_permission"]=="BLOCKED_UNTIL_REVIEW" for x in m["resources"]))
  self.assertFalse(m["execution"]["production_enabled"])
  self.assertEqual(m["model"]["weights_status"],"UNTRAINED_BLUEPRINT_READY_FOR_TRAINING")
 def test_complete_inventory_and_division_coverage(self):
  index,manifests,division_manifests=build()
  self.assertEqual(index["counts"]["business_micro_bots"],55)
  self.assertEqual(index["counts"]["masterbot_learning_divisions"],65)
  self.assertEqual(index["counts"]["domain_learning_divisions"],55)
  self.assertEqual(index["counts"]["division_learning_manifests"],120)
  self.assertEqual(len(division_manifests),120)
  self.assertEqual(len(index["domain_learning_divisions"]),55)
  self.assertEqual(len(index["learning_divisions"]),65)
  self.assertTrue(all(len(x["resources"])==100 for x in division_manifests))
  self.assertEqual({x["source_kind"] for x in manifests},{"canonical_fleet","legacy_original_bot_or_system","commercial_business_microbot"})
  business=[x for x in manifests if x["source_kind"]=="commercial_business_microbot"]
  legacy_systems=[x for x in manifests if x["source_kind"]=="legacy_original_bot_or_system" and x["bot_id"].endswith("master-bot-system")]
  self.assertTrue(all(x["model"]["target_parameters"]==18500000 for x in business))
  self.assertEqual(len(legacy_systems),1)
  self.assertEqual(legacy_systems[0]["model"]["target_parameters"],45000000)
  self.assertEqual(index["counts"]["legacy_income_bots"],200)
  self.assertEqual(index["counts"]["legacy_major_systems"],12)
  self.assertEqual(index["counts"]["resource_slots_per_bot"],100)
  self.assertEqual(index["counts"]["individual_bot_manifests"],1499)
  self.assertEqual(index["counts"]["resource_slots_if_materialized"],161900)
  self.assertEqual(len(manifests),index["counts"]["individual_bot_manifests"])
  self.assertEqual(len({m["bot_id"] for m in manifests}),len(manifests))
if __name__=="__main__": unittest.main()
