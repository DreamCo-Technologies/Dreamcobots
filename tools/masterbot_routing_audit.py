#!/usr/bin/env python3
"""Report bot-to-MasterBot routing candidates without moving or deleting files."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
EXT=json.loads((ROOT/'config/masterbot-20-extension.json').read_text())
NAMES={x['name'].lower():x['name'] for x in EXT['new_masterbots']}
ROOTS=[ROOT/'App_bots',ROOT/'bots',ROOT/'original-bots',ROOT/'website'/'data'/'bot-fleet']

def main():
    rows=[]
    for base in ROOTS:
        if not base.exists(): continue
        for p in base.rglob('*'):
            if not p.is_file(): continue
            rel=str(p.relative_to(ROOT)).lower()
            compact=re.sub(r'[^a-z0-9]','',rel)
            hits=[v for k,v in NAMES.items() if re.sub(r'[^a-z0-9]','',k) in compact]
            rows.append({'path':str(p.relative_to(ROOT)),'candidates':hits,'status':'routable' if len(hits)==1 else ('review' if hits else 'unclassified')})
    print(json.dumps({'masterbot_extension':20,'files_scanned':len(rows),'routable':sum(x['status']=='routable' for x in rows),'review':sum(x['status']=='review' for x in rows),'unclassified':sum(x['status']=='unclassified' for x in rows),'policy':'review evidence before changing primary ownership','results':rows},indent=2))

if __name__=='__main__': main()
