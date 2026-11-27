import unittest
from tools.validate_buddy_division_masterbot_learning_paths import validate

class DivisionMasterbotLearningPathTests(unittest.TestCase):
 def setUp(self):
  self.registry={"divisions":[{"id":1,"name":"MB1"},{"id":2,"name":"MB2"}]}
  self.crosswalk={"domains":[]}
  self.contract="export const DIVISION_DOMAIN_PROFILES: Record<string, DivisionDomainProfile> = {\n  Alpha: {\n    purpose: \"Purpose\", serves: [\"users\"], outcome: \"Outcome\", boundary: \"Boundary\", focusAreas: [\"area\"],\n  },\n  Beta: {\n    purpose: \"Purpose\", serves: [\"users\"], outcome: \"Outcome\", boundary: \"Boundary\", focusAreas: [\"area\"],\n  },\n};"
  stages=["mission_and_boundaries","domain_fundamentals","tools_and_software","professional_workflows","specialist_capabilities","benchmark_and_transfer","instructor_and_improvement"]
  self.paths={"schema":"dreamco.division_masterbot_ordered_learning_paths.v1","stage_template":[{"id":x} for x in stages],"divisions":[{"division_name":"Alpha","purpose":"P","outcome":"O","boundary":"B","focus_areas":["x"]},{"division_name":"Beta","purpose":"P","outcome":"O","boundary":"B","focus_areas":["x"]}],"masterbot_lanes":[{"masterbot_id":1,"masterbot_name":"MB1","division_mapping":None},{"masterbot_id":2,"masterbot_name":"MB2","division_mapping":None}],"ownership_policy":{"exact_name_match_is_proposal_only":True}}
 def test_exact_canonical_coverage(self):
  self.assertEqual(validate(self.paths,self.registry,self.crosswalk,self.contract),[])
 def test_missing_division_is_detected(self):
  self.paths["divisions"].pop()
  self.assertTrue(any("division coverage mismatch" in e for e in validate(self.paths,self.registry,self.crosswalk,self.contract)))
 def test_duplicate_masterbot_lane_is_rejected(self):
  self.paths["masterbot_lanes"][1]["masterbot_id"]=1
  self.assertTrue(any("unique" in e for e in validate(self.paths,self.registry,self.crosswalk,self.contract)))
 def test_proposed_ownership_cannot_be_approved_implicitly(self):
  self.paths["masterbot_lanes"][0]["division_mapping"]={"review_required":False,"owner_approval":None}
  self.assertTrue(any("must remain unapproved" in e for e in validate(self.paths,self.registry,self.crosswalk,self.contract)))

if __name__=="__main__": unittest.main()
