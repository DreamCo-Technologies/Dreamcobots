"""Offline regression coverage for benchmark gap plan integrity and review truth."""
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'tools' / 'plan_parallel_benchmark_gaps.py'


def run_plan(tmp_path, suites):
    root = tmp_path
    (root / 'config').mkdir(exist_ok=True)
    (root / 'tools').mkdir(exist_ok=True)
    (root / 'tools' / SCRIPT.name).write_text(SCRIPT.read_text())
    (root / 'config' / 'buddy-guardrails-benchmark-program.json').write_text(json.dumps({
        'parallel_builder_team': {'maximum_parallel_lanes': 2},
        'benchmark_domains': ['correctness'],
        'global_guardrails': ['deny_unapproved_actions'],
    }))
    (root / 'config' / 'repository-test-suites.json').write_text(json.dumps(suites))
    process = subprocess.run([sys.executable, str(root / 'tools' / SCRIPT.name)],
                             cwd=root, capture_output=True, text=True)
    out = root / 'config' / 'generated' / 'parallel-benchmark-gap-plan.json'
    return process, json.loads(out.read_text()) if out.exists() else None


def test_plan_pending_review_never_claims_mastery(tmp_path):
    suites = {'suites': [{'id': 'routing', 'name': 'Model routing', 'area': 'Models',
                          'tests': ['tests/test_routing.py'], 'sources': ['server/router.ts']}]}
    proc, plan = run_plan(tmp_path, suites)
    assert proc.returncode == 0, proc.stderr
    assert plan['lane_count'] == 1
    entry = plan['lanes'][0]['suites'][0]
    assert entry['suite_id'] == 'routing'
    assert entry['gap_state'] == 'unknown'
    assert entry['gap_closure_contract']['review']['status'] == 'requires_suite_specific_review'
    assert entry['gap_closure_contract']['review']['reviewer'] is None
    assert entry['gap_closure_contract']['production_ready'] is False
    assert entry['gap_closure_contract']['required_regressions'] == ['tests/test_routing.py']


def test_duplicate_ids_fail_closed_without_plan(tmp_path):
    suites = {'suites': [{'id': 'same', 'name': 'First'}, {'id': 'same', 'name': 'Second'}]}
    proc, plan = run_plan(tmp_path, suites)
    assert proc.returncode != 0
    assert 'duplicate benchmark suite id' in proc.stderr
    assert plan is None


def test_missing_or_empty_registry_fails_closed(tmp_path):
    for value in ({}, {'suites': []}, {'suites': None}, {'suites': {}}):
        root = tmp_path / str(len(list(tmp_path.iterdir())))
        root.mkdir()
        proc, plan = run_plan(root, value)
        assert proc.returncode != 0
        assert plan is None


def test_malformed_suite_rows_fail_closed(tmp_path):
    invalid = [None, {'id': '', 'name': 'X'}, {'id': 3, 'name': 'X'},
               {'id': 'ok', 'name': ''}, {'id': 'ok', 'name': 'X', 'tests': 'not-array'},
               {'id': 'ok', 'name': 'X', 'sources': [None]},
               {'id': 'ok', 'name': 'X', 'scripts': ['']}]
    for index, row in enumerate(invalid):
        root = tmp_path / str(index)
        root.mkdir()
        proc, plan = run_plan(root, {'suites': [row]})
        assert proc.returncode != 0
        assert plan is None


def test_multiple_lanes_keep_stable_ids_and_bounded_slots(tmp_path):
    rows = [{'id': 'a', 'name': 'Alpha', 'area': 'Security'},
            {'id': 'b', 'name': 'Beta', 'area': 'Models'},
            {'id': 'c', 'name': 'Gamma', 'area': 'Website'}]
    proc, plan = run_plan(tmp_path, {'suites': rows})
    assert proc.returncode == 0, proc.stderr
    assert plan['lane_count'] == 3
    assert sorted(s['suite_id'] for lane in plan['lanes'] for s in lane['suites']) == ['a', 'b', 'c']
    assert all(1 <= lane['parallel_slot'] <= 2 for lane in plan['lanes'])
