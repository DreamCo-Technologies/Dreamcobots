#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
p=Path('config/actions-page-operating-system.json'); d=json.loads(p.read_text())
required={'command_center','health','goals','execution','training','benchmarks','65_divisions','local_model','data_sources','repairs','security','releases'}
errors=[]
if d.get('division_contract',{}).get('count') != 65: errors.append('division count must be 65')
if not required.issubset(set(d.get('sections',[]))): errors.append('missing required Actions sections')
for x in ['unknown_is_not_pass','planned_is_not_executed','training_is_not_mastery','one_successful_run_is_not_mastery','stale_evidence_is_not_current_health']:
    if x not in d.get('truth_rules',[]): errors.append('missing truth rule: '+x)
for x in ['owner','purpose','inputs','command_or_workflow','success_criteria','evidence_path','timeout','failure_action']:
    if x not in d.get('every_job_requires',[]): errors.append('missing job field: '+x)
print(json.dumps({'valid':not errors,'errors':errors},indent=2)); sys.exit(1 if errors else 0)
