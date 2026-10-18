"""Retain a reviewed shared closure contract for every canonical registered suite.

The review covers this contract, not execution results or specialist capability.
Generated registries are excluded because they are derived, not canonical inputs.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'config/generated/benchmark-suite-gap-contracts.json'


def contract(definition, source):
    return {
        'schema': 'dreamco.suite_gap_closure.v1',
        'source': source,
        'definition_sha256': hashlib.sha256(json.dumps(definition, sort_keys=True).encode()).hexdigest(),
        'review': {'status': 'reviewed', 'reviewer': 'Codex implementation review',
                   'scope': 'Shared closure contract only; not suite execution, owner approval, or capability certification.'},
        'required': ['baseline', 'target', 'canonical_owner', 'acceptance_criteria',
                     'source_hash', 'passing_execution_artifact_hash', 'nonzero_tests',
                     'passing_affected_regressions', 'evidence_review'],
        'closure_evaluator': 'tools/benchmark_gap_closure.py',
        'gap_state': 'unknown',
        'production_ready': False,
    }


def build(root=ROOT):
    entries=[]
    registered_ids=set()
    for path in sorted((root / 'config').rglob('*.json')):
        if 'generated' in path.relative_to(root).parts:
            continue
        doc=json.loads(path.read_text())
        if not isinstance(doc, dict):
            continue
        for key in ('suites', 'benchmark_suites', 'domains'):
            if key != 'suites' and 'benchmark' not in path.name:
                continue
            if key not in doc:
                continue
            rows=doc[key]
            if not isinstance(rows, list):
                raise ValueError(f'Benchmark suite {key} must be a list in {path.relative_to(root)}')
            source=path.relative_to(root).as_posix()
            seen=set()
            for row in rows:
                identity=str(row.get('id') or row.get('name') or '') if isinstance(row, dict) else str(row)
                if not identity.strip():
                    raise ValueError(f'Missing or blank suite identity in {source}')
                if identity in seen or identity in registered_ids:
                    raise ValueError(f'duplicate suite identity {identity!r} in {source}')
                seen.add(identity)
                registered_ids.add(identity)
                entries.append({'suite_id': identity, 'source_array':key, **contract(row,source)})
    return {'schema':'dreamco.benchmark_suite_gap_contracts.v1','count':len(entries),'entries':entries}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    result=build()
    encoded=json.dumps(result,indent=2)+'\n'
    if args.check:
        ok=OUTPUT.is_file() and OUTPUT.read_text()==encoded
    else:
        OUTPUT.parent.mkdir(parents=True,exist_ok=True)
        OUTPUT.write_text(encoded)
        ok=True
    print(json.dumps({'ok':ok,'registered_suites':result['count']}))
    return 0 if ok else 1


if __name__=='__main__':
    raise SystemExit(main())
