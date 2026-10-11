#!/usr/bin/env python3
"""Compile source-backed operations; never manufacture missing operation names."""
import argparse
import hashlib
import html
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CAPABILITIES=['division_manifest','bot_registry','capability_router','tool_registry','model_router','research_engine','task_planner','workflow_engine','memory_system','simulation_gateway','testing_framework','benchmark_engine','error_recovery','permission_controller','evidence_ledger','cost_monitor','dashboard_integration','collaboration_bus','learning_feedback_loop','certification_pipeline']

def compile_source(text):
    sha=hashlib.sha256(text.encode()).hexdigest();divisions={};operations={};active=None;mode=None
    for line_no,line in enumerate(text.splitlines(),1):
        m=re.match(r'^\s*Division\s+(\d+)\s*:\s*(.+?)\s*$',line,re.I)
        if m:
            active=int(m[1]);mode=None
            if not 1<=active<=62:active=None;continue
            name=m[2].strip()
            if active not in divisions:divisions[active]={'id':active,'name':name,'source_line':line_no,'source_sha256':sha,'capabilities':CAPABILITIES,'status':'defined','production_ready':False,'frontier':False,'mastery':False,'page':f'division-{active:02}.html'}
            continue
        if active is None:continue
        if line.startswith('Upgrades '):mode='upgrade';continue
        if re.match(r'(?:200 Specialist Operations|Operations [\d,]+)',line):mode='operation';continue
        if re.search(r'Category\s+\d+\s*:',line,re.I):mode='operation' if active>=61 else mode;continue
        if '20 UPGRADES EVERY DIVISION' in line:active=None;continue
        m=re.match(r'^\s*(\d{1,4})\.\s+(.+)',line)
        if not m or mode is None:continue
        number=int(m[1]);name=m[2].strip();limit=range((active-1)*10+1,active*10+1) if active<=60 else range(1,201) if active==61 else range(1401,1601)
        if number not in limit:continue
        key=f'd{active:02}-op-{number:04}'
        title,_,description=name.partition(' — ')
        op={'id':key,'division_id':active,'source_number':number,'name':title.rstrip('.'),'description':description,'source_sha256':sha,'source_line':line_no,'status':'defined','implementation_ref':None,'production_ready':False,'frontier':False,'mastery':False}
        if key in operations and operations[key]['name'].casefold()!=op['name'].casefold():raise ValueError(f'Conflicting operation {key}')
        operations.setdefault(key,op)
        if number == limit.stop - 1: mode=None
    missing=sorted(set(range(1,63))-set(divisions))
    return {'schema':'dreamco.source_division_catalog.v1','source_sha256':sha,'divisions':list(divisions.values()),'operations':list(operations.values()),'missing_divisions':missing,'target_operations':1600,'actual_operations':len(operations),'catalog_complete':not missing and len(operations)>=1600,'production_ready':False}

def render(catalog,output):
    output.mkdir(parents=True,exist_ok=True)
    def page(title,body):return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>'+html.escape(title)+'</title><style>body{font:16px system-ui;max-width:1100px;margin:2rem auto;padding:1rem;background:#101725;color:#eee}a{color:#95d9ff}article{padding:1rem;border:1px solid #597086;margin:1rem 0}nav{display:flex;gap:1rem;flex-wrap:wrap}</style><body><h1>'+html.escape(title)+'</h1>'+body+'<script src="../repository-actions.js" data-repository-actions="true" defer></script></body></html>'
    links=[]
    for d in catalog['divisions']:
        title=d['name'];links.append(f'<article><a href="{d["page"]}">Division {d["id"]}: {html.escape(title)}</a></article>')
        cards=[]
        for op in catalog['operations']:
            if op['division_id']!=d['id']:continue
            cards.append(f'<article id="{op["id"]}"><h2>{html.escape(op["name"])}</h2><p>{html.escape(op["description"])}</p><p>Defined · execution not verified · production blocked</p><nav><a href="../general-intelligence.html">Evidence</a><a href="../benchmarks.html">Benchmarks</a><a href="../actions.html">Tests</a><a href="../resource-connection-center.html">Connect resources</a></nav></article>')
        (output/d['page']).write_text(page(title,'<a href="index.html">All divisions</a><p>Source-backed proposals. No live operation or purchase is implied.</p>'+''.join(cards)))
    (output/'index.html').write_text(page('DreamCo Division Catalog',f'<p>{len(catalog["divisions"])} divisions · {catalog["actual_operations"]} source-backed operations · target 1,600. Unimplemented operations remain defined.</p>'+''.join(links)))

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=ROOT/'docs/imports/dreamco-superbot-source.txt');a=p.parse_args()
    result=compile_source(a.source.read_text());out=ROOT/'config/generated/source-divisions';out.mkdir(parents=True,exist_ok=True)
    (out/'catalog.json').write_text(json.dumps(result,indent=2)+'\n')
    for d in result['divisions']:(out/f'division-{d["id"]:02}.json').write_text(json.dumps({**d,'operations':[x['id'] for x in result['operations'] if x['division_id']==d['id']]},indent=2)+'\n')
    render(result,ROOT/'website/divisions');print(json.dumps({k:result[k] for k in ('actual_operations','missing_divisions','catalog_complete')}))
if __name__=='__main__':main()
