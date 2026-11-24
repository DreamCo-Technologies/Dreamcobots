import unittest,sys,subprocess
from pathlib import Path
from tools.buddy_safe_repair import repair_plan,run_safe_repair
class BuddySafeRepairTests(unittest.TestCase):
 def test_repair_module_imports_from_repository_root(self):
  root=Path(__file__).resolve().parents[1]
  result=subprocess.run([sys.executable,"-m","tools.buddy_safe_repair","--help"],cwd=root,text=True,capture_output=True,check=False)
  self.assertEqual(result.returncode,0,result.stderr)
  self.assertIn("--observation",result.stdout)
 def test_generated_dataset_index_has_exact_allowlisted_rebuild(self):
  p=repair_plan({"workflow":"Buddy Dataset Hub","job":"route-build","failed_step":"generated index mismatch"})
  self.assertEqual(p,[[sys.executable,"tools/build_buddy_dataset_routes.py"]])
 def test_safe_repair_workflow_rebuilds_all_allowlisted_indexes(self):
  p=repair_plan({"workflow":"Buddy CI Safe Generated-Artifact Repair","job":"regenerate-and-verify","failed_step":"Verify repaired indexes and Buddy repair-learning tests"})
  self.assertEqual([command[1] for command in p],["tools/build_buddy_dataset_routes.py","tools/build_division_model_fleet.py","tools/build_pages_connection_index.py","tools/build_actions_prospectus.py","tools/build_file_prospectus.py"])
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
 def test_repair_diagnosis_records_specialist_route(self):
  result=run_safe_repair({"failure_class":"security"},Path("."))
  self.assertEqual(result["primary_masterbot_id"],24)
  self.assertEqual(result["collaborating_masterbot_ids"],[56])
  self.assertFalse(result["executed"])
 def test_security_and_unknown_failures_never_run_commands(self):
  self.assertEqual(repair_plan({"failure_class":"security"}),[])
  self.assertEqual(repair_plan({"workflow":"random","job":"job","failed_step":"unknown"}),[])
if __name__=="__main__":unittest.main()
