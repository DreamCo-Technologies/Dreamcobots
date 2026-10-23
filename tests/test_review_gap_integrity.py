import copy
import hashlib
import json
from tools.benchmark_gap_closure import plan
from tools import plan_parallel_benchmark_gaps as planner
from benchmarks.buddy_benchmark_runner import evaluate_task
from tools.benchmark_suite_contracts import build


def test_every_canonical_suite_retains_unknown_state_and_reviewed_contract():
    result = build()
    # Keep the established suites and include the newly integrated evaluation suites.
    assert result['count'] == 205
    assert len({(r['source'], r['source_array'], r['suite_id']) for r in result['entries']}) == result['count']
    assert any(r['suite_id'] == 'human-reviewed-evaluation' for r in result['entries'])
    assert all(r['gap_state'] == 'unknown' and r['production_ready'] is False for r in result['entries'])
    assert all(r['review']['status'] == 'requires_suite_specific_review' and r['review']['reviewer'] is None
               and 'passing_affected_regressions' in r['required'] for r in result['entries'])


def test_declared_or_overridden_scores_do_not_establish_mastery():
    for score in (None, 1.0):
        result = evaluate_task({'task_id': 'claim', 'baseline_score': 1.0}, score)
        assert result.status == 'unmeasured'
        assert not result.passed
        assert result.evidence == []


def test_scores_alone_cannot_close_a_gap():
    assert plan({'division_id': 'd', 'benchmark_id': 'b', 'baseline': 100, 'target': 60})['status'] != 'closed'


def test_invalid_measurements_fail_closed():
    for value in (True, '100', float('nan'), float('inf'), None):
        assert plan({'division_id': 'd', 'benchmark_id': 'b', 'baseline': value, 'target': 60})['status'] == 'blocked'


def test_closure_requires_source_matched_passing_artifacts(tmp_path):
    source = tmp_path / 'source.txt'
    source.write_text('canonical input')
    artifact = tmp_path / 'result.json'
    artifact.write_text(json.dumps({'benchmark_id': 'b', 'status': 'passed', 'score': 80, 'target': 60,
                                    'regression_status': 'passed', 'tests_run': 2, 'tests_failed': 0,
                                    'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest()}))
    row = {'division_id': 'd', 'benchmark_id': 'b', 'baseline': 80, 'target': 60,
           'evidence': {'review_status': 'reviewed', 'reviewer': 'test-reviewer',
                        'source': 'source.txt', 'artifact': 'result.json',
                        'artifact_sha256': hashlib.sha256(artifact.read_bytes()).hexdigest()}}
    assert plan(row, root=tmp_path)['status'] == 'closed'
    for change in ({'artifact_sha256': 'bad'}, {'reviewer': ''}, {'source': '../escape'}, {'review_status': 'pending'}):
        bad = copy.deepcopy(row)
        bad['evidence'].update(change)
        assert plan(bad, root=tmp_path)['status'] != 'closed'
    source.write_text('changed source')
    assert plan(row, root=tmp_path)['status'] != 'closed'


def test_all_registered_suites_keep_contracts_when_slots_are_limited(tmp_path, monkeypatch):
    program = json.loads(planner.PROGRAM.read_text())
    program['parallel_builder_team']['maximum_parallel_lanes'] = 2
    path = tmp_path / 'program.json'
    path.write_text(json.dumps(program))
    monkeypatch.setattr(planner, 'PROGRAM', path)
    monkeypatch.setattr(planner, 'OUT', tmp_path / 'plan.json')
    planner.main()
    out = json.loads(planner.OUT.read_text())
    rows = [s for lane in out['lanes'] for s in lane['suites']]
    expected = json.loads(planner.SUITES.read_text())['suites']
    assert {s['suite_id'] for s in rows} == {s['id'] for s in expected}
    assert all(s['gap_closure_contract']['review']['status'] == 'requires_suite_specific_review'
               and s['gap_closure_contract']['review']['reviewer'] is None for s in rows)
    assert all(s['gap_state'] == 'unknown' for s in rows)
    assert all(1 <= lane['parallel_slot'] <= 2 for lane in out['lanes'])
