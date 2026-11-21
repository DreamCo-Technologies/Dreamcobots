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
 def test_verified_repair_exports_dataset_builder_event_with_provenance(self):
  v={"original_failure":True,"regressions":True,"human_reviewed":True,"training_allowed":True,
   "rights_status":"VERIFIED","contains_secrets":False,"contains_personal_data":False,
   "third_party_content_included":False,"root_cause":"relative link escaped public site",
   "repair":"use canonical GitHub report URL","evidence":["workflow run 44846614900"],
   "source_url":"https://github.com/DreamCo-Technologies/Dreamcobots/commit/"+
    "0"*40,"commit_sha":"0"*40,"run_id":"44846614900",
   "acceptance_criteria":["public-site link check passes"],"test_evidence":["Buddy Pages Link Check passed"]}
  event=build_training_event(self.observation,v)
  self.assertEqual(event["evidence_type"],"verified_bug_fix")
  self.assertFalse(event["training_approved"]);self.assertFalse(event["weights_trained"])
  self.assertEqual(event["primary_masterbot_id"],41)
 def test_training_event_rejects_unverified_rights_or_missing_provenance(self):
  v={"original_failure":True,"regressions":True,"human_reviewed":True,"training_allowed":True,
   "rights_status":"PENDING","contains_secrets":False,"contains_personal_data":False,
   "third_party_content_included":False,"root_cause":"cause","repair":"fix","evidence":["run"],
   "source_url":"https://github.com/example/repo","commit_sha":"0"*40,"run_id":"1",
   "acceptance_criteria":["check"],"test_evidence":["passed"]}
  with self.assertRaises(ValueError):build_training_event(self.observation,v)
 def test_data_and_benchmark_route_to_specialists(self):
  self.assertEqual(route_masterbots("data"),[7,41]);self.assertEqual(route_masterbots("benchmark"),[47,63])
if __name__=="__main__":unittest.main()
