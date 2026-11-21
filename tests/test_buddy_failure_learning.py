import unittest
from tools.buddy_failure_learning import classify,fingerprint,recommend,update_memory,route_masterbots,build_training_candidate,build_training_event
class BuddyFailureLearningTests(unittest.TestCase):
 def setUp(self):
  self.observation={"repository":"DreamCo-Technologies/Dreamcobots","workflow":"Actions Health",
   "job":"contract-tests","failed_step":"validate generated prospectus","error_signature":"inventory mismatch"}
 def test_fingerprint_ignores_run_and_commit_identifiers(self):
  self.assertEqual(fingerprint({**self.observation,"run_id":12,"commit":"abc"}),
   fingerprint({**self.observation,"run_id":99,"commit":"def"}))
 def test_classifies_generated_index_failure(self):self.assertEqual(classify(self.observation),"generated-index")
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
  sha="a1234567890b1234567890c1234567890d123456"
  return {"original_failure":True,"regressions":True,"human_reviewed":True,"training_allowed":True,
   "rights_status":"VERIFIED","contains_secrets":False,"contains_personal_data":False,
   "third_party_content_included":False,"root_cause":"The health inventory omitted YAML workflow definitions.",
   "repair":"Include both .yml and .yaml files in the canonical workflow inventory.",
   "source_url":"https://github.com/DreamCo-Technologies/Dreamcobots/commit/"+sha,
   "source_commit":sha,"run_id":run_id,
   "acceptance_criteria":["The report count matches both YAML extensions."],
   "test_evidence":["GitHub Actions run 44866516527 passed the Actions inventory contract."]}
 def test_verified_repair_exports_dataset_builder_compatible_candidate(self):
  from tools.build_dreamco_training_examples import build
  events=[build_training_event(self.observation,self._verified_event_inputs(str(i))) for i in (1,2,3)]
  self.assertEqual(events[0]["schema"],"dreamco.verified_repair_training_event.v1")
  self.assertRegex(events[0]["source_fingerprint"],r"^[0-9a-f]{24}$")
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
 def test_training_event_rejects_noncanonical_or_mismatched_commit_url(self):
  verification=self._verified_event_inputs()
  verification["source_url"]="https://example.com/not-dreamco"
  with self.assertRaises(ValueError):build_training_event(self.observation,verification)
  verification=self._verified_event_inputs()
  verification["source_commit"]="f"*40
  with self.assertRaises(ValueError):build_training_event(self.observation,verification)
if __name__=="__main__":unittest.main()
