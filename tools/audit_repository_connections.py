#!/usr/bin/env python3
from __future__ import annotations

import json, re
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
POLICY=json.loads((ROOT/'config/repository-system-connection-policy.json').read_text())
OUT=ROOT/'config/generated/repository-system-connections.json'
MAP=ROOT/'config/generated/repo-wide-connection-map.json'
BACKLOG=ROOT/'config/generated/repo-connection-builder-backlog.json'
REPORT=ROOT/'reports/REPOSITORY_SYSTEM_CONNECTIONS.md'
PATH_RE=re.compile(r"(?<![A-Za-z0-9_.-])((?:tools|tests|config|server|shared|client|website|App_bots|docs|\.github)/(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+)")
API_RE=re.compile(r"\{\s*name:\s*['\"]([^'\"]+)['\"]\s*,\s*category:\s*['\"]([^'\"]+)['\"]")

def text(p): return p.read_text(encoding='utf-8',errors='replace') if p.exists() else ''
def doc(p,default):
    try: return json.loads(p.read_text()) if p.exists() else default
    except Exception: return default

def scan_refs(path,klass,required):
    rows=[]
    for ref in sorted(set(PATH_RE.findall(text(path)))):
        ref=ref.rstrip('.,;:)]}'); target=ROOT/ref
        generated=ref.startswith(('config/generated/','website/data/','tmp/'))
        state='resolved' if target.exists() else ('generated_at_runtime' if generated else 'missing')
        rows.append({'source':str(path.relative_to(ROOT)),'source_class':klass,'reference':ref,'state':state,'required':required})
    return rows

def collect(obj,key):
    out=[]
    if isinstance(obj,dict):
        if key in obj: out.append(obj[key])
        for v in obj.values(): out.extend(collect(v,key))
    elif isinstance(obj,list):
        for v in obj: out.extend(collect(v,key))
    return out

def explicit_api_verified(name,obj):
    """Only trust verification attached to the same object/subtree that names the API."""
    needle=name.casefold()
    if isinstance(obj,dict):
        local=' '.join(str(v) for k,v in obj.items() if k.lower() in {'name','provider','integration','adapter','id','slug'}).casefold()
        explicit=(obj.get('runtime_verified') is True or obj.get('verified') is True or obj.get('connected') is True or str(obj.get('status','')).casefold() in {'runtime_verified','verified','connected','working','live_verified'})
        if needle in local and explicit: return True
        return any(explicit_api_verified(name,v) for v in obj.values())
    if isinstance(obj,list): return any(explicit_api_verified(name,v) for v in obj)
    return False

def builder_team(kind,state):
    a=POLICY['builder_assignment']
    if state=='duplicate': return a['duplicate']
    if state=='missing_dependency': return a['dependency']
    if kind in {'bot','capability'}: return a['bot_or_capability']
    if kind=='division': return a['division']
    if kind=='API/integration': return a['API/integration']
    if kind in {'tool','workflow'}: return a['tool_or_workflow']
    return ['chief_architect','sandbox_qa_builder','release_reviewer']

def add_entity(rows,kind,eid,name,state,evidence,source=None,parent=None,blocker=None):
    actionable=state not in {'working','generated_at_runtime'}
    rows.append({'entity_class':kind,'entity_id':eid,'name':name,'state':state,'source':source,'parent':parent,'evidence':evidence,'blocker':blocker,'needs_builder_bot':actionable,'builder_team':builder_team(kind,state) if actionable else [],'next_action':('keep under regression/freshness checks' if state=='working' else 'run canonical builder' if state=='generated_at_runtime' else 'measure missing connection stage, repair at canonical owner, sandbox-test and retest')})

def main():
    refs=[]
    important=[(ROOT/'tools/run_everything_now.py','Run Everything Now steps',True),(ROOT/'tools/build_full_system_certification.py','Full System Certification dependencies',True),(ROOT/'package.json','package scripts',True),(ROOT/'config/run-everything-now.json','Run Everything config',True)]
    for p,k,r in important:
        if p.exists(): refs+=scan_refs(p,k,r)
        else: refs.append({'source':str(p.relative_to(ROOT)),'source_class':k,'reference':str(p.relative_to(ROOT)),'state':'missing','required':r})
    for folder,glob,klass in [(ROOT/'.github/workflows','*.yml','workflow run commands'),(ROOT/'.github/agents','*.agent.md','agent command references')]:
        if folder.exists():
            for p in sorted(folder.glob(glob)): refs+=scan_refs(p,klass,False)
    ref_blockers=[r for r in refs if r['required'] and r['state']=='missing']

    package=text(ROOT/'package.json'); runner=text(ROOT/'tools/run_everything_now.py'); workflows='\n'.join(text(p) for p in sorted((ROOT/'.github/workflows').glob('*.yml'))) if (ROOT/'.github/workflows').exists() else ''
    tests='\n'.join(text(p) for p in sorted((ROOT/'tests').glob('*')) if p.is_file()) if (ROOT/'tests').exists() else ''
    routes=(text(ROOT/'server/routes.ts')+'\n'+text(ROOT/'server/fleet-runtime.ts')).casefold()
    fleetgen=text(ROOT/'tools/generate_bot_fleet_catalog.ts')
    catalog=doc(ROOT/'config/generated/bots.catalog.json',{})
    catalog_blob=json.dumps(catalog).casefold(); catalog_slugs={str(v).casefold() for v in collect(catalog,'slug') if isinstance(v,(str,int))}
    runtime_doc=doc(ROOT/'config/generated/runtime-connection-readiness.json',{})

    entities=[]; bot_sources=defaultdict(list); bot_rows=[]; divisions=[]
    app=ROOT/'App_bots'
    if not app.exists(): add_entity(entities,'critical dependency','dependency:App_bots','App_bots','missing_dependency',['canonical bot source root absent'],'App_bots',blocker='canonical bot source root missing')
    else:
        for p in sorted(app.glob('*.json')):
            d=doc(p,{}); division=str(d.get('division') or p.stem); bots=d.get('bots',[]) if isinstance(d.get('bots'),list) else []
            divisions.append((division,p,len(bots)))
            for b in bots:
                if not isinstance(b,dict): continue
                slug=str(b.get('slug') or '').strip()
                if slug: bot_sources[slug].append(str(p.relative_to(ROOT))); bot_rows.append((division,p,b))

    for division,p,count in divisions:
        shard=ROOT/'website/data/bot-fleet'/f'{division}.json'; ev=[f'source={p.relative_to(ROOT)}',f'declared_bots={count}',f'generated_shard={shard.exists()}']
        state='working' if count and shard.exists() else ('partial' if count else 'disconnected')
        add_entity(entities,'division',f'division:{division}',division,state,ev,str(p.relative_to(ROOT)),blocker=None if state=='working' else 'division source or generated fleet shard incomplete')

    dupes={s for s,v in bot_sources.items() if len(v)>1}
    for division,p,b in bot_rows:
        slug=str(b['slug']); low=slug.casefold(); ev=[f'source={p.relative_to(ROOT)}',f'division={division}',f'generated_catalog={low in catalog_slugs}',f'route_reference={low in routes}']
        if slug in dupes: state='duplicate'; blocker=f'duplicate slug in {bot_sources[slug]}'
        elif low in catalog_slugs and ('App_bots' in fleetgen or low in routes): state='working'; blocker=None
        elif 'App_bots' in fleetgen: state='partial'; blocker='discoverable by fleet generator but generated/runtime evidence incomplete'
        else: state='disconnected'; blocker='canonical fleet/router path not found'
        add_entity(entities,'bot',f'bot:{slug}',b.get('displayName') or slug,state,ev,str(p.relative_to(ROOT)),division,blocker)
        for i,cap in enumerate(b.get('capabilities') or []):
            cap=str(cap).strip()
            if not cap: continue
            cap_state='working' if state=='working' and cap.casefold() in catalog_blob else ('duplicate' if state=='duplicate' else 'partial')
            add_entity(entities,'capability',f'capability:{slug}:{i}',cap,cap_state,[f'parent_bot={slug}',f'catalog_evidence={cap.casefold() in catalog_blob}'],str(p.relative_to(ROOT)),slug,None if cap_state=='working' else 'capability lacks complete current catalog/runtime evidence')

    orchestrators='\n'.join([package,runner,workflows])
    tool_dir=ROOT/'tools'
    if tool_dir.exists():
        for p in sorted(tool_dir.iterdir()):
            if not p.is_file() or p.name.startswith('.'): continue
            rel=str(p.relative_to(ROOT)); referenced=rel in orchestrators or p.name in orchestrators; tested=rel in tests or p.name in tests
            state='working' if referenced and (tested or p.name in runner) else ('partial' if referenced else 'disconnected')
            add_entity(entities,'tool',f'tool:{rel}',p.name,state,[f'referenced={referenced}',f'tested={tested}'],rel,blocker=None if state=='working' else 'tool exists but orchestration/test linkage is incomplete')

    wf=ROOT/'.github/workflows'
    if wf.exists():
        for p in sorted(wf.glob('*.yml')):
            t=text(p); state='working' if 'jobs:' in t and ('run:' in t or 'uses:' in t) else 'partial'
            add_entity(entities,'workflow',f'workflow:{p.name}',p.stem,state,[f'path={p.relative_to(ROOT)}'],str(p.relative_to(ROOT)))

    api=ROOT/'shared/api-registry.ts'; seen=set()
    for name,category in API_RE.findall(text(api)):
        key=(name.casefold(),category.casefold())
        if key in seen: continue
        seen.add(key); verified=explicit_api_verified(name,runtime_doc); state='working' if verified else 'external_adapter_unverified'
        add_entity(entities,'API/integration',f'api:{category}:{name}',name,state,[f'declared={api.relative_to(ROOT)}',f'category={category}',f'explicit_runtime_verified={verified}'],str(api.relative_to(ROOT)),blocker=None if verified else 'no explicit authorized runtime verification attached to this integration')

    for r in refs:
        if r['state']=='missing': add_entity(entities,'critical dependency',f"dependency:{r['source']}->{r['reference']}",r['reference'],'missing_dependency',[f"consumer={r['source']}"],r['source'],blocker='referenced path missing')
        elif r['state']=='generated_at_runtime': add_entity(entities,'generated artifact',f"generated:{r['reference']}",r['reference'],'generated_at_runtime',[f"consumer={r['source']}"],r['source'])

    states=Counter(e['state'] for e in entities); kinds=Counter(e['entity_class'] for e in entities); backlog=[e for e in entities if e['needs_builder_bot']]; load=Counter(w for e in backlog for w in e['builder_team'])
    legacy={'schema':'dreamco.repository_system_connections.v2','reference_count':len(refs),'state_counts':dict(Counter(r['state'] for r in refs)),'release_blocker_count':len(ref_blockers)+len(dupes),'release_blockers':ref_blockers+[{'type':'duplicate canonical bot slug','slug':s,'sources':bot_sources[s]} for s in sorted(dupes)],'references':refs,'entity_summary':{'entities':len(entities),'states':dict(states),'builder_backlog':len(backlog)},'ok':not ref_blockers and not dupes,'truth_boundary':POLICY['truth_rule']}
    mapdoc={'schema':'dreamco.repo_wide_connection_map.v2','entity_count':len(entities),'entity_class_counts':dict(kinds),'state_counts':dict(states),'working_count':states.get('working',0),'nonworking_count':len(entities)-states.get('working',0),'builder_backlog_count':len(backlog),'duplicate_bot_slugs':sorted(dupes),'entities':entities,'truth_boundary':POLICY['truth_rule']}
    back={'schema':'dreamco.repo_connection_builder_backlog.v1','backlog_count':len(backlog),'builder_load':dict(load),'parallel_rule':'independent canonical owners run in parallel; same-owner edits serialize and reconcile','gaps':backlog,'truth_boundary':POLICY['truth_rule']}
    OUT.parent.mkdir(parents=True,exist_ok=True); REPORT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(legacy,indent=2)+'\n'); MAP.write_text(json.dumps(mapdoc,indent=2)+'\n'); BACKLOG.write_text(json.dumps(back,indent=2)+'\n')
    lines=['# Repository System Connections','',f'- Repo-wide entities mapped: **{len(entities)}**',f'- Working: **{states.get("working",0)}**',f'- Builder backlog: **{len(backlog)}**',f'- Duplicate bot slugs: **{len(dupes)}**','','## Connection states','']+[f'- {k}: {v}' for k,v in sorted(states.items())]
    if backlog: lines+=['','## Builder backlog sample','']+[f"- `{e['entity_id']}` → **{e['state']}** → {', '.join(e['builder_team'])}" for e in backlog[:300]]
    REPORT.write_text('\n'.join(lines)+'\n')
    print(json.dumps({'ok':legacy['ok'],'references':len(refs),'entities':len(entities),'states':dict(states),'builder_backlog':len(backlog),'outputs':[str(OUT.relative_to(ROOT)),str(MAP.relative_to(ROOT)),str(BACKLOG.relative_to(ROOT))]},indent=2))
    return 0 if legacy['ok'] else 1

if __name__=='__main__': raise SystemExit(main())
