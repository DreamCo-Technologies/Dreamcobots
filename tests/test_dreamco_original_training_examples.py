import unittest
from tools.build_dreamco_training_examples import build

def event(n,owner=41):
 return {"event_id":f"event-{n}","source_url":f"https://github.com/DreamCo-Technologies/Dreamcobots/commit/{n:040d}",
  "evidence_type":"verified_test","verified":True,"human_reviewed":True,"training_allowed":True,
  "rights_status":"VERIFIED","contains_secrets":False,"contains_personal_data":False,"third_party_content_included":False,
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
 def test_mixed_masterbot_ownership_is_rejected(self):
  with self.assertRaises(ValueError):
   build([event(1,41),event(2,42),event(3,43)])
 def test_personal_data_is_rejected(self):
  bad=event(1);bad["task"]="Send a message to person@example.com"
  with self.assertRaises(ValueError):
   build([bad,event(2),event(3)])
 def test_wrong_masterbot_is_rejected(self):
  bad=event(1,999)
  with self.assertRaises(ValueError):
   build([bad,event(2),event(3)])
 def test_validated_provenance_hashes_are_not_scanned_as_free_text(self):
  sha="a1234567890b1234567890c1234567890d123456"
  events=[event(1),event(2),event(3)]
  for row in events:
   row["source_commit"]=sha
   row["source_url"]=f"https://github.com/DreamCo-Technologies/Dreamcobots/commit/{sha}"
   row["source_fingerprint"]="a1234567890ba1234567890b"
   row["run_id"]="44866516527"
  result=build(events)
  self.assertEqual(result["accepted_source_events"],3)
  self.assertTrue(all(row["source_commit"]==sha for row in result["rows"]))
 def test_phone_in_training_text_is_still_rejected(self):
  bad=event(1);bad["verified_lesson"] += " Contact 555-123-4567 for details."
  with self.assertRaises(ValueError):
   build([bad,event(2),event(3)])
 def test_noncanonical_or_mismatched_provenance_is_rejected(self):
  bad=event(1);bad["source_url"]="https://example.com/DreamCo-Technologies/Dreamcobots/commit/"+"1"*40
  result=build([event(2),event(3),event(4),bad])
  self.assertEqual(result["accepted_source_events"],3)
  self.assertEqual(len(result["rejected_source_events"]),1)
  bad=event(5);bad["source_commit"]="f"*40
  result=build([event(6),event(7),event(8),bad])
  self.assertEqual(result["accepted_source_events"],3)
  self.assertEqual(len(result["rejected_source_events"]),1)
 def test_secrets_and_missing_secret_attestation_are_rejected(self):
  bad=event(1);bad["contains_secrets"]=True
  result=build([event(2),event(3),event(4),bad])
  self.assertEqual(result["accepted_source_events"],3)
  self.assertEqual(len(result["rejected_source_events"]),1)
  missing=event(5);del missing["contains_secrets"]
  result=build([event(6),event(7),event(8),missing])
  self.assertEqual(result["accepted_source_events"],3)
  self.assertEqual(len(result["rejected_source_events"]),1)
if __name__=="__main__":unittest.main()
