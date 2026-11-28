"""Policy-owner signer for commercial-training authorization manifests.

This command is intentionally separate from cataloging and dataset generation.
It signs only after every source row passes the existing policy gate or has an
explicit DreamCo-original owner attestation. Keep private keys off GitHub.
"""
from __future__ import annotations
import argparse, base64, hashlib, json
from pathlib import Path
from .policy_gate import load_registry, evaluate_source
import importlib
_guard=importlib.import_module("stages.05_model_foundry.guardrails")
canonical_json=_guard.canonical_json
sha256_file=_guard.sha256_file

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",type=Path,required=True)
    ap.add_argument("--registry",type=Path,required=True)
    ap.add_argument("--private-key",type=Path,required=True)
    ap.add_argument("--signature-output",type=Path,required=True)
    ap.add_argument("--approve-commercial-training",action="store_true")
    ap.add_argument("--approved-by",required=True)
    ap.add_argument("--policy-decision-id",required=True)
    a=ap.parse_args()
    if not a.approve_commercial_training:
        raise PermissionError("explicit --approve-commercial-training is required")
    data=json.loads(a.manifest.read_text(encoding="utf-8"))
    if data.get("schema")!="dreamco.foundry.authorization.v1" or not data.get("datasets"):
        raise ValueError("unsupported or empty foundry authorization manifest")
    registry=load_registry(a.registry)
    for item in data["datasets"]:
        if item.get("license_tier") not in {"PUBLIC_DOMAIN","PERMISSIVE_COMMERCIAL","DREAMCO_ORIGINAL"}:
            raise PermissionError("only commercial-use tiers may be signed")
        item["policy_decision_id"]=a.policy_decision_id
        item["approved_by"]=a.approved_by
        if item["license_tier"]=="DREAMCO_ORIGINAL":
            evidence=Path(item.get("owner_attestation_path",""))
            if not evidence.is_file() or sha256_file(evidence)!=item.get("owner_attestation_sha256"):
                raise PermissionError("DreamCo-original records require matching owner attestation evidence")
        else:
            sources=item.get("source_evidence")
            if not isinstance(sources,list) or not sources:
                raise PermissionError("third-party datasets require item-level source_evidence")
            for source in sources:
                result=evaluate_source(source,registry,purpose="commercial_training")
                if not result["allowed"] or result.get("permission_tier")!=item["license_tier"]:
                    raise PermissionError(f"policy gate rejected source: {result['reason']}")
    try:
        from cryptography.hazmat.primitives.serialization import load_pem_private_key
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    except ImportError as exc:
        raise RuntimeError("Install cryptography to sign foundry manifests") from exc
    key=load_pem_private_key(a.private_key.read_bytes(),password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise ValueError("policy signing key must be Ed25519")
    signature=key.sign(canonical_json(data))
    a.signature_output.parent.mkdir(parents=True,exist_ok=True)
    a.signature_output.write_text(base64.b64encode(signature).decode("ascii")+"\n",encoding="ascii")
    a.manifest.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"signed":True,"dataset_count":len(data["datasets"]),
      "approved_by":a.approved_by,"policy_decision_id":a.policy_decision_id,
      "manifest_sha256":hashlib.sha256(canonical_json(data)).hexdigest()},sort_keys=True))
if __name__=="__main__": main()
