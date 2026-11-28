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

def verify_signed_manifest(manifest_path: Path, signature_path: Path, public_key_path: Path,
                           *, verify_dataset_hashes: bool = True) -> dict:
    """Verify manifest signature and paths; optionally hash all dataset contents."""
    try:
        from cryptography.hazmat.primitives.serialization import load_pem_public_key
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except ImportError as exc:
        raise RuntimeError("Install cryptography to verify foundry signatures") from exc
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != SCHEMA:
        raise ValueError(f"manifest schema must be {SCHEMA}")
    signature = base64.b64decode(signature_path.read_text(encoding="ascii").strip(), validate=True)
    key = load_pem_public_key(public_key_path.read_bytes())
    if not isinstance(key, Ed25519PublicKey):
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
        if item.get("category") not in {"study_guides", "verified_trajectories", "general_replay", "verified_preferences", "holdout_benchmarks"}:
            raise ValueError(f"{dataset_id}: unsupported dataset category")
        if item.get("license_tier") not in ALLOWED_TIERS or item.get("commercial_use") is not True:
            raise PermissionError(f"{dataset_id}: commercial training rights not explicitly approved")
        if item.get("policy_decision_id") is None or not str(item["policy_decision_id"]).strip():
            raise PermissionError(f"{dataset_id}: missing policy decision reference")
        if not isinstance(item.get("approved_by"), str) or not item["approved_by"].strip():
            raise PermissionError(f"{dataset_id}: missing policy-owner approval identity")
        p = (root / str(item.get("path", ""))).resolve()
        if p == root or root not in p.parents:
            raise ValueError(f"{dataset_id}: dataset path escapes manifest directory")
        if not p.is_file():
            raise FileNotFoundError(p)
        expected = str(item.get("sha256", "")).lower()
        if len(expected) != 64:
            raise ValueError(f"{dataset_id}: invalid dataset SHA-256")
        item["_resolved_path"] = str(p)
        if verify_dataset_hashes:
            if sha256_file(p) != expected:
                raise ValueError(f"{dataset_id}: dataset SHA-256 mismatch")
            item["_hash_verified"] = True
    manifest["_source_manifest_sha256"] = sha256_file(manifest_path)
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
        if not dataset.get("_hash_verified"):
            if sha256_file(path) != dataset.get("sha256"):
                raise ValueError(f"{dataset['dataset_id']}: dataset SHA-256 mismatch")
            dataset["_hash_verified"] = True
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

def verify_manifest_dataset_hashes(manifest: dict, *, categories: set[str]) -> None:
    """Hash only selected dataset categories, leaving holdout contents untouched."""
    for dataset in manifest["datasets"]:
        if dataset.get("category") not in categories:
            continue
        path = Path(dataset["_resolved_path"])
        if sha256_file(path) != dataset.get("sha256"):
            raise ValueError(f"{dataset['dataset_id']}: dataset SHA-256 mismatch")
        dataset["_hash_verified"] = True

def assert_training_split(rows):
    for row in rows:
        if row.get("_split") != "train":
            raise PermissionError("only deterministic train buckets 00-89 may enter training")

def validate_shard_payload(payload: dict, root: Path, source_manifest_path: Path,
                           *, attach_paths: bool = True) -> dict:
    """Validate signed shard metadata, containment, sequence geometry and bytes."""
    if payload.get("schema") != "dreamco.foundry.token_shards.v1":
        raise ValueError("unsupported token-shard manifest schema")
    sequence_length = payload.get("sequence_length")
    if not isinstance(sequence_length, int) or sequence_length < 8:
        raise ValueError("invalid token-shard sequence_length")
    if payload.get("dtype") != "uint32":
        raise ValueError("token shards must use uint32 storage")
    if payload.get("training_splits") != ["train"] or "holdout" not in payload.get("excluded_splits", []):
        raise PermissionError("token-shard manifest must declare train-only input and holdout exclusion")
    if payload.get("mix_percent") != {"study_guides": 60, "verified_trajectories": 25, "general_replay": 15}:
        raise ValueError("token-shard manifest must declare the approved 60/25/15 curriculum")
    if payload.get("source_manifest_sha256") != sha256_file(source_manifest_path):
        raise PermissionError("token shards do not match the verified source authorization manifest")
    validation_expected = payload.get("validation_splits") == ["validation"]
    if payload.get("validation_splits") not in ([], ["validation"]):
        raise ValueError("validation_splits must be empty or contain only validation")
    root = root.resolve()
    for name in ("train", "validation"):
        entry = payload.get(name)
        if entry is None and name == "validation" and not validation_expected:
            continue
        if not isinstance(entry, dict):
            raise ValueError(f"missing {name} shard manifest entry")
        relative = str(entry.get("file", ""))
        if not relative or Path(relative).is_absolute():
            raise ValueError(f"invalid {name} shard path")
        path = (root / relative).resolve()
        if path == root or root not in path.parents or not path.is_file():
            raise ValueError(f"invalid {name} shard path")
        tokens = entry.get("tokens")
        sequences = entry.get("sequences")
        if not isinstance(tokens, int) or tokens <= 0 or tokens % sequence_length:
            raise ValueError(f"{name} shard token count is not sequence-aligned")
        if sequences != tokens // sequence_length or path.stat().st_size != tokens * 4:
            raise ValueError(f"{name} shard size/sequence metadata mismatch")
        expected_prefix = f"{name}-"
        if not Path(relative).name.startswith(expected_prefix):
            raise ValueError(f"{name} shard filename must start with {expected_prefix}")
        if sha256_file(path) != entry.get("sha256"):
            raise ValueError(f"{name} shard SHA-256 mismatch")
        if attach_paths:
            entry["_resolved_path"] = str(path)
    if validation_expected != (payload.get("validation") is not None):
        raise ValueError("validation split declaration and validation shard entry disagree")
    return payload

def verify_signed_shard_manifest(shard_manifest_path: Path, shard_signature_path: Path,
                                  source_manifest_path: Path, source_signature_path: Path,
                                  public_key_path: Path) -> dict:
    """Verify source authorization, Ed25519 shard signature, and shard bytes."""
    verify_signed_manifest(
        source_manifest_path, source_signature_path, public_key_path,
        verify_dataset_hashes=False
    )
    try:
        from cryptography.hazmat.primitives.serialization import load_pem_public_key
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except ImportError as exc:
        raise RuntimeError("Install cryptography to verify foundry signatures") from exc
    payload = json.loads(shard_manifest_path.read_text(encoding="utf-8"))
    key = load_pem_public_key(public_key_path.read_bytes())
    if not isinstance(key, Ed25519PublicKey):
        raise ValueError("trusted policy key must be Ed25519")
    signature = base64.b64decode(shard_signature_path.read_text(encoding="ascii").strip(), validate=True)
    key.verify(signature, canonical_json(payload))
    return validate_shard_payload(
        payload, shard_manifest_path.parent, source_manifest_path, attach_paths=True
    )

def require_model_authorization(manifest: dict, model_id: str, revision: str) -> dict:
    """Require signed, item-level commercial permission for an exact model revision."""
    if not isinstance(model_id, str) or not model_id.strip():
        raise ValueError("base model ID is required")
    if not isinstance(revision, str) or len(revision) != 40 or any(c not in "0123456789abcdef" for c in revision):
        raise ValueError("base model revision must be a pinned 40-character commit SHA")
    matches = [
        item for item in manifest.get("models", [])
        if item.get("model_id") == model_id and item.get("revision") == revision
    ]
    if len(matches) != 1:
        raise PermissionError("signed policy manifest must authorize this exact base model revision")
    item = matches[0]
    if item.get("license_tier") not in ALLOWED_TIERS or item.get("commercial_use") is not True:
        raise PermissionError("base model is not approved for commercial training")
    if (not str(item.get("policy_decision_id", "")).strip()
            or not str(item.get("license_evidence_id", "")).strip()
            or not str(item.get("approved_by", "")).strip()):
        raise PermissionError("base model requires signed policy decision, owner and license evidence references")
    return item
