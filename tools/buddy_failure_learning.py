#!/usr/bin/env python3
"""Failure classification, MasterBot routing, and verified lesson candidates for Buddy."""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_MEMORY=ROOT/"artifacts"/"failure-learning-memory.json"
SAFE_CLASSES={"documentation","formatting","generated-index","deterministic-test-fixture"}
GATED_CLASSES={"security","permissions","secrets","production","data-migration","dependency-major","billing"}
ROUTES={
 "security":[24,56],"permissions":[56,24],"secrets":[56,24],
 "dependency-major":[4,41],"generated-index":[41,63],"formatting":[41,63],
 "documentation":[41,48],"deterministic-test-fixture":[63,41],
 "test":[63,41],"data":[7,41],"database":[7,4],
 "deployment":[4,19],"infrastructure":[4,19],"benchmark":[47,63],
 "unknown":[62,41]
}
def _clean(value:Any)->str:return re.sub(r"\s+"," ",str(value or "").strip().lower())
def fingerprint(observation:dict[str,Any])->str:
 parts=[_clean(observation.get(k)) for k in ("repository","workflow","job","failed_step")]
 parts += [_clean(observation.get("failure_class","unknown")),_clean(observation.get("error_signature"))]
 return hashlib.sha256("|".join(parts).encode()).hexdigest()[:24]
def classify(observation:dict[str,Any])->str:
 explicit=_clean(observation.get("failure_class"))
 if explicit:return explicit.replace(" ","-")
 text=" ".join(_clean(observation.get(k)) for k in ("workflow","job","failed_step","error_signature"))
 rules=[
  ("security",("secret","permission","codeql","vulnerability","unauthorized")),
  ("dependency-major",("dependency","lockfile","package version","pip resolver")),
  ("generated-index",("prospectus","generated index","inventory mismatch","stale generated","dataset route","route index","division model fleet","generated artifact")),
  ("documentation",("markdown","link check","documentation")),
  ("deployment",("deploy","pages","release")),
  ("database",("database","migration","sql","postgres","sqlite")),
  ("data",("dataset","data pipeline","etl","schema drift")),
  ("benchmark",("benchmark","eval","score regression")),
  ("formatting",("format","lint","ruff","black","prettier")),
  ("test",("assertion","pytest","unittest","test failed")),
 ]
 for label,needles in rules:
  if any(n in text for n in needles):return label
 return "unknown"
def route_masterbots(kind:str)->list[int]:
 return ROUTES.get(kind,ROUTES["unknown"])
def recommend(observation:dict[str,Any],memory:dict[str,Any])->dict[str,Any]:
 kind=classify(observation);key=fingerprint({**observation,"failure_class":kind})
 prior=next((x for x in memory.get("incidents",[]) if x.get("fingerprint")==key),None)
 verified=prior.get("verified_lesson") if prior else None
 gated=kind in GATED_CLASSES or bool(observation.get("production_impact"))
 auto=kind in SAFE_CLASSES and not gated
 return {"fingerprint":key,"failure_class":kind,"primary_masterbot_id":route_masterbots(kind)[0],
  "collaborating_masterbot_ids":route_masterbots(kind)[1:],
  "recurrence_count":int(prior.get("occurrence_count",0))+1 if prior else 1,
  "prior_verified_lesson":verified,
  "recommended_action":"reapply_verified_lesson_in_isolated_branch" if verified and auto else
   ("run_read_only_diagnostics_and_open_repair_pr" if auto else "escalate_for_human_approval_before_changes"),
  "automatic_code_change_allowed":bool(auto),"requires_human_approval":bool(gated or not auto),
  "must_verify":["original_failure","targeted_regression","dependent_checks"]}
def update_memory(memory:dict[str,Any],observation:dict[str,Any],verification:dict[str,Any])->dict[str,Any]:
 if verification.get("original_failure") is not True or verification.get("regressions") is not True:
  raise ValueError("A lesson can only be stored after original failure and regression checks pass.")
 result=dict(memory);incidents=list(result.get("incidents",[]));kind=classify(observation)
 key=fingerprint({**observation,"failure_class":kind})
 item=next((x for x in incidents if x.get("fingerprint")==key),None)
 if item is None:item={"fingerprint":key,"failure_class":kind,"occurrence_count":0};incidents.append(item)
 item["occurrence_count"]=int(item.get("occurrence_count",0))+1
 item["verified_lesson"]={"root_cause":str(verification.get("root_cause","")),
  "repair":str(verification.get("repair","")),"evidence":list(verification.get("evidence",[])),
  "verified_at":str(verification.get("verified_at",""))}
 result["schema"]="dreamco.buddy_failure_learning_memory.v1";result["incidents"]=incidents
 return result
def build_training_candidate(observation:dict[str,Any],verification:dict[str,Any])->dict[str,Any]:
 required=("root_cause","repair","evidence")
 if verification.get("original_failure") is not True or verification.get("regressions") is not True:
  raise ValueError("Unverified failure repairs cannot become training examples.")
 if verification.get("human_reviewed") is not True or verification.get("training_allowed") is not True:
  raise ValueError("Human review and explicit training permission are required.")
 if verification.get("contains_secrets") is not False or verification.get("contains_personal_data") is not False:
  raise ValueError("Secrets and personal data must be affirmatively excluded.")
 if any(not verification.get(k) for k in required):raise ValueError("Root cause, repair and evidence are required.")
 kind=classify(observation);bots=route_masterbots(kind)
 return {"schema":"dreamco.failure_training_candidate.v1","training_approved":False,
  "primary_masterbot_id":bots[0],"collaborating_masterbot_ids":bots[1:],
  "source_fingerprint":fingerprint({**observation,"failure_class":kind}),
  "instruction":f"Diagnose and repair this {kind} repository failure: {_clean(observation.get('error_signature'))}",
  "verified_lesson":{"root_cause":verification["root_cause"],"repair":verification["repair"],
   "evidence":list(verification["evidence"])},"rights_status":"PENDING_DATASET_CARD_REVIEW",
  "note":"Candidate only. Register in a versioned dataset after provenance, rights, privacy, split and quality review."}
def build_training_event(observation:dict[str,Any],verification:dict[str,Any])->dict[str,Any]:
 """Export a verified repair as a dataset-builder-compatible, review-gated event."""
 if verification.get("original_failure") is not True or verification.get("regressions") is not True:
  raise ValueError("Original failure and regression checks must both be verified.")
 if verification.get("human_reviewed") is not True or verification.get("training_allowed") is not True:
  raise ValueError("Human review and explicit training permission are required.")
 if verification.get("rights_status") != "VERIFIED":
  raise ValueError("Rights must be affirmatively verified before dataset admission.")
 if verification.get("contains_secrets") is not False or verification.get("contains_personal_data") is not False:
  raise ValueError("Secrets and personal data must be affirmatively excluded.")
 if verification.get("third_party_content_included") is not False:
  raise ValueError("Third-party content must be affirmatively excluded.")
 required=("root_cause","repair","source_url","source_commit","run_id")
 if any(not str(verification.get(key) or "").strip() for key in required):
  raise ValueError("Root cause, repair, source URL, immutable commit and run ID are required.")
 commit=str(verification["source_commit"]).strip().lower()
 if not re.fullmatch(r"[0-9a-f]{40}",commit):
  raise ValueError("Source commit must be an immutable 40-character SHA.")
 source_url=str(verification["source_url"]).strip()
 if not source_url.startswith("https://"):
  raise ValueError("Training evidence must use an HTTPS source URL.")
 criteria=[str(x).strip() for x in verification.get("acceptance_criteria",[]) if str(x).strip()]
 evidence=[str(x).strip() for x in verification.get("test_evidence",[]) if str(x).strip()]
 if not criteria or not evidence:
  raise ValueError("At least one acceptance criterion and test evidence reference are required.")
 kind=classify(observation);bots=route_masterbots(kind)
 owner=int(verification.get("primary_masterbot_id",bots[0]))
 collaborators=[int(x) for x in verification.get("collaborating_masterbot_ids",bots[1:]) if int(x)!=owner]
 task=str(verification.get("task") or f"Diagnose and repair this {kind} repository failure: {observation.get('error_signature','')}").strip()
 lesson=" ".join([f"Root cause: {verification['root_cause']}",f"Verified repair: {verification['repair']}","Evidence: "+"; ".join(map(str,verification.get("evidence",[])))])
 if len(task)<12 or len(lesson)<30:
  raise ValueError("Training task and verified lesson must contain substantive detail.")
 event_id="repair-"+hashlib.sha256(f"{fingerprint({**observation,'failure_class':kind})}:{commit}:{verification['run_id']}".encode()).hexdigest()
 return {"schema":"dreamco.verified_repair_training_event.v1","event_id":event_id,
  "evidence_type":"verified_bug_fix","source_url":source_url,"source_commit":commit,"run_id":str(verification["run_id"]),
  "primary_masterbot_id":owner,"collaborating_masterbot_ids":collaborators,"task":task,"verified_lesson":lesson,
  "acceptance_criteria":criteria,"test_evidence":evidence,"verified":True,"human_reviewed":True,
  "training_allowed":True,"rights_status":"VERIFIED","contains_secrets":False,
  "contains_personal_data":False,"third_party_content_included":False,
  "dataset_admission":"CANDIDATE_ONLY_REQUIRES_DATASET_CARD_QUALITY_AND_SPLIT_REVIEW",
  "training_approved":False,"weights_trained":False}
def main()->int:
 parser=argparse.ArgumentParser();parser.add_argument("--observation",required=True)
 parser.add_argument("--memory",default=str(DEFAULT_MEMORY));parser.add_argument("--output",required=True)
 args=parser.parse_args();obs=json.loads(Path(args.observation).read_text())
 path=Path(args.memory);memory=json.loads(path.read_text()) if path.exists() else {"incidents":[]}
 result=recommend(obs,memory);Path(args.output).write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(result,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
