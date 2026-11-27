#!/usr/bin/env python3
"""Generate clean-room, untrained DreamCo Model Foundry buyer kits."""
from __future__ import annotations
import argparse, hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DIVISION_REGISTRY = ROOT / "config/masterbot-65-registry.json"
BUSINESS_PROFILE_CATALOG = ROOT / "config/buddy-55-division-specialist-course-drafts.json"
OUTPUT_ROOT = ROOT / "commercial_kits"
MODEL_BLUEPRINTS: dict[str, dict[str, Any]] = {
 "45m-edge": {"display_name":"DreamCo 45M Edge Execution Agent","parameter_target":45040128,"parameter_label":"45,040,128 parameters (computed from the declared Llama-style config)","training_hardware":"CPU experimentation or 4GB+ VRAM GPU; full training is workload-dependent","inference_q4_estimate":"approximately 22.5 MB raw 4-bit weight payload; quantization metadata and runtime overhead are additional","config":{"architectures":["LlamaForCausalLM"],"model_type":"llama","vocab_size":32000,"hidden_size":512,"intermediate_size":1042,"num_hidden_layers":12,"num_attention_heads":8,"num_key_value_heads":4,"max_position_embeddings":2048,"rms_norm_eps":1e-6,"tie_word_embeddings":True,"torch_dtype":"bfloat16"},"curriculum":["tokenizer design","causal language modeling","SFT","JSON contract tasks","routing and safety holdouts"]},
 "350m-workstation": {"display_name":"DreamCo 350M Workstation Synthesis Agent","parameter_target":349996032,"parameter_label":"349,996,032 parameters (computed from the declared Llama-style config)","training_hardware":"8GB-12GB VRAM class for constrained/parameter-efficient workflows; full pretraining needs more","inference_q4_estimate":"approximately 175 MB raw 4-bit weight payload; quantization metadata and runtime overhead are additional","config":{"architectures":["LlamaForCausalLM"],"model_type":"llama","vocab_size":32000,"hidden_size":1024,"intermediate_size":3278,"num_hidden_layers":24,"num_attention_heads":16,"num_key_value_heads":8,"max_position_embeddings":4096,"rms_norm_eps":1e-6,"tie_word_embeddings":True,"torch_dtype":"bfloat16"},"curriculum":["tokenizer design","multi-division synthesis","sequence packing","SFT","DPO","GGUF packaging"]},
 "1b-sovereign": {"display_name":"DreamCo 1B Sovereign Flagship Agent","parameter_target":1020086272,"parameter_label":"1,020,086,272 parameters (computed from the declared Llama-style config)","training_hardware":"24GB+ VRAM or 32GB+ unified memory for constrained workflows; full pretraining may require multi-GPU","inference_q4_estimate":"approximately 510 MB raw 4-bit weight payload; quantization metadata and runtime overhead are additional","config":{"architectures":["LlamaForCausalLM"],"model_type":"llama","vocab_size":32000,"hidden_size":2048,"intermediate_size":5990,"num_hidden_layers":18,"num_attention_heads":16,"num_key_value_heads":8,"max_position_embeddings":4096,"rms_norm_eps":1e-6,"tie_word_embeddings":False,"torch_dtype":"bfloat16"},"curriculum":["tokenizer design","sequence-packed pretraining","multi-stage SFT","preference alignment","Buddy routing","65-division independent holdouts"]}
}
def estimate_llama_parameters(config: dict[str, Any]) -> int:
    """Count parameters for the declared bias-free Llama-style decoder config.

    Includes token embeddings, optional untied LM head, per-layer Q/K/V/O
    projections, SwiGLU gate/up/down projections, RMSNorm weights and final norm.
    The instantiated model implementation must still verify this estimate.
    """
    vocab = int(config["vocab_size"])
    hidden = int(config["hidden_size"])
    intermediate = int(config["intermediate_size"])
    layers = int(config["num_hidden_layers"])
    heads = int(config["num_attention_heads"])
    kv_heads = int(config["num_key_value_heads"])
    if hidden % heads:
        raise ValueError("hidden_size must be divisible by num_attention_heads")
    head_dim = hidden // heads
    kv_dim = kv_heads * head_dim
    embeddings = vocab * hidden * (1 if config.get("tie_word_embeddings", False) else 2)
    attention = 2 * hidden * hidden + 2 * hidden * kv_dim
    mlp = 3 * hidden * intermediate
    norms = 2 * hidden
    return embeddings + layers * (attention + mlp + norms) + hidden


def load_divisions():
 r=json.loads(DIVISION_REGISTRY.read_text(encoding="utf-8")); ds=r.get("divisions",[])
 if r.get("canonical_count")!=65 or len(ds)!=65: raise ValueError("Canonical MasterBot registry must contain exactly 65 divisions")
 if sorted(int(d["id"]) for d in ds)!=list(range(1,66)) or len({d["name"] for d in ds})!=65: raise ValueError("Division IDs/names are not canonical")
 return sorted(ds,key=lambda d:int(d["id"]))
def slugify(s): return re.sub(r"[^a-z0-9]+","-",s.casefold()).strip("-")
def load_business_profiles():
 data=json.loads(BUSINESS_PROFILE_CATALOG.read_text(encoding="utf-8"))
 profiles=data.get("divisions",[])
 if data.get("division_count")!=55 or len(profiles)!=55:
  raise ValueError("Business-domain course catalog must contain exactly 55 profiles")
 ids=[str(p.get("division_id","")) for p in profiles]
 if any(not x for x in ids) or len(set(ids))!=55:
  raise ValueError("Business-profile IDs must be present and unique")
 if any(not p.get("division_name") or not p.get("purpose") or not p.get("outcome") or not p.get("boundary") or not p.get("focus_areas") for p in profiles):
  raise ValueError("Every business profile must have mission, outcome, boundary and focus areas")
 return sorted(profiles,key=lambda p:str(p["division_id"]))

def build_business_profile_foundry_kit(profile,output_root=OUTPUT_ROOT):
 s=MODEL_BLUEPRINTS["45m-edge"]
 profile_id=str(profile["division_id"]); name=str(profile["division_name"])
 computed_count=estimate_llama_parameters(s["config"])
 if computed_count != s["parameter_target"]:
  raise ValueError(f"45M parameter target mismatch: {computed_count} != {s['parameter_target']}")
 kit=Path(output_root)/"business_profiles"/f"dreamco_{slugify(name)}_45m-edge_kit"
 for sub in ("blueprint","curriculum","gates"): (kit/sub).mkdir(parents=True,exist_ok=True)
 cfg=dict(s["config"]); cfg.update({
  "computed_parameter_count":computed_count,"dreamco_business_profile_id":profile_id,
  "dreamco_business_profile":name,"dreamco_tier":"45m-edge",
  "dreamco_parameter_target":s["parameter_target"],
  "weights_status":"UNTRAINED_BLUEPRINT_READY_FOR_TRAINING","initialization":"random",
  "domain_specialization":"curriculum_and_future_training_data_only"
 })
 (kit/"blueprint/config.json").write_text(json.dumps(cfg,indent=2)+"\\n",encoding="utf-8")
 units=[{"id":u.get("unit_id"),"title":u.get("title"),"learning_objective":u.get("learning_objective"),"lab":u.get("lab"),"assessment":u.get("assessment")} for u in profile.get("ordered_units",[])]
 manifest={
  "schema":"dreamco.business_profile_foundry_manifest.v1",
  "sku":f"DCI-BIZ-{slugify(name).upper()}-45M",
  "product":f"DreamCo 45M {name} Domain Agent Blueprint",
  "business_profile_id":profile_id,"business_profile":name,
  "purpose":profile["purpose"],"serves":profile.get("serves",[]),
  "outcome":profile["outcome"],"boundary":profile["boundary"],
  "focus_areas":profile["focus_areas"],"tier":"45m-edge",
  "parameter_target":s["parameter_target"],"computed_parameter_count":computed_count,
  "parameter_label":s["parameter_label"],"weights_included":False,
  "weights_status":"UNTRAINED_BLUEPRINT_READY_FOR_TRAINING","domain_weights_status":"NOT_TRAINED",
  "training_hardware_guidance":s["training_hardware"],
  "quantized_inference_footprint_guidance":s["inference_q4_estimate"],
  "benchmark_status":"NOT_RUN","dataset_status":"NO_DATASET_ADMITTED",
  "buyer_data_policy":"Buyer data remains on buyer-controlled infrastructure unless separately authorized.",
  "ownership":{"architecture_license":"subject_to_purchase_agreement","buyer_trained_weights":"buyer_owned_subject_to_agreement_and_law","royalties_on_buyer_trained_weights":0,"third_party_components":"each component retains its own license and terms"},
  "generated_at_utc":datetime.now(timezone.utc).isoformat(),"curriculum_units":units,
  "required_gates":["dataset_rights","source_provenance","clean_room","training_reproducibility","private_holdout","safety_regression","independent_review"]
 }
 manifest["kit_seal_sha256"]=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
 (kit/"BUYER_MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\\n",encoding="utf-8")
 curriculum={"schema":"dreamco.business_profile_foundry_curriculum.v1","profile_id":profile_id,"profile":name,"course_title":profile.get("course_title"),"course_goal":profile.get("course_goal"),"prerequisites":profile.get("prerequisites",[]),"focus_areas":profile["focus_areas"],"modules":units,"capstone":profile.get("capstone"),"completion_requires":["practice_evidence","unit_tests","unseen_holdout","review_record"]}
 (kit/"curriculum/LEARNING_PATH.json").write_text(json.dumps(curriculum,indent=2)+"\\n",encoding="utf-8")
 release={"schema":"dreamco.foundry_release_policy.v1","weights_status":"UNTRAINED_BLUEPRINT_READY_FOR_TRAINING","domain_weights_status":"NOT_TRAINED","promotion_requires":["verified_checkpoint_hash","tokenizer_hash","dataset_rights_evidence","training_run_manifest","independent_holdout_pass","safety_regression_pass","human_review"],"missing_evidence":"BLOCK"}
 (kit/"gates/RELEASE_POLICY.json").write_text(json.dumps(release,indent=2)+"\\n",encoding="utf-8")
 return kit


def build_catalog():
 kits=[]
 for d in load_divisions():
  for tier,spec in MODEL_BLUEPRINTS.items():
   kits.append({"sku":f"DCI-{int(d['id']):03d}-{tier.upper()}","catalog_family":"masterbot_division","division_id":int(d["id"]),"division":d["name"],"tier":tier,"product":spec["display_name"],"parameter_target":spec["parameter_target"],"computed_parameter_count":estimate_llama_parameters(spec["config"]),"weights_included":False,"weights_status":"UNTRAINED_BLUEPRINT_READY_FOR_TRAINING","commercial_position":"architecture_blueprint_and_training_curriculum_license","buyer_owns_resulting_weights":True,"royalty_on_buyer_trained_weights":0,"benchmark_status":"NOT_RUN","availability_status":"BLUEPRINT_SPECIFICATION"})
 for profile in load_business_profiles():
  spec=MODEL_BLUEPRINTS["45m-edge"]
  kits.append({"sku":f"DCI-BIZ-{slugify(profile['division_name']).upper()}-45M","catalog_family":"business_profile_domain_model","business_profile_id":profile["division_id"],"business_profile":profile["division_name"],"tier":"45m-edge","product":f"DreamCo 45M {profile['division_name']} Domain Agent Blueprint","parameter_target":spec["parameter_target"],"computed_parameter_count":estimate_llama_parameters(spec["config"]),"weights_included":False,"weights_status":"UNTRAINED_BLUEPRINT_READY_FOR_TRAINING","domain_weights_status":"NOT_TRAINED","commercial_position":"domain_architecture_blueprint_and_training_curriculum_license","buyer_owns_resulting_weights":True,"royalty_on_buyer_trained_weights":0,"benchmark_status":"NOT_RUN","availability_status":"BLUEPRINT_SPECIFICATION"})
 return {"schema":"dreamco.institute_model_foundry_catalog.v1","catalog_version":"1.1.0","brand":"DreamCo Institute — Turnkey AI Model Foundry & Curriculum-in-a-Box","masterbot_division_count":65,"business_profile_count":55,"masterbot_tier_count":3,"business_profile_tier":"45m-edge","masterbot_kit_count":195,"business_profile_kit_count":55,"kit_count":len(kits),"weights_policy":"No pretrained weights are included in DIY blueprint kits.","benchmark_policy":"No score may be advertised until a trained artifact passes independent holdouts.","kits":kits}
def build_buyer_foundry_kit(tier_key,division,output_root=OUTPUT_ROOT):
 if tier_key not in MODEL_BLUEPRINTS: raise ValueError(f"Unknown tier: {tier_key}")
 s=MODEL_BLUEPRINTS[tier_key]; did=int(division["id"]); name=str(division["name"])
 kit=Path(output_root)/f"dreamco_{did:03d}_{slugify(name)}_{tier_key}_kit"
 for sub in ("blueprint","curriculum","gates"): (kit/sub).mkdir(parents=True,exist_ok=True)
 computed_count=estimate_llama_parameters(s["config"])
 if computed_count != s["parameter_target"]: raise ValueError(f"parameter target mismatch for {tier_key}: {computed_count} != {s['parameter_target']}")
 cfg=dict(s["config"]); cfg.update({"computed_parameter_count":computed_count,"dreamco_division_id":did,"dreamco_division":name,"dreamco_tier":tier_key,"dreamco_parameter_target":s["parameter_target"],"weights_status":"UNTRAINED_BLUEPRINT_READY_FOR_TRAINING","initialization":"random"})
 (kit/"blueprint/config.json").write_text(json.dumps(cfg,indent=2)+"\n",encoding="utf-8")
 manifest={"schema":"dreamco.buyer_foundry_manifest.v1","sku":f"DCI-{did:03d}-{tier_key.upper()}","product":s["display_name"],"division_id":did,"division":name,"tier":tier_key,"parameter_target":s["parameter_target"],"computed_parameter_count":computed_count,"parameter_label":s["parameter_label"],"weights_included":False,"weights_status":"UNTRAINED_BLUEPRINT_READY_FOR_TRAINING","training_hardware_guidance":s["training_hardware"],"quantized_inference_footprint_guidance":s["inference_q4_estimate"],"benchmark_status":"NOT_RUN","dataset_status":"NO_DATASET_ADMITTED","buyer_data_policy":"Buyer data remains on buyer-controlled infrastructure unless separately authorized.","ownership":{"architecture_license":"subject_to_purchase_agreement","buyer_trained_weights":"buyer_owned_subject_to_agreement_and_law","royalties_on_buyer_trained_weights":0,"third_party_components":"each component retains its own license and terms"},"generated_at_utc":datetime.now(timezone.utc).isoformat(),"curriculum":s["curriculum"],"required_gates":["dataset_rights","source_provenance","clean_room","training_reproducibility","private_holdout","safety_regression","independent_review"]}
 manifest["kit_seal_sha256"]=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
 (kit/"BUYER_MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
 (kit/"curriculum/LEARNING_PATH.json").write_text(json.dumps({"schema":"dreamco.foundry_curriculum.v1","modules":s["curriculum"],"completion_requires":["practice_evidence","unit_tests","unseen_holdout","review_record"]},indent=2)+"\n",encoding="utf-8")
 (kit/"gates/RELEASE_POLICY.json").write_text(json.dumps({"schema":"dreamco.foundry_release_policy.v1","weights_status":"UNTRAINED_BLUEPRINT_READY_FOR_TRAINING","promotion_requires":["verified_checkpoint_hash","tokenizer_hash","dataset_rights_evidence","training_run_manifest","independent_holdout_pass","safety_regression_pass","human_review"],"missing_evidence":"BLOCK"},indent=2)+"\n",encoding="utf-8")
 return kit
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--catalog-only",action="store_true")
 p.add_argument("--tier",choices=sorted(MODEL_BLUEPRINTS))
 p.add_argument("--division-id",type=int,help="Select one of the 65 MasterBot divisions")
 p.add_argument("--business-profiles-only",action="store_true",help="Generate the 55 business-profile 45M kits only")
 p.add_argument("--business-profile-id",help="Generate one business-profile 45M kit by profile ID")
 p.add_argument("--output",type=Path,default=OUTPUT_ROOT)
 a=p.parse_args()
 ds=load_divisions(); profiles=load_business_profiles(); cat=build_catalog(); a.output.mkdir(parents=True,exist_ok=True)
 cp=a.output/"CATALOG.json"; cp.write_text(json.dumps(cat,indent=2)+"\\n",encoding="utf-8")
 if a.catalog_only:
  print(json.dumps({"status":"CATALOG_GENERATED","sku_count":cat["kit_count"],"masterbot_kits":cat["masterbot_kit_count"],"business_profile_kits":cat["business_profile_kit_count"],"path":str(cp)})); return 0
 if a.business_profiles_only or a.business_profile_id:
  selected_profiles=profiles if a.business_profile_id is None else [x for x in profiles if x["division_id"]==a.business_profile_id]
  if not selected_profiles: raise SystemExit(f"Unknown business profile ID: {a.business_profile_id}")
  built=[str(build_business_profile_foundry_kit(x,a.output)) for x in selected_profiles]
  print(json.dumps({"status":"BUSINESS_PROFILE_BLUEPRINT_KITS_PACKAGED","kit_count":len(built),"catalog_skus":cat["kit_count"],"paths":built})); return 0
 selected=ds if a.division_id is None else [d for d in ds if int(d["id"])==a.division_id]
 if not selected: raise SystemExit(f"Unknown MasterBot division ID: {a.division_id}")
 tiers=[a.tier] if a.tier else list(MODEL_BLUEPRINTS)
 built=[str(build_buyer_foundry_kit(t,d,a.output)) for d in selected for t in tiers]
 if a.division_id is None and a.tier is None:
  built.extend(str(build_business_profile_foundry_kit(x,a.output)) for x in profiles)
 print(json.dumps({"status":"BLUEPRINT_KITS_PACKAGED","kit_count":len(built),"catalog_skus":cat["kit_count"],"paths":built})); return 0
if __name__=="__main__": raise SystemExit(main())
