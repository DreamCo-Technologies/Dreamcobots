#!/usr/bin/env python3
"""Losslessly compact JSON in the deployable website after canonical checks.

This is a packaging step. Source generators keep their original formatting.
No records or assets are removed and all values must round-trip unchanged.
"""
import json
from pathlib import Path


def compact(path):
    original = path.read_text(encoding="utf-8")
    data = json.loads(original)
    packed = json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n"
    if json.loads(packed) != data:
        raise ValueError("JSON round-trip changed data: " + str(path))
    saved = len(original.encode()) - len(packed.encode())
    if saved > 0:
        path.write_text(packed, encoding="utf-8")
    return max(0, saved)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1] / "website"
    saved = sum(compact(path) for path in root.rglob("*.json"))
    print(f"Static packaging: removed {saved:,} bytes of JSON whitespace; all values preserved.")
