"""Offline inspection of safetensors headers: shapes and dtypes, never tensor payloads.

Input must be a trusted local file; no network, model execution, or pickle loading.
"""
from __future__ import annotations
import json
import os
import struct
from pathlib import Path

DTYPE_BITS = {"F64":64,"F32":32,"F16":16,"BF16":16,"I64":64,"I32":32,"I16":16,"I8":8,"U8":8,"BOOL":8,"F8_E4M3":8,"F8_E5M2":8}
MAX_HEADER_BYTES = 8 * 1024 * 1024
MAX_TENSORS = 100000

def inspect_safetensors(path: str) -> dict:
    target = Path(path)
    if not target.is_file() or target.is_symlink():
        raise ValueError("regular, non-symlink file required")
    with target.open("rb") as stream:
        length_raw = stream.read(8)
        if len(length_raw) != 8:
            raise ValueError("truncated header")
        length = struct.unpack("<Q", length_raw)[0]
        if length < 2 or length > MAX_HEADER_BYTES:
            raise ValueError("invalid header length")
        raw = stream.read(length)
        if len(raw) != length:
            raise ValueError("truncated header")
    data = json.loads(raw)
    if not isinstance(data, dict) or len(data) > MAX_TENSORS + 1:
        raise ValueError("invalid tensor map")
    count = 0
    params = 0
    by_dtype = {}
    file_bytes = target.stat().st_size
    for name, tensor in data.items():
        if name == "__metadata__":
            continue
        if not isinstance(tensor, dict) or not isinstance(tensor.get("shape"), list):
            raise ValueError("invalid tensor metadata")
        dtype = tensor.get("dtype")
        shape = tensor["shape"]
        offsets = tensor.get("data_offsets")
        if dtype not in DTYPE_BITS or not isinstance(offsets, list) or len(offsets) != 2:
            raise ValueError("unsupported tensor metadata")
        if any(type(d) is not int or d < 0 for d in shape):
            raise ValueError("invalid dimensions")
        start, end = offsets
        if any(type(v) is not int for v in offsets) or not (0 <= start <= end <= file_bytes - 8 - length):
            raise ValueError("invalid data offsets")
        elements = 1
        for dim in shape:
            elements *= dim
            if elements > 10**13:
                raise ValueError("tensor too large")
        expected = (elements * DTYPE_BITS[dtype] + 7) // 8
        if end - start != expected:
            raise ValueError("tensor byte length mismatch")
        count += 1
        params += elements
        by_dtype[dtype] = by_dtype.get(dtype, 0) + elements
    return {"tensor_count": count, "parameter_count": params,
            "parameters_by_dtype": dict(sorted(by_dtype.items())),
            "file_bytes": file_bytes, "inspection_only": True,
            "training_performed": False, "license_verified": False}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    print(json.dumps(inspect_safetensors(args.file), indent=2))
