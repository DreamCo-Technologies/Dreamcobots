import unittest
from tools.validate_buddy_onet_31_subject_guides import validate
class Onet31SubjectGuideTests(unittest.TestCase):
 def setUp(self):
  self.curriculum={"schema":"dreamco.buddy_onet_content_model_curriculum.v1","source":{"current_reference_release":"31.0"},"subject_inventory":[{"id":"s1"},{"id":"s2"}]}
  base={"learning_goal":"Goal","lesson_outline":["one","two","three"],"hands_on_lab":"Lab","assessment":"Assessment","professional_safeguard":"Safeguard","required_evidence":["artifact"],"rights_and_source_policy":"CC BY","mastery_status":"not_assessed","lesson_status":"original_draft_needs_human_review"}
  self.guides={"schema":"dreamco.onet_31_subject_study_guides.v1","source_release":"31.0","attribution":"O*NET 31.0 Database","subjects":[dict(base,subject_id="s1"),dict(base,subject_id="s2")]}
 def test_exact_subject_coverage_passes(self): self.assertEqual(validate(self.curriculum,self.guides),[])
 def test_missing_subject_is_reported(self):
  self.guides["subjects"].pop(); self.assertTrue(any("subject coverage mismatch" in e for e in validate(self.curriculum,self.guides)))
 def test_duplicate_subject_is_rejected(self):
  self.guides["subjects"].append(dict(self.guides["subjects"][0])); self.assertTrue(any("unique" in e for e in validate(self.curriculum,self.guides)))
 def test_draft_cannot_claim_mastery(self):
  self.guides["subjects"][0]["mastery_status"]="mastered"; self.assertTrue(any("cannot claim mastery" in e for e in validate(self.curriculum,self.guides)))
 def test_release_mismatch_is_rejected(self):
  self.guides["source_release"]="30.0"; self.assertTrue(any("release mismatch" in e for e in validate(self.curriculum,self.guides)))
if __name__=="__main__": unittest.main()
