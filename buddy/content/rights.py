#!/usr/bin/env python3
"""Permission to use a voice or image. This does not train or render a clone."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _clean(value: str) -> str:
    return " ".join((value or "").split())[:80]


def grant(owner: str, other: str, kind: str, statement: str) -> dict:
    owner_name = _clean(owner)
    other_name = _clean(other) or owner_name
    words = _clean(statement).lower()
    base = {"kind": kind, "trained": False, "rendered": False, "elevenlabs_called": False, "revoked": False}
    if kind not in {"voice", "image"}:
        return {**base, "accepted": False, "reason": "Choose voice or image."}
    if len(owner_name) < 2 or owner_name.lower() not in words or "allow" not in words:
        return {**base, "accepted": False, "reason": "The owner has to write the permission, including their name and the word allow."}
    if other_name.lower() not in words:
        return {**base, "accepted": False, "reason": "Name the person who may use it, in the owner's own words."}
    if any(word in words for word in ("child", "kid", "minor", "teen")):
        return {**base, "accepted": False, "reason": "Buddy will not take a child's voice or image."}
    return {
        **base,
        "accepted": True,
        "owner": owner_name,
        "user": other_name,
        "reason": "Permission is recorded. No voice model and no image model is in this repository, so nothing is cloned.",
    }


def revoke(grants: list[dict], owner: str, other: str, kind: str) -> dict:
    owner_name = _clean(owner)
    other_name = _clean(other) or owner_name
    found = False
    for item in grants or []:
        if item.get("owner") == owner_name and item.get("user") == other_name and item.get("kind") == kind:
            item["revoked"] = True
            found = True
    if not found:
        return {"accepted": False, "revoked": False, "reason": "No matching permission to revoke."}
    return {"accepted": True, "revoked": True, "trained": False, "reason": "Permission revoked. The original file, if any, stays on this device."}


def use(grants: list[dict], owner: str, other: str, kind: str) -> dict:
    owner_name = _clean(owner)
    other_name = _clean(other) or owner_name
    match = next((item for item in grants or [] if item.get("accepted") and not item.get("revoked") and item.get("owner") == owner_name and item.get("user") == other_name and item.get("kind") == kind), None)
    if match is None:
        return {"accepted": False, "trained": False, "rendered": False, "reason": "That person has not allowed this use."}
    return {"accepted": True, "trained": False, "rendered": False, "elevenlabs_called": False, "reason": match["reason"]}


def missing() -> dict:
    voice_weights = list(ROOT.glob("**/*.safetensors")) + list(ROOT.glob("**/*.onnx"))
    return {
        "production_ready": False,
        "elevenlabs_called": False,
        "voice_weights": bool(voice_weights),
        "image_weights": bool(voice_weights),
        "note_model_is_a_voice_clone": False,
        "social_tasks_in_local_code": True,
        "needed": [
            "A voice model file trained from recordings the owner is allowed to use.",
            "An image model file trained from photos the owner is allowed to use.",
            "The release file still says this repository is not production ready.",
            "A passing runtime result for the benchmark workflows.",
        ],
    }


if __name__ == "__main__":
    own = grant("Ada", "Ada", "voice", "I Ada allow Ada to use my voice")
    friend = grant("Ada", "Bo", "image", "I Ada allow Bo to use my image")
    blocked = grant("Ada", "Bo", "voice", "please clone this")
    child = grant("Ada", "Bo", "voice", "I Ada allow Bo to use a child's voice")
    assert own["accepted"] and own["trained"] is False and own["elevenlabs_called"] is False
    assert friend["accepted"] and use([friend], "Ada", "Bo", "image")["accepted"]
    assert use([friend], "Ada", "Bo", "voice")["accepted"] is False
    assert revoke([friend], "Ada", "Bo", "image")["revoked"] is True
    assert use([friend], "Ada", "Bo", "image")["accepted"] is False
    assert blocked["accepted"] is False and child["accepted"] is False
    gap = missing()
    assert gap["production_ready"] is False and gap["voice_weights"] is False and gap["elevenlabs_called"] is False
    print(json.dumps({"granted": True, "trained": False, "production_ready": False, "weights": False}))
