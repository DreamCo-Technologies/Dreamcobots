import importlib.util, json, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
 s=importlib.util.spec_from_file_location(name,ROOT/path); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
clean=load("clean","stages/02_clean_room_synth/clean_room.py")
learn=load("learn","stages/03_learning_engine/learning_engine.py")
matrix=load("matrix","stages/04_division_matrix/division_matrix.py")
foundry=load("foundry","stages/05_model_foundry/holdout.py")
dash=load("dash","stages/07_dashboard/dashboard.py")
class TestCompletionStages(unittest.TestCase):
 def test_clean_room_contract_and_similarity(self):
  guide={"guide_id":"g1","title":"Original lesson","learning_objectives":["Explain a process"],"lesson":"Write a new explanation.","practice_lab":"Use synthetic data.","assessment":"Solve a new case.","safety_notes":["No live actions"]}
  self.assertEqual(clean.validate_guide(guide),[])
  self.assertFalse(clean.clean_room_gate(guide,["Write a new explanation. Use synthetic data. Solve a new case."])["accepted"])
  self.assertTrue(clean.clean_room_gate(guide,[])["accepted"])
 def test_learning_requires_lab_and_teachback_evidence(self):
  with tempfile.TemporaryDirectory() as d:
   e=learn.LearningEngine(Path(d)/"p.db")
   with self.assertRaises(ValueError): e.record_teach_back("l","g",.9,{"reviewer":"r","unseen_question_id":"q"})
   self.assertEqual(e.record_lab("l","g",.9,{"sandbox_run_id":"run1"}),"LAB_PASSED")
   self.assertEqual(e.record_teach_back("l","g",.9,{"reviewer":"r","unseen_question_id":"q"}),"TEACH_BACK_VERIFIED")
   e.close()
 def test_division_matrix_uses_canonical_65_and_never_fabricates_onet(self):
  out=matrix.build_matrix(ROOT/"config/masterbot-65-registry.json")
  self.assertEqual(out["division_count"],65); self.assertEqual(out["verified_onet_mappings"],0)
  self.assertTrue(all(x["onet_mapping_status"]=="unverified_not_mapped" for x in out["divisions"]))
 def test_holdout_is_deterministic_and_disjoint(self):
  tasks=[{"task_id":f"t{i}","prompt":str(i)} for i in range(100)]
  a=foundry.split_tasks(tasks); b=foundry.split_tasks(tasks)
  self.assertEqual(a,b); self.assertFalse(set(a["train_ids"])&set(a["holdout_ids"]))
  self.assertEqual(set(a["train_ids"])|set(a["holdout_ids"]),{x["task_id"] for x in tasks})
 def test_dashboard_reports_no_unproven_model(self):
  with tempfile.TemporaryDirectory() as d:
   db=learn.LearningEngine(Path(d)/"p.db"); db.close()
   result=dash.build_dashboard(ROOT/"config/masterbot-65-registry.json",Path(d)/"p.db",Path(d)/"truth.json")
   self.assertEqual(result["canonical_divisions"],65); self.assertFalse(result["trained_model_claim"])
if __name__=="__main__": unittest.main()
