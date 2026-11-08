"""Verify independently signed release attestations with Ed25519 (cryptography package).

Only public verification keys live in CI; signing keys remain with independent reviewers.
"""
import base64
import json
from datetime import datetime, timezone
from pathlib import Path

def canonical_bytes(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def verify_attestation(envelope, public_keys, *, now=None):
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        from cryptography.exceptions import InvalidSignature
    except ImportError as exc:
        raise RuntimeError("Install cryptography to validate release evidence") from exc
    try:
        payload=envelope["payload"]
        key_id=envelope["key_id"]
        if not isinstance(key_id,str) or key_id not in public_keys:
            return False
        if payload["schema"]!="dreamco.signed_release_evidence.v1":
            return False
        issued=datetime.fromisoformat(payload["issued_at"].replace("Z","+00:00"))
        expires=datetime.fromisoformat(payload["expires_at"].replace("Z","+00:00"))
        now=now or datetime.now(timezone.utc)
        if issued.tzinfo is None or expires.tzinfo is None or not issued<=now<expires:
            return False
        if not isinstance(payload["goal_id"],str) or not payload["goal_id"]:
            return False
        if not isinstance(payload["commit_sha"],str) or len(payload["commit_sha"])!=40:
            return False
        if not isinstance(payload["checks"],dict):
            return False
        signature=base64.b64decode(envelope["signature"],validate=True)
        key=Ed25519PublicKey.from_public_bytes(base64.b64decode(public_keys[key_id],validate=True))
        key.verify(signature,canonical_bytes(payload))
        return True
    except (KeyError,TypeError,ValueError,InvalidSignature):
        return False

def verified_goal_checks(envelopes,public_keys,commit_sha):
    verified={}
    for envelope in envelopes:
        if not verify_attestation(envelope,public_keys):
            continue
        payload=envelope["payload"]
        if payload["commit_sha"]!=commit_sha:
            continue
        # Merge only signed true checks; unsigned user-provided claims never qualify.
        row=verified.setdefault(payload["goal_id"],{})
        for name,value in payload["checks"].items():
            if value is True:
                row[name]=True
    return {"goals":verified}
