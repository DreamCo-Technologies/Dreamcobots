import json, subprocess, sys
from pathlib import Path

def test_gap_planner(tmp_path):
    src=tmp_path/'input.json'; out=tmp_path/'out.json'
    src.write_text(json.dumps({'records':[{'division_id':'d1','benchmark_id':'b1','baseline':40,'target':60},{'division_id':'d2','benchmark_id':'b2','baseline':70,'target':60}]}))
    subprocess.run([sys.executable,'tools/benchmark_gap_closure.py',str(src),'--output',str(out)],check=True)
    data=json.loads(out.read_text())
    assert data['records'][0]['status']=='open'
    assert data['records'][0]['gap']==20
    assert data['records'][1]['status']=='open'
    assert data['records'][1]['evidence_verified'] is False


def test_registry_reports_all_suites_blocked_without_fabricated_evidence(tmp_path):
    src=tmp_path/'registry.json'; out=tmp_path/'out.json'
    src.write_text(json.dumps({'schema':'dreamco.benchmark_suite_gap_contracts.v1','count':2,'entries':[
        {'suite_id':'hallucination','source':'config/buddy/trust-benchmark-suite.json'},
        {'suite_id':'deception','source':'config/buddy/trust-benchmark-suite.json'}]}))
    subprocess.run([sys.executable,'tools/benchmark_gap_closure.py',str(src),'--output',str(out)],check=True)
    rows=json.loads(out.read_text())['records']
    assert [r['suite_id'] for r in rows] == ['hallucination','deception']
    assert all(r['status']=='blocked' and r['evidence_verified'] is False for r in rows)
    assert all(r['review_status']=='requires_suite_specific_review' for r in rows)


def test_registry_count_mismatch_fails_closed(tmp_path):
    src=tmp_path/'registry.json'; out=tmp_path/'out.json'
    src.write_text(json.dumps({'schema':'dreamco.benchmark_suite_gap_contracts.v1','count':205,'entries':[
        {'suite_id':'hallucination'}]}))
    proc=subprocess.run([sys.executable,'tools/benchmark_gap_closure.py',str(src),'--output',str(out)],capture_output=True,text=True)
    assert proc.returncode != 0
    assert not out.exists()
