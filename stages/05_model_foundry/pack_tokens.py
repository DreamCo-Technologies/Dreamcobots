"""Pack signed training records into fixed-length uint32 binary shards."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from .guardrails import iter_authorized_records, verify_signed_manifest, assert_training_split

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",type=Path,required=True); ap.add_argument("--signature",type=Path,required=True)
    ap.add_argument("--public-key",type=Path,required=True); ap.add_argument("--tokenizer",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True); ap.add_argument("--sequence-length",type=int,default=1024)
    a=ap.parse_args()
    if a.sequence_length<8: raise ValueError("sequence length must be >= 8")
    import numpy as np
    from transformers import AutoTokenizer
    manifest=verify_signed_manifest(a.manifest,a.signature,a.public_key)
    tok=AutoTokenizer.from_pretrained(a.tokenizer)
    if tok.eos_token_id is None: raise ValueError("tokenizer must define EOS")
    a.output.mkdir(parents=True,exist_ok=True)
    # Explicit curriculum mix: 60/25/15. All three sources must exist and be signed.
    weights={"study_guides":60,"verified_trajectories":25,"general_replay":15}
    rows={k:list(iter_authorized_records(manifest,categories={k},splits={"train"})) for k in weights}
    if any(not rows[k] for k in weights): raise ValueError("all three signed training categories are required for the 60/25/15 mix")
    tokens=[]
    for category,weight in weights.items():
        pool=[]
        for row in rows[category]:
            assert_training_split([row])
            text=row.get("content") or row.get("text") or row.get("title","")
            if row.get("messages"):
                text="\n".join(f"<|{m.get('role','user')}|> {m.get('content','')}" for m in row["messages"])
            ids=tok.encode(str(text),add_special_tokens=False)
            pool.extend(ids+[tok.eos_token_id])
        # Deterministic category weighting, no validation/holdout records.
        repeats=max(1,weight//5)
        tokens.extend(pool*repeats)
    usable=(len(tokens)//a.sequence_length)*a.sequence_length
    if usable==0: raise ValueError("not enough authorized tokens to form one sequence")
    arr=np.asarray(tokens[:usable],dtype=np.uint32)
    path=a.output/"train-00000.bin"; arr.tofile(path)
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    report={"schema":"dreamco.foundry.token_shards.v1","sequence_length":a.sequence_length,
      "dtype":"uint32","training_splits":["train"],"excluded_splits":["validation","holdout"],
      "mix_percent":weights,"tokens":int(usable),"sequences":int(usable//a.sequence_length),
      "shards":[{"file":path.name,"sha256":digest,"tokens":int(usable)}],
      "source_manifest_sha256":hashlib.sha256(a.manifest.read_bytes()).hexdigest()}
    (a.output/"manifest.json").write_text(json.dumps(report,indent=2)+"\n")
if __name__=="__main__": main()
