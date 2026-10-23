#!/usr/bin/env python3
"""Convert real division-contract measurements; reject missing or contradictory evidence."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path


def convert(source: object) -> dict:
    if not isinstance(source, dict) or source.get('schema') != 'dreamco.daily_division_contract_benchmark.v2':
        raise ValueError('missing or invalid division benchmark schema')
    items = source.get('divisionResults')
    if not isinstance(items, list) or not items:
        raise ValueError('divisionResults must be a nonempty list of measured divisions')
    if type(source.get('divisions')) is not int or source['divisions'] != len(items):
        raise ValueError('declared division count does not match measured divisions')
    seen = set()
    rows = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f'divisionResults[{index}] must be an object')
        division, score, status = item.get('division'), item.get('score'), item.get('status')
        passed, total = item.get('passed'), item.get('total')
        if not isinstance(division, str) or not division.strip() or division in seen:
            raise ValueError(f'divisionResults[{index}] has an invalid or duplicate division')
        if (type(passed) is not int or type(total) is not int or total < 1
                or passed < 0 or passed > total):
            raise ValueError(f'divisionResults[{index}] has invalid check counts')
        if type(score) not in (int, float) or not math.isfinite(score) or not 0 <= score <= 100:
            raise ValueError(f'divisionResults[{index}] has an invalid score')
        if not math.isclose(score, 100 * passed / total, rel_tol=1e-9, abs_tol=1e-9):
            raise ValueError(f'divisionResults[{index}] has contradictory score and check counts')
        if status not in ('pass', 'needs_remediation') or (status == 'pass') != (passed == total):
            raise ValueError(f'divisionResults[{index}] has contradictory status')
        seen.add(division)
        rows.append({'division': division, 'benchmark': 'buddy-division-contract',
                     'score': score, 'target': 100, 'status': 'pass' if status == 'pass' else 'failed',
                     'evidence_count': passed, 'source': 'run_daily_division_benchmarks'})
    return {'schema': 'dreamco.benchmark_scores.v1', 'results': rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    result = convert(json.loads(Path(args.input).read_text()))
    Path(args.output).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'divisions': len(result['results']), 'measured': len(result['results'])}, indent=2))


if __name__ == '__main__':
    main()
