#!/usr/bin/env python3
"""Build a privacy-safe command-center data observability snapshot."""
from __future__ import annotations
import argparse, hashlib, json, re, sqlite3
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
OUTPUTS=(ROOT/"command-center/data/data-observability.json",ROOT/"website/data/command-center/data-observability.json")
IGNORED={".git","__pycache__",".pytest_cache","node_modules","dist",".cache"}
SECRET=re.compile(r"(^|/)(\.env($|\.)|.*\.(pem|p12|pfx|key)$|id_(rsa|ed25519)$)",re.I)

def files_under(relative:str,suffixes:tuple[str,...]=())->list[Path]:
    base=ROOT/relative
    if not base.exists(): return []
    return sorted(p for p in base.rglob("*") if p.is_file()
        and not any(x in IGNORED for x in p.relative_to(ROOT).parts)
        and (not suffixes or p.suffix.lower() in suffixes)
        and not SECRET.search(p.relative_to(ROOT).as_posix()))

def build()->dict[str,Any]:
    roots=["data/dreamco_knowledge/packages","study_packs/datasets","datasets","data/datasets"]
    datasets=sorted({p for root in roots for p in files_under(root)})
    cards=[p for p in datasets if p.name.lower() in {"manifest.json","dataset_card.json","card.json"}]
    jobs=files_under("artifacts/buddy-training-jobs",(".json",))
    routes=files_under("artifacts/buddy-dataset-hub",(".json",))
    model_files=[p for root in ("models","artifacts/models","artifacts/model-registry")
        for p in files_under(root) if p.suffix.lower() in {".safetensors",".bin",".gguf",".onnx",".pt",".pth",".json"}]
    source_rows=[
      {"id":"dreamco_knowledge","name":"DreamCo knowledge packages","files":len(files_under("data/dreamco_knowledge/packages")),"status":"repository_inventory"},
      {"id":"study_packs","name":"Study packs and curriculum","files":len(files_under("study_packs/datasets")),"status":"repository_inventory"},
      {"id":"repository_datasets","name":"Repository dataset folders","files":len(files_under("datasets"))+len(files_under("data/datasets")),"status":"repository_inventory"},
      {"id":"huggingface","name":"Hugging Face datasets and model metadata","files":0,"status":"metadata_adapter_network_opt_in"},
      {"id":"openml","name":"OpenML metadata","files":0,"status":"metadata_adapter_network_opt_in"},
      {"id":"uci","name":"UCI repository metadata","files":0,"status":"metadata_adapter_network_opt_in"},
      {"id":"github","name":"Authorized GitHub repositories","files":0,"status":"scoped_metadata_and_file_adapter"},
      {"id":"sqlite_postgres","name":"Authorized database snapshots","files":0,"status":"read_only_allowlisted_adapter"}]
    runtime={"available":False,"dataset_versions":None,"datasets":None,"training_approved_versions":None,"holdout_versions":None}
    dbpath=ROOT/".dreamco/dataset-hub/catalog.sqlite3"
    if dbpath.is_file():
      try:
        with sqlite3.connect(f"file:{dbpath}?mode=ro",uri=True) as db:
          row=db.execute("SELECT COUNT(*),COUNT(DISTINCT dataset_id),SUM(training_approved),SUM(holdout) FROM datasets").fetchone()
        runtime={"available":True,"dataset_versions":row[0],"datasets":row[1],"training_approved_versions":row[2] or 0,"holdout_versions":row[3] or 0}
      except (sqlite3.Error,OSError): runtime={"available":True,"read_status":"unavailable_or_schema_mismatch"}
    return {"schema":"dreamco.command_center.data_observability.v1",
      "generated_from":"repository inventory and optional local SQLite aggregate",
      "privacy":{"raw_dataset_rows_exposed":False,"credentials_exposed":False,"private_cards_exposed":False,"model_weight_files_exposed":False},
      "summary":{"repository_dataset_files":len(datasets),"dataset_cards_or_manifests":len(cards),
        "dreamco_knowledge_packages":len(list((ROOT/"data/dreamco_knowledge/packages").glob("*"))) if (ROOT/"data/dreamco_knowledge/packages").exists() else 0,
        "training_job_manifests":len(jobs),"unknown_problem_route_artifacts":len(routes),"model_artifact_files":len(model_files),
        "runtime_catalog_available":runtime["available"],"external_sources_with_metadata_adapters":4,"database_adapter_families":2},
      "runtime_catalog":runtime,"sources":source_rows,
      "datasets":{"files":[p.relative_to(ROOT).as_posix() for p in datasets[:500]],"cards":[p.relative_to(ROOT).as_posix() for p in cards[:250]],"truncated":len(datasets)>500},
      "training":{"job_manifests":[p.relative_to(ROOT).as_posix() for p in jobs[:250]],"executed_jobs":0,"weights_updated_by_manifest_builder":0},
      "unknown_problems":{"route_artifacts":[p.relative_to(ROOT).as_posix() for p in routes[:250]]},
      "model_artifacts":{"count":len(model_files),"paths":[p.relative_to(ROOT).as_posix() for p in model_files[:100]],"truncated":len(model_files)>100},
      "observability_gaps":["Public Pages is a generated snapshot, not live telemetry.","External adapters do not prove successful authentication or source availability.","Private production databases require authenticated runtime telemetry.","Training manifests are requests, not completed training; model and benchmark evidence must come from registered runners."]}

def main()->int:
    parser=argparse.ArgumentParser(); parser.add_argument("--check",action="store_true"); args=parser.parse_args()
    expected=json.dumps(build(),indent=2,sort_keys=True,ensure_ascii=False)+"\n"
    stale=[]
    for path in OUTPUTS:
      if args.check:
        if not path.exists() or path.read_text(encoding="utf-8")!=expected: stale.append(path.relative_to(ROOT).as_posix())
      else:
        path.parent.mkdir(parents=True,exist_ok=True); path.write_text(expected,encoding="utf-8")
    if stale: print("Stale data observability artifacts:\n"+"\n".join(stale)); return 1
    print("Data observability snapshot "+("validated" if args.check else "generated")+" in both command-center destinations")
    return 0
if __name__=="__main__": raise SystemExit(main())
