#!/usr/bin/env python3
"""Bounded offline build/test bundles for the existing shared fleet runtime.

Never generates fake specialist implementations or changes readiness/production.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from buddy.fleet_runtime.contract import load_manifests, load_fixtures
from buddy.fleet_runtime.executor import FleetExecutor
from buddy.fleet_runtime.smoke import generic_smoke, fixture_smoke


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def plan(request, collection=None):
    allowed={'schema_version','request_id','enabled','selection','bot_ids','max_items','batch_size','max_parallel'}
    if not isinstance(request,dict) or set(request)!=allowed or request['schema_version']!=1:
        raise ValueError('Invalid build request schema')
    if not isinstance(request['request_id'],str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}',request['request_id']):
        raise ValueError('Invalid request ID')
    if type(request['enabled']) is not bool:
        raise ValueError('enabled must be boolean')
    for key,minimum,maximum in [('max_items',1,5000),('batch_size',1,100),('max_parallel',1,8)]:
        if type(request[key]) is not int or not minimum<=request[key]<=maximum:
            raise ValueError(f'{key} must be {minimum}–{maximum}')
    if request['selection'] not in {'all_existing','explicit'}:
        raise ValueError('Unknown selection mode')
    if not isinstance(request['bot_ids'],list) or not all(isinstance(s,str) for s in request['bot_ids']):
        raise ValueError('bot_ids must be a list of strings')
    if len(set(request['bot_ids'])) != len(request['bot_ids']):
        raise ValueError('Duplicate requested bot IDs')
    collection=collection or load_manifests()
    known={b['slug'] for b in collection['bots']}
    if request['selection']=='all_existing' and request['bot_ids']:
        raise ValueError('all_existing cannot also contain explicit IDs')
    ids=sorted(known) if request['selection']=='all_existing' else request['bot_ids']
    unknown=set(ids)-known
    if unknown:raise ValueError('Unknown bot IDs: '+', '.join(sorted(unknown)[:10]))
    if len(ids)>request['max_items']:
        raise ValueError('Request exceeds its item budget; choose an explicit subset or raise the bounded budget')
    if not request['enabled']:ids=[]
    size=request['batch_size']
    batches=[{'shard':index//size,'bot_ids':ids[index:index+size]} for index in range(0,len(ids),size)]
    return {'schema_version':1,'request':request,'request_hash':digest(request),'manifest_hash':digest(collection),
            'selected_count':len(ids),'max_parallel':request['max_parallel'],'batches':batches,
            'boundary':'Builds tested shared-engine bundles only; not specialist mastery, live integrations or production readiness.'}


def build_batch(build_plan, shard, output):
    collection=load_manifests()
    if digest(collection)!=build_plan['manifest_hash']:
        raise ValueError('Manifest changed after request planning')
    expected=plan(build_plan['request'],collection)
    if expected!=build_plan:
        raise ValueError('Build plan was changed after validation')
    batch=next((b for b in build_plan['batches'] if b['shard']==shard),None)
    if batch is None:raise ValueError('Unknown shard')
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    executor=FleetExecutor(env={})  # Explicitly ignore ambient provider credentials.
    fixtures=load_fixtures()['fixtures']
    results=[]
    for slug in batch['bot_ids']:
        if not re.fullmatch(r'[a-zA-Z0-9_-]+',slug):raise ValueError('Unsafe artifact identifier')
        manifest=executor.manifest(slug)
        row={'bot':slug,'engine':manifest['engine'],'run_policy':manifest.get('run_policy','spec_only'),
             'live_external_action_taken':False,'specialist_capability_verified':False,'production_ready':False}
        if manifest.get('enabled') is False or row['run_policy']!='allowed':
            row.update(status='blocked',reason='Existing run policy or customization does not permit this bot to run.')
        elif slug not in fixtures:
            row.update(status='blocked',reason='A required bot fixture is missing; no tested bundle emitted.')
        else:
            generic=generic_smoke(executor,slug);fixture=fixture_smoke(executor,slug,fixtures[slug])
            row.update(generic_smoke=generic,fixture_smoke=fixture,
                       status='shared_engine_bundle_tested' if generic['passed'] and fixture['passed'] else 'failed')
        with zipfile.ZipFile(output/f'{slug}.zip','w',zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('manifest.json',json.dumps(manifest,indent=2))
            archive.writestr('verification.json',json.dumps(row,indent=2))
            archive.writestr('README.md',f"# {slug}\n\nStatus: {row['status']}.\n\nThis bundle reuses buddy.fleet_runtime in the inspected repository. It is not a standalone specialist implementation. Generic/generated-fixture smoke results do not establish domain accuracy. No live services, payment, publishing or training are enabled. Run from an environment with this repository on PYTHONPATH.\n")
            if row['status']=='shared_engine_bundle_tested':
                archive.writestr('run.py',
                    'import argparse,json\nfrom buddy.fleet_runtime.executor import FleetExecutor\n'
                    'p=argparse.ArgumentParser();p.add_argument("--objective",required=True);p.add_argument("--input",default="{}");a=p.parse_args()\n'
                    'executor=FleetExecutor(env={})\n'
                    f'slug={slug!r}\n'
                    'm=executor.manifest(slug)\n'
                    'if m.get("enabled") is False or m.get("run_policy")!="allowed":raise SystemExit("Bot run policy is blocked")\n'
                    'print(json.dumps(executor.run(slug,{"objective":a.objective,"input":json.loads(a.input),"action_level":"sandbox"}),indent=2))\n')
        results.append(row)
    summary={'schema_version':1,'request_hash':build_plan['request_hash'],'manifest_hash':build_plan['manifest_hash'],
             'shard':shard,'results':results,'counts':dict(Counter(r['status'] for r in results))}
    (output/f'shard-{shard}.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary


def reduce_results(build_plan, reports):
    expected={b['shard']:set(b['bot_ids']) for b in build_plan['batches']}
    seen=set();rows=[]
    for report in reports:
        shard=report['shard']
        if shard in seen or shard not in expected:raise ValueError('Duplicate or unexpected shard')
        if report['request_hash']!=build_plan['request_hash'] or report['manifest_hash']!=build_plan['manifest_hash']:
            raise ValueError('Evidence does not match this request and source')
        ids=[r['bot'] for r in report['results']]
        if len(ids)!=len(set(ids)) or set(ids)!=expected[shard]:raise ValueError('Incomplete or duplicated bot evidence')
        if any(r['status'] not in {'blocked','failed','shared_engine_bundle_tested'} or r['live_external_action_taken'] or r['production_ready'] or r['specialist_capability_verified'] for r in report['results']):
            raise ValueError('Invalid result or unsupported promotion')
        seen.add(shard);rows.extend(report['results'])
    missing=sorted(set(expected)-seen)
    counts=dict(Counter(r['status'] for r in rows))
    return {'schema_version':1,'request_hash':build_plan['request_hash'],'manifest_hash':build_plan['manifest_hash'],
            'requested':build_plan['selected_count'],'processed':len(rows),'missing_shards':missing,
            'counts':counts,'ok':not missing and not counts.get('failed',0),
            'all_requested_built':not missing and len(rows)==counts.get('shared_engine_bundle_tested',0),
            'specialist_capability_verified':False,'production_ready':False,
            'results':rows,'boundary':build_plan['boundary']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['plan','build','reduce'])
    parser.add_argument('--request',type=Path,default=ROOT/'config/bots/daily-build-request.json')
    parser.add_argument('--plan',type=Path)
    parser.add_argument('--shard',type=int)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--reports',type=Path)
    parser.add_argument('--github-output',type=Path)
    args=parser.parse_args()
    if args.command=='plan':
        if args.request.stat().st_size>1_000_000:parser.error('Request exceeds 1 MB')
        result=plan(json.loads(args.request.read_text()));args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,indent=2)+'\n')
        if args.github_output:
            with args.github_output.open('a') as stream:
                stream.write('matrix='+json.dumps({'include':[{'shard':b['shard']} for b in result['batches']]})+'\n')
                stream.write(f"count={len(result['batches'])}\nparallel={result['max_parallel']}\n")
    elif args.command=='build':
        if args.plan is None or args.shard is None:parser.error('build needs --plan and --shard')
        result=build_batch(json.loads(args.plan.read_text()),args.shard,args.out)
    else:
        if args.plan is None or args.reports is None:parser.error('reduce needs --plan and --reports')
        result=reduce_results(json.loads(args.plan.read_text()),[json.loads(p.read_text()) for p in sorted(args.reports.rglob('shard-*.json'))])
        args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in {'results','batches','request'}}))
    return 1 if result.get('ok') is False or result.get('counts',{}).get('failed') else 0


if __name__=='__main__':raise SystemExit(main())
