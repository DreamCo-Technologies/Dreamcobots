import unittest
from pathlib import Path
from tools.buddy_safe_repair import repair_plan
class BuddySafeRepairTests(unittest.TestCase):
 def test_generated_dataset_index_has_exact_allowlisted_rebuild(self):
  p=repair_plan({"workflow":"Buddy Dataset Hub","job":"route-build","failed_step":"generated index mismatch"})
  self.assertEqual(p,[["python","tools/build_buddy_dataset_routes.py"]])
 def test_division_fleet_rebuild_is_narrowly_allowlisted(self):
  p=repair_plan({"workflow":"DreamCo Division Mastery Engine","job":"division fleet","failed_step":"generated index mismatch"})
  self.assertEqual(p,[["python","tools/build_division_model_fleet.py"]])
 def test_security_and_unknown_failures_never_run_commands(self):
  self.assertEqual(repair_plan({"failure_class":"security"}),[])
  self.assertEqual(repair_plan({"workflow":"random","job":"job","failed_step":"unknown"}),[])
if __name__=="__main__":unittest.main()
