import unittest
from tools.validate_buddy_freecodecamp_category_guides import validate
class FreeCodeCampCategoryGuideTests(unittest.TestCase):
 def setUp(self):
  self.catalog={"schema":"dreamco.freecodecamp_catalog.v1","inventory_status":"partial","categories":[{"id":"python"},{"id":"sql"}]}
  base={"learning_goal":"Goal","ordered_units":[{"order":1},{"order":2},{"order":3},{"order":4}],"capstone_project":"Capstone","assessment":"Assessment","evaluation_dimensions":["correctness"],"evidence_required":["test"],"rights_and_safety":"Rights","mastery_status":"not_assessed","status":"original_category_guide_draft_needs_human_review"}
  self.guides={"schema":"dreamco.freecodecamp_22_category_study_guides.v1","source_inventory_status":"partial","category_count":2,"categories":[dict(base,category_id="python"),dict(base,category_id="sql")]}
 def test_exact_category_coverage(self): self.assertEqual(validate(self.catalog,self.guides),[])
 def test_missing_category_is_detected(self):
  self.guides["categories"].pop(); self.assertTrue(any("coverage mismatch" in e for e in validate(self.catalog,self.guides)))
 def test_duplicate_category_is_rejected(self):
  self.guides["categories"].append(dict(self.guides["categories"][0])); self.assertTrue(any("unique" in e for e in validate(self.catalog,self.guides)))
 def test_mastery_claim_is_rejected(self):
  self.guides["categories"][0]["mastery_status"]="mastered"; self.assertTrue(any("cannot claim mastery" in e for e in validate(self.catalog,self.guides)))
 def test_source_completeness_status_is_preserved(self):
  self.guides["source_inventory_status"]="complete"; self.assertTrue(any("status mismatch" in e for e in validate(self.catalog,self.guides)))
if __name__=="__main__": unittest.main()
