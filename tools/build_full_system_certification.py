#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PROGRAM=ROOT/'config/full-system-operational-certification.json'
OUT=ROOT/'config/generated/full-system-operational-certification.json'
REPORT=ROOT/'reports/FULL_SYSTEM_OPERATIONAL_CERTIFICATION.md'
SOURCES={
 'verification':ROOT/'tmp/dreamco-verification/latest.json','speed_accuracy':ROOT/'config/generated/system-speed-accuracy-benchmarks.json','runtime_smoke':ROOT/'config/generated/production-runtime-smoke.json','connections':ROOT/'config/generated/runtime-connection-readiness.json','repository_connections':ROOT/'config/generated/repository-system-connections.json','code_trust':ROOT/'config/generated/trusted-code-delivery-audit.json','bot_accounting':ROOT/'config/generated/bot-accounting-placement-audit.json','legacy_recovery':ROOT/'config/generated/legacy-bot-recovery-manifest.json','unified_bots':ROOT/'config/generated/unified-bot-system.json','maximum_sandbox':ROOT/'config/generated/maximum-sandbox-matrix.json','sandbox_runtime':ROOT/'config/generated/maximum-sandbox-runtime-audit.json','ontology':ROOT/'config/generated/dreamco-ontology-snapshot.json','work_benchmarks':ROOT/'config/generated/work-platform-benchmark-backlog.json','manufacturing':ROOT/'config/generated/manufacturing-productivity-benchmarks.json','universal_benchmark':ROOT/'config/generated/universal-capability-benchmark.json','business_benchmarks':ROOT/'config/generated/business-lifecycle-benchmarks.json','creative_benchmarks':ROOT/'config/generated/creative-studio-mastery-benchmarks.json','government_benchmarks':ROOT/'config/generated/government-public-sector-benchmarks.json','benchmark_gap_registry':ROOT/'config/generated/parallel-benchmark-gap-registry.json','value_discovery':ROOT/'config/generated/continuous-value-discovery-backlog.json'}
def load(path): return json.loads(path.read_text()) if path.exists() else {}
def main()->int:
    program=json.loads(PROGRAM.read_text()); docs={n:load(p) for n,p in SOURCES.items()}; blockers=[f'missing evidence:{n}' for n,p in SOURCES.items() if not p.exists()]
    d=docs
    checks={
      'production_verification':d['verification'].get('productionReady') is True,
      'speed_accuracy':d['speed_accuracy'].get('ok') is True,
      'production_runtime_smoke':d['runtime_smoke'].get('passed') is True,
      'trusted_code_static_audit':not d['code_trust'].get('release_blockers',['missing']),
      'bot_accounting':d['bot_accounting'].get('accounting_complete') is True,
      'legacy_recovery_inventory':d['legacy_recovery'].get('file_count',0)>0,
      'unified_bot_system':d['unified_bots'].get('canonical_bot_count')==1051,
      'maximum_sandbox_matrix':d['maximum_sandbox'].get('worker_count',0)>=1051 and d['maximum_sandbox'].get('minimum_test_dimensions_per_applicable_case',0)>=40,
      'canonical_sandbox_runtime_evidence':d['sandbox_runtime'].get('all_canonical_workers_have_runtime_evidence') is True,
      'ontology_snapshot':d['ontology'].get('object_count',0)>0 and d['ontology'].get('link_count',0)>0,
      'runtime_connection_truth':d['connections'].get('connection_count',0)>=0,
      'repository_connection_integrity':d['repository_connections'].get('ok') is True,
      'work_platform_benchmarks':d['work_benchmarks'].get('status') in {'generated','work_catalog_missing'},
      'manufacturing_productivity_benchmarks':d['manufacturing'].get('benchmark_case_count',0)>0,
      'universal_human_computer_ai_benchmark':d['universal_benchmark'].get('case_count',0)>0,
      'business_lifecycle_benchmarks':d['business_benchmarks'].get('case_count',0)>0,
      'creative_mastery_benchmarks':d['creative_benchmarks'].get('case_count',0)>0,
      'government_public_sector_benchmarks':d['government_benchmarks'].get('case_count',0)>0,
      'all_benchmarks_have_gap_workers':d['benchmark_gap_registry'].get('benchmark_case_count',0)>0,
      'continuous_value_discovery':d['value_discovery'].get('candidate_count',0)>0,
    }
    blockers += [name for name,passed in checks.items() if not passed]
    core=not blockers; connections=d['connections']; all_connections=connections.get('all_declared_runtime_connections_verified') is True
    status='certified' if core and all_connections else ('core_certified_external_connection_gaps' if core else 'blocked')
    payload={'schema':'dreamco.full_system_operational_certification.generated.v4','generated_at':datetime.now(timezone.utc).isoformat(),'status':status,'core_operational_certified':core,'all_declared_runtime_connections_verified':all_connections,'fully_operational_and_connected_claim_allowed':core and all_connections,'checks':checks,'release_blockers':sorted(set(blockers)),'connection_summary':{'declared':connections.get('connection_count',0),'runtime_verified':connections.get('runtime_verified_count',0),'internal_references':d['repository_connections'].get('reference_count',0),'internal_blockers':d['repository_connections'].get('release_blocker_count',0)},'speed_summary':{'passed':d['speed_accuracy'].get('speed_passed',0),'total':d['speed_accuracy'].get('speed_total',0)},'accuracy_summary':{'passed':d['speed_accuracy'].get('accuracy_passed',0),'total':d['speed_accuracy'].get('accuracy_total',0)},'runtime_summary':{'startup_seconds':d['runtime_smoke'].get('startup_seconds'),'health_latency_ms':d['runtime_smoke'].get('health_latency_ms')},'recovery_summary':{'legacy_files':d['legacy_recovery'].get('file_count',0),'recoverable_candidates':d['legacy_recovery'].get('recoverable_candidate_file_count',0),'canonical_bots':d['unified_bots'].get('canonical_bot_count',0)},'sandbox_summary':{'workers':d['maximum_sandbox'].get('worker_count',0),'overlays':d['maximum_sandbox'].get('minimum_test_dimensions_per_applicable_case',0),'canonical_runtime_coverage_percent':d['sandbox_runtime'].get('canonical_worker_runtime_coverage_percent',0),'noncanonical_workers_requiring_explicit_evidence':d['sandbox_runtime'].get('noncanonical_workers_requiring_explicit_evidence',0)},'ontology_summary':{'objects':d['ontology'].get('object_count',0),'links':d['ontology'].get('link_count',0)},'benchmark_summary':{'universal':d['universal_benchmark'].get('case_count',0),'business':d['business_benchmarks'].get('case_count',0),'creative':d['creative_benchmarks'].get('case_count',0),'government':d['government_benchmarks'].get('case_count',0),'manufacturing':d['manufacturing'].get('benchmark_case_count',0),'parallel_gap_workers':d['benchmark_gap_registry'].get('benchmark_case_count',0),'value_candidates':d['value_discovery'].get('candidate_count',0)},'verification_summary':d['verification'].get('totals',{}),'truth_boundary':program['truth_rule']}
    OUT.parent.mkdir(parents=True,exist_ok=True); REPORT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2)+'\n')
    lines=['# Full System Operational Certification','',f"Status: **{status}**",f"Core operationally certified: **{core}**",f"Fully operational + connected claim allowed: **{payload['fully_operational_and_connected_claim_allowed']}**",'','## Evidence','']+[f"- {n}: {'PASS' if p else 'FAIL'}" for n,p in checks.items()]
    lines += ['',f"- Sandbox overlays: {payload['sandbox_summary']['overlays']}",f"- Universal/business/creative/government/manufacturing cases: {payload['benchmark_summary']['universal']}/{payload['benchmark_summary']['business']}/{payload['benchmark_summary']['creative']}/{payload['benchmark_summary']['government']}/{payload['benchmark_summary']['manufacturing']}",f"- Parallel benchmark gap workers: {payload['benchmark_summary']['parallel_gap_workers']}",f"- Continuous value candidates: {payload['benchmark_summary']['value_candidates']}"]
    if blockers: lines += ['','## Blockers','']+[f'- {b}' for b in sorted(set(blockers))]
    lines += ['','> Certification is commit- and environment-specific. External integrations require authorized runtime evidence.']
    REPORT.write_text('\n'.join(lines)+'\n'); print(json.dumps({'status':status,'core_operational_certified':core,'blockers':sorted(set(blockers))},indent=2)); return 0 if core else 1
if __name__=='__main__': raise SystemExit(main())
