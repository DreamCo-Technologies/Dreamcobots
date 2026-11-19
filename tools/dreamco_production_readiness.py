#!/usr/bin/env python3
"""Generate an evidence-first daily production-readiness master list."""
from __future__ import annotations
import hashlib,json,re,subprocess,os
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"artifacts/dreamco-reconciliation"
POLICY=ROOT/"governance/dreamco-always-on-policy.json"
EVIDENCE=ROOT/"governance/dreamco-requirement-evidence.json"
REGISTRY=ROOT/"config/masterbot-65-registry.json"
def sha(s): return hashlib.sha256(s.encode()).hexdigest()
def tracked():
 try: rows=subprocess.check_output(["git","ls-files","-z"],cwd=ROOT).decode().split("\0")
 except Exception: rows=[p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file()]
 return [ROOT/x for x in rows if x and (x.endswith(".md") or x.endswith(".mdx"))]
def main():
 now=datetime.now(timezone.utc).isoformat()
 policy=json.loads(POLICY.read_text()) if POLICY.exists() else {}
 evidence=json.loads(EVIDENCE.read_text()) if EVIDENCE.exists() else {"requirements":{}}
 mapped=evidence.get("requirements",{})
 reqs=[]; routes=[]; findings=[]
 for p in tracked():
  try: lines=p.read_text(encoding="utf-8",errors="replace").splitlines()
  except OSError: continue
  section=""
  for n,line in enumerate(lines,1):
   s=line.strip()
   if s.startswith("#"): section=re.sub(r"^#+\s*","",s)
   m=re.match(r"^(?:[-*+]\s+(?:\\[[ xX]\\]\s+)?|\\d+[.)]\s+)(.+)$",s)
   if not m or len(m.group(1).strip())<12: continue
   body=m.group(1).strip(); rid="DCO-"+sha(p.relative_to(ROOT).as_posix()+"\0"+re.sub(r"\s+"," ",body))[:14].upper()
   ev=mapped.get(rid,{})
   req={"id":rid,"source":p.relative_to(ROOT).as_posix(),"line":n,"section":section,"text":body,"evidence":ev}
   reqs.append(req)
   missing=[k for k in ("implementation","tests","runtime_routes","benchmark_evidence") if not ev.get(k)]
   if missing: findings.append({"id":"GAP-"+rid,"kind":"requirement_evidence_gap","severity":"high","requirement_id":rid,"source":req["source"],"line":n,"missing":missing,"status":"BLOCKED","next_action":"Map this source requirement to real code, executable tests, a runtime route, and benchmark evidence where applicable."})
 files=[p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file() and not any(x in p.parts for x in (".git","node_modules",".venv","dist","build"))]
 workflows=[x for x in files if x.startswith(".github/workflows/") and x.endswith((".yml",".yaml"))]
 tests=[x for x in files if (x.startswith("tests/") or "/tests/" in x or x.startswith("test_")) and x.endswith((".py",".js",".ts",".tsx"))]
 resource_patterns={"runtime_service":r"(service|server|worker|runtime)","api_route":r"(routes?/|router|endpoint|openapi)","integration":r"(integration|connector|mcp|webhook)","database":r"(schema|migration|database|supabase|postgres)","monitor":r"(monitor|observability|telemetry|alert)","backup":r"(backup|restore)","security_control":r"(security|auth|permission|secret|policy)","benchmark":r"(benchmark|eval|holdout)"}
 for kind,pat in resource_patterns.items():
  matches=[x for x in files if re.search(pat,x,re.I)]
  routes.append({"resource_class":kind,"discovered_paths":matches[:500],"count":len(matches),"verification":"DISCOVERED_NOT_RUNTIME_VERIFIED"})
 for w in workflows:
  if not any(re.search(r"(test|validate|check|gate|health|ci)",w,re.I) for _ in [0]):
   findings.append({"id":"WF-"+sha(w)[:12],"kind":"workflow_test_coverage","severity":"medium","source":w,"status":"UNVERIFIED","next_action":"Add workflow contract tests for triggers, permissions, concurrency, failure handling and artifacts."})
 for resource in ("runtime_service","api_route","integration","database","monitor","backup","security_control","benchmark"):
  if not any(x["resource_class"]==resource and x["count"] for x in routes):
   findings.append({"id":"RES-"+resource.upper(),"kind":"resource_inventory_gap","severity":"high","resource_class":resource,"status":"UNVERIFIED","next_action":"Inventory this resource class and provide owner, route, test, and runtime evidence."})
 try:
  registry=json.loads(REGISTRY.read_text()); bots=registry.get("masterbots") or registry.get("divisions") or []
 except Exception: bots=[]
 pr_inventory=OUT/"pull-request-inventory.json"
 pr_count=0
 if pr_inventory.exists():
  try: pr_count=len(json.loads(pr_inventory.read_text()).get("pull_requests",[]))
  except Exception: pass
 summary={"generated_at":now,"repository":os.getenv("GITHUB_REPOSITORY","DreamCo-Technologies/Dreamcobots"),"requirements_candidate_count":len(reqs),"requirements_with_any_evidence":sum(bool(x.get("evidence")) for x in reqs),"workflow_count":len(workflows),"test_file_count":len(tests),"masterbot_registry_count":len(bots),"pull_request_inventory_count":pr_count,"finding_count":len(findings),"production_readiness":"BLOCKED" if findings else "UNVERIFIED","limitations":["Markdown list extraction is a candidate inventory, not semantic proof of all prose/table requirements.","Path discovery does not verify a live runtime route.","Private ChatGPT conversations require owner-approved exports.","No test, benchmark, deployment, restore or runtime result is invented."]}
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/"production-readiness-master-list.json").write_text(json.dumps({"summary":summary,"requirements":reqs,"findings":findings,"resource_routes":routes},indent=2)+"\\n")
 lines=["# DreamCo Production Readiness Master List","",f"Generated: {now}","",f"**Status: {summary['production_readiness']}**","",f"- Candidate requirements: {len(reqs)}",f"- Evidence-mapped candidates: {summary['requirements_with_any_evidence']}",f"- Workflows: {len(workflows)}",f"- Test files: {len(tests)}",f"- MasterBot registry entries: {len(bots)}",f"- PR inventory entries: {pr_count}",f"- Findings: {len(findings)}",""]
 for f in sorted(findings,key=lambda x:({"critical":0,"high":1,"medium":2,"low":3}.get(x.get("severity"),4),x["id"])):
  lines += [f"## {f['id']} — {f['kind']}",f"- Severity: {f.get('severity','unranked')}",f"- Status: {f.get('status','UNVERIFIED')}",f"- Source: {f.get('source',f.get('requirement_id','repository'))}",f"- Next action: {f['next_action']}",""]
 lines += ["## Limitations",""]+["- "+x for x in summary["limitations"]]
 (OUT/"production-readiness-master-list.md").write_text("\\n".join(lines)+"\\n")
 (OUT/"resource-routing-inventory.json").write_text(json.dumps({"generated_at":now,"routes":routes,"workflow_paths":workflows,"test_paths":tests},indent=2)+"\\n")
 print(json.dumps(summary,indent=2))
 return 0
if __name__=="__main__": raise SystemExit(main())
