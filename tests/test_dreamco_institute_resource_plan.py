import json,unittest
from pathlib import Path
from tools.build_dreamco_institute_resource_plan import build_plan,ROOT,DIVISIONS,RESOURCES
class InstituteResourcePlanTests(unittest.TestCase):
 def test_routes_all_100_sources_to_all_65_divisions_as_metadata_only(self):
  plan=build_plan(json.loads(DIVISIONS.read_text()),json.loads(RESOURCES.read_text()))
  self.assertEqual(plan["division_count"],65);self.assertEqual(plan["source_count"],100);self.assertEqual(plan["assignment_count"],6500)
  self.assertTrue(all(d["resource_count"]==100 for d in plan["divisions"]))
  self.assertTrue(all(not r["content_acquired"] and not r["training_enabled"] for d in plan["divisions"] for r in d["resources"]))
 def test_unknown_rights_remain_blocked(self):
  plan=build_plan(json.loads(DIVISIONS.read_text()),json.loads(RESOURCES.read_text()))
  self.assertTrue(all(r["quarantine_status"]=="BLOCKED_PENDING_REVIEW" for d in plan["divisions"] for r in d["resources"]))
if __name__=="__main__":unittest.main()
