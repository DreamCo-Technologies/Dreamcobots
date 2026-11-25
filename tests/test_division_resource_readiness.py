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

 def test_shared_platform_masterbots_are_not_marked_as_unresolved_domain_owners(self):
  routes=self.payload()["routes"]
  platform=[x for x in routes if 46<=x["masterbot_id"]<=65]
  core=[x for x in routes if 1<=x["masterbot_id"]<=45]
  self.assertEqual(len(platform),20)
  self.assertTrue(all(x["domain_mapping"]["mapping_status"]=="shared_platform_service_no_primary_domain" for x in platform))
  self.assertTrue(all(x["domain_mapping"]["shared_platform_service"] is True and x["domain_mapping"]["unresolved"] is False and x["domain_mapping"]["owner_review_required"] is False and x["domain_mapping"]["domain_id"] is None for x in platform))
  self.assertTrue(all(x["domain_mapping"]["shared_platform_service"] is False and x["domain_mapping"]["owner_review_required"] is True for x in core))

 def test_all_55_domain_profiles_receive_linked_or_standalone_resource_bundles(self):
  result=self.payload()
  domains=result["domain_routes"]
  self.assertEqual(len(domains),55)
  self.assertEqual(len({x["domain_id"] for x in domains}),55)
  linked=[x for x in domains if x["route_type"]=="linked_to_masterbot_resource_bundle"]
  standalone=[x for x in domains if x["route_type"]=="standalone_domain_resource_bundle"]
  self.assertEqual(len(linked),45)
  self.assertEqual(len(standalone),10)
  self.assertTrue(all(x["resource_bundle_id"] and len(x["dataset_search_queries"])>=3 for x in domains))
  self.assertTrue(all(x["dataset_training_approved"] is False for x in domains))
  self.assertTrue(all(x["masterbot_id"] is None for x in standalone))
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
 def test_shared_platform_services_are_not_counted_as_unresolved_domain_mappings(self):
  result=self.payload();review=result["owner_review"]
  self.assertEqual(result["counts"]["unresolved_masterbot_mappings"],0)
  self.assertEqual(result["counts"]["proposed_exact_name_matches"],45)
  self.assertEqual(result["counts"]["shared_platform_masterbots"],20)
  self.assertEqual(len(review["masterbot_domain_decisions"]),0)
  self.assertEqual([x["masterbot_id"] for x in review["shared_platform_services"]],list(range(46,66)))
  self.assertTrue(all(x["primary_domain_id"] is None and x["decision"]=="SHARED_PLATFORM_SERVICE_NO_PRIMARY_DOMAIN" for x in review["shared_platform_services"]))
 def test_45_exact_name_matches_and_10_supplemental_links_retain_chat_approval_provenance(self):
  review=self.payload()["owner_review"]
  self.assertEqual(len(review["proposed_exact_name_matches"]),45)
  self.assertTrue(all(x["user_approval_status"]=="APPROVED_BY_USER_IN_CHAT_PENDING_GITHUB_IDENTITY_ATTESTATION" and x["owner_approval"] is None for x in review["proposed_exact_name_matches"]))
  self.assertEqual(len(review["unassigned_domain_profiles"]),10)
  self.assertTrue(all(x["user_approval_status"]=="APPROVED_BY_USER_IN_CHAT_PENDING_GITHUB_IDENTITY_ATTESTATION" and x["proposed_collaborator_masterbot_id"] for x in review["unassigned_domain_profiles"]))
 def test_no_training_or_provider_is_marked_live_by_resource_blueprint(self):
  result=self.payload()
  self.assertEqual(result["status"],"requirements_defined_not_provisioned")
  self.assertIn("contract_only",{x["implementation_status"] for x in self.router["connectors"]})
  self.assertTrue(all(not r["dataset_training_approved"] for r in result["routes"]))

if __name__=="__main__":unittest.main()
