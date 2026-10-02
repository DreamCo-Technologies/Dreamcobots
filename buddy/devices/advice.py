#!/usr/bin/env python3
"""Expert advice for any user's device. Do not store one owner's machine."""
from __future__ import annotations

import json
from pathlib import Path


def classify(memory_gb: float) -> str:
    if memory_gb < 2:
        raise ValueError("Need a memory size.")
    if memory_gb <= 4:
        return "phone"
    if memory_gb <= 8:
        return "small-laptop"
    if memory_gb <= 16:
        return "everyday-laptop"
    return "large-computer"


def advise(topic: str, memory_gb: float, cores: int = 0) -> dict:
    kind = classify(memory_gb)
    rules = {
        "phone": "Write and review here. Do not load a weight file or a clone model on this device.",
        "small-laptop": "Load one model. Use 16-bit only for about 1B parameters or fewer. Use 4-bit for a 7B model, and leave 2GB free.",
        "everyday-laptop": "A 7B model can fit in 4-bit or 8-bit. Still unload it before you load a second one.",
        "large-computer": "You can study a larger open model. Keep one heavy model loaded, and do not upload another person's voice or face.",
    }
    topics = {
        "weights": "Read the license on the model card before you download. A catalog row is not a benchmark score.",
        "clone": "Consent has to match the exact file. A child is refused. Kokoro speaks, but it does not clone.",
        "plans": "A lesson marked ready is not a trained model. A passing check does not give permission to act.",
        "content": "The script costs nothing here. Playing it uses this browser's voice, not a copied person.",
    }
    if topic not in topics:
        raise ValueError("Unknown topic.")
    return {
        "device_class": kind,
        "cores": cores,
        "advice": [rules[kind], topics[topic]],
        "learned_from_one_owner": False,
        "uploaded": False,
    }


def remember(devices: list[dict], device: dict, folder: Path | None = None) -> dict:
    """Keep a device note for this user. Refuse the shared repository."""
    if "serial" in device:
        raise ValueError("Do not store a serial number.")
    root = Path(__file__).resolve().parents[2]
    if folder is not None and (root in Path(folder).resolve().parents or Path(folder).resolve() == root):
        raise ValueError("Device notes stay on that user's computer.")
    saved = devices + [{"memory_gb": device["memory_gb"], "cores": device.get("cores", 0), "class": classify(device["memory_gb"])}]
    return {"devices": len(saved), "uploaded": False, "saved": saved}


if __name__ == "__main__":
    phone = advise("weights", 4, 6)
    small = advise("clone", 8, 6)
    large = advise("plans", 32, 12)
    assert phone["device_class"] == "phone" and small["device_class"] == "small-laptop"
    assert phone["learned_from_one_owner"] is False and large["uploaded"] is False
    assert "4-bit" in small["advice"][0]
    remembered = remember([], {"memory_gb": 16, "cores": 8})
    assert remembered["devices"] == 1 and remembered["uploaded"] is False
    try:
        remember([], {"memory_gb": 8, "serial": "hidden"})
        raise SystemExit("serial was accepted")
    except ValueError:
        pass
    print(json.dumps({"classes": 4, "uploaded": False}))
