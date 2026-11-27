"""Run deterministic domain task evaluations against isolated private holdouts.

Reports contain aggregate metrics and task IDs only; prompts, references, and
generated answers are never copied into benchmark evidence.
"""
from __future__ import annotations
import hashlib,json,math,os,re,time
from pathlib import Path
from typing import Any
from .hub import DatasetHub,sha256_file

class PrivateHoldoutBenchmarkError(RuntimeError):
    """A private holdout benchmark failed validation or execution."""

def _rows(path:Path,masterbot_id:int)->list[dict[str,Any]]:
    output=[]
    for number,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
        if not line.strip(): continue
        try: row=json.loads(line)
        except json.JSONDecodeError as exc: raise PrivateHoldoutBenchmarkError(f"invalid_holdout_jsonl_line_{number}") from exc
        if (not isinstance(row,dict) or row.get("masterbot_id")!=masterbot_id or row.get("split")!="test"
            or not str(row.get("task_id","")).strip() or not str(row.get("prompt","")).strip()
            or not str(row.get("expected","")).strip() or row.get("metric") not in {"exact_match","token_f1"}):
            raise PrivateHoldoutBenchmarkError("every row must be a valid test-only task for the assigned MasterBot")
        output.append(row)
    if not output: raise PrivateHoldoutBenchmarkError("private_holdout_is_empty")
    return output

def _normalize(text:str)->str:
    return " ".join(re.findall(r"\w+",text.casefold()))

def _token_f1(prediction:str,reference:str)->float:
    pred=_normalize(prediction).split();ref=_normalize(reference).split()
    if not pred or not ref: return float(pred==ref)
    from collections import Counter
    p,r=Counter(pred),Counter(ref);common=sum((p&r).values())
    if not common: return 0.0
    precision=common/len(pred);recall=common/len(ref)
    return 2*precision*recall/(precision+recall)

def score_prediction(prediction:str,reference:str)->dict[str,float]:
    return {"exact_match":float(_normalize(prediction)==_normalize(reference)),
            "token_f1":_token_f1(prediction,reference)}

def validate_private_holdout_job(job:dict,approval_id:str)->tuple[Path,list[dict[str,Any]]]:
    if job.get("schema")!="dreamco.private_holdout_benchmark_job.v1" or job.get("execution_status")!="NOT_EXECUTED":
        raise PrivateHoldoutBenchmarkError("invalid_or_already_executed_holdout_job")
    if not approval_id or approval_id!=job.get("compute_approval_id"):
        raise PrivateHoldoutBenchmarkError("compute_approval_id_mismatch")
    hub=Path(job["dataset_hub_path"]).resolve()
    card=DatasetHub(hub).get(job["dataset_id"],int(job["dataset_version"]))
    if not card or card.get("data_plane")!="evaluation_only_holdout" or card.get("holdout") is not True:
        raise PrivateHoldoutBenchmarkError("dataset_is_not_an_evaluation_only_holdout")
    if card.get("training_approved") is not False or card.get("evaluation_approved") is not True or card.get("rights_status")!="VERIFIED":
        raise PrivateHoldoutBenchmarkError("holdout_rights_or_training_exclusion_changed")
    if card.get("primary_masterbot_id")!=job.get("masterbot_id"):
        raise PrivateHoldoutBenchmarkError("holdout_masterbot_owner_mismatch")
    if hashlib.sha256(json.dumps(card,sort_keys=True).encode()).hexdigest()!=job.get("dataset_card_sha256"):
        raise PrivateHoldoutBenchmarkError("holdout_dataset_card_changed")
    if card.get("content_sha256")!=job.get("dataset_sha256") or card.get("split_manifest")!=job.get("split_manifest"):
        raise PrivateHoldoutBenchmarkError("holdout_hash_or_split_manifest_changed")
    obj=(hub/job["dataset_object_path"]).resolve()
    if hub not in obj.parents or not obj.is_file() or card.get("object_path")!=job["dataset_object_path"]:
        raise PrivateHoldoutBenchmarkError("holdout_object_missing_or_unsafe")
    if sha256_file(obj)!=job["dataset_sha256"]:
        raise PrivateHoldoutBenchmarkError("holdout_content_hash_mismatch")
    rows=_rows(obj,int(job["masterbot_id"]))
    canonical="".join(json.dumps(row,sort_keys=True,ensure_ascii=False)+"\n" for row in rows)
    if hashlib.sha256(canonical.encode()).hexdigest()!=job["split_manifest"].get("test_sha256"):
        raise PrivateHoldoutBenchmarkError("holdout_test_split_hash_mismatch")
    candidates=job.get("candidates") or []
    if len(candidates)<2 or sum(1 for c in candidates if c.get("role")=="baseline")!=1:
        raise PrivateHoldoutBenchmarkError("exactly_one_baseline_and_one_candidate_required")
    for c in candidates:
        if (not c.get("model_id") or not re.fullmatch(r"[0-9a-f]{40}",str(c.get("revision","")))
            or c.get("license_status")!="VERIFIED" or not c.get("license")
            or not str(c.get("license_url","")).startswith("https://") or not c.get("license_evidence")):
            raise PrivateHoldoutBenchmarkError("candidate_revision_or_license_evidence_invalid")
    return obj,rows

def execute_private_holdout_benchmark(job_path:str|Path,approval_id:str,output_root:str|Path,
                                      allow_model_download:bool=False,max_new_tokens:int=128)->dict[str,Any]:
    job=json.loads(Path(job_path).read_text(encoding="utf-8"))
    _,rows=validate_private_holdout_job(job,approval_id)
    if allow_model_download and os.environ.get("DREAMCO_ALLOW_MODEL_DOWNLOAD")!="1":
        raise PrivateHoldoutBenchmarkError("set_DREAMCO_ALLOW_MODEL_DOWNLOAD=1_to_authorize_model_download")
    if not 1<=max_new_tokens<=512: raise PrivateHoldoutBenchmarkError("max_new_tokens_out_of_range")
    try:
        import torch
        from transformers import AutoModelForCausalLM,AutoTokenizer
    except ImportError as exc:
        raise PrivateHoldoutBenchmarkError("torch_and_transformers_required_for_execution") from exc
    results=[]
    for candidate in job["candidates"]:
        start=time.perf_counter()
        try:
            tokenizer=AutoTokenizer.from_pretrained(candidate["model_id"],revision=candidate["revision"],local_files_only=not allow_model_download)
            model=AutoModelForCausalLM.from_pretrained(candidate["model_id"],revision=candidate["revision"],local_files_only=not allow_model_download)
            if tokenizer.pad_token is None: tokenizer.pad_token=tokenizer.eos_token
            device="cuda" if torch.cuda.is_available() else "cpu";model.to(device);model.eval()
            if device=="cuda": torch.cuda.reset_peak_memory_stats()
            exact=[];f1=[];durations=[];generated_tokens=0
            for row in rows:
                encoded=tokenizer(row["prompt"],return_tensors="pt",truncation=True,max_length=2048)
                input_ids=encoded["input_ids"].to(device)
                started=time.perf_counter()
                with torch.no_grad():
                    output=model.generate(input_ids,max_new_tokens=max_new_tokens,do_sample=False,
                        pad_token_id=tokenizer.pad_token_id,eos_token_id=tokenizer.eos_token_id)
                durations.append(time.perf_counter()-started)
                new_tokens=output[0][input_ids.shape[1]:]
                prediction=tokenizer.decode(new_tokens,skip_special_tokens=True).strip()
                generated_tokens+=int(new_tokens.numel())
                score=score_prediction(prediction,row["expected"])
                exact.append(score["exact_match"]);f1.append(score["token_f1"])
            elapsed=time.perf_counter()-start
            ordered=sorted(durations)
            p95=ordered[min(len(ordered)-1,math.ceil(len(ordered)*0.95)-1)]*1000
            results.append({"model_id":candidate["model_id"],"revision":candidate["revision"],"role":candidate["role"],
                "status":"SCORED","sample_count":len(rows),"exact_match_accuracy":sum(exact)/len(exact),
                "token_f1":sum(f1)/len(f1),"latency_p95_ms":round(p95,3),
                "generated_tokens":generated_tokens,"tokens_per_second":generated_tokens/max(elapsed,1e-9),
                "peak_cuda_memory_bytes":torch.cuda.max_memory_allocated() if device=="cuda" else None,
                "device":device,"raw_prompts_stored":False,"raw_predictions_stored":False})
        except Exception as exc:
            results.append({"model_id":candidate["model_id"],"revision":candidate["revision"],
                "role":candidate["role"],"status":"FAILED","error_type":type(exc).__name__})
    baseline=next(x for x in results if x["role"]=="baseline")
    trained=[x for x in results if x["role"]=="trained_candidate" and x["status"]=="SCORED"]
    thresholds=job["thresholds"]
    qualified=[x for x in trained if x["exact_match_accuracy"]>=thresholds["min_exact_match"]
        and x["token_f1"]>=thresholds["min_token_f1"] and baseline.get("status")=="SCORED"
        and x["exact_match_accuracy"]>=baseline["exact_match_accuracy"]-thresholds["max_regression"]]
    report={"schema":"dreamco.private_holdout_benchmark_result.v1","job_id":job["job_id"],
        "dataset_id":job["dataset_id"],"dataset_sha256":job["dataset_sha256"],
        "masterbot_id":job["masterbot_id"],"results":results,
        "private_holdout_status":"PASS" if qualified else "FAIL",
        "domain_benchmark_status":"PASS" if qualified else "FAIL",
        "baseline_model":baseline["model_id"],"test_split_used_for_training":False,
        "training_started":False,"safety_status":"NOT_RUN",
        "thresholds":thresholds,"raw_prompts_stored":False,"raw_references_stored":False,
        "production_promotion":False,
        "interpretation":"This report scores deterministic exact-match and token-F1 tasks on an evaluation-only holdout. It does not measure safety, broad general capability, or production readiness."}
    root=Path(output_root);root.mkdir(parents=True,exist_ok=True)
    path=root/f"{job['job_id']}-results.json";path.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    report["result_path"]=str(path);report["result_sha256"]=hashlib.sha256(path.read_bytes()).hexdigest()
    return report
