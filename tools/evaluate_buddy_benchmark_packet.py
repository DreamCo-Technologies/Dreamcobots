"""Score submitted Buddy benchmark evidence packets without executing untrusted tasks."""
from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"config/buddy-core-capability-benchmark-definitions.json"
REQUIRED_EVIDENCE=("run_id","evaluated_at_utc","result_sha256","source_commit","evaluator_version","reviewer_id")
def load_definitions(path:Path=REGISTRY)->dict[str,Any]:
 data=json.loads(path.read_text(encoding="utf-8"))
 if data.get("schema")!="dreamco.core_capability_benchmark_definitions.v1": raise ValueError("unsupported benchmark definitions schema")
 return data
def evaluate_packet(packet:dict[str,Any],definitions:dict[str,Any])->dict[str,Any]:
 if packet.get("schema")!="dreamco.buddy_benchmark_evidence_packet.v1": raise ValueError("unsupported benchmark evidence packet schema")
 rows={row["benchmark_id"]:row for row in definitions.get("benchmarks",[])}
 benchmark_id=packet.get("benchmark_id")
 if benchmark_id not in rows: raise ValueError(f"unknown benchmark_id: {benchmark_id}")
 definition=rows[benchmark_id]; rubric=definition.get("rubric",[])
 expected={item["dimension"] for item in rubric}; scores=packet.get("scores")
 if not isinstance(scores,dict) or set(scores)!=expected: raise ValueError("scores must contain exactly the rubric dimensions")
 for dimension,value in scores.items():
  if not isinstance(value,int) or isinstance(value,bool) or not 0<=value<=4: raise ValueError(f"{dimension}: score must be an integer from 0 to 4")
 gates=packet.get("critical_gates"); required_gates=definition.get("critical_gates",[])
 if not isinstance(gates,dict) or set(gates)!=set(required_gates): raise ValueError("critical_gates must contain exactly the defined gate names")
 if any(value is not True and value is not False for value in gates.values()): raise ValueError("critical gate values must be booleans")
 evidence=packet.get("evidence")
 if not isinstance(evidence,dict): raise ValueError("evidence must be an object")
 missing=[field for field in REQUIRED_EVIDENCE if not isinstance(evidence.get(field),str) or not evidence[field].strip()]
 if missing: raise ValueError("missing evidence fields: "+", ".join(missing))
 digest=evidence["result_sha256"]
 if len(digest)!=64 or any(ch not in "0123456789abcdef" for ch in digest): raise ValueError("result_sha256 must be a lowercase SHA-256 digest")
 try: datetime.fromisoformat(evidence["evaluated_at_utc"].replace("Z","+00:00"))
 except ValueError as exc: raise ValueError("evaluated_at_utc must be ISO-8601") from exc
 hashes=(packet.get("training_fixture_sha256"),packet.get("holdout_fixture_sha256"))
 if not all(isinstance(x,str) and len(x)==64 and all(c in "0123456789abcdef" for c in x) for x in hashes): raise ValueError("training and holdout fixture hashes must be lowercase SHA-256 digests")
 if hashes[0]==hashes[1]: raise ValueError("holdout fixture must be distinct from training fixture")
 score=round(sum(scores[item["dimension"]]*item["weight"] for item in rubric)/4,2)
 failed=sorted(name for name,passed in gates.items() if not passed)
 candidate=score>=definition["pass_threshold"] and not failed
 packet_hash=hashlib.sha256(json.dumps(packet,sort_keys=True,separators=(",",":")).encode()).hexdigest()
 return {"schema":"dreamco.buddy_benchmark_evaluation_result.v1","benchmark_id":benchmark_id,"capability_id":definition["capability_id"],"model_id":packet.get("model_id"),"model_version":packet.get("model_version"),"weighted_score":score,"pass_threshold":definition["pass_threshold"],"candidate_pass":candidate,"failed_critical_gates":failed,"score_dimensions":scores,"holdout_fixture_distinct":True,"evidence_packet_sha256":packet_hash,"independent_verification":"pending","benchmark_execution_verified":False,"mastery_claimed":False,"truth_boundary":"This is a deterministic score calculation over a submitted packet. It does not execute or independently verify the run, validate the fixture contents, or establish mastery."}
def main()->int:
 parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("--input",required=True,type=Path); parser.add_argument("--output",type=Path); args=parser.parse_args()
 packet=json.loads(args.input.read_text(encoding="utf-8")); result=evaluate_packet(packet,load_definitions()); rendered=json.dumps(result,indent=2)+"\n"
 if args.output: args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(rendered,encoding="utf-8")
 print(rendered,end=""); return 0
if __name__=="__main__": raise SystemExit(main())
