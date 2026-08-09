#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
POLICY=json.loads((ROOT/'config/repository-system-connection-policy.json').read_text())
OUT=ROOT/'config/generated/repository-system-connections.json'
REPORT=ROOT/'reports/REPOSITORY_SYSTEM_CONNECTIONS.md'
PATH_RE=re.compile(r"(?<![A-Za-z0-9_.-])((?:tools|tests|config|server|shared|client|website|App_bots|docs|\.github)/(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+)")

def scan_file(path:Path,source_class:str,required:bool=True):
    text=path.read_text(encoding='utf-8',errors='replace'); rows=[]
    for ref in sorted(set(PATH_RE.findall(text))):
        # Strip punctuation occasionally captured by prose-like command strings.
        ref=ref.rstrip('.,;:)]}')
        target=ROOT/ref
        generated=ref.startswith('config/generated/') or ref.startswith('website/data/') or ref.startswith('tmp/')
        state='resolved' if target.exists() else ('generated_at_runtime' if generated else 'missing')
        rows.append({'source':str(path.relative_to(ROOT)),'source_class':source_class,'reference':ref,'state':state,'required':required})
    return rows

def main()->int:
    rows=[]
    important=[
      (ROOT/'tools/run_everything_now.py','Run Everything Now steps',True),
      (ROOT/'tools/build_full_system_certification.py','Full System Certification dependencies',True),
      (ROOT/'package.json','package scripts',True),
      (ROOT/'config/run-everything-now.json','Run Everything config',True),
    ]
    for path,source_class,required in important:
        if path.exists(): rows.extend(scan_file(path,source_class,required))
        else: rows.append({'source':str(path.relative_to(ROOT)),'source_class':source_class,'reference':str(path.relative_to(ROOT)),'state':'missing','required':required})
    workflows=ROOT/'.github/workflows'
    if workflows.exists():
        for path in sorted(workflows.glob('*.yml')): rows.extend(scan_file(path,'workflow run commands',False))
    agents=ROOT/'.github/agents'
    if agents.exists():
        for path in sorted(agents.glob('*.agent.md')): rows.extend(scan_file(path,'agent command references',False))
    counts=Counter(r['state'] for r in rows)
    blockers=[r for r in rows if r['required'] and r['state']=='missing']
    payload={'schema':'dreamco.repository_system_connections.v1','reference_count':len(rows),'state_counts':dict(counts),'release_blocker_count':len(blockers),'release_blockers':blockers,'references':rows,'ok':not blockers,'truth_boundary':POLICY['truth_rule']}
    OUT.parent.mkdir(parents=True,exist_ok=True); REPORT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n')
    lines=['# Repository System Connections','',f"- References checked: **{len(rows)}**",f"- Required missing references: **{len(blockers)}**",'']
    for state,count in sorted(counts.items()): lines.append(f'- {state}: {count}')
    if blockers:
        lines += ['','## Required missing references','']
        for row in blockers: lines.append(f"- `{row['source']}` → `{row['reference']}`")
    REPORT.write_text('\n'.join(lines)+'\n')
    print(json.dumps({'ok':not blockers,'references':len(rows),'states':dict(counts),'blockers':len(blockers),'output':str(OUT.relative_to(ROOT))},indent=2)); return 0 if not blockers else 1
if __name__=='__main__': raise SystemExit(main())
