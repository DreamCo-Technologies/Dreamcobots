import unittest,sys
from pathlib import Path
from tools.buddy_safe_repair import repair_plan
class BuddySafeRepairTests(unittest.TestCase):
 def test_generated_dataset_index_has_exact_allowlisted_rebuild(self):
  p=repair_plan({"workflow":"Buddy Dataset Hub","job":"route-build","failed_step":"generated index mismatch"})
  self.assertEqual(p,[[sys.executable,"tools/build_buddy_dataset_routes.py"]])
 def test_unrelated_generated_index_failure_is_not_guessed(self):
  self.assertEqual(repair_plan({"workflow":"Repository Inventory","job":"inventory","failed_step":"generated index mismatch"}),[])
 def test_division_fleet_rebuild_is_narrowly_allowlisted(self):
  p=repair_plan({"workflow":"DreamCo Division Mastery Engine","job":"division fleet","failed_step":"generated index mismatch"})
  self.assertEqual(p,[[sys.executable,"tools/build_division_model_fleet.py"]])
 def test_pages_connection_index_rebuild_is_exactly_allowlisted(self):
  p=repair_plan({"workflow":"Buddy Pages Connection Index","job":"pages connection","failed_step":"generated index mismatch"})
  self.assertEqual(p,[[sys.executable,"tools/build_pages_connection_index.py"]])
 def test_actions_prospectus_rebuild_is_exactly_allowlisted(self):
  p=repair_plan({"workflow":"Actions Health","job":"actions prospectus","failed_step":"generated index mismatch"})
  self.assertEqual(p,[[sys.executable,"tools/build_actions_prospectus.py"]])
 def test_file_prospectus_rebuild_is_exactly_allowlisted(self):
  p=repair_plan({"workflow":"Repository File Prospectus","job":"file prospectus","failed_step":"generated index mismatch"})
  self.assertEqual(p,[[sys.executable,"tools/build_file_prospectus.py"]])
 def test_security_and_unknown_failures_never_run_commands(self):
  self.assertEqual(repair_plan({"failure_class":"security"}),[])
  self.assertEqual(repair_plan({"workflow":"random","job":"job","failed_step":"unknown"}),[])
if __name__=="__main__":unittest.main()
