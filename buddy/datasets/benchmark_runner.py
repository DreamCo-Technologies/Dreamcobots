"""Compare licensed open-weight candidates on the same isolated holdout."""
from __future__ import annotations
import hashlib,json,math,os,re,time
from pathlib import Path
from typing import Any
from buddy.datasets.hub import DatasetHub
from .transformers_runner import _load_rows,_split_hash,TrainingExecutionError

class BenchmarkExecutionError(RuntimeError): pass

def validate_benchmark_job(job:dict,approval_id:str)->tuple[Path,list[dict]]:
 if job.get("schema")!="dreamco.cross_model_benchmark_job.v1" or job.get("execution_status")!="NOT_EXECUTED":
  raise BenchmarkExecutionError("Invalid or already executed benchmark manifest")
 if not approval_id or approval_id!=job.get("compute_approval_id"): raise BenchmarkExecutionError("Compute approval ID mismatch")
 hub=Path(job["dataset_hub_path"]).resolve()
 card=DatasetHub(hub).get(job["dataset_id"],int(job["dataset_version"]))
 if not card or card.get("rights_status")!="VERIFIED" or not card.get("training_approved") or card.get("holdout"):
  raise BenchmarkExecutionError("Dataset card no longer authorizes this benchmark")
 card_hash=hashlib.sha256(json.dumps(card,sort_keys=True).encode()).hexdigest()
 if card_hash!=job.get("dataset_card_sha256") or card.get("content_sha256")!=job.get("dataset_sha256"):
  raise BenchmarkExecutionError("Dataset card or object provenance changed")
 allowed={int(card.get("primary_masterbot_id"))}|{int(x) for x in card.get("collaborating_masterbot_ids",[])}
 if int(job["masterbot_id"]) not in allowed: raise BenchmarkExecutionError("Benchmark dataset is not assigned to this MasterBot")
 obj=(hub/job["dataset_object_path"]).resolve()
 if hub not in obj.parents or not obj.is_file() or card.get("object_path")!=job["dataset_object_path"]:
  raise BenchmarkExecutionError("Benchmark data object missing or path mismatch")
 if hashlib.sha256(obj.read_bytes()).hexdigest()!=job.get("dataset_sha256"): raise BenchmarkExecutionError("Benchmark data hash mismatch")
 rows=_load_rows(obj)
 for split in ("train","validation","test"):
  if _split_hash(rows,split)!=job.get("split_manifest",{}).get(f"{split}_sha256"): raise BenchmarkExecutionError(f"{split} split hash mismatch")
 test=[x for x in rows if x["split"]=="test" and x["masterbot_id"]==int(job["masterbot_id"])]
 if not test: raise BenchmarkExecutionError("No isolated test examples for this MasterBot")
 candidates=job.get("candidates",[])
 if len(candidates)<2 or sum(1 for x in candidates if x.get("role")=="baseline")!=1: raise BenchmarkExecutionError("Benchmark must have exactly one baseline and one alternative")
 for x in candidates:
  if x.get("license_status")!="VERIFIED" or not x.get("license_evidence") or not x.get("license") or not str(x.get("license_url","")).startswith("https://") or not re.fullmatch(r"[0-9a-f]{40}",str(x.get("revision",""))):
   raise BenchmarkExecutionError("Candidate license evidence or immutable revision is invalid")
 return obj,test

def execute_benchmark(job_path:str|Path,approval_id:str,output_root:str|Path,allow_model_download:bool=False)->dict[str,Any]:
 job=json.loads(Path(job_path).read_text(encoding="utf-8"))
 _,rows=validate_benchmark_job(job,approval_id)
 if allow_model_download and os.environ.get("DREAMCO_ALLOW_MODEL_DOWNLOAD")!="1":
  raise BenchmarkExecutionError("Set DREAMCO_ALLOW_MODEL_DOWNLOAD=1 to authorize model downloads")
 try:
  import torch
  from transformers import AutoModelForCausalLM,AutoTokenizer
 except ImportError as exc: raise BenchmarkExecutionError("torch and transformers are required for model benchmarks") from exc
 results=[]
 for candidate in job["candidates"]:
  start=time.perf_counter()
  try:
   tokenizer=AutoTokenizer.from_pretrained(candidate["model_id"],revision=candidate["revision"],local_files_only=not allow_model_download)
   model=AutoModelForCausalLM.from_pretrained(candidate["model_id"],revision=candidate["revision"],local_files_only=not allow_model_download)
   model.eval()
   if tokenizer.pad_token is None: tokenizer.pad_token=tokenizer.eos_token
   total_nll=0.0;total_bytes=0;total_tokens=0
   device="cuda" if torch.cuda.is_available() else "cpu";model.to(device)
   if device=="cuda": torch.cuda.reset_peak_memory_stats()
   with torch.no_grad():
    for row in rows:
     text=row.get("text") or f"Instruction: {row.get('instruction','')} Response: {row.get('output','')}"
     encoded=tokenizer(text,return_tensors="pt",truncation=True,max_length=512)
     input_ids=encoded["input_ids"].to(device)
     if input_ids.shape[1]<2: continue
     outputs=model(input_ids=input_ids,labels=input_ids)
     count=input_ids.shape[1]-1
     total_nll+=float(outputs.loss.detach().cpu())*count
     total_tokens+=count;total_bytes+=len(text.encode("utf-8"))
   elapsed=time.perf_counter()-start
   result={"model_id":candidate["model_id"],"revision":candidate["revision"],"role":candidate["role"],
    "bits_per_utf8_byte":total_nll/math.log(2)/max(1,total_bytes),"tokens":total_tokens,
    "bytes":total_bytes,"seconds":elapsed,"tokens_per_second":total_tokens/max(elapsed,1e-9),
    "device":device,"peak_cuda_memory_bytes":torch.cuda.max_memory_allocated() if device=="cuda" else None,
    "status":"SCORED"}
  except Exception as exc:
   result={"model_id":candidate["model_id"],"revision":candidate["revision"],"role":candidate["role"],
    "status":"FAILED","error_type":type(exc).__name__}
  results.append(result)
 scored=sorted((x for x in results if x["status"]=="SCORED"),key=lambda x:x["bits_per_utf8_byte"])
 baseline=next(x for x in results if x["role"]=="baseline")
 report={"schema":"dreamco.cross_model_benchmark_result.v1","job_id":job["job_id"],
  "dataset_id":job["dataset_id"],"masterbot_id":job["masterbot_id"],"metric":"bits_per_utf8_byte",
  "results":results,"ranking":[x["model_id"] for x in scored],
  "baseline_model":baseline["model_id"],"baseline_score":baseline.get("bits_per_utf8_byte"),
  "test_split_used_for_training":False,"production_promotion":False,
  "interpretation":"Lower bits-per-UTF8-byte is better on this language-modeling holdout; this metric is not a complete domain task benchmark."}
 root=Path(output_root);root.mkdir(parents=True,exist_ok=True)
 path=root/f"{job['job_id']}-results.json";path.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 report["result_path"]=str(path);return report
