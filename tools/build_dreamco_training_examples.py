"""Create original DreamCo training candidates from verified work evidence only."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"config/masterbot-65-registry.json"
ALLOWED_TYPES={"verified_commit","verified_test","approved_pr","approved_workflow","verified_bug_fix","original_lesson","approved_synthetic"}
PII={
 "email":re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",re.I),
 "phone":re.compile(r"(?<!\d)(?:\+1[ .-]?)?(?:\(?\d{3}\)?[ .-]?)\d{3}[ .-]?\d{4}(?!\d)"),
 "ssn":re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")
}
def _sha(value:str)->str:
 return hashlib.sha256(value.encode("utf-8")).hexdigest()
def _text(value:Any)->str:
 return " ".join(str(value or "").split())
def _valid_source_url(value:str)->bool:
 try:
  parsed=urlsplit(value)
  port=parsed.port
 except ValueError:
  return False
 if parsed.scheme!="https" or parsed.hostname!="github.com" or port not in (None,443):
  return False
 if parsed.username or parsed.password or parsed.query or parsed.fragment:
  return False
 parts=[part for part in parsed.path.split("/") if part]
 if len(parts)<3 or parts[:2]!=["DreamCo-Technologies","Dreamcobots"] or any(part in {".",".."} for part in parts):
  return False
 kind=parts[2]
 if kind=="commit":
  return len(parts)==4 and re.fullmatch(r"[0-9a-f]{40}",parts[3],re.I) is not None
 if kind in {"pull","issues"}:
  return len(parts)==4 and parts[3].isdigit()
 if kind=="actions":
  return len(parts)==5 and parts[3]=="runs" and parts[4].isdigit()
 if kind in {"blob","tree"}:
  return len(parts)>=5 and parts[3] not in {"", ".", ".."}
 return False
def _valid_source_metadata(event:dict,source_url:str)->bool:
 if not _valid_source_url(source_url):
  return False
 commit=_text(event.get("source_commit")).lower()
 if commit and not re.fullmatch(r"[0-9a-f]{40}",commit):
  return False
 parts=[part for part in urlsplit(source_url).path.split("/") if part]
 if parts[2]=="commit" and commit and parts[3].lower()!=commit:
  return False
 fingerprint=_text(event.get("source_fingerprint")).lower()
 if fingerprint and not re.fullmatch(r"[0-9a-f]{24,64}",fingerprint):
  return False
 run_id=_text(event.get("run_id"))
 if run_id and not re.fullmatch(r"\d{1,20}",run_id):
  return False
 return True
def _redact_run_reference(value:str)->str:
 return re.sub(r"(?i)\b(?:github\s+actions\s+)?(?:workflow\s+)?run\s*[:#]?\s*\d{8,}\b","[workflow-run-reference]",value)
def _split_rows(rows:list[dict])->dict[str,str]:
 result={}
 for split in ("train","validation","test"):
  body="".join(json.dumps(row,sort_keys=True,ensure_ascii=False)+"\n" for row in rows if row["split"]==split)
  result[f"{split}_sha256"]=_sha(body)
 return result
def build(events:list[dict],masterbot_registry:Path=REGISTRY)->dict:
 registry=json.loads(masterbot_registry.read_text(encoding="utf-8"))
 valid={int(x["id"]):x["name"] for x in registry.get("divisions",[])}
 accepted=[]; rejected=[]
 for event in events:
  eid=_text(event.get("event_id")); source=_text(event.get("source_url"))
  kind=_text(event.get("evidence_type"))
  task=_text(event.get("task")); lesson=_text(event.get("verified_lesson"))
  owner=event.get("primary_masterbot_id")
  if not eid or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}",eid) or not _valid_source_metadata(event,source) or kind not in ALLOWED_TYPES:
   rejected.append({"event_id":eid,"reason":"missing/invalid ID, non-canonical evidence source, invalid provenance metadata, or unapproved evidence type"}); continue
  if event.get("verified") is not True or event.get("human_reviewed") is not True or event.get("training_allowed") is not True or event.get("rights_status")!="VERIFIED":
   rejected.append({"event_id":eid,"reason":"verification, human review, explicit training permission, or rights verification missing"}); continue
  if event.get("contains_secrets") is not False or event.get("contains_personal_data") is not False or event.get("third_party_content_included") is not False:
   rejected.append({"event_id":eid,"reason":"secrets, personal data, or unlicensed third-party content is not allowed in generated examples"}); continue
  if not isinstance(owner,int) or owner not in valid or len(task)<12 or len(lesson)<30:
   rejected.append({"event_id":eid,"reason":"invalid MasterBot owner or insufficient original task/lesson"}); continue
  criteria=[_text(x) for x in event.get("acceptance_criteria",[]) if _text(x)]
  evidence=[_text(x) for x in event.get("test_evidence",[]) if _text(x)]
  if not criteria or not evidence:
   rejected.append({"event_id":eid,"reason":"acceptance criteria and verified test evidence are required"}); continue
  # Provenance hashes, canonical repository URLs, and numeric run IDs are
  # structured metadata. Validate them above; scan only human-authored text.
  source_text="\n".join(_redact_run_reference(value) for value in [task,lesson,*criteria,*evidence])
  if any(pattern.search(source_text) for pattern in PII.values()):
   rejected.append({"event_id":eid,"reason":"basic PII pattern detected in training text"}); continue
  accepted.append({"event_id":eid,"source_url":source,"source_commit":_text(event.get("source_commit")),
   "source_fingerprint":_text(event.get("source_fingerprint")),"run_id":_text(event.get("run_id")),
   "evidence_type":kind,"masterbot_id":owner,"masterbot":valid[owner],
   "task":task,"lesson":lesson,"criteria":criteria,"test_evidence":evidence})
 if len(accepted)<3:
  raise ValueError(f"At least three independently verified, rights-cleared work records are required; found {len(accepted)}")
 owners={item["masterbot_id"] for item in accepted}
 if len(owners)!=1:
  raise ValueError("Build one dataset per MasterBot lane; mixed-division datasets are rejected")
 accepted.sort(key=lambda x:_sha(x["event_id"]))
 rows=[]
 for index,event in enumerate(accepted):
  split="test" if index==len(accepted)-1 else "validation" if index==len(accepted)-2 else "train"
  instruction=f"How should {event['masterbot']} handle this verified task: {event['task']}?"
  output=" ".join([
   _redact_run_reference(event["lesson"]),
   "Acceptance criteria: "+"; ".join(_redact_run_reference(x) for x in event["criteria"])+".",
   "Verified evidence: "+"; ".join(_redact_run_reference(x) for x in event["test_evidence"])+"."
  ])
  rows.append({"text":"### Instruction:\n"+instruction+"\n### Response:\n"+output,
   "split":split,"masterbot_id":event["masterbot_id"],"source_event_id":event["event_id"],
   "source_url":event["source_url"],"source_commit":event["source_commit"],
   "source_fingerprint":event["source_fingerprint"],"run_id":event["run_id"],
   "evidence_type":event["evidence_type"],
   "derivation":"original_synthesis_from_verified_DreamCo_work"})
 return {"schema":"dreamco.original_training_candidate.v1","generated_by":"DreamCo verified-work example builder",
  "accepted_source_events":len(accepted),"rejected_source_events":rejected,"rows":rows,
  "split_manifest":_split_rows(rows),"primary_masterbot_ids":sorted({x["masterbot_id"] for x in rows}),
  "training_approved":False,"rights_status":"PENDING_FINAL_DATASET_CARD_REVIEW",
  "source_files_copied":False,"third_party_text_copied":False,"weights_trained":False,
  "notice":"Candidate examples are original syntheses, not automatically training-approved. A human must review the card, source permissions, split quality and ownership before registration or training."}
def main()->int:
 parser=argparse.ArgumentParser()
 parser.add_argument("--events",required=True)
 parser.add_argument("--out",required=True)
 parser.add_argument("--card-out",required=True)
 parser.add_argument("--name",default="DreamCo Verified Engineering Lessons")
 parser.add_argument("--license-url",required=True)
 parser.add_argument("--masterbot-id",required=True,type=int)
 args=parser.parse_args()
 events=[json.loads(line) for line in Path(args.events).read_text(encoding="utf-8").splitlines() if line.strip()]
 events=[event for event in events if event.get("primary_masterbot_id")==args.masterbot_id]
 result=build(events)
 out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text("".join(json.dumps(row,ensure_ascii=False)+"\n" for row in result["rows"]),encoding="utf-8")
 card={"schema":"dreamco.dataset_card_candidate.v1","name":args.name,"owner":"DreamCo Technologies",
  "license":"DreamCo internal authored synthesis - pending human review","license_url":args.license_url,
  "source_url":"https://github.com/DreamCo-Technologies/Dreamcobots",
  "data_plane":"dreamco_owned_training","rights_status":"PENDING_HUMAN_REVIEW","training_approved":False,
  "primary_masterbot_id":args.masterbot_id,
  "collaborating_masterbot_ids":[],
  "split_manifest":result["split_manifest"],"source_event_count":result["accepted_source_events"],
  "candidate_data_path":str(out),"review_required":True}
 Path(args.card_out).write_text(json.dumps(card,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"accepted_events":result["accepted_source_events"],"rejected_events":len(result["rejected_source_events"]),"examples":len(result["rows"]),"training_approved":False,"weights_trained":False}))
 return 0
if __name__=="__main__": raise SystemExit(main())
