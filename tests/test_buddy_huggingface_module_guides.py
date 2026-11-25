import unittest
from tools.validate_buddy_huggingface_module_guides import validate
class HuggingFaceModuleGuideTests(unittest.TestCase):
 def setUp(self):
  self.source={"schema":"dreamco.buddy_huggingface_full_learning_map.v1","ecosystem_modules":[{"id":"M1"},{"id":"M2"}],"official_courses":[{"id":"C1"}]}
  base={"learning_objectives":["a","b","c"],"lesson_sequence":[{"order":1},{"order":2},{"order":3}],"hands_on_lab":"lab","assessment":{"task":"task"},"failure_cases":["failure"],"required_evidence":["artifact"],"rights_policy":"rights","execution_status":"guide_draft_not_studied_or_benchmarked"}
  self.guides={"schema":"dreamco.huggingface_18_ecosystem_module_guides.v1","ecosystem_module_count":2,"modules":[dict(base,module_id="M1"),dict(base,module_id="M2")],"official_courses":[{"id":"C1"}]}
 def test_exact_module_and_course_coverage(self): self.assertEqual(validate(self.source,self.guides),[])
 def test_missing_module_detected(self):
  self.guides["modules"].pop(); self.assertTrue(any("module coverage mismatch" in e for e in validate(self.source,self.guides)))
 def test_course_inventory_mismatch_detected(self):
  self.guides["official_courses"]=[]; self.assertTrue(any("official course link inventory mismatch" in e for e in validate(self.source,self.guides)))
 def test_completion_claim_rejected(self):
  self.guides["modules"][0]["execution_status"]="completed"; self.assertTrue(any("invalid completion status" in e for e in validate(self.source,self.guides)))
if __name__=="__main__": unittest.main()
