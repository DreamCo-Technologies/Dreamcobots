"""Evaluation-only gate for isolated 95-99 holdout records; never trains or promotes."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from .guardrails import iter_authorized_records, verify_signed_manifest

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",type=Path,required=True); ap.add_argument("--signature",type=Path,required=True)
    ap.add_argument("--public-key",type=Path,required=True); ap.add_argument("--baseline",type=Path,required=True)
    ap.add_argument("--candidate",type=Path,required=True); ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    m=verify_signed_manifest(a.manifest,a.signature,a.public_key)
    rows=list(iter_authorized_records(m,splits={"holdout"}))
    if not rows: raise ValueError("no isolated holdout records found")
    baseline=json.loads(a.baseline.read_text()); candidate=json.loads(a.candidate.read_text())
    keys=("pass_rate","safety_gate_pass_rate")
    regressions={k:{"baseline":baseline.get(k),"candidate":candidate.get(k)}
      for k in keys if not isinstance(baseline.get(k),(int,float)) or not isinstance(candidate.get(k),(int,float)) or candidate[k]<baseline[k]}
    report={"schema":"dreamco.foundry.holdout_evaluation.v1","holdout_records":len(rows),
      "holdout_access":"evaluation_only","training_access":False,"regressions":regressions,
      "promotion_eligible":not regressions,"candidate_checkpoint_sha256":candidate.get("checkpoint_sha256")}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(report,indent=2)+"\n")
    if regressions: raise SystemExit("HOLDOUT REGRESSION: promotion blocked")
if __name__=="__main__": main()
