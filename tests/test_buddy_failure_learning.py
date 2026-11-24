import unittest
from tools.buddy_failure_learning import classify,fingerprint,recommend,update_memory,route_masterbots,build_training_candidate,build_training_event,historical_candidates
class BuddyFailureLearningTests(unittest.TestCase):
 def setUp(self):
  self.observation={"repository":"DreamCo-Technologies/Dreamcobots","workflow":"Actions Health",
   "job":"contract-tests","failed_step":"validate generated prospectus","error_signature":"inventory mismatch"}
 def test_historical_candidates_are_ranked_but_never_verified_or_auto_applied(self):
  index={"records":[
   {"commit":"a"*40,"subject":"fix generated inventory mismatch","search_terms":["generated","inventory","mismatch"],
    "changed_paths":["tools/inventory.py"],"test_paths":["tests/test_inventory.py"],
    "verified_fix":False,"training_eligible":False},
   {"commit":"b"*40,"subject":"unrelated documentation","search_terms":["documentation"],
    "changed_paths":["README.md"],"test_paths":[],"verified_fix":False,"training_eligible":False},
   {"commit":"c"*40,"subject":"unsafe candidate","search_terms":["inventory","mismatch"],
    "changed_paths":["tools/x.py"],"verified_fix":True,"training_eligible":True}
  ]}
  candidates=historical_candidates(self.observation,index)
  self.assertEqual(len(candidates),1)
  self.assertEqual(candidates[0]["commit"],"a"*40)
  self.assertFalse(candidates[0]["verified_fix"])
  self.assertFalse(candidates[0]["training_eligible"])
  self.assertFalse(candidates[0]["auto_apply_allowed"])
 def test_recommendation_exposes_historical_leads_without_changing_risk_policy(self):
  index={"records":[{"commit":"d"*40,"subject":"inventory mismatch repair",
   "search_terms":["inventory","mismatch"],"changed_paths":["tools/inventory.py"],
   "test_paths":["tests/test_inventory.py"],"verified_fix":False,"training_eligible":False}]}
  plan=recommend(self.observation,{"incidents":[]},index)
  self.assertTrue(plan["automatic_code_change_allowed"])
  self.assertEqual(plan["historical_candidates"][0]["commit"],"d"*40)
  self.assertFalse(plan["historical_candidates"][0]["auto_apply_allowed"])
 def test_fingerprint_ignores_run_and_commit_identifiers(self):
  self.assertEqual(fingerprint({**self.observation,"run_id":12,"commit":"abc"}),
   fingerprint({**self.observation,"run_id":99,"commit":"def"}))
 def test_classifies_generated_index_failure(self):self.assertEqual(classify(self.observation),"generated-index")
 def test_classifies_real_safe_repair_verification_step_as_generated_index(self):
  observation={"repository":"DreamCo-Technologies/Dreamcobots",
   "workflow":"Buddy CI Safe Generated-Artifact Repair","job":"regenerate-and-verify",
   "failed_step":"Verify repaired indexes and Buddy repair-learning tests",
   "error_signature":"Verify repaired indexes and Buddy repair-learning tests"}
  self.assertEqual(classify(observation),"generated-index")
  plan=recommend(observation,{"incidents":[]})
  self.assertEqual(plan["primary_masterbot_id"],41)
 def test_safe_generated_index_can_use_bounded_automation(self):
  p=recommend(self.observation,{"incidents":[]});self.assertTrue(p["automatic_code_change_allowed"])
  self.assertFalse(p["requires_human_approval"]);self.assertEqual(p["primary_masterbot_id"],41)
 def test_security_failure_requires_human_approval(self):
  p=recommend({**self.observation,"failure_class":"security"},{"incidents":[]})
  self.assertFalse(p["automatic_code_change_allowed"]);self.assertTrue(p["requires_human_approval"])
  self.assertEqual(p["primary_masterbot_id"],24)
 def test_verified_lesson_is_reused_on_recurrence(self):
  m={"incidents":[{"fingerprint":fingerprint({**self.observation,"failure_class":"generated-index"}),
   "occurrence_count":2,"verified_lesson":{"root_cause":"stale index","repair":"regenerate"}}]}
  p=recommend(self.observation,m);self.assertEqual(p["recurrence_count"],3)
  self.assertEqual(p["recommended_action"],"reapply_verified_lesson_in_isolated_branch")
 def test_unverified_repairs_never_become_lessons(self):
  with self.assertRaises(ValueError):update_memory({"incidents":[]},self.observation,{"original_failure":True,"regressions":False})
 def test_verified_repair_is_saved(self):
  m=update_memory({"incidents":[]},self.observation,{"original_failure":True,"regressions":True,
   "root_cause":"stale report","repair":"regenerate report","evidence":["run:123"],"verified_at":"2026-11-20T12:00:00Z"})
  self.assertEqual(len(m["incidents"]),1);self.assertEqual(m["incidents"][0]["verified_lesson"]["repair"],"regenerate report")
 def test_training_candidate_requires_review_and_exclusions(self):
  v={"original_failure":True,"regressions":True,"human_reviewed":True,"training_allowed":True,
   "contains_secrets":False,"contains_personal_data":False,"root_cause":"bad fixture","repair":"fix fixture","evidence":["run:1"]}
  row=build_training_candidate(self.observation,v);self.assertFalse(row["training_approved"])
  self.assertEqual(row["primary_masterbot_id"],41)
  v["contains_secrets"]=True
  with self.assertRaises(ValueError):build_training_candidate(self.observation,v)
 def test_data_and_benchmark_route_to_specialists(self):
  self.assertEqual(route_masterbots("data"),[7,41]);self.assertEqual(route_masterbots("benchmark"),[47,63])
 def _verified_event_inputs(self,run_id="123"):
  return {"original_failure":True,"regressions":True,"human_reviewed":True,"training_allowed":True,
   "rights_status":"VERIFIED","contains_secrets":False,"contains_personal_data":False,
   "third_party_content_included":False,"root_cause":"The health inventory omitted YAML workflow definitions.",
   "repair":"Include both .yml and .yaml files in the canonical workflow inventory.",
   "source_url":"https://github.com/DreamCo-Technologies/Dreamcobots/commit/"+"a"*40,
   "source_commit":"a"*40,"run_id":run_id,
   "acceptance_criteria":["The report count matches both YAML extensions."],
   "test_evidence":["GitHub Actions run 44866516527 passed the Actions inventory contract."]}
 def test_verified_repair_exports_dataset_builder_compatible_candidate(self):
  from tools.build_dreamco_training_examples import build
  events=[build_training_event(self.observation,self._verified_event_inputs(str(i))) for i in (1,2,3)]
  self.assertEqual(events[0]["schema"],"dreamco.verified_repair_training_event.v1")
  self.assertEqual(events[0]["event_id"],build_training_event(self.observation,self._verified_event_inputs("1"))["event_id"])
  candidate=build(events)
  self.assertEqual(candidate["accepted_source_events"],3)
  self.assertFalse(candidate["training_approved"])
  self.assertFalse(candidate["weights_trained"])
  events[0]["contains_secrets"]=True
  with self.assertRaises(ValueError):build(events)
 def test_training_event_rejects_unverified_rights_and_missing_evidence(self):
  verification=self._verified_event_inputs()
  verification["rights_status"]="PENDING"
  with self.assertRaises(ValueError):build_training_event(self.observation,verification)
  verification=self._verified_event_inputs()
  verification["test_evidence"]=[]
  with self.assertRaises(ValueError):build_training_event(self.observation,verification)
if __name__=="__main__":unittest.main()
