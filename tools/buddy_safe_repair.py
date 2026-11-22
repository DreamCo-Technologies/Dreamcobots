#!/usr/bin/env python3
"""Allowlisted, deterministic repository repairs only; never edits source code."""
from __future__ import annotations
import argparse,json,subprocess,sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.buddy_failure_learning import classify,route_masterbots


def repair_plan(observation:dict)->list[list[str]]:
 kind=classify(observation)
 step=str(observation.get("failed_step","")).lower()
 workflow=str(observation.get("workflow","")).lower()
 job=str(observation.get("job","")).lower()
 if kind=="generated-index":
  context=" ".join((workflow,job,step))
  if "division" in workflow or "fleet" in job:
   return [[sys.executable,"tools/build_division_model_fleet.py"]]
  if "dataset" in context or "route" in context:
   return [[sys.executable,"tools/build_buddy_dataset_routes.py"]]
  if "pages" in context and "connection" in context:
   return [[sys.executable,"tools/build_pages_connection_index.py"]]
  if "actions" in context and "prospectus" in context:
   return [[sys.executable,"tools/build_actions_prospectus.py"]]
  if "file" in context and "prospectus" in context:
   return [[sys.executable,"tools/build_file_prospectus.py"]]
 return []

def run_safe_repair(observation:dict,root:Path)->dict:
 commands=repair_plan(observation)
 kind=classify(observation); bots=route_masterbots(kind)
 result={"schema":"dreamco.safe_repair_result.v1","failure_class":kind,
  "primary_masterbot_id":bots[0],"collaborating_masterbot_ids":bots[1:],"commands":commands,"executed":False,"success":False,"changed_files":[],"requires_human_review":True}
 if not commands:
  result["status"]="NO_ALLOWLISTED_AUTOMATIC_REPAIR";return result
 for command in commands:
  proc=subprocess.run(command,cwd=root,text=True,capture_output=True,timeout=300,check=False)
  result["executed"]=True
  result.setdefault("command_results",[]).append({"argv":command,"returncode":proc.returncode,
   "stdout_tail":proc.stdout[-4000:],"stderr_tail":proc.stderr[-4000:]})
  if proc.returncode:
   result["status"]="REPAIR_COMMAND_FAILED";return result
 status=subprocess.run(["git","status","--porcelain","--untracked-files=all"],cwd=root,text=True,capture_output=True,check=True).stdout
 result["changed_files"]=[line[3:] for line in status.splitlines() if len(line)>3 and not line[3:].startswith("artifacts/buddy-safe-repair/")]
 result["success"]=True
 result["status"]="REPAIR_CANDIDATE_READY_FOR_PR" if result["changed_files"] else "REPAIR_RAN_NO_CHANGES"
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument("--observation",required=True);p.add_argument("--out",default="artifacts/buddy-safe-repair/result.json")
 a=p.parse_args();root=ROOT
 obs=json.loads(Path(a.observation).read_text(encoding="utf-8"))
 result=run_safe_repair(obs,root)
 out=root/a.out;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 output=Path(__import__("os").environ.get("GITHUB_OUTPUT","/dev/null"))
 with output.open("a",encoding="utf-8") as f:
  f.write(f"changed={'true' if result['success'] and result['changed_files'] else 'false'}\n")
  f.write(f"status={result['status']}\n")
 print(json.dumps(result,sort_keys=True))
 return 0 if result["success"] or result["status"]=="NO_ALLOWLISTED_AUTOMATIC_REPAIR" else 1
if __name__=="__main__":raise SystemExit(main())
