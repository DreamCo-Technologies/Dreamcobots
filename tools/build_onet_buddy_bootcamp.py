#!/usr/bin/env python3
"""Build a repository-aware O*NET sandbox curriculum.

The builder accepts an O*NET tabular database directory. It discovers
occupations, tasks, work activities and skills when those files are present,
then creates deterministic benchmark contracts for Buddy/coding bots.
It never marks a capability mastered merely because a test was generated.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, re
from pathlib import Path

FILES = {
    "occupations": ["Occupation Data.txt", "occupation_data.csv", "occupation_data.json"],
    "tasks": ["Task Statements.txt", "task_statements.csv", "task_statements.json"],
    "activities": ["Work Activities.txt", "work_activities.csv", "work_activities.json"],
    "skills": ["Skills.txt", "skills.csv", "skills.json"],
    "knowledge": ["Knowledge.txt", "knowledge.csv", "knowledge.json"],
    "abilities": ["Abilities.txt", "abilities.csv", "abilities.json"],
    "work_styles": ["Work Styles.txt", "work_styles.csv", "work_styles.json"],
    "technology": ["Technology Skills.txt", "technology_skills.csv", "technology_skills.json"],
}

def locate(root: Path, names: list[str]) -> Path | None:
    by_lower = {p.name.lower(): p for p in root.rglob("*") if p.is_file()}
    for name in names:
        if name.lower() in by_lower:
            return by_lower[name.lower()]
    return None

def rows(path: Path, limit: int = 200_000) -> list[dict]:
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
        if isinstance(data, dict):
            for key in ("rows", "data", "items", "results"):
                if isinstance(data.get(key), list): return data[key][:limit]
            return [data]
        return data[:limit]
    text = path.read_text(encoding="utf-8-sig", errors="ignore")
    sample = text[:4096]
    dialect = csv.Sniffer().sniff(sample, delimiters="\t,|") if sample.strip() else csv.excel_tab
    return list(csv.DictReader(text.splitlines(), dialect=dialect))[:limit]

def value(row: dict, *keys: str) -> str:
    normalized = {re.sub(r"[^a-z0-9]", "", str(k).lower()): str(v or "") for k,v in row.items()}
    for key in keys:
        v = normalized.get(re.sub(r"[^a-z0-9]", "", key.lower()))
        if v: return v
    return ""

def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:100]

def make_case(kind: str, code: str, title: str, prompt: str, source: str) -> dict:
    bid = hashlib.sha256(f"onet|{kind}|{code}|{prompt}".encode()).hexdigest()[:16]
    return {"benchmark_id": f"onet-{kind}-{bid}", "onet_kind": kind, "onet_code": code, "title": title, "prompt": prompt, "source": source, "status": "generated", "mastery": False, "evidence_required": True, "metrics": ["quality", "speed", "efficiency", "reliability", "safety"]}

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--root", required=True); ap.add_argument("--out", default="config/generated/onet-buddy-bootcamp.json"); ap.add_argument("--max-cases-per-category", type=int, default=5000); args=ap.parse_args()
    root=Path(args.root); found={k:locate(root,names) for k,names in FILES.items()}
    datasets={k: rows(p) if p else [] for k,p in found.items()}
    cases=[]
    for r in datasets["occupations"]:
        code=value(r,"O*NET-SOC Code","onetsoc_code","code"); title=value(r,"Title","title"); desc=value(r,"Description","description")
        if code and title: cases.append(make_case("occupation",code,title,f"Act as a capable professional for the occupation '{title}'. Demonstrate the relevant knowledge, reasoning, communication, planning and execution skills for this occupation. Context: {desc}",str(found["occupations"])))
    mappings=[("tasks","Task Statements","task"),("activities","Element Name","activity"),("skills","Element Name","skill"),("knowledge","Element Name","knowledge"),("abilities","Element Name","ability"),("work_styles","Element Name","work-style"),("technology","Technology","technology")]
    for dataset,key,kind in mappings:
        for r in datasets[dataset]:
            code=value(r,"O*NET-SOC Code","onetsoc_code","code"); title=value(r,key,"Title","title","Name","name"); statement=value(r,"Task","Task Statement","Description","description","Element Name","element_name")
            if title or statement:
                label=title or statement[:160]; prompt=f"Complete and explain a high-quality solution for this O*NET {kind}: {label}. Preserve constraints, verify the result, and report uncertainty." 
                cases.append(make_case(kind,code,label,prompt,str(found[dataset])))
    # deterministic cap per kind
    grouped={}
    for case in cases: grouped.setdefault(case["onet_kind"],[]).append(case)
    selected=[]
    for kind in sorted(grouped): selected.extend(grouped[kind][:args.max_cases_per_category])
    out={"schema_version":"dreamco.onet_buddy_bootcamp.v1","source_policy":"O*NET source data must be supplied to the workflow; generated tests are not mastery evidence.","datasets":{k:(str(v) if v else None) for k,v in found.items()},"counts":{"raw":len(cases),"generated":len(selected),"by_kind":{k:min(len(v),args.max_cases_per_category) for k,v in grouped.items()}},"mastery_rule":{"requires_real_execution":True,"metrics":["quality","speed","efficiency","reliability","safety"],"requires_evidence":True},"cases":selected}
    dest=Path(args.out); dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out["counts"],indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
