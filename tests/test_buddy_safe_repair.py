import unittest,sys,subprocess
from pathlib import Path
from tools.buddy_safe_repair import repair_plan,run_safe_repair,safe_observation_path,safe_output_path
class BuddySafeRepairTests(unittest.TestCase):
 def test_repair_module_imports_from_repository_root(self):
  root=Path(__file__).resolve().parents[1]
  result=subprocess.run([sys.executable,"-m","tools.buddy_safe_repair","--help"],cwd=root,text=True,capture_output=True,check=False)
  self.assertEqual(result.returncode,0,result.stderr)
  self.assertIn("--observation",result.stdout)
 def test_safe_repair_summary_uses_printf_without_shell_command_substitution(self):
  workflow=(Path(__file__).resolve().parents[1]/".github/workflows/buddy-ci-safe-repair.yml").read_text(encoding="utf-8")
  self.assertIn("printf 'Verified generated repairs are available on [%s]",workflow)
  self.assertNotIn("echo \"Verified generated repairs are available on [`$REPAIR_BRANCH`]",workflow)
 def test_safe_repair_branch_name_avoids_directory_file_namespace_conflicts(self):
  workflow=(Path(__file__).resolve().parents[1]/".github/workflows/buddy-ci-safe-repair.yml").read_text(encoding="utf-8")
  self.assertIn("REPAIR_BRANCH: ${{ format('buddy-ci-repair-{0}', github.event.workflow_run.id || github.run_id) }}",workflow)
  self.assertNotIn("buddy/ci-repair-",workflow)
 def test_generated_dataset_index_has_exact_allowlisted_rebuild(self):
  p=repair_plan({"workflow":"Buddy Dataset Hub","job":"route-build","failed_step":"generated index mismatch"})
  self.assertEqual(p,[[sys.executable,"tools/build_buddy_dataset_routes.py"]])
 def test_safe_repair_workflow_rebuilds_all_allowlisted_indexes(self):
  p=repair_plan({"workflow":"Buddy CI Safe Generated-Artifact Repair","job":"regenerate-and-verify","failed_step":"Verify repaired indexes and Buddy repair-learning tests"})
  self.assertEqual([command[1] for command in p],["tools/build_buddy_dataset_routes.py","tools/build_division_model_fleet.py","tools/build_pages_connection_index.py","tools/generate_bot_manifests.py","tools/refresh_repository_evidence.py","tools/generate_command_center_data.py"])
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
 def test_markdown_audit_and_file_prospectus_refresh_after_fleet_evidence(self):
  workflow=(Path(__file__).resolve().parents[1]/".github/workflows/buddy-ci-safe-repair.yml").read_text(encoding="utf-8")
  catalog=workflow.index("      - name: Regenerate canonical bot fleet catalog after certification drift")
  e2e=workflow.index("      - name: Regenerate canonical fleet end-to-end evidence after certification drift")
  markdown=workflow.index("python tools/audit_markdown_implementation_gaps.py --write")
  prospectus=workflow.index("      - name: Regenerate file prospectus after all generated source inventories")
  verify=workflow.index("      - name: Verify repaired indexes and Buddy repair-learning tests")
  self.assertLess(catalog,markdown)
  self.assertLess(e2e,markdown)
  self.assertLess(markdown,prospectus)
  self.assertLess(prospectus,verify)
 def test_safe_repair_result_never_persists_command_output(self):
  from unittest.mock import patch
  completed = subprocess.CompletedProcess(["python", "builder.py"], 0, "secret-like stdout", "secret-like stderr")
  status = subprocess.CompletedProcess(["git", "status"], 0, "", "")
  observation = {"workflow": "Buddy Dataset Hub", "job": "route-build", "failed_step": "generated index mismatch"}
  with patch("tools.buddy_safe_repair.subprocess.run", side_effect=[completed, status]):
   result = run_safe_repair(observation, Path("."))
  self.assertEqual(result["command_results"], [{"argv": [sys.executable, "tools/build_buddy_dataset_routes.py"], "returncode": 0}])
  self.assertNotIn("secret-like stdout", str(result))
  self.assertNotIn("secret-like stderr", str(result))


 def test_safe_observation_path_blocks_traversal(self):
  root=Path(__file__).resolve().parents[1]
  self.assertEqual(
   safe_observation_path(root,"artifacts/buddy-safe-repair/observation.json"),
   root/"artifacts/buddy-safe-repair/observation.json",
  )
  with self.assertRaises(ValueError):
   safe_observation_path(root,"../../outside.json")

 def test_safe_repair_blocks_unregistered_builder_commands(self):
  from unittest.mock import patch
  with patch("tools.buddy_safe_repair.repair_plan", return_value=[[sys.executable,"tools/evil.py"]]):
   result=run_safe_repair({"failure_class":"generated-index"},Path("."))
  self.assertEqual(result["status"],"BLOCKED_UNSAFE_COMMAND")
  self.assertFalse(result["executed"])


 def test_safe_output_path_accepts_only_dedicated_repair_artifact_directory(self):
  root=Path(__file__).resolve().parents[1]
  self.assertEqual(
   safe_output_path(root,"artifacts/buddy-safe-repair/result.json"),
   root/"artifacts/buddy-safe-repair/result.json",
  )
  with self.assertRaises(ValueError):
   safe_output_path(root,"../../outside.json")

if __name__=="__main__":unittest.main()



 def test_repair_output_path_is_confined_to_repair_artifacts(self):
  from tools.buddy_safe_repair import safe_output_path
  root=Path("/tmp/dreamco-repair-test")
  self.assertEqual(safe_output_path(root,"artifacts/buddy-safe-repair/result.json"),root/"artifacts/buddy-safe-repair/result.json")
  with self.assertRaises(ValueError):
   safe_output_path(root,"../.github/workflows/unsafe.yml")
  with self.assertRaises(ValueError):
   safe_output_path(root,"reports/public.json")


 def test_generated_repair_path_allowlist_blocks_sources_and_credentials(self):
  from tools.buddy_safe_repair import repair_path_allowed
  self.assertTrue(repair_path_allowed("website/data/bot-fleet-catalog.json"))
  self.assertTrue(repair_path_allowed("config/master_bot_registry.json"))
  self.assertFalse(repair_path_allowed("server/app.py"))
  self.assertFalse(repair_path_allowed("reports/.env"))
  self.assertFalse(repair_path_allowed("reports/private.pem"))
