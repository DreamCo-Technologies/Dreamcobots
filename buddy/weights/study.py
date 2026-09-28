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
    if dtype not in DTYPE_BYTES or params < 1 or memory_gb < 2:
        raise ValueError("Need a known dtype, a parameter count, and at least 2GB.")
    file_gb = params * DTYPE_BYTES[dtype] / 1_000_000_000
    run_gb = round(file_gb * 1.3, 3)
    reserve = 2.0 if memory_gb <= 8 else 4.0
    fits = run_gb <= memory_gb - reserve
    return {"file_gb": round(file_gb, 3), "run_gb": run_gb, "fits": fits, "fits_8gb": fits if memory_gb == 8 else run_gb <= 6, "one_model_at_a_time": True}


def for_user(memory_gb: float) -> dict:
    """Same catalog for every user. The fit uses that user's memory, not one owner's laptop."""
    rows = []
    for item in CATALOG:
        fit = {dtype: plan(item["params"], dtype, memory_gb)["fits"] for dtype in ("F16", "I8", "I4")}
        best = next(dtype for dtype in ("F16", "I8", "I4") if fit[dtype])
        rows.append({"repo": item["repo"], "efficient_dtype": best, "fits": fit})
    return {"for_every_user": True, "owner_only": False, "memory_gb": memory_gb, "stored_in_repository": False, "models": rows}


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


def download(repo: str, allow: bool = False, folder: Path | None = None) -> dict:
    known = {item["repo"] for item in CATALOG}
    root = Path(__file__).resolve().parents[2]
    if repo not in known:
        return {"downloaded": False, "reason": "That repo is not in the shared open-weight catalog."}
    if folder is not None and root in Path(folder).resolve().parents or Path(folder).resolve() == root:
        return {"downloaded": False, "reason": "A user's weights stay on that user's computer, not in the shared repository."}
    if not allow:
        return {"downloaded": False, "reason": "Each user passes allow=True on their own computer. This call does not download."}
    return {"downloaded": False, "reason": "The connector is ready for any user, and this process still does not fetch weights."}


def benchmark() -> dict:
    return {"benchmarked": False, "weights_trained": False, "reason": "No benchmark command has been run. A catalog row is not a score."}


if __name__ == "__main__":
    rows = catalog()
    assert rows[0]["fit"]["F16"]["fits_8gb"] is True
    assert plan(7_000_000_000, "F16")["fits_8gb"] is False
    assert plan(7_000_000_000, "I4")["fits_8gb"] is True
    assert download(rows[0]["repo"])["downloaded"] is False
    assert download(rows[0]["repo"], folder=Path(__file__).resolve().parents[2] / "weights")["downloaded"] is False
    mine = for_user(8)
    theirs = for_user(32)
    assert mine["owner_only"] is False and mine["for_every_user"] is True
    assert mine["models"][2]["efficient_dtype"] == "F16"
    assert theirs["memory_gb"] == 32 and theirs["stored_in_repository"] is False
    assert benchmark()["benchmarked"] is False
    header = {"weight": {"dtype": "F32", "shape": [4], "data_offsets": [0, 16]}}
    blob = json.dumps(header).encode()
    path = Path("/tmp/buddy-weight-header.safetensors")
    path.write_bytes(struct.pack("<Q", len(blob)) + blob + b"\x00" * 16)
    assert read_header(path)["stored_bytes"] == 16
    print(json.dumps({"models": len(rows), "downloaded": False, "benchmarked": False}))
