#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--queue',required=True); ap.add_argument('--curriculum',required=True); ap.add_argument('--out',required=True); a=ap.parse_args()
    q=json.loads(Path(a.queue).read_text()).get('queue',[])
    c=json.loads(Path(a.curriculum).read_text())
    bots={str(b.get('division')):b for b in c.get('bots',[])}
    manifest=[]
    for item in q:
        division=str(item.get('division'))
        bot=bots.get(division)
        if not bot:
            manifest.append({**item,'execution_status':'blocked','reason':'division not present in sandbox curriculum'})
            continue
        action=item.get('action')
        if action=='TRAIN_TARGETED': mode='TARGETED_GAP_TRAINING'
        elif action=='SANDBOX_VALIDATE': mode='SANDBOX_VALIDATION'
        elif action=='REGRESSION_RETEST': mode='REGRESSION_RETEST'
        else: mode='BASELINE_MEASUREMENT'
        manifest.append({**item,'execution_status':'ready','mode':mode,'division_source':bot.get('source'),'curriculum_contract':{'requires_runtime_evidence':True,'requires_all_applicable_tests_pass':True,'requires_efficiency_baseline':True}})
    Path(a.out).write_text(json.dumps({'schema':'dreamco.training_execution_manifest.v1','items':manifest,'source_truth':'existing bot sandbox curriculum','no_auto_mastery':True},indent=2)+'\n')
    print(json.dumps({'items':len(manifest),'ready':sum(x['execution_status']=='ready' for x in manifest),'blocked':sum(x['execution_status']=='blocked' for x in manifest)},indent=2))
if __name__=='__main__': main()
