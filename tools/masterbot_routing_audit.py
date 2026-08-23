#!/usr/bin/env python3
"""Conservative audit of bot inventory against the 65-MasterBot registry."""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"config/masterbot-65-registry.json"
ROOTS=[ROOT/"App_bots",ROOT/"bots",ROOT/"original-bots",ROOT/"website/data/bot-fleet"]
def load(): return json.loads(REGISTRY.read_text(encoding="utf-8"))
def explicit(path):
    if path.suffix!=".json": return None
    try: d=json.loads(path.read_text(encoding="utf-8"))
    except Exception: return None
    if isinstance(d,dict):
        for k in ("division","masterBot","masterbotDivision","category"):
            if isinstance(d.get(k),str): return d[k]
    return None
def hints(path,names):
    h=re.sub(r"[^a-z0-9]","",str(path.relative_to(ROOT)).lower()); out=[]
    for n in names:
        if re.sub(r"[^a-z0-9]","",n.lower()) in h: out.append(n)
    return out
def main():
    reg=load(); names=[d["name"] for d in reg["divisions"]]; results=[]; seen=set()
    for root in ROOTS:
        if not root.exists(): continue
        for p in root.rglob("*"):
            if not p.is_file() or p.suffix not in {".json",".ts",".tsx",".js",".jsx",".py"}: continue
            rel=str(p.relative_to(ROOT))
            if rel in seen: continue
            seen.add(rel); ex=explicit(p); hs=hints(p,names)
            status="routable" if ex or len(hs)==1 else ("review" if len(hs)>1 else "unclassified")
            results.append({"path":rel,"explicit_division":ex,"path_hints":hs,"status":status})
    summary={"registry_divisions":len(names),"files_scanned":len(results),"routable":sum(x["status"]=="routable" for x in results),"review":sum(x["status"]=="review" for x in results),"unclassified":sum(x["status"]=="unclassified" for x in results),"results":results}
    print(json.dumps(summary,indent=2,sort_keys=True))
if __name__=="__main__": main()
