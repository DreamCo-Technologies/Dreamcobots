"""Create a customer/bot curriculum from capability gaps without provider lock-in."""
from __future__ import annotations
import json, os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'config/buddy-bot-bootcamp-engine-v1.json'
OUT=ROOT/'artifacts'/'buddy-bootcamp'

def main():
    cfg=json.loads(CONFIG.read_text())
    goals=[x.strip() for x in os.getenv('BUDDY_BOOTCAMP_GOALS','software engineering,debugging,web research,AI agents').split(',') if x.strip()]
    budget=float(os.getenv('BUDDY_BOOTCAMP_COMPUTE_BUDGET','1.0'))
    curriculum={
      'schema':cfg['schema'],
      'goals':goals,
      'compute_budget':budget,
      'stages':cfg['pipeline'],
      'policies':cfg['training_policy'],
      'mastery':cfg['mastery'],
      'artifacts':cfg['artifacts'],
      'provider_lock_in':False,
      'next_action':'run_capability_gap_scan_then_rank_sources_and_generate_original_training_assets'
    }
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'latest-curriculum.json').write_text(json.dumps(curriculum,indent=2)+'\n')
    print(json.dumps(curriculum,indent=2))
if __name__=='__main__': main()
