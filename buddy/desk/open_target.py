#!/usr/bin/env python3
"""Open a public file, or send the user to try, test, or look it up.

Weight files are not loaded here.
"""
from __future__ import annotations

import json
from pathlib import Path

WEIGHTS = {".safetensors", ".bin", ".gguf", ".pt", ".pth", ".onnx", ".ckpt", ".msgpack"}
MODES = {"open", "try", "test", "lookup"}


def _clean(kind: str, name: str, path: str) -> tuple[str, str, str]:
    kind = (kind or "").strip().lower()
    name = (name or "").strip().strip("/")
    path = (path or "").strip().lstrip("/")
    if kind not in {"github", "huggingface"}:
        raise ValueError("Choose GitHub or Hugging Face.")
    if "/" not in name or name.startswith("/") or ".." in name.split("/"):
        raise ValueError("Use owner/name.")
    if ".." in path.split("/"):
        raise ValueError("That path is not allowed.")
    return kind, name, path


def choose(mode: str, kind: str, name: str, path: str = "") -> dict:
    mode = (mode or "").strip().lower()
    if mode not in MODES:
        raise ValueError("Choose open, try, test, or lookup.")
    kind, name, path = _clean(kind, name, path)
    suffix = Path(path).suffix.lower()
    if kind == "github":
        page = f"https://github.com/{name}" + (f"/blob/main/{path}" if path else "")
        search = f"https://github.com/search?q=repo:{name}&type=code"
        raw = f"https://api.github.com/repos/{name}/contents/{path}" if path else page
    else:
        page = f"https://huggingface.co/{name}" + (f"/blob/main/{path}" if path else "")
        search = f"https://huggingface.co/search/full-text?q={name}"
        raw = f"https://huggingface.co/{name}/raw/main/{path}" if path else page
    if mode == "lookup":
        return {"mode": mode, "opens": search, "loads_weights": False, "reads_file": False, "reason": "Lookup opens search on the site you chose."}
    if mode == "try":
        target = page if kind == "huggingface" else f"https://github.com/{name}"
        return {"mode": mode, "opens": target, "loads_weights": False, "reads_file": False, "reason": "Try opens the model or project on its own site."}
    if mode == "test":
        return {
            "mode": mode,
            "opens": page,
            "loads_weights": False,
            "reads_file": False,
            "reason": "Test stays a plan until a hidden check runs on a machine you control.",
        }
    if suffix in WEIGHTS:
        return {
            "mode": "open",
            "opens": page,
            "loads_weights": False,
            "reads_file": False,
            "reason": "This is a weight file. Buddy opens its page and does not load the weights.",
        }
    if not path:
        return {"mode": "open", "opens": page, "loads_weights": False, "reads_file": False, "reason": "No file path was given, so Buddy opens the project."}
    return {
        "mode": "open",
        "opens": page,
        "read_url": raw,
        "loads_weights": False,
        "reads_file": True,
        "reason": "Buddy can read this text file. It still does not load a model.",
    }


if __name__ == "__main__":
    text = choose("open", "github", "DreamCo-Technologies/Dreamcobots", "README.md")
    assert text["reads_file"] is True and text["loads_weights"] is False
    weight = choose("open", "huggingface", "org/model", "model.safetensors")
    assert weight["reads_file"] is False and weight["loads_weights"] is False
    assert choose("lookup", "github", "DreamCo-Technologies/Dreamcobots")["opens"].startswith("https://github.com/search")
    assert choose("try", "huggingface", "org/model")["opens"] == "https://huggingface.co/org/model"
    try:
        choose("open", "github", "org/model", "../secrets")
        raise SystemExit("path escape was allowed")
    except ValueError:
        pass
    print(json.dumps({"open": text["mode"], "weights_loaded": False}))
