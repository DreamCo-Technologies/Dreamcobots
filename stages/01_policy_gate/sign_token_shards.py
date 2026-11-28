"""Sign packed token-shard manifests after verifying their signed source datasets."""
from __future__ import annotations
import argparse, base64, json, importlib
from pathlib import Path
g=importlib.import_module("stages.05_model_foundry.guardrails")
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--shard-manifest",type=Path,required=True)
    p.add_argument("--source-manifest",type=Path,required=True)
    p.add_argument("--source-signature",type=Path,required=True)
    p.add_argument("--public-key",type=Path,required=True)
    p.add_argument("--private-key",type=Path,required=True)
    p.add_argument("--signature-output",type=Path,required=True)
    a=p.parse_args()
    g.verify_signed_manifest(a.source_manifest,a.source_signature,a.public_key)
    data=json.loads(a.shard_manifest.read_text(encoding="utf-8"))
    if data.get("schema")!="dreamco.foundry.token_shards.v1": raise ValueError("unsupported token-shard manifest")
    if data.get("source_manifest_sha256")!=g.sha256_file(a.source_manifest): raise PermissionError("source manifest digest mismatch")
    if data.get("training_splits")!=["train"] or "holdout" not in data.get("excluded_splits",[]): raise PermissionError("shards must be train-only and exclude holdout")
    root=a.shard_manifest.parent.resolve()
    for name in ("train","validation"):
        entry=data.get(name)
        if entry is None and name=="validation": continue
        if not isinstance(entry,dict): raise ValueError(f"missing {name} shard entry")
        path=(root/str(entry.get("file",""))).resolve()
        if path==root or root not in path.parents or not path.is_file(): raise ValueError(f"invalid {name} shard path")
        if g.sha256_file(path)!=entry.get("sha256"): raise ValueError(f"{name} shard hash mismatch")
    try:
        from cryptography.hazmat.primitives.serialization import load_pem_private_key
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    except ImportError as exc: raise RuntimeError("Install cryptography to sign foundry shards") from exc
    key=load_pem_private_key(a.private_key.read_bytes(),password=None)
    if not isinstance(key,Ed25519PrivateKey): raise ValueError("policy signing key must be Ed25519")
    signature=key.sign(g.canonical_json(data))
    a.signature_output.parent.mkdir(parents=True,exist_ok=True)
    a.signature_output.write_text(base64.b64encode(signature).decode("ascii")+"\n",encoding="ascii")
    print(json.dumps({"signed":True,"train_tokens":data["train"]["tokens"],"holdout_included":False},sort_keys=True))
if __name__=="__main__": main()
