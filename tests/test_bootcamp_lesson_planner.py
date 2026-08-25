import json, subprocess, sys

def test_planner_blocks_missing_provenance(tmp_path):
 src=tmp_path/'in.json'; out=tmp_path/'out.json'
 src.write_text(json.dumps({'units':[{'capability_id':'c1','objective':'learn','benchmark':'b1'},{'capability_id':'c2','objective':'learn','benchmark':'b2','provenance':'licensed'}]}))
 subprocess.run([sys.executable,'tools/bootcamp_lesson_planner.py',str(src),'--output',str(out)],check=True)
 d=json.loads(out.read_text())
 assert d['units'][0]['status']=='blocked'
 assert d['units'][1]['status']=='ready'
