"""Inventory repository paths that contain benchmark artifacts or references.

This is a path-based discovery pass, not an exhaustive parser of every textual
benchmark reference. It creates a review queue and never claims runs or scores.
"""
from __future__ import annotations
import argparse,json,os
from pathlib import Path
from typing import Any

EXCLUDED={".git",".venv","venv","node_modules","dist","build",".next","__pycache__",".pytest_cache","coverage","vendor"}
TEXT_EXTENSIONS={".py",".json",".yaml",".yml",".md",".ts",".tsx",".js",".mjs",".cjs",".html",".toml",".sh",".sql",".txt"}

def classify(path:Path)->str:
 parts=[part.casefold() for part in path.parts]
 name=path.name.casefold()
 if ".github" in parts and "workflows" in parts: return "workflow"
 if any(part in {"tests","test","eval"} for part in parts) or name.startswith(("test_","test.")) or ".test." in name: return "test_or_evaluation"
 if any(part in {"docs","documentation"} for part in parts) or path.suffix.casefold()==".md": return "documentation"
 if path.suffix.casefold() in {".json",".yaml",".yml",".toml"}: return "configuration_or_manifest"
 if any(part in {"benchmarks","benchmark"} for part in parts): return "benchmark_suite_or_fixture"
 if any(part in {"tools","scripts"} for part in parts): return "builder_or_tool"
 return "runtime_or_other"

def scan_repository(root:Path)->dict[str,Any]:
 root=root.resolve()
 rows=[]
 for current,dirs,files in os.walk(root):
  dirs[:]=[name for name in dirs if name not in EXCLUDED]
  for filename in files:
   path=Path(current)/filename
   relative=path.relative_to(root)
   if "benchmark" not in str(relative).casefold(): continue
   if path.suffix.casefold() not in TEXT_EXTENSIONS: continue
   rel=relative.as_posix()
   rows.append({"path":rel,"artifact_type":classify(relative),"guide_status":"individual_guide_linkage_not_verified","test_status":"test_linkage_not_verified","execution_status":"not_measured_by_scanner","measured":False,"required_work":["identify_canonical_benchmark_id","document_purpose_and_capability","document_inputs_and_dataset_provenance","document_environment_and_baseline","define_metrics_and_source_backed_thresholds","document_holdout_and_contamination_controls","document_safety_and_permissions","link_executable_tests_and_evidence_schema","record_known_limitations_and_review"]})
 rows.sort(key=lambda row:row["path"])
 return {"schema":"dreamco.repository_benchmark_artifact_inventory.v1","root":"repository","scan_mode":"path_name_only","artifact_count":len(rows),"status":"discovery_inventory_requires_content_reconciliation","artifacts":rows,"truth_boundary":"A path containing benchmark is a discovery candidate, not proof that it is a benchmark, has an individual guide, has a working test, or has been executed. This scanner does not inspect all textual references and cannot establish exhaustive repository coverage."}

def main()->int:
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--root",type=Path,default=Path.cwd());parser.add_argument("--output",type=Path);args=parser.parse_args()
 result=scan_repository(args.root);rendered=json.dumps(result,indent=2)+"\n"
 if args.output: args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(rendered,encoding="utf-8")
 print(json.dumps({"artifact_count":result["artifact_count"],"scan_mode":result["scan_mode"],"status":result["status"]},indent=2))
 return 0
if __name__=="__main__":raise SystemExit(main())
