#!/usr/bin/env python3
"""Allowlisted, deterministic repository repairs only; never edits source code."""
from __future__ import annotations
import argparse,json,subprocess,sys
from pathlib import Path,PurePosixPath
from tools.buddy_failure_learning import classify,route_masterbots

REPAIR_ALLOWED_PREFIXES = (
 "artifacts/buddy-dataset-hub/", "artifacts/division-model-fleet/",
 "command-center/data/", "config/bots/", "config/buddy/", "config/generated/",
 "reports/", "website/data/",
)
REPAIR_ALLOWED_FILES = {
 "config/master_bot_registry.json",
 "config/freecodecamp-complete-learning-path.json",
 "config/buddy-continuous-study-policy.json",
}
OUTPUT_PREFIX = "artifacts/buddy-safe-repair/"
REPAIR_ALLOWED_COMMANDS = {
 "tools/build_buddy_dataset_routes.py",
 "tools/build_division_model_fleet.py",
 "tools/build_pages_connection_index.py",
 "tools/generate_bot_manifests.py",
 "tools/refresh_repository_evidence.py",
 "tools/generate_command_center_data.py",
 "tools/build_actions_prospectus.py",
 "tools/build_file_prospectus.py",
}


def repair_path_allowed(path:str)->bool:
 p=PurePosixPath(path)
 if (not p.parts or p.is_absolute() or "\\" in path
     or any(x in {"", ".", ".."} for x in p.parts)
     or p.name.lower() in {".env", ".env.local", ".env.production", "credentials.json", "secrets.json"}
     or p.suffix.lower() in {".pem", ".key", ".p12", ".pfx"}):
  return False
 return path in REPAIR_ALLOWED_FILES or any(p.as_posix().startswith(prefix) for prefix in REPAIR_ALLOWED_PREFIXES)


def safe_observation_path(root:Path,value:str)->Path:
 p=PurePosixPath(value)
 if (not p.parts or p.is_absolute() or "\\" in value or ".." in p.parts
     or not p.as_posix().startswith(OUTPUT_PREFIX)):
  raise ValueError("Observation must remain under artifacts/buddy-safe-repair/.")
 out=(root/Path(*p.parts)).resolve()
 try: relative=out.relative_to(root.resolve()).as_posix()
 except ValueError: raise ValueError("Observation resolves outside the repository.")
 if not relative.startswith(OUTPUT_PREFIX):
  raise ValueError("Observation resolves outside artifacts/buddy-safe-repair/.")
 return out


def safe_output_path(root:Path,value:str)->Path:
 p=PurePosixPath(value)
 if (not p.parts or p.is_absolute() or "\\" in value or ".." in p.parts
     or p.name.lower() in {".env", ".env.local", "credentials.json", "secrets.json"}
     or p.suffix.lower() in {".pem", ".key", ".p12", ".pfx"}
     or not p.as_posix().startswith(OUTPUT_PREFIX)):
  raise ValueError("Repair output must remain under artifacts/buddy-safe-repair/ and cannot be a credential file.")
 out=(root/Path(*p.parts)).resolve()
 try: relative=out.relative_to(root.resolve()).as_posix()
 except ValueError: raise ValueError("Repair output resolves outside the repository.")
 if not relative.startswith(OUTPUT_PREFIX) or not repair_path_allowed(relative):
  raise ValueError("Repair output resolves outside the safe generated-artifact path allowlist.")
 return out


def repair_plan(observation:dict)->list[list[str]]:
 kind=classify(observation)
 step=str(observation.get("failed_step","")).lower()
 workflow=str(observation.get("workflow","")).lower()
 job=str(observation.get("job","")).lower()
 if workflow=="buddy ci safe generated-artifact repair" and ("verify repaired indexes" in step or "detect allowlisted generated changes" in step):
  return [[sys.executable,"tools/build_buddy_dataset_routes.py"],[sys.executable,"tools/build_division_model_fleet.py"],[sys.executable,"tools/build_pages_connection_index.py"],[sys.executable,"tools/generate_bot_manifests.py"],[sys.executable,"tools/refresh_repository_evidence.py"],[sys.executable,"tools/generate_command_center_data.py"]]
 if kind=="generated-index":
  context=" ".join((workflow,job,step))
  if "buddy ci safe generated-artifact repair" in workflow:
   return [[sys.executable,"tools/build_buddy_dataset_routes.py"],[sys.executable,"tools/build_division_model_fleet.py"],[sys.executable,"tools/build_pages_connection_index.py"],[sys.executable,"tools/generate_bot_manifests.py"],[sys.executable,"tools/refresh_repository_evidence.py"],[sys.executable,"tools/generate_command_center_data.py"]]
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
  if len(command)!=2 or command[0]!=sys.executable or command[1] not in REPAIR_ALLOWED_COMMANDS:
   result["status"]="BLOCKED_UNSAFE_COMMAND";return result
  proc=subprocess.run([sys.executable,command[1]],cwd=root,text=True,capture_output=True,timeout=300,check=False)
  result["executed"]=True
  result.setdefault("command_results",[]).append({"argv":command,"returncode":proc.returncode})
  if proc.returncode:
   result["status"]="REPAIR_COMMAND_FAILED";return result
 status=subprocess.run(["git","status","--porcelain","--untracked-files=all"],cwd=root,text=True,capture_output=True,check=True).stdout
 entries=[line for line in status.splitlines() if len(line)>3 and not line[3:].startswith("artifacts/buddy-safe-repair/")]
 blocked=[]
 for line in entries:
  path=line[3:]
  if line[:2].strip() not in {"M","A","??"} or not repair_path_allowed(path):
   blocked.append(path)
 if blocked:
  result["status"]="BLOCKED_UNEXPECTED_PATH";result["success"]=False
  result["blocked_paths"]=sorted(set(blocked));return result
 result["changed_files"]=sorted({line[3:] for line in entries})
 result["success"]=True
 result["status"]="REPAIR_CANDIDATE_READY_FOR_PR" if result["changed_files"] else "REPAIR_RAN_NO_CHANGES"
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument("--observation",required=True);p.add_argument("--out",default="artifacts/buddy-safe-repair/result.json")
 a=p.parse_args();root=Path(__file__).resolve().parents[1]
 try:
  observation_path=safe_observation_path(root,a.observation)
  if observation_path.stat().st_size>5*1024*1024: raise ValueError("Observation exceeds the 5 MiB safety limit.")
  obs=json.loads(observation_path.read_text(encoding="utf-8"))
  if not isinstance(obs,dict): raise ValueError("Observation must be a JSON object.")
 except (OSError,ValueError,json.JSONDecodeError) as exc:
  p.error(str(exc))
 result=run_safe_repair(obs,root)
 out=safe_output_path(root,a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 output=Path(__import__("os").environ.get("GITHUB_OUTPUT","/dev/null"))
 with output.open("a",encoding="utf-8") as f:
  f.write(f"changed={'true' if result['success'] and result['changed_files'] else 'false'}\n")
  f.write(f"status={result['status']}\n")
 print(json.dumps(result,sort_keys=True))
 return 0 if result["success"] or result["status"]=="NO_ALLOWLISTED_AUTOMATIC_REPAIR" else 1
if __name__=="__main__":raise SystemExit(main())
