#!/usr/bin/env python3
"""Create public-safe prospectuses for every discovered bot division."""
from __future__ import annotations
import json, re
from pathlib import Path

def slug(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
def files(root): return [p for p in root.rglob('*') if p.is_file() and not any(part in {'.git','node_modules','.venv','dist','build'} for part in p.parts)]
def main():
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--out',default='website/data/bot-division-prospectus.json'); a=ap.parse_args()
    root=Path(a.root); all_files=files(root); divisions={}
    for p in all_files:
        parts=p.relative_to(root).parts
        if len(parts)<2: continue
        top=parts[0]
        if top in {'original-bots','bots','divisions','bot_divisions','src','server','client'} or 'bot' in top.lower():
            divisions.setdefault(top,{'files':0,'paths':[]}); divisions[top]['files']+=1
            if len(divisions[top]['paths'])<25: divisions[top]['paths'].append(str(p))
    # Also infer named bot-like directories anywhere in the repository.
    for p in all_files:
        if p.parent != root and ('bot' in p.parent.name.lower() or 'division' in p.parent.name.lower()):
            key=p.parent.name; divisions.setdefault(key,{'files':0,'paths':[]}); divisions[key]['files']+=1
            if len(divisions[key]['paths'])<25: divisions[key]['paths'].append(str(p))
    records=[]
    for name,info in sorted(divisions.items(),key=lambda x:x[0].lower()):
        records.append({'id':slug(name),'name':name,'file_count':info['files'],'sample_files':info['paths'],'prospectus_url':f'actions.html#division-{slug(name)}','capabilities':['code generation','testing','debugging','benchmarking','documentation','workflow orchestration'],'tooling_plan':['inventory','sandbox','benchmark','quality gate','regression monitor'],'status':'discovered','mastery':False,'evidence_required':True})
    out={'schema_version':'dreamco.bot_division_prospectus.v1','generated_from':'repository filesystem scan','division_count':len(records),'divisions':records}
    d=Path(a.out); d.parent.mkdir(parents=True,exist_ok=True); d.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'division_count':len(records)},indent=2))
if __name__=='__main__': main()
