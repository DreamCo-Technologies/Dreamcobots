"""Regression checks for generated code and factory evidence; no live providers."""
import copy
import importlib
import json
from pathlib import Path
import subprocess
import sys
from tools import compile_md_bots as compiler
from tools import fleet_daily_factory as factory


def test_committed_modules_have_canonical_shared_runtime():
    assert (compiler.OUT_DIR / 'base.py').read_text() == compiler.BASE_MODULE
    for name in ('3d_asset_mgr', '5s_audit_tool'):
        result = importlib.import_module('runtime.compiled_bots.' + name).create().run({'objective': 'offline smoke'})
        assert result['status'] == 'success'
        assert result['data']['mode'] == 'sandbox'
        assert result['data']['live_actions'] == []
        assert result['metrics']['live_writes'] == 0


def test_compilation_is_not_execution_evidence(tmp_path, monkeypatch):
    bots = tmp_path / 'bots'
    bots.mkdir()
    (bots / 'sample.md').write_text('# Sample\n## Capabilities\n- summarize\n')
    monkeypatch.setattr(compiler, 'ROOT', tmp_path)
    monkeypatch.setattr(compiler, 'BOTS_DIR', bots)
    monkeypatch.setattr(compiler, 'OUT_DIR', tmp_path / 'runtime/compiled_bots')
    monkeypatch.setattr(sys, 'argv', ['compile_md_bots.py'])
    assert compiler.main() == 0
    rows = json.loads((compiler.OUT_DIR / 'registry.json').read_text())['bots']
    assert rows[0]['status'] == 'generated_unverified'
    assert rows[0]['evidence_state'] == 'not_tested'


def test_factory_rejects_unsupported_smoke_claims(tmp_path):
    request = json.loads((factory.ROOT / 'config/bots/daily-build-request.json').read_text())
    plan = factory.plan({**request, 'selection': 'explicit', 'bot_ids': ['analytics-hub']})
    report = factory.build_batch(plan, 0, tmp_path)
    assert factory.reduce_results(plan, [report])['all_requested_built']
    for key, value in [('generic_smoke', None), ('fixture_smoke', {'passed': False}), ('generic_smoke', {'passed': 'true'})]:
        bad = copy.deepcopy(report)
        bad['results'][0][key] = value
        import pytest
        with pytest.raises(ValueError):
            factory.reduce_results(plan, [bad])
    bad = copy.deepcopy(report)
    bad['counts'] = {'shared_engine_bundle_tested': 999}
    import pytest
    with pytest.raises(ValueError):
        factory.reduce_results(plan, [bad])


def test_daily_scan_compiles_before_scanning():
    text = (compiler.ROOT / '.github/workflows/daily-bot-study-scan.yml').read_text()
    assert text.index('tools/compile_md_bots.py') < text.index('tools/daily_bot_study_scan.py')
