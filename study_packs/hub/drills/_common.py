"""Shared helpers for the HF Hub Day-1 drills (metadata/config only, never weights).

Exit-code convention used by every drill:
  0  PASS        - drill ran and every check held
  1  CHECK_FAIL  - drill ran but a verification/finding failed (details printed)
  2  HUB_ERROR   - network / Hub unreachable / unexpected HTTP error
  3  USAGE       - bad arguments or inventory config missing
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

EXIT_PASS, EXIT_CHECK_FAIL, EXIT_HUB_ERROR, EXIT_USAGE = 0, 1, 2, 3

REPO_ROOT = Path(__file__).resolve().parents[3]
STUDY_CFG = REPO_ROOT / "config" / "huggingface-two-week-study.json"
MAP_CFG = REPO_ROOT / "config" / "hf-capability-download-map.json"
PACKS_CFG = REPO_ROOT / "config" / "huggingface-capability-packs.json"

# File extensions that indicate model weights. Drills must never fetch these.
WEIGHT_EXTS = (".safetensors", ".bin", ".pt", ".pth", ".ckpt", ".h5", ".msgpack",
               ".onnx", ".gguf", ".ot", ".tflite", ".mlmodel", ".pb", ".npz")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def inventory() -> dict:
    """Return {'models': {repo_id: [sources]}, 'datasets': {repo_id: [sources]}} from the repo configs."""
    models: dict[str, list[str]] = {}
    datasets: dict[str, list[str]] = {}
    study = _load(STUDY_CFG)
    for rid in study.get("student_shortlist", []):
        models.setdefault(rid, []).append("config/huggingface-two-week-study.json:student_shortlist")
    mapping = _load(MAP_CFG)
    for pack, ids in mapping.get("seed_models", {}).items():
        for rid in ids:
            models.setdefault(rid, []).append(f"config/hf-capability-download-map.json:seed_models.{pack}")
    for pack, ids in mapping.get("seed_datasets", {}).items():
        for rid in ids:
            datasets.setdefault(rid, []).append(f"config/hf-capability-download-map.json:seed_datasets.{pack}")
    return {"models": models, "datasets": datasets}


def token_present() -> bool:
    try:
        from huggingface_hub import get_token
        return bool(get_token())
    except Exception:
        return bool(os.environ.get("HF_TOKEN"))


def banner(name: str) -> None:
    import huggingface_hub
    print(f"== {name} | huggingface_hub {huggingface_hub.__version__} | "
          f"token_present={token_present()} | HF_TOKEN env set={'HF_TOKEN' in os.environ}")


def is_weight(path: str) -> bool:
    return path.lower().endswith(WEIGHT_EXTS)


def hub_error_exit(exc: BaseException) -> int:
    print(f"HUB_ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
    return EXIT_HUB_ERROR
