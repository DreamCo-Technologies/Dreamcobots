"""Cryptographically authorized dataset access and strict holdout isolation.

A boolean field in a data row is never an authorization. The caller must supply
an Ed25519-signed manifest and a trusted public key obtained out-of-band.
"""
from __future__ import annotations
import base64, hashlib, json
from pathlib import Path
from typing import Any, Iterator

SCHEMA = "dreamco.foundry.authorization.v1"
ALLOWED_TIERS = {"PUBLIC_DOMAIN", "PERMISSIVE_COMMERCIAL", "DREAMCO_ORIGINAL"}
ALLOWED_SPLITS = {"train", "validation", "holdout"}

def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def split_bucket(record_id: str) -> int:
    if not isinstance(record_id, str) or not record_id.strip():
        raise ValueError("record id/task_id is required")
    return int(hashlib.sha256(record_id.encode("utf-8")).hexdigest()[:8], 16) % 100

def split_name(record_id: str) -> str:
    n = split_bucket(record_id)
    return "train" if n < 90 else "validation" if n < 95 else "holdout"

def verify_signed_manifest(manifest_path: Path, signature_path: Path, public_key_path: Path) -> dict:
    """Verify Ed25519 signature over canonical manifest JSON, then all data hashes."""
    try:
        from cryptography.hazmat.primitives.serialization import load_pem_public_key
    except ImportError as exc:
        raise RuntimeError("Install cryptography to verify foundry signatures") from exc
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != SCHEMA:
        raise ValueError(f"manifest schema must be {SCHEMA}")
    signature = base64.b64decode(signature_path.read_text(encoding="ascii").strip(), validate=True)
    key = load_pem_public_key(public_key_path.read_bytes())
    if key.__class__.__name__ != "_Ed25519PublicKey":
        raise ValueError("trusted policy key must be Ed25519")
    key.verify(signature, canonical_json(manifest))
    entries = manifest.get("datasets")
    if not isinstance(entries, list) or not entries:
        raise ValueError("signed manifest must contain datasets")
    root = manifest_path.parent.resolve()
    seen = set()
    for item in entries:
        dataset_id = item.get("dataset_id")
        if not isinstance(dataset_id, str) or not dataset_id or dataset_id in seen:
            raise ValueError("dataset_id values must be unique non-empty strings")
        seen.add(dataset_id)
        if item.get("license_tier") not in ALLOWED_TIERS or item.get("commercial_use") is not True:
            raise PermissionError(f"{dataset_id}: commercial training rights not explicitly approved")
        if item.get("policy_decision_id") is None or not str(item["policy_decision_id"]).strip():
            raise PermissionError(f"{dataset_id}: missing policy decision reference")
        p = (root / str(item.get("path", ""))).resolve()
        if p == root or root not in p.parents:
            raise ValueError(f"{dataset_id}: dataset path escapes manifest directory")
        if not p.is_file():
            raise FileNotFoundError(p)
        expected = str(item.get("sha256", "")).lower()
        if len(expected) != 64 or sha256_file(p) != expected:
            raise ValueError(f"{dataset_id}: dataset SHA-256 mismatch")
        item["_resolved_path"] = str(p)
    return manifest

def iter_authorized_records(manifest: dict, *, categories: set[str] | None = None,
                            splits: set[str] | None = None) -> Iterator[dict]:
    """Yield only signature-verified, hash-verified, commercially cleared JSONL rows."""
    requested = splits or {"train"}
    if not requested <= ALLOWED_SPLITS:
        raise ValueError("unknown split requested")
    if "holdout" in requested and requested != {"holdout"}:
        raise PermissionError("holdout cannot be mixed with training or validation reads")
    for dataset in manifest["datasets"]:
        if categories and dataset.get("category") not in categories:
            continue
        path = Path(dataset["_resolved_path"])
        with path.open(encoding="utf-8") as stream:
            for line_no, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                row = json.loads(line)
                rid = str(row.get("task_id") or row.get("id") or "")
                actual = split_name(rid)
                if actual not in requested:
                    continue
                if actual == "holdout" and requested != {"holdout"}:
                    raise PermissionError("holdout record reached a non-evaluation consumer")
                yield {**row, "_split": actual, "_dataset_id": dataset["dataset_id"],
                       "_license_tier": dataset["license_tier"],
                       "_policy_decision_id": dataset["policy_decision_id"]}

def assert_training_split(rows):
    for row in rows:
        if row.get("_split") != "train":
            raise PermissionError("only deterministic train buckets 00-89 may enter training")
