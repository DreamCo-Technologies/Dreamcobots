#!/usr/bin/env python3
"""Build occupation/task learning paths from an official O*NET Task Statements export.

Input is the official O*NET database Task Statements file (tab-delimited).
The tool preserves source IDs and does not invent credentials, job readiness,
or authority to perform regulated work.
"""
from __future__ import annotations
import argparse, csv, json
from collections import defaultdict
from pathlib import Path
from typing import Any

def read_rows(path:Path)->list[dict[str,str]]:
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        sample=f.read(4096); f.seek(0)
        try: dialect=csv.Sniffer().sniff(sample,delimiters="\t,;")
        except csv.Error: dialect=csv.excel_tab
        return list(csv.DictReader(f,dialect=dialect))

def pick(row:dict[str,str],*names:str)->str:
    normalized={str(k).strip().lower().replace("_"," ").replace("-"," "):str(v or "").strip() for k,v in row.items()}
    for name in names:
        value=normalized.get(name.lower().replace("_"," ").replace("-"," "))
        if value: return value
    return ""

def build(rows:list[dict[str,str]],version:str)->dict[str,Any]:
    occupations:dict[str,dict[str,Any]]=defaultdict(lambda:{"occupation_code":"","tasks":[]})
    for row in rows:
        code=pick(row,"O*NET-SOC Code","O*NET SOC Code","occupation code")
        task_id=pick(row,"Task ID","task id")
        title=pick(row,"Task","Task Statement","task statement")
        if not code or not task_id or not title: continue
        item=occupations[code]
        item["occupation_code"]=code
        item["tasks"].append({"task_id":task_id,"task":title,
          "task_type":pick(row,"Task Type","task type") or "unspecified",
          "date":pick(row,"Date","date"),"domain_source":pick(row,"Domain Source","domain source")})
    output=[]
    for code,item in sorted(occupations.items()):
        tasks=sorted(item["tasks"],key=lambda x:(x["task_type"]!="Core",x["task_id"]))
        item["task_count"]=len(tasks)
        item["learning_path"]={
          "phase_1":"Understand occupation purpose, work context, knowledge, skills and tools using the official occupation profile.",
          "phase_2":"Study every listed core and supplemental task; identify prerequisites, safety requirements and quality standards.",
          "phase_3":"Practice with simulations and supervised projects; do not claim occupational competence from reading.",
          "phase_4":"Create an ethical service/business-development playbook only where a legitimate buyer and permitted scope exist.",
          "phase_5":"Complete independent assessment, portfolio evidence, references and any required credential or license checks."
        }
        item["task_playbooks"]=[{
          "task_id":t["task_id"],"task":t["task"],
          "learning_summary_required":True,
          "practice_required":True,
          "commercial_pathway":{"status":"research_required","possible_buyer_types":[],"offer":"Define only after buyer research and credential/scope review.",
            "sales_sequence":["identify legitimate buyer","confirm problem and authority","qualify need and budget","define scope and exclusions","estimate labor/material/overhead/insurance","prepare truthful proposal","obtain human approval","deliver and document quality"],
            "not_a_claim_of_qualification":True},
          "community_pathway":{"status":"partner_review_required","possible_beneficiaries":["job seekers","veterans","people experiencing homelessness","people receiving public benefits"],"safeguards":["consent","privacy","no benefits eligibility promises","licensed provider referral when required"]}
        } for t in tasks]
        output.append(item)
    return {"schema":"dreamco.onet_task_curricula.v1","source":{"name":"O*NET Database Task Statements","version":version,"official_url":"https://www.onetcenter.org/database.html","attribution_required":True},
      "inventory":{"input_rows":len(rows),"occupations":len(output),"task_statements":sum(x["task_count"] for x in output),"status":"built_from_supplied_official_export","coverage_warning":"Completeness depends on the version and integrity of the supplied official O*NET export."},
      "occupations":output,
      "truth_boundary":"These curricula are study and practice plans, not occupational certification, licenses, job placement, or proof that Buddy can perform the work safely."}

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True,help="Official O*NET Task Statements export")
    p.add_argument("--version",required=True,help="O*NET database version, e.g. 31.0")
    p.add_argument("--out-dir",required=True)
    a=p.parse_args()
    rows=read_rows(Path(a.input))
    result=build(rows,a.version)
    out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
    (out/"onet-task-curricula.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    summary=["# O*NET occupation and task learning paths","",
      f"- Database version: {a.version}",f"- Occupations: {result['inventory']['occupations']}",
      f"- Task statements: {result['inventory']['task_statements']}","",
      "Each occupation receives a study path and every task receives a practice and supervised commercial/community pathway template.",
      "Reading or summarizing a task does not certify Buddy or a user to perform it."]
    (out/"onet-task-curricula.md").write_text("\n".join(summary)+"\n",encoding="utf-8")
    print(json.dumps(result["inventory"],indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
