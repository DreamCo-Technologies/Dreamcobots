import unittest
from tools.validate_buddy_division_specialist_courses import validate
class DivisionSpecialistCourseTests(unittest.TestCase):
 def setUp(self):
  self.source='export const DIVISION_DOMAIN_PROFILES = {\n  Alpha: {\n    purpose: "P", outcome: "O", boundary: "B", focusAreas: ["Research", "Planning"],\n  },\n  Beta: {\n    purpose: "P", outcome: "O", boundary: "B", focusAreas: ["Operations"],\n  },\n};'
  unit=lambda title:{"title":title,"learning_objective":"Goal","lesson_outline":["1","2"],"lab":"Lab","assessment":"Assess","required_evidence":["artifact"],"status":"original_specialist_unit_draft_needs_human_review"}
  self.courses={"schema":"dreamco.buddy_55_division_specialist_course_drafts.v1","division_count":2,"unit_count":3,"divisions":[
   {"division_name":"Alpha","purpose":"P","outcome":"O","boundary":"B","focus_areas":["Research","Planning"],"ordered_units":[unit("Research"),unit("Planning")],"course_status":"original_specialist_course_draft_needs_human_review","mastery_status":"not_assessed"},
   {"division_name":"Beta","purpose":"P","outcome":"O","boundary":"B","focus_areas":["Operations"],"ordered_units":[unit("Operations")],"course_status":"original_specialist_course_draft_needs_human_review","mastery_status":"not_assessed"}
  ]}
 def test_exact_division_and_focus_area_coverage(self): self.assertEqual(validate(self.source,self.courses),[])
 def test_missing_division_is_detected(self):
  self.courses["divisions"].pop(); self.assertTrue(any("coverage mismatch" in e for e in validate(self.source,self.courses)))
 def test_missing_focus_area_unit_is_detected(self):
  self.courses["divisions"][0]["ordered_units"].pop(); self.assertTrue(any("focus area" in e for e in validate(self.source,self.courses)))
 def test_course_cannot_claim_mastery(self):
  self.courses["divisions"][0]["mastery_status"]="mastered"; self.assertTrue(any("cannot claim mastery" in e for e in validate(self.source,self.courses)))
if __name__=="__main__": unittest.main()
