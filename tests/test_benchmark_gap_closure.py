import json, subprocess, sys
from pathlib import Path

def test_gap_planner(tmp_path):
    src=tmp_path/'input.json'; out=tmp_path/'out.json'
    src.write_text(json.dumps({'records':[{'division_id':'d1','benchmark_id':'b1','baseline':40,'target':60},{'division_id':'d2','benchmark_id':'b2','baseline':70,'target':60}]}))
    subprocess.run([sys.executable,'tools/benchmark_gap_closure.py',str(src),'--output',str(out)],check=True)
    data=json.loads(out.read_text())
    assert data['records'][0]['status']=='open'
    assert data['records'][0]['gap']==20
    assert data['records'][1]['status']=='closed'
