#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,hashlib,math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def passing_evidence(record, root):
    """Require reviewed, hash-bound local results; declarations never prove closure."""
    evidence = record.get('evidence')
    if not isinstance(evidence, dict) or evidence.get('review_status') != 'reviewed' or not evidence.get('reviewer'):
        return False
    try:
        root = root.resolve()
        source = (root / evidence['source']).resolve()
        artifact = (root / evidence['artifact']).resolve()
        if not source.is_relative_to(root) or not artifact.is_relative_to(root):
            return False
        raw = artifact.read_bytes()
        if hashlib.sha256(raw).hexdigest() != evidence['artifact_sha256']:
            return False
        result = json.loads(raw)
        return (result.get('benchmark_id') == record['benchmark_id']
                and result.get('source_sha256') == hashlib.sha256(source.read_bytes()).hexdigest()
                and result.get('status') == 'passed' and result.get('regression_status') == 'passed'
                and type(result.get('tests_run')) is int and result['tests_run'] > 0
                and type(result.get('tests_failed')) is int and result['tests_failed'] == 0
                and type(result.get('score')) in (int, float) and math.isfinite(result['score'])
                and result.get('target') == record['target']
                and result['score'] >= record['target']
                # New closures pin the historical baseline separately from the passing rerun.
                # Preserve legacy receipts only if their original baseline already passed.
                and (
                    (type(result.get('baseline')) in (int, float)
                     and math.isfinite(result['baseline'])
                     and result['baseline'] == record['baseline'])
                    or (result.get('baseline') is None
                        and record['baseline'] >= record['target']
                        and result['score'] == record['baseline'])
                ))
    except (KeyError, TypeError, ValueError, OSError):
        return False

def plan(record, root=ROOT, *, registry_only=False):
    required=['division_id','benchmark_id','baseline','target']
    missing=[k for k in required if k not in record]
    if registry_only:
        missing.append('independent_measurement_ledger')
    if missing:
        blocked = {'status':'blocked','missing':missing, 'evidence_verified': False}
        if 'suite_id' in record:
            blocked.update({
                'suite_id': record['suite_id'],
                'source': record.get('source'),
                'review_status': 'requires_suite_specific_review',
                'remediation_design': [
                    'measure_and_pin_before_evidence',
                    'diagnose_root_cause',
                    'propose_smallest_shared_safe_fix_with_rollback',
                    'apply_only_in_review_branch_or_sandbox',
                    'run_targeted_tests_and_benchmark',
                    'compare_before_after_evidence',
                    'retest_dependent_suites_and_review_or_remain_blocked',
                ],
            })
        return blocked
    if any(type(record[k]) not in (int, float) or not math.isfinite(record[k]) for k in ('baseline', 'target')):
        return {'status': 'blocked', 'reason': 'finite numeric measurements required'}
    gap=record['target']-record['baseline']
    closed = passing_evidence(record, Path(root))
    return {'status':'closed' if closed else 'open','division_id':record['division_id'],'benchmark_id':record['benchmark_id'],'gap':gap,'next_action':'regression_check' if closed or gap<=0 else 'train_practice_sandbox_transfer', 'evidence_verified': closed}


def _validated_measurements(records):
    # A raw measurement ledger must not count one benchmark twice. Missing
    # identities remain visible as blocked records; malformed entries fail closed.
    seen = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f'measurement at index {index} must be an object')
        division, benchmark = record.get('division_id'), record.get('benchmark_id')
        if 'division_id' not in record or 'benchmark_id' not in record:
            continue
        if (type(division) not in (str, int) or not str(division).strip()
                or not isinstance(benchmark, str) or not benchmark.strip()):
            raise ValueError(f'invalid measurement identity at index {index}')
        identity = (str(division).strip(), benchmark.strip())
        if identity in seen:
            raise ValueError(f'duplicate measurement identity: {identity[0]}/{identity[1]}')
        seen.add(identity)
    return records


def load_records(data):
    if isinstance(data, list):
        return _validated_measurements(data)
    if not isinstance(data, dict):
        raise ValueError('expected a list or a recognized records/registry object')
    if data.get('schema') == 'dreamco.benchmark_suite_gap_contracts.v1':
        entries = data.get('entries')
        if not isinstance(entries, list) or not entries:
            raise ValueError('benchmark registry entries must be a nonempty list')
        if type(data.get('count')) is not int or data['count'] != len(entries):
            raise ValueError('benchmark registry count does not match entries')
        if any(not isinstance(e, dict) or not isinstance(e.get('suite_id'), str) or not e['suite_id'] for e in entries):
            raise ValueError('every benchmark registry entry requires a suite_id')
        ids = [e['suite_id'] for e in entries]
        if len(ids) != len(set(ids)):
            raise ValueError('duplicate suite_id in benchmark registry')
        # A registry contract is not a measurement ledger.
        # Preserve all entries as blocked, without invented baselines.
        return entries
    records = data.get('records')
    if not isinstance(records, list):
        raise ValueError('expected records list or benchmark suite registry')
    return _validated_measurements(records)

def main():
    p=argparse.ArgumentParser(); p.add_argument('input'); p.add_argument('--output',default='benchmark-gap-plan.json'); a=p.parse_args()
    data=json.loads(Path(a.input).read_text())
    try:
        records=load_records(data)
    except ValueError as exc:
        p.error(str(exc))
    registry_only = isinstance(data, dict) and data.get('schema') == 'dreamco.benchmark_suite_gap_contracts.v1'
    result=[plan(r, registry_only=registry_only) for r in records]
    Path(a.output).write_text(json.dumps({'schema':'dreamco.benchmark_gap_plan.v1','records':result},indent=2)+'\n')
    print(json.dumps({'records':len(result),'open':sum(x.get('status')=='open' for x in result),'blocked':sum(x.get('status')=='blocked' for x in result)},indent=2))
if __name__=='__main__': main()
