"""Offline coverage report for Buddy's canonical MasterBot registry."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def build(divisions_registry, benchmark_registry, taxonomy, goals):
    divisions = divisions_registry['divisions']
    tasks = benchmark_registry['tasks']
    ids = [d['id'] for d in divisions]
    names = [d['name'] for d in divisions]
    if len(ids) != len(set(ids)) or len(names) != len(set(names)) or len(divisions) != divisions_registry['canonical_count']:
        raise ValueError('Division registry duplicate or count mismatch')
    if not tasks or len(tasks) != len(set(tasks)):
        raise ValueError('Benchmark tasks missing or duplicated')
    mapped = {e['division'] for e in taxonomy.get('examples', [])}
    return {'schema':'dreamco.buddy_division_evidence.v1', 'counts':{'registered_divisions':len(divisions),'benchmark_task_types':len(tasks),'required_division_task_pairs':len(divisions)*len(tasks),'measured_pairs_in_this_report':0,'divisions_without_model_route_example':sum(d['name'] not in mapped for d in divisions),'goal_records':len(goals.get('goals',[])),'goal_statuses':{s:sum(g.get('status')==s for g in goals.get('goals',[])) for s in sorted({g.get('status','UNKNOWN') for g in goals.get('goals',[])})}},'divisions':[{'id':d['id'],'name':d['name'],'status':'unmeasured','route_example_present':d['name'] in mapped} for d in divisions], 'production_ready':False,'trained_weights_verified':False,'scope':'Static registry inventory only; no independent evaluation runs were loaded.'}

def main():
    paths=['config/masterbot-65-registry.json','config/buddy-benchmark-task-registry.json','config/task-model-taxonomy.json','reports/goals_to_gates.json']
    inputs=[json.loads((ROOT/p).read_text(encoding='utf-8')) for p in paths]
    report=build(*inputs)
    output=ROOT/'website/data/buddy-division-evidence.json'
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report['counts']))

if __name__=='__main__':main()
