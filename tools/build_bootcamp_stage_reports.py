"""Generate auditable division and learner-truth reports for CI."""
from __future__ import annotations
import importlib.util, json, sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,ROOT/path)
 module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
def main():
 out=ROOT/"reports/bootcamp"; out.mkdir(parents=True,exist_ok=True)
 matrix=load("division_matrix","stages/04_division_matrix/division_matrix.py")
 dashboard=load("dashboard","stages/07_dashboard/dashboard.py")
 registry=ROOT/"config/masterbot-65-registry.json"
 matrix_data=matrix.build_matrix(registry,ROOT/"config/dreamco-division-curricula-manifest.json")
 (out/"division-matrix.json").write_text(json.dumps(matrix_data,indent=2)+"\n")
 db=out/"learner-progress.sqlite3"
 con=sqlite3.connect(db); con.execute("""CREATE TABLE IF NOT EXISTS learner_progress(learner_id TEXT,guide_id TEXT,state TEXT,lab_score REAL,teach_back_score REAL,evidence_json TEXT,updated_at INTEGER,PRIMARY KEY(learner_id,guide_id))"""); con.commit(); con.close()
 truth=dashboard.build_dashboard(registry,db,out/"bootcamp-truth.json")
 print(json.dumps({"division_count":matrix_data["division_count"],"mapped_curricula":matrix_data["mapped_curricula"],"verified_onet_mappings":matrix_data["verified_onet_mappings"],"verified_masteries":truth["verified_masteries"],"trained_model_claim":truth["trained_model_claim"]},sort_keys=True))
if __name__=="__main__": main()
