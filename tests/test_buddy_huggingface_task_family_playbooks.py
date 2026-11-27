import unittest
from tools.validate_buddy_huggingface_task_family_playbooks import validate
class HuggingFaceTaskFamilyPlaybookTests(unittest.TestCase):
 def setUp(self):
  self.taxonomy={"schema":"dreamco.huggingface_task_taxonomy.v1","task_families":[{"id":"text-classification"},{"id":"image-classification"}]}
  base={"learning_objectives":["a","b"],"ordered_workflow":["1","2","3","4","5","6"],"practice_lab":"lab","evaluation_metrics":["F1"],"risk_checks":["privacy"],"acceptance_criteria":["holdout"],"required_evidence":["hash"],"mastery_status":"not_assessed"}
  self.playbooks={"schema":"dreamco.huggingface_task_family_playbooks.v1","task_family_count":2,"modules":[dict(base,task_id="text-classification"),dict(base,task_id="image-classification")]}
 def test_exact_task_coverage(self): self.assertEqual(validate(self.taxonomy,self.playbooks),[])
 def test_missing_task_is_detected(self):
  self.playbooks["modules"].pop(); self.assertTrue(any("coverage mismatch" in e for e in validate(self.taxonomy,self.playbooks)))
 def test_duplicate_task_is_rejected(self):
  self.playbooks["modules"].append(dict(self.playbooks["modules"][0])); self.assertTrue(any("unique" in e for e in validate(self.taxonomy,self.playbooks)))
 def test_draft_cannot_claim_mastery(self):
  self.playbooks["modules"][0]["mastery_status"]="mastered"; self.assertTrue(any("cannot claim mastery" in e for e in validate(self.taxonomy,self.playbooks)))
if __name__=="__main__": unittest.main()
