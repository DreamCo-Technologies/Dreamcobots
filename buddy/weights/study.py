#!/usr/bin/env python3
"""Study open weights on the user's machine. Do not download or benchmark them from here."""
from __future__ import annotations

import json
import struct
from pathlib import Path

DTYPE_BYTES = {"F32": 4.0, "F16": 2.0, "BF16": 2.0, "F8": 1.0, "I8": 1.0, "U8": 1.0, "I4": 0.5}
# Published sizes. This process has not measured the files.
CATALOG = (
    {"repo": "HuggingFaceTB/SmolLM2-135M-Instruct", "params": 135_000_000, "license": "Apache-2.0", "access": "open_source", "gated": False},
    {"repo": "Qwen/Qwen2.5-0.5B-Instruct", "params": 500_000_000, "license": "Apache-2.0", "access": "open_weights", "gated": False},
    {"repo": "TinyLlama/TinyLlama-1.1B-Chat-v1.0", "params": 1_100_000_000, "license": "Apache-2.0", "access": "open_source", "gated": False},
    {"repo": "openai/whisper-tiny", "params": 39_000_000, "license": "MIT", "access": "open_source", "gated": False},
    {"repo": "hexgrad/Kokoro-82M", "params": 82_000_000, "license": "Apache-2.0", "access": "open_weights", "gated": False},
)


def catalog() -> list[dict]:
    rows = []
    for item in CATALOG:
        fit = {dtype: plan(item["params"], dtype) for dtype in ("I4", "I8", "F16", "F32")}
        best = next(dtype for dtype in ("F16", "I8", "I4", "F32") if fit[dtype]["fits_8gb"])
        rows.append({**item, "fit": fit, "efficient_dtype_for_8gb": best, "downloaded": False, "benchmarked": False, "weights_trained": False})
    return rows


def plan(params: int, dtype: str, memory_gb: float = 8.0) -> dict:
    if dtype not in DTYPE_BYTES or params < 1:
        raise ValueError("Need a known dtype and a parameter count.")
    file_gb = params * DTYPE_BYTES[dtype] / 1_000_000_000
    run_gb = round(file_gb * 1.3, 3)
    reserve = 2.0 if memory_gb <= 8 else 4.0
    return {"file_gb": round(file_gb, 3), "run_gb": run_gb, "fits_8gb": run_gb <= memory_gb - reserve, "one_model_at_a_time": True}


def read_header(path: Path) -> dict:
    """Read a safetensors header and sum stored bytes. Do not load the tensors."""
    data = Path(path).read_bytes()
    if len(data) < 8:
        raise ValueError("Not a weight file.")
    length = struct.unpack_from("<Q", data, 0)[0]
    header = json.loads(data[8 : 8 + length])
    tensors = []
    total = 0
    for name, meta in header.items():
        if name == "__metadata__" or not isinstance(meta, dict) or "data_offsets" not in meta:
            continue
        start, end = meta["data_offsets"]
        total += end - start
        tensors.append({"name": name, "dtype": meta.get("dtype"), "bytes": end - start})
    return {"tensors": len(tensors), "stored_bytes": total, "loaded_into_a_model": False}


def download(repo: str, allow: bool = False) -> dict:
    known = {item["repo"] for item in CATALOG}
    if repo not in known:
        return {"downloaded": False, "reason": "That repo is not in the open-weight catalog."}
    if not allow:
        return {"downloaded": False, "reason": "On your own computer, pass allow=True. This call does not download."}
    return {"downloaded": False, "reason": "The download connector is ready, and this process still does not fetch weights."}


def benchmark() -> dict:
    return {"benchmarked": False, "weights_trained": False, "reason": "No benchmark command has been run. A catalog row is not a score."}


if __name__ == "__main__":
    rows = catalog()
    assert rows[0]["fit"]["F16"]["fits_8gb"] is True
    assert plan(7_000_000_000, "F16")["fits_8gb"] is False
    assert plan(7_000_000_000, "I4")["fits_8gb"] is True
    assert download(rows[0]["repo"])["downloaded"] is False
    assert benchmark()["benchmarked"] is False
    header = {"weight": {"dtype": "F32", "shape": [4], "data_offsets": [0, 16]}}
    blob = json.dumps(header).encode()
    path = Path("/tmp/buddy-weight-header.safetensors")
    path.write_bytes(struct.pack("<Q", len(blob)) + blob + b"\x00" * 16)
    assert read_header(path)["stored_bytes"] == 16
    print(json.dumps({"models": len(rows), "downloaded": False, "benchmarked": False}))
