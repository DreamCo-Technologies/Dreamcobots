import unittest
from tools.build_dreamco_training_examples import build

def event(n,owner=41):
 return {"event_id":f"event-{n}","source_url":f"https://github.com/DreamCo-Technologies/Dreamcobots/commit/{n:040d}",
  "evidence_type":"verified_test","verified":True,"human_reviewed":True,"training_allowed":True,
  "rights_status":"VERIFIED","contains_personal_data":False,"third_party_content_included":False,
  "primary_masterbot_id":owner,"task":f"Implement capability number {n} with dependency-aware routing",
  "verified_lesson":"The verified implementation validates inputs, records evidence, and retests the capability.",
  "acceptance_criteria":["the route is deterministic","the evidence is reproducible"],
  "test_evidence":["unit test passed","held-out regression passed"]}
class DreamCoOriginalTrainingExamplesTests(unittest.TestCase):
 def test_verified_work_becomes_original_split_examples(self):
  result=build([event(1),event(2),event(3)])
  self.assertEqual(len(result["rows"]),3)
  self.assertEqual({x["split"] for x in result["rows"]},{"train","validation","test"})
  self.assertFalse(result["training_approved"])
  self.assertTrue(all(x["derivation"]=="original_synthesis_from_verified_DreamCo_work" for x in result["rows"]))
 def test_unverified_or_unlicensed_records_are_rejected(self):
  bad=event(1);bad["training_allowed"]=False
  result=build([event(2),event(3),event(4),bad])
  self.assertEqual(len(result["rows"]),3)
  self.assertEqual(len(result["rejected_source_events"]),1)
 def test_personal_data_is_rejected(self):
  bad=event(1);bad["task"]="Send a message to person@example.com"
  with self.assertRaises(ValueError):
   build([bad,event(2),event(3)])
 def test_wrong_masterbot_is_rejected(self):
  bad=event(1,999)
  with self.assertRaises(ValueError):
   build([bad,event(2),event(3)])
if __name__=="__main__":unittest.main()
