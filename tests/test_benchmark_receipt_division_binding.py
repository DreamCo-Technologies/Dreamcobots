"""Prevent reuse of a passing benchmark receipt for a different division."""
import hashlib
import json

from tools.benchmark_gap_closure import plan


def fixture(tmp_path, *, receipt_division='alpha', record_division='alpha'):
    source = tmp_path / 'suite.json'
    source.write_text('{"fixture":true}\n')
    payload = {'division_id': receipt_division, 'benchmark_id': 'shared',
               'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
               'status': 'passed', 'regression_status': 'passed',
               'tests_run': 2, 'tests_failed': 0, 'score': 80, 'target': 70,
               'baseline': 60}
    artifact = tmp_path / 'result.json'
    artifact.write_text(json.dumps(payload))
    return {'division_id': record_division, 'benchmark_id': 'shared',
            'baseline': 60, 'target': 70,
            'evidence': {'review_status': 'reviewed', 'reviewer': 'fixture-only',
                         'source': source.name, 'artifact': artifact.name,
                         'artifact_sha256': hashlib.sha256(artifact.read_bytes()).hexdigest()}}


def test_same_division_receipt_can_close(tmp_path):
    assert plan(fixture(tmp_path), tmp_path)['status'] == 'closed'


def test_cross_division_receipt_cannot_close(tmp_path):
    assert plan(fixture(tmp_path, record_division='beta'), tmp_path)['status'] == 'open'


def test_receipt_without_division_cannot_close(tmp_path):
    record = fixture(tmp_path)
    artifact = tmp_path / 'result.json'
    payload = json.loads(artifact.read_text())
    payload.pop('division_id')
    artifact.write_text(json.dumps(payload))
    record['evidence']['artifact_sha256'] = hashlib.sha256(artifact.read_bytes()).hexdigest()
    assert plan(record, tmp_path)['status'] == 'open'
