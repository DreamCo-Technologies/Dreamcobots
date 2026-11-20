"""Create an approval-gated cross-model benchmark manifest."""
from __future__ import annotations
import json,re,uuid
from datetime import datetime,timezone
from pathlib import Path
from buddy.datasets.hub import DatasetHub,DatasetPolicyError
ROOT=Path(__file__).resolve().parents[2]
def create_benchmark_job(hub:DatasetHub,dataset_id:str,masterbot_id:int,candidates:list[dict],
                         compute_approval_id:str,output_dir:str|Path="artifacts/buddy-model-benchmarks")->dict:
 card=hub.get(dataset_id)
 if not card or card.get("rights_status")!="VERIFIED" or not card.get("training_approved"):
  raise DatasetPolicyError("Benchmark dataset requires verified rights and an approved card")
 if card.get("holdout") or not card.get("content_sha256") or not card.get("object_path"):
  raise DatasetPolicyError("A versioned dataset object with an isolated test split is required")
 owners={int(card.get("primary_masterbot_id"))}|{int(x) for x in card.get("collaborating_masterbot_ids",[])}
 if masterbot_id not in owners: raise DatasetPolicyError("Dataset is not assigned to this MasterBot")
 if not compute_approval_id.strip(): raise DatasetPolicyError("Benchmark compute approval ID is required")
 if len(candidates)<2: raise DatasetPolicyError("Provide a baseline and at least one alternative candidate")
 roles=[x.get("role") for x in candidates]
 if roles.count("baseline")!=1: raise DatasetPolicyError("Exactly one baseline candidate is required")
 clean=[]
 for item in candidates:
  if not item.get("model_id") or not re.fullmatch(r"[0-9a-f]{40}",str(item.get("revision",""))):
   raise DatasetPolicyError("Every candidate requires a model ID and immutable 40-character revision")
  if item.get("license_status")!="VERIFIED" or not item.get("license") or not str(item.get("license_url","")).startswith("https://") or not item.get("license_evidence"):
   raise DatasetPolicyError("Every candidate requires verified model-license evidence")
  if item.get("role") not in {"baseline","trained_candidate","open_weight_alternative"}:
   raise DatasetPolicyError("Unsupported benchmark candidate role")
  clean.append({k:item[k] for k in ("model_id","revision","license","license_url","license_status","license_evidence","role")})
 payload={"schema":"dreamco.cross_model_benchmark_job.v1","job_id":"bench-"+uuid.uuid4().hex[:16],
  "created_at":datetime.now(timezone.utc).isoformat(),"dataset_id":dataset_id,"dataset_version":card["version"],
  "dataset_sha256":card["content_sha256"],"dataset_card_sha256":__import__("hashlib").sha256(json.dumps(card,sort_keys=True).encode()).hexdigest(),
  "dataset_hub_path":str(hub.home.resolve()),"dataset_object_path":card["object_path"],
  "split_manifest":card["split_manifest"],"masterbot_id":masterbot_id,"compute_approval_id":compute_approval_id,
  "candidates":clean,"metric":"bits_per_utf8_byte","test_split_only":True,"status":"READY_FOR_EXPLICIT_BENCHMARK",
  "execution_status":"NOT_EXECUTED","production_promotion":False}
 root=Path(output_dir);root.mkdir(parents=True,exist_ok=True)
 path=root/f"{payload['job_id']}.json";path.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
 payload["manifest_path"]=str(path);return payload
