import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.build_division_resource_readiness_map import build

class DivisionResourceReadinessTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.registry=json.loads((ROOT/"config/masterbot-65-registry.json").read_text())
  cls.taxonomy=json.loads((ROOT/"config/generated/division-huggingface-taxonomy-map.json").read_text())
  cls.crosswalk=json.loads((ROOT/"config/generated/masterbot-55-domain-crosswalk.json").read_text())
  cls.packs=json.loads((ROOT/"config/hf-capability-download-map.json").read_text())
  cls.router=json.loads((ROOT/"config/buddy-model-router.json").read_text())
 @classmethod
 def payload(cls):
  return build(cls.registry,cls.taxonomy,cls.crosswalk,cls.packs,cls.router,{"fixture":"0"*40})
 def test_every_masterbot_has_complete_unique_resource_bundle(self):
  result=self.payload();routes=result["routes"]
  self.assertEqual(len(routes),65)
  self.assertEqual(len({r["resource_bundle_id"] for r in routes}),65)
  self.assertEqual({r["masterbot_id"] for r in routes},{b["id"] for b in self.registry["divisions"]})
  required={"logical_database_namespace","dataset_discovery_lane_id","domain_mapping"}
  for route in routes:
   self.assertTrue(required.issubset(route))
   self.assertEqual(route["readiness_status"],"requirements_defined_not_provisioned")
   self.assertTrue(route["logical_database_namespace"])
   self.assertTrue(route["dataset_discovery_lane_id"])
   self.assertFalse(route["dataset_training_approved"])
 def test_teacher_models_are_candidates_not_certified_or_approved(self):
  result=self.payload()
  self.assertGreaterEqual(len(result["machine_learning_practices"]),20)
  self.assertEqual(set(result["resource_templates"]),{"database","datasets","teacher_models","reverse_engineering","distillation","model_routing","compute","evaluation","operations"})
  seed_catalog=result["resource_templates"]["teacher_models"]["seed_models_by_capability_pack"]
  for route in result["routes"]:
   self.assertTrue(set(route["capability_pack_ids"]).issubset(seed_catalog))
 def test_distillation_and_reverse_engineering_have_rights_gates(self):
  templates=self.payload()["resource_templates"]
  self.assertIn("teacher/provider terms",templates["distillation"]["required_lineage"][2])
  self.assertTrue(any("authentication" in x for x in templates["reverse_engineering"]["prohibited"]))
  self.assertTrue(any("copying protected" in x for x in templates["reverse_engineering"]["prohibited"]))
 def test_unresolved_20_masterbots_and_10_domain_profiles_stay_unassigned(self):
  result=self.payload();review=result["owner_review"]
  self.assertEqual(len(review["masterbot_domain_decisions"]),20)
  self.assertEqual(len(review["unassigned_domain_profiles"]),10)
  self.assertTrue(all(x["candidate_domain_ids"]==[] and x["decision"]=="PENDING_OWNER_REVIEW" for x in review["masterbot_domain_decisions"]))
  self.assertTrue(all(x["candidate_masterbot_ids"]==[] and x["decision"]=="PENDING_OWNER_REVIEW" for x in review["unassigned_domain_profiles"]))
 def test_no_training_or_provider_is_marked_live_by_resource_blueprint(self):
  result=self.payload()
  self.assertEqual(result["status"],"requirements_defined_not_provisioned")
  self.assertIn("contract_only",{x["implementation_status"] for x in self.router["connectors"]})
  self.assertTrue(all(not r["dataset_training_approved"] for r in result["routes"]))

if __name__=="__main__":unittest.main()
