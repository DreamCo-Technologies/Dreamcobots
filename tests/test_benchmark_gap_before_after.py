import hashlib
import json
from pathlib import Path

import pytest

from tools.benchmark_gap_closure import plan


def case(tmp_path: Path, *, before=40, after=65, target=60, regression='passed', with_before=True):
    source = tmp_path / 'suite.json'
    source.write_text('{"fixture": true}\n')
    result = {'benchmark_id': 'synthetic', 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'status': 'passed', 'regression_status': regression, 'tests_run': 3,
              'tests_failed': 0, 'score': after, 'target': target}
    if with_before:
        result['baseline'] = before
    artifact = tmp_path / 'result.json'
    artifact.write_text(json.dumps(result))
    return {'division_id': 'sandbox', 'benchmark_id': 'synthetic', 'baseline': before,
            'target': target, 'evidence': {'review_status': 'reviewed',
            'reviewer': 'synthetic-test-only', 'source': source.name,
            'artifact': artifact.name,
            'artifact_sha256': hashlib.sha256(artifact.read_bytes()).hexdigest()}}


def test_measured_improvement_closes_without_rewriting_baseline(tmp_path):
    row = plan(case(tmp_path), tmp_path)
    assert (row['status'], row['gap'], row['evidence_verified']) == ('closed', 20, True)


@pytest.mark.parametrize('kwargs', [
    {'after': 59}, {'regression': 'failed'}, {'with_before': False},
])
def test_insufficient_evidence_does_not_close(tmp_path, kwargs):
    assert plan(case(tmp_path, **kwargs), tmp_path)['status'] == 'open'


def test_baseline_mismatch_does_not_close(tmp_path):
    record = case(tmp_path)
    record['baseline'] = 41
    assert plan(record, tmp_path)['status'] == 'open'


def test_legacy_already_passing_receipt_preserved(tmp_path):
    assert plan(case(tmp_path, before=65, after=65, with_before=False), tmp_path)['status'] == 'closed'


def test_tampered_receipt_does_not_close(tmp_path):
    record = case(tmp_path)
    (tmp_path / 'result.json').write_text('{}')
    assert plan(record, tmp_path)['status'] == 'open'


def test_registry_contract_never_claims_mastery(tmp_path):
    record = case(tmp_path)
    record['suite_id'] = 'synthetic'
    assert plan(record, tmp_path, registry_only=True)['status'] == 'blocked'
