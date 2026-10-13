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


def test_registry_fabricated_measurement_stays_blocked(tmp_path):
    import hashlib
    source=tmp_path/'source.json'
    source.write_text('{"fixture":true}\n')
    artifact=tmp_path/'result.json'
    artifact.write_text(json.dumps({'benchmark_id':'forged','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                                    'status':'passed','regression_status':'passed','tests_run':10,'tests_failed':0,
                                    'score':100,'target':100}))
    src=tmp_path/'registry.json'; out=tmp_path/'out.json'
    src.write_text(json.dumps({'schema':'dreamco.benchmark_suite_gap_contracts.v1','count':1,'entries':[
        {'suite_id':'forged','source':'source.json','division_id':'d1','benchmark_id':'forged',
         'baseline':100,'target':100,'evidence':{'review_status':'reviewed','reviewer':'self-declared',
         'source':'source.json','artifact':'result.json','artifact_sha256':hashlib.sha256(artifact.read_bytes()).hexdigest()}}]}))
    subprocess.run([sys.executable,'tools/benchmark_gap_closure.py',str(src),'--output',str(out)],check=True)
    row=json.loads(out.read_text())['records'][0]
    assert row['status']=='blocked' and row['evidence_verified'] is False
    assert row['suite_id']=='forged' and row['review_status']=='requires_suite_specific_review'
    assert len(row['remediation_design']) == 7


def test_registry_injected_measurements_stay_blocked(tmp_path):
    src=tmp_path/'registry.json'; out=tmp_path/'out.json'
    src.write_text(json.dumps({'schema':'dreamco.benchmark_suite_gap_contracts.v1','count':1,'entries':[
        {'suite_id':'injected','source':'source.json','division_id':'d1','benchmark_id':'b1',
         'baseline':100,'target':100}]}))
    subprocess.run([sys.executable,'tools/benchmark_gap_closure.py',str(src),'--output',str(out)],check=True)
    row=json.loads(out.read_text())['records'][0]
    assert row['status']=='blocked' and row['evidence_verified'] is False
    assert row['suite_id']=='injected' and row['source']=='source.json'
