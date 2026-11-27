#!/usr/bin/env python3
"""Generate clean-room, untrained DreamCo Model Foundry buyer kits."""
from __future__ import annotations
import argparse, hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DIVISION_REGISTRY = ROOT / "config/masterbot-65-registry.json"
OUTPUT_ROOT = ROOT / "commercial_kits"
MODEL_BLUEPRINTS: dict[str, dict[str, Any]] = {
 "45m-edge": {"display_name":"DreamCo 45M Edge Execution Agent","parameter_target":45038208,"parameter_label":"approximately 45M design target; verify instantiated tensor count","training_hardware":"CPU or entry GPU for constrained experiments; full pretraining is workload-dependent","inference_q4_estimate":"approximately 32 MB weights; runtime overhead is additional","config":{"architectures":["LlamaForCausalLM"],"model_type":"llama","vocab_size":32000,"hidden_size":512,"intermediate_size":1376,"num_hidden_layers":12,"num_attention_heads":8,"num_key_value_heads":4,"max_position_embeddings":2048,"rms_norm_eps":1e-6,"tie_word_embeddings":True,"torch_dtype":"bfloat16"},"curriculum":["tokenizer design","causal language modeling","SFT","JSON contract tasks","routing and safety holdouts"]},
 "350m-workstation": {"display_name":"DreamCo 350M Workstation Synthesis Agent","parameter_target":354800000,"parameter_label":"approximately 354.8M design target; verify instantiated tensor count","training_hardware":"8GB-12GB VRAM class for constrained/parameter-efficient workflows; full pretraining needs more","inference_q4_estimate":"approximately 240 MB weights; runtime overhead is additional","config":{"architectures":["LlamaForCausalLM"],"model_type":"llama","vocab_size":32000,"hidden_size":1024,"intermediate_size":2816,"num_hidden_layers":24,"num_attention_heads":16,"num_key_value_heads":8,"max_position_embeddings":4096,"rms_norm_eps":1e-6,"tie_word_embeddings":True,"torch_dtype":"bfloat16"},"curriculum":["tokenizer design","multi-division synthesis","sequence packing","SFT","DPO","GGUF packaging"]},
 "1b-sovereign": {"display_name":"DreamCo 1B Sovereign Flagship Agent","parameter_target":1020000000,"parameter_label":"approximately 1.02B design target; verify instantiated tensor count","training_hardware":"24GB+ VRAM or 32GB+ unified memory for constrained workflows; full pretraining may require multi-GPU","inference_q4_estimate":"approximately 680 MB weights; runtime overhead is additional","config":{"architectures":["LlamaForCausalLM"],"model_type":"llama","vocab_size":32000,"hidden_size":2048,"intermediate_size":5504,"num_hidden_layers":18,"num_attention_heads":16,"num_key_value_heads":8,"max_position_embeddings":4096,"rms_norm_eps":1e-6,"tie_word_embeddings":False,"torch_dtype":"bfloat16"},"curriculum":["tokenizer design","sequence-packed pretraining","multi-stage SFT","preference alignment","Buddy routing","65-division independent holdouts"]}
}
def load_divisions():
 r=json.loads(DIVISION_REGISTRY.read_text(encoding="utf-8")); ds=r.get("divisions",[])
 if r.get("canonical_count")!=65 or len(ds)!=65: raise ValueError("Canonical MasterBot registry must contain exactly 65 divisions")
 if sorted(int(d["id"]) for d in ds)!=list(range(1,66)) or len({d["name"] for d in ds})!=65: raise ValueError("Division IDs/names are not canonical")
 return sorted(ds,key=lambda d:int(d["id"]))
def slugify(s): return re.sub(r"[^a-z0-9]+","-",s.casefold()).strip("-")
def build_catalog():
 kits=[]
 for d in load_divisions():
  for tier,s in MODEL_BLUEPRINTS.items():
   kits.append({"sku":f"DCI-{int(d['id']):03d}-{tier.upper()}","division_id":int(d["id"]),"division":d["name"],"tier":tier,"product":s["display_name"],"parameter_target":s["parameter_target"],"parameter_count_verified":False,"weights_included":False,"weights_status":"UNTRAINED_BLUEPRINT_READY_FOR_TRAINING","commercial_position":"architecture_blueprint_and_training_curriculum_license","buyer_owns_resulting_weights":True,"royalty_on_buyer_trained_weights":0,"benchmark_status":"NOT_RUN","availability_status":"BLUEPRINT_SPECIFICATION"})
 return {"schema":"dreamco.institute_model_foundry_catalog.v1","catalog_version":"1.0.0","brand":"DreamCo Institute — Turnkey AI Model Foundry & Curriculum-in-a-Box","canonical_division_count":65,"tier_count":3,"kit_count":len(kits),"weights_policy":"No pretrained weights are included in DIY blueprint kits.","benchmark_policy":"No score may be advertised until a trained artifact passes independent holdouts.","kits":kits}
def build_buyer_foundry_kit(tier_key,division,output_root=OUTPUT_ROOT):
 if tier_key not in MODEL_BLUEPRINTS: raise ValueError(f"Unknown tier: {tier_key}")
 s=MODEL_BLUEPRINTS[tier_key]; did=int(division["id"]); name=str(division["name"])
 kit=Path(output_root)/f"dreamco_{did:03d}_{slugify(name)}_{tier_key}_kit"
 for sub in ("blueprint","curriculum","gates"): (kit/sub).mkdir(parents=True,exist_ok=True)
 cfg=dict(s["config"]); cfg.update({"dreamco_division_id":did,"dreamco_division":name,"dreamco_tier":tier_key,"dreamco_parameter_target":s["parameter_target"],"weights_status":"UNTRAINED_BLUEPRINT_READY_FOR_TRAINING","initialization":"random"})
 (kit/"blueprint/config.json").write_text(json.dumps(cfg,indent=2)+"\n",encoding="utf-8")
 manifest={"schema":"dreamco.buyer_foundry_manifest.v1","sku":f"DCI-{did:03d}-{tier_key.upper()}","product":s["display_name"],"division_id":did,"division":name,"tier":tier_key,"parameter_target":s["parameter_target"],"parameter_label":s["parameter_label"],"parameter_count_verified":False,"weights_included":False,"weights_status":"UNTRAINED_BLUEPRINT_READY_FOR_TRAINING","training_hardware_guidance":s["training_hardware"],"quantized_inference_footprint_guidance":s["inference_q4_estimate"],"benchmark_status":"NOT_RUN","dataset_status":"NO_DATASET_ADMITTED","buyer_data_policy":"Buyer data remains on buyer-controlled infrastructure unless separately authorized.","ownership":{"architecture_license":"subject_to_purchase_agreement","buyer_trained_weights":"buyer_owned_subject_to_agreement_and_law","royalties_on_buyer_trained_weights":0,"third_party_components":"each component retains its own license and terms"},"generated_at_utc":datetime.now(timezone.utc).isoformat(),"curriculum":s["curriculum"],"required_gates":["dataset_rights","source_provenance","clean_room","training_reproducibility","private_holdout","safety_regression","independent_review"]}
 manifest["kit_seal_sha256"]=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
 (kit/"BUYER_MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
 (kit/"curriculum/LEARNING_PATH.json").write_text(json.dumps({"schema":"dreamco.foundry_curriculum.v1","modules":s["curriculum"],"completion_requires":["practice_evidence","unit_tests","unseen_holdout","review_record"]},indent=2)+"\n",encoding="utf-8")
 (kit/"gates/RELEASE_POLICY.json").write_text(json.dumps({"schema":"dreamco.foundry_release_policy.v1","weights_status":"UNTRAINED_BLUEPRINT_READY_FOR_TRAINING","promotion_requires":["verified_checkpoint_hash","tokenizer_hash","dataset_rights_evidence","training_run_manifest","independent_holdout_pass","safety_regression_pass","human_review"],"missing_evidence":"BLOCK"},indent=2)+"\n",encoding="utf-8")
 return kit
def main():
 p=argparse.ArgumentParser(description=__doc__); p.add_argument("--catalog-only",action="store_true"); p.add_argument("--tier",choices=sorted(MODEL_BLUEPRINTS)); p.add_argument("--division-id",type=int); p.add_argument("--output",type=Path,default=OUTPUT_ROOT); a=p.parse_args()
 ds=load_divisions(); cat=build_catalog(); a.output.mkdir(parents=True,exist_ok=True); cp=a.output/"CATALOG.json"; cp.write_text(json.dumps(cat,indent=2)+"\n",encoding="utf-8")
 if a.catalog_only: print(json.dumps({"status":"CATALOG_GENERATED","sku_count":cat["kit_count"],"path":str(cp)})); return 0
 selected=ds if a.division_id is None else [d for d in ds if int(d["id"])==a.division_id]
 if not selected: raise SystemExit(f"Unknown division ID: {a.division_id}")
 tiers=[a.tier] if a.tier else list(MODEL_BLUEPRINTS); built=[str(build_buyer_foundry_kit(t,d,a.output)) for d in selected for t in tiers]
 print(json.dumps({"status":"BLUEPRINT_KITS_PACKAGED","kit_count":len(built),"catalog_skus":cat["kit_count"],"paths":built})); return 0
if __name__=="__main__": raise SystemExit(main())
