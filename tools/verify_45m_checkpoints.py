"""Fail-closed verification for DreamCo's canonical 45,038,208-parameter fleet.

This validates artifact structure and hash-bound training evidence. It does not
claim that a self-authored stamp is independently audited or that a model is
production-ready; independent review remains a release requirement.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import struct
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config" / "masterbot-65-registry.json"
EXPECTED_PARAMETERS = 45_038_208


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def safetensors_parameter_count(path: Path) -> int:
    """Parse the safetensors header and verify tensor byte ranges."""
    size = path.stat().st_size
    if size < 10:
        raise ValueError("model.safetensors is empty or truncated")
    with path.open("rb") as stream:
        raw_len = stream.read(8)
        if len(raw_len) != 8:
            raise ValueError("invalid safetensors header length")
        header_len = struct.unpack("<Q", raw_len)[0]
        if header_len < 2 or header_len > min(size - 8, 100 * 1024 * 1024):
            raise ValueError("invalid safetensors header size")
        header_bytes = stream.read(header_len)
    try:
        header = json.loads(header_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid safetensors JSON header") from exc
    if not isinstance(header, dict):
        raise ValueError("safetensors header must be an object")
    data_size = size - 8 - header_len
    total = 0
    ranges = []
    for name, tensor in header.items():
        if name == "__metadata__":
            continue
        if not isinstance(tensor, dict):
            raise ValueError(f"invalid tensor metadata: {name}")
        shape, offsets, dtype = tensor.get("shape"), tensor.get("data_offsets"), tensor.get("dtype")
        if not isinstance(shape, list) or not shape or any(type(x) is not int or x < 0 for x in shape):
            raise ValueError(f"invalid tensor shape: {name}")
        if not isinstance(offsets, list) or len(offsets) != 2 or any(type(x) is not int for x in offsets):
            raise ValueError(f"invalid tensor offsets: {name}")
        start, end = offsets
        if start < 0 or end <= start or end > data_size:
            raise ValueError(f"invalid tensor byte range: {name}")
        if not isinstance(dtype, str) or not dtype:
            raise ValueError(f"missing tensor dtype: {name}")
        ranges.append((start, end))
        count = math.prod(shape)
        if count <= 0:
            raise ValueError(f"empty tensor: {name}")
        total += count
    if not ranges:
        raise ValueError("safetensors contains no model tensors")
    ranges.sort()
    cursor = 0
    for start, end in ranges:
        if start != cursor:
            raise ValueError("safetensors tensor ranges contain gaps or overlaps")
        cursor = end
    if cursor != data_size:
        raise ValueError("safetensors tensor data is not fully accounted for")
    return total


def validate_division(directory: Path, division_key: str) -> dict[str, Any]:
    checkpoint = directory / "model.safetensors"
    tokenizer = directory / "tokenizer.json"
    stamp = directory / "evidence_stamp.json"
    for path in (checkpoint, tokenizer, stamp):
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f"required non-empty artifact missing: {path.name}")

    parameter_count = safetensors_parameter_count(checkpoint)
    if parameter_count != EXPECTED_PARAMETERS:
        raise ValueError(f"parameter count {parameter_count} != {EXPECTED_PARAMETERS}")

    try:
        tokenizer_data = json.loads(tokenizer.read_text(encoding="utf-8"))
        evidence = json.loads(stamp.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("tokenizer or evidence stamp is not valid UTF-8 JSON") from exc
    if not isinstance(tokenizer_data, dict) or not isinstance(tokenizer_data.get("model"), dict):
        raise ValueError("tokenizer.json is not a trained tokenizer artifact")
    vocab = tokenizer_data["model"].get("vocab")
    if not isinstance(vocab, dict) or len(vocab) < 2:
        raise ValueError("tokenizer model vocabulary is missing or implausibly empty")
    if not isinstance(evidence, dict):
        raise ValueError("evidence_stamp.json must be an object")

    steps = evidence.get("steps_completed")
    if type(steps) is not int or steps < 100:
        raise ValueError("steps_completed must be an integer >= 100")
    if evidence.get("parameter_count") != EXPECTED_PARAMETERS:
        raise ValueError("evidence parameter_count does not match canonical architecture")
    for field, artifact in (("checkpoint_sha256", checkpoint), ("tokenizer_sha256", tokenizer)):
        expected = evidence.get(field)
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise ValueError(f"{field} must be a lowercase SHA-256")
        if sha256(artifact) != expected:
            raise ValueError(f"{field} does not match the artifact")
    for field in ("training_run_id", "dataset_manifest_sha256", "training_config_sha256"):
        value = evidence.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} is required")
    for field in ("dataset_manifest_sha256", "training_config_sha256"):
        if not re.fullmatch(r"[0-9a-f]{64}", evidence[field]):
            raise ValueError(f"{field} must be a lowercase SHA-256")

    losses = evidence.get("loss_history")
    if not isinstance(losses, list) or len(losses) < 2:
        raise ValueError("loss_history must contain at least two observations")
    if any(type(loss) not in (int, float) or not math.isfinite(loss) or loss < 0 for loss in losses):
        raise ValueError("loss_history must contain only finite non-negative numbers")
    if losses[-1] >= losses[0]:
        raise ValueError("loss_history does not show convergence (final loss must be below initial loss)")
    return {
        "division_key": division_key,
        "status": "STRUCTURALLY_VERIFIED_EVIDENCE_REQUIRES_INDEPENDENT_AUDIT",
        "parameter_count": parameter_count,
        "steps_completed": steps,
        "initial_loss": losses[0],
        "final_loss": losses[-1],
        "checkpoint_sha256": sha256(checkpoint),
        "tokenizer_sha256": sha256(tokenizer),
    }


def validate_fleet(registry_path: Path, checkpoint_root: Path) -> dict[str, Any]:
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    bots = registry.get("divisions", [])
    if registry.get("canonical_count") != 65 or len(bots) != 65:
        raise ValueError("canonical registry must contain exactly 65 MasterBots")
    ids = [bot.get("id") for bot in bots]
    names = [bot.get("name") for bot in bots]
    if len(set(ids)) != 65 or len(set(names)) != 65 or any(not isinstance(x, str) or not x for x in names):
        raise ValueError("canonical MasterBot IDs and names must be unique and complete")
    results = []
    for name in names:
        key = slug(name)
        directory = checkpoint_root / f"buddy-{key}-45m"
        try:
            results.append(validate_division(directory, key))
        except (OSError, ValueError, TypeError) as exc:
            results.append({"division_key": key, "status": "BLOCKED", "reason": str(exc)})
    verified = sum(row["status"].startswith("STRUCTURALLY_VERIFIED") for row in results)
    return {
        "schema": "dreamco.verified_45m_checkpoint_audit.v1",
        "canonical_masterbot_count": 65,
        "verified_count": verified,
        "blocked_count": 65 - verified,
        "fleet_status": "VERIFIED_ARTIFACTS_PENDING_INDEPENDENT_AUDIT" if verified == 65 else "BLOCKED",
        "results": results,
        "weights_modified": False,
        "training_performed": False,
        "production_release_performed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--checkpoint-root", type=Path, default=ROOT / "checkpoints")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = validate_fleet(args.registry, args.checkpoint_root)
    rendered = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["fleet_status"] != "BLOCKED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
