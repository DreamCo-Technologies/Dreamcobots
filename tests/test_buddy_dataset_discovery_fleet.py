import unittest
from buddy.datasets.license_policy import assess_training_candidate,normalize_license
from buddy.datasets.discovery_fleet import _load_taxonomy_routes,_query_for,run_discovery_fleet
from unittest.mock import patch
from buddy.datasets.hub import DatasetHub
class DatasetLicensePolicyTests(unittest.TestCase):
 def candidate(self):
  return {"source":"huggingface","id":"org/dataset","url":"https://huggingface.co/datasets/org/dataset",
   "license":"cc-by-4.0","ai_training_allowed":True,"content_rights_verified":True,"privacy_review":"PASSED"}
 def test_allowlisted_license_is_only_a_candidate_not_approval(self):
  result=assess_training_candidate(self.candidate())
  self.assertIn("CANDIDATE",result["status"])
  self.assertFalse(result["training_approved"])
 def test_public_listing_or_license_alone_does_not_allow_training(self):
  item=self.candidate();item.pop("ai_training_allowed")
  self.assertEqual(assess_training_candidate(item)["status"],"BLOCKED_NO_EXPLICIT_AI_TRAINING_PERMISSION")
 def test_unknown_or_restrictive_license_is_blocked(self):
  item=self.candidate();item["license"]="CC-BY-NC-4.0"
  self.assertEqual(assess_training_candidate(item)["status"],"BLOCKED_LICENSE_REQUIRES_MANUAL_TERMS_REVIEW")
  item["license"]="unknown"
  self.assertEqual(assess_training_candidate(item)["status"],"BLOCKED_UNKNOWN_LICENSE")
 def test_unverified_privacy_and_rights_are_blocked(self):
  item=self.candidate();item["privacy_review"]="PENDING"
  self.assertEqual(assess_training_candidate(item)["status"],"BLOCKED_PRIVACY_REVIEW")
  item["privacy_review"]="PASSED";item["content_rights_verified"]=False
  self.assertEqual(assess_training_candidate(item)["status"],"BLOCKED_CONTENT_RIGHTS_UNVERIFIED")
 def test_aliases_normalize(self):
  self.assertEqual(normalize_license("Apache 2.0"),"Apache-2.0")
 def test_discovered_candidate_is_persisted_and_routed(self):
  import tempfile
  with tempfile.TemporaryDirectory() as temp:
   hub=DatasetHub(temp)
   key=hub.record_external_candidate({"source":"huggingface","id":"org/sample",
    "url":"https://huggingface.co/datasets/org/sample","license":"cc-by-4.0",
    "rights_status":"UNVERIFIED"} ,41,"code")
   self.assertTrue(key)
   rows=hub.external_candidates(masterbot_id=41)
   self.assertEqual(len(rows),1)
   self.assertFalse(rows[0]["metadata"].get("training_approved",False))
 def test_fleet_persists_and_routes_candidates_to_each_selected_lane(self):
  import tempfile
  candidate={"source":"zenodo","id":"record-1","name":"Example data",
   "url":"https://zenodo.org/records/1","license":"CC0-1.0",
   "rights_status":"UNVERIFIED_REQUIRES_RECORD_AND_FILE_LICENSE_REVIEW"}
  response={"results":[candidate],"model_results":[],"source_errors":{}}
  with tempfile.TemporaryDirectory() as temp:
   hub=DatasetHub(temp)
   with patch("buddy.datasets.discovery_fleet.discover",return_value=response):
    result=run_discovery_fleet(hub=hub,lanes_per_run=2,offset=0,limit=1)
   self.assertEqual(len(result["lanes_scanned"]),2)
   self.assertEqual(result["candidates_recorded"],2)
   self.assertEqual(len(hub.external_candidates(limit=10)),2)
   self.assertEqual({x["masterbot_id"] for x in hub.external_candidates(limit=10)},{1,2})
   for row in hub.external_candidates(limit=10):
    self.assertIn("dreamco_taxonomy",row["metadata"])
    self.assertFalse(row["metadata"]["training_approved"])
    self.assertEqual(row["metadata"]["dreamco_taxonomy"]["routing_status"],"DISCOVERY_ONLY_NOT_TRAINING_APPROVED")
 def test_all_masterbots_have_query_fallback(self):
  self.assertTrue(_query_for("DreamFinance"))
  self.assertTrue(_query_for("DreamUnknownDivision"))
 def test_taxonomy_map_covers_all_65_masterbots(self):
  routes=_load_taxonomy_routes()
  self.assertEqual(len(routes),65)
  self.assertTrue(all(row["lane_id"] for row in routes.values()))
  self.assertTrue(all(row["training_approved"] is False for row in routes.values()))
 def test_taxonomy_queries_drive_discovery_and_are_persisted(self):
  route=_load_taxonomy_routes()[1]
  self.assertEqual(_query_for("DreamFinance",route),route["search_queries"][0])
if __name__=="__main__":unittest.main()
