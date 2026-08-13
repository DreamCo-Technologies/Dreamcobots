#!/usr/bin/env python3
"""Build public-safe Actions control prospectus from the repository health catalog."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
contract=json.loads((ROOT/'config/actions-control-prospectus.json').read_text())
health=json.loads((ROOT/'website/data/actions-health-report.json').read_text())
by_id={item['id']:item for item in contract['controls']}
rows=[]
for workflow in health.get('findings',[]):
    controls=workflow.get('controls',{})
    evidence='static_checks_passed' if workflow.get('static_status')=='static_checks_passed' else 'blocked'
    rows.append({
        'workflow':workflow['workflow'], 'name':workflow['display_name'], 'purpose':workflow['purpose'],
        'github_url':workflow.get('github_url'), 'status':evidence,
        'errors':len(workflow.get('errors',[])), 'warnings':len(workflow.get('warnings',[])),
        'runner_jobs':controls.get('runner_jobs',0), 'upgrades':workflow.get('upgrades',[]),
        'progress': 'configured' if evidence=='static_checks_passed' else 'blocked',
        'investor_note':'Operational evidence is required before claiming health or mastery.'
    })
controls=[]
for item in contract['controls']:
    controls.append({**item,'progress':'configured','workflow_count':len(rows)})
out={'schema':'dreamco.actions_prospectus.v1','generated_from':['config/actions-control-prospectus.json','website/data/actions-health-report.json'],'controls':controls,'workflows':rows,'progress_model':contract['progress_model'],'truth_boundary':contract['truth_boundary']}
for path in [ROOT/'website/data/actions-prospectus.json',ROOT/'config/generated/actions-prospectus.json']:
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(out,indent=2)+'\n')
print(f'Generated Actions prospectus: {len(rows)} workflows, {len(controls)} controls')
