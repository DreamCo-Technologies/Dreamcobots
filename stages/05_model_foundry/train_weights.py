"""Opt-in PT/CPT, SFT and DPO runner; validates signed data before loading a model.

This runner never downloads data. Weight updates require a signed policy manifest
and an explicit runtime authorization reference. CPU smoke checks use synthetic
fixtures; production runs belong on an explicitly managed GPU runner.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from .guardrails import iter_authorized_records, verify_signed_manifest

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--stage",choices=["pretrain","sft","dpo"],required=True)
    ap.add_argument("--manifest",type=Path,required=True); ap.add_argument("--signature",type=Path,required=True)
    ap.add_argument("--public-key",type=Path,required=True); ap.add_argument("--recipe",type=Path,required=True)
    ap.add_argument("--authorize-weight-updates",action="store_true")
    ap.add_argument("--authorization-reference")
    ap.add_argument("--dry-run",action="store_true")
    a=ap.parse_args()
    recipe=json.loads(a.recipe.read_text(encoding="utf-8")) if a.recipe.suffix==".json" else __import__("yaml").safe_load(a.recipe.read_text(encoding="utf-8"))
    manifest=verify_signed_manifest(a.manifest,a.signature,a.public_key)
    categories={"pretrain":{"study_guides","verified_trajectories","general_replay"},
                "sft":{"verified_trajectories"},"dpo":{"verified_preferences"}}[a.stage]
    rows=list(iter_authorized_records(manifest,categories=categories,splits={"train"}))
    if not rows: raise ValueError(f"no signed, authorized train rows for {a.stage}")
    if not a.dry_run and (not a.authorize_weight_updates or not a.authorization_reference):
        raise PermissionError("weight updates require --authorize-weight-updates and --authorization-reference")
    summary={"schema":"dreamco.foundry.training_preflight.v1","stage":a.stage,
      "authorized_train_records":len(rows),"dataset_categories":sorted(categories),
      "excluded_splits":["validation","holdout"],"dry_run":a.dry_run,
      "weight_updates_started":False,"note":"Preflight only. Connect a pinned, reviewed backend recipe before running PT/CPT, SFT or DPO."}
    out=Path(recipe.get("artifact_dir","artifacts/foundry"))/f"{a.stage}-preflight.json"
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,sort_keys=True))
if __name__=="__main__": main()
