"""Offline, deterministic retrieval evaluation for Buddy WikiSearch."""
import hashlib
import json

def evaluate(cases, predictions, k=10):
    if not isinstance(k,int) or not 1 <= k <= 100: raise ValueError("Invalid k")
    if not cases: raise ValueError("No cases")
    seen=set(); questions={}; holdouts=[]
    for c in cases:
        cid=c["id"]; split=c["split"]; q=" ".join(c["question"].casefold().split())
        if cid in seen or (q in questions and questions[q] != split): raise ValueError("Duplicate ID or split leakage")
        seen.add(cid); questions[q]=split
        if not c.get("rights_verified") or not c.get("privacy_safe"): raise ValueError("Rights/privacy not verified")
        if split=="holdout": holdouts.append(c)
    if not holdouts: raise ValueError("Independent holdouts required")
    expected_ids={c["id"] for c in holdouts}
    if set(predictions)!=expected_ids: raise ValueError("Predictions must match holdouts exactly")
    hits=0; rr=0.0
    for c in holdouts:
        actual=predictions[c["id"]]
        if len(actual)!=len(set(actual)): raise ValueError("Duplicate result")
        relevant=set(c["expected_external_ids"])
        rank=next((i for i,x in enumerate(actual[:k],1) if x in relevant),None)
        hits+=int(rank is not None)
        rr+=1/rank if rank else 0
    payload={"k":k,"holdouts":len(holdouts),"recall_at_k":hits/len(holdouts),"mrr_at_k":rr/len(holdouts),"evaluated":True}
    payload["receipt_sha256"]=hashlib.sha256(json.dumps({"cases":cases,"predictions":predictions,"metrics":payload},sort_keys=True).encode()).hexdigest()
    return payload
