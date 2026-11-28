"""Truth dashboard assembled from persisted evidence, never hand-entered success counters."""
from __future__ import annotations
import json, sqlite3
from pathlib import Path
def build_dashboard(registry_path:str|Path,progress_db:str|Path,output_path:str|Path)->dict:
    registry=json.loads(Path(registry_path).read_text())
    con=sqlite3.connect(str(progress_db))
    try:
        rows=con.execute("SELECT state,COUNT(*) FROM learner_progress GROUP BY state").fetchall()
    except sqlite3.OperationalError: rows=[]
    finally: con.close()
    counts={state:0 for state in ("NOT_STARTED","IN_PROGRESS","LAB_PASSED","TEACH_BACK_VERIFIED")}
    counts.update(dict(rows))
    result={"schema":"dreamco.bootcamp_truth_dashboard.v1","canonical_divisions":len(registry.get("divisions",[])),
      "learner_progress_by_state":counts,"verified_masteries":counts["TEACH_BACK_VERIFIED"],
      "generated_from":"masterbot-65-registry.json + learner_progress SQLite evidence",
      "training_checkpoint_count":0,"trained_model_claim":False,
      "truth_boundary":"No checkpoint or benchmark is claimed unless a separately verified artifact is supplied."}
    Path(output_path).parent.mkdir(parents=True,exist_ok=True)
    Path(output_path).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    return result
