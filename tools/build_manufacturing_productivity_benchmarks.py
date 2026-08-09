#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'config/universal-business-manufacturing-productivity-program.json').read_text())
OUT=ROOT/'config/generated/manufacturing-productivity-benchmarks.json'

SCENARIOS=[
 ('production_planning',['cycle_time','throughput','schedule_adherence','lead_time']),
 ('quality_inspection',['first_pass_yield','scrap_rate','rework_rate','defects_per_million']),
 ('maintenance',['uptime','downtime','OEE','cost_per_unit']),
 ('inventory',['inventory_turns','stockout_rate','on_time_delivery','lead_time']),
 ('supplier_management',['supplier_otd','supplier_quality','cost_per_unit','lead_time']),
 ('changeover',['changeover_time','throughput','OEE','schedule_adherence']),
 ('labor_productivity',['labor_hours_per_unit','cost_per_unit','throughput','touch_time']),
 ('energy_efficiency',['energy_per_unit','cost_per_unit','throughput']),
 ('root_cause_analysis',['downtime','scrap_rate','rework_rate','first_pass_yield']),
 ('warehouse_shipping',['on_time_delivery','queue_time','touch_time','inventory_turns'])
]

def main()->int:
    metrics=set(CFG['productivity_metrics']); rows=[]
    for scenario,metric_names in SCENARIOS:
        for metric in metric_names:
            if metric not in metrics: continue
            rows.append({
              'scenario':scenario,'metric':metric,'baseline_required':True,'post_change_measurement_required':True,
              'minimum_evidence':['baseline sample','intervention description','post-change sample','sample period','data source','confounder notes'],
              'sandbox_tests':['correctness','edge cases','failure recovery','safety boundary','latency','cost','explainability'],
              'claim_status':'no_improvement_claim_until_measured'
            })
    payload={'schema':'dreamco.manufacturing_productivity_benchmarks.v1','scenario_count':len(SCENARIOS),'benchmark_case_count':len(rows),'cases':rows,'truth_boundary':CFG['truth_rule']}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps({'ok':True,'scenarios':len(SCENARIOS),'cases':len(rows),'output':str(OUT.relative_to(ROOT))},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
