import json,unittest
from pathlib import Path
from tools.build_buddy_bootcamp_curriculum import build_curriculum,validate_curriculum

ROOT=Path(__file__).resolve().parents[1]

class BuddyBootcampCurriculumTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.masterbots=json.loads((ROOT/"config/masterbot-65-registry.json").read_text())
  cls.tasks=json.loads((ROOT/"config/huggingface-task-taxonomy.json").read_text())
  cls.packs=json.loads((ROOT/"config/hf-capability-download-map.json").read_text())
  cls.division_map=json.loads((ROOT/"config/generated/division-huggingface-taxonomy-map.json").read_text())
  cls.serving=json.loads((ROOT/"config/buddy-model-serving-policy.json").read_text())
 def build(self):
  return build_curriculum(self.masterbots,self.tasks,self.packs,self.division_map,self.serving,
   {"fixture":"0"*64})
 def test_curriculum_covers_all_65_divisions_37_tasks_and_10_packs(self):
  payload=self.build();validate_curriculum(payload)
  self.assertEqual(payload["coverage"]["divisions"],65)
  self.assertEqual(payload["coverage"]["task_families"],37)
  self.assertEqual(payload["coverage"]["capability_packs"],10)
  self.assertEqual(payload["coverage"]["division_task_coverage"],65*37)
  self.assertEqual(len(payload["divisions"]),65)
  self.assertEqual(len(payload["core_modules"]),13)
 def test_every_division_gets_every_task_family_and_unique_model_identity(self):
  payload=self.build()
  for division in payload["divisions"]:
   self.assertEqual(len(division["curriculum"]["global_task_families"]),37)
   self.assertTrue(division["model"]["model_name"].startswith("dreamco/"))
   self.assertTrue(division["resources"]["database_schema"].startswith("dreamco_division_"))
  self.assertEqual(len({x["model"]["model_name"] for x in payload["divisions"]}),65)
 def test_unresolved_domain_crosswalks_remain_pending(self):
  payload=self.build()
  unresolved=[x for x in payload["divisions"] if x["huggingface"]["domain_crosswalk"]["mapping_status"]=="unresolved"]
  self.assertEqual(len(unresolved),20)
  self.assertTrue(all(x["huggingface"]["owner_review_required"] for x in unresolved))
  self.assertTrue(all(x["huggingface"]["owner_approval"] is None for x in unresolved))
 def test_curriculum_does_not_claim_training_or_teacher_model_readiness(self):
  payload=self.build()
  self.assertEqual(payload["status"],"CURRICULUM_SPECIFIED_NOT_TRAINED")
  self.assertIn("NOT_A_CLAIM",payload["teacher_model_role"]["status"])
  self.assertTrue(all(x["model"]["status"]=="SPECIFIED_NOT_TRAINED" for x in payload["divisions"]))
 def test_task_families_preserve_structured_records_and_stable_ids(self):
  payload=self.build()
  families=payload["global_task_families"]
  self.assertEqual(len(families),37)
  self.assertTrue(all(isinstance(row["task_family"],dict) for row in families))
  self.assertEqual(len({row["task_family"]["id"] for row in families}),37)

 def test_duplicate_task_family_ids_are_rejected(self):
  tasks=json.loads(json.dumps(self.tasks))
  tasks["task_families"][1]["id"]=tasks["task_families"][0]["id"]
  with self.assertRaisesRegex(ValueError,"unique Hugging Face task family IDs"):
   build_curriculum(self.masterbots,tasks,self.packs,self.division_map,self.serving)

 def test_missing_task_family_ids_are_rejected(self):
  tasks=json.loads(json.dumps(self.tasks))
  del tasks["task_families"][0]["id"]
  with self.assertRaisesRegex(ValueError,"stable id"):
   build_curriculum(self.masterbots,tasks,self.packs,self.division_map,self.serving)

 def test_unknown_capability_pack_is_rejected(self):
  division_map=json.loads(json.dumps(self.division_map))
  division_map["routes"][0]["capability_pack_ids"].append("pack.unknown")
  with self.assertRaisesRegex(ValueError,"unknown capability packs"):
   build_curriculum(self.masterbots,self.tasks,self.packs,division_map,self.serving)

if __name__=="__main__": unittest.main()
