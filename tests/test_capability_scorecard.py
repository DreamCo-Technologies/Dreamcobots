import json, subprocess, sys

def test_scorecard(tmp_path):
    src=tmp_path/'input.json'; out=tmp_path/'out.json'
    src.write_text(json.dumps({k:100 for k in ['capability_coverage','benchmark_mastery','study_plan_completion','training_execution','reliability','regression_control','evidence_quality']}))
    subprocess.run([sys.executable,'tools/capability_scorecard.py',str(src),'--output',str(out)],check=True)
    d=json.loads(out.read_text()); assert d['overall_score']==100

def test_scorecard_identifies_gaps(tmp_path):
    src=tmp_path/'input.json'; out=tmp_path/'out.json'
    src.write_text(json.dumps({'capability_coverage':100,'benchmark_mastery':40,'study_plan_completion':80,'training_execution':70,'reliability':90,'regression_control':100,'evidence_quality':50}))
    subprocess.run([sys.executable,'tools/capability_scorecard.py',str(src),'--output',str(out)],check=True)
    d=json.loads(out.read_text()); assert d['top_gaps'][0][0]=='benchmark_mastery'
