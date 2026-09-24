#!/usr/bin/env python3
"""Attach a resource you may use to one unknown benchmark. Do not train weights."""
from __future__ import annotations

import json

KINDS = {"text", "video", "movie", "reel", "notes"}


def assign(benchmark: str, kind: str, note: str, rights: bool, hidden_test: str) -> dict:
    benchmark = (benchmark or "").strip()
    kind = (kind or "").strip().lower()
    note = " ".join((note or "").split())
    hidden_test = " ".join((hidden_test or "").split())
    if not benchmark or kind not in KINDS:
        return {"accepted": False, "reason": "Name one benchmark and choose text, video, movie, reel, or notes."}
    if kind in {"video", "movie", "reel"} and not rights:
        return {"accepted": False, "reason": "A video, movie, or reel can be studied only when you have the right to use it."}
    if not rights:
        return {"accepted": False, "reason": "Do not train on a resource you do not have the right to use."}
    if len(note) < 20:
        return {"accepted": False, "reason": "Write what you learned in your own words. The file itself is not uploaded."}
    if len(hidden_test) < 10:
        return {"accepted": False, "reason": "Keep one question the note does not answer."}
    return {
        "accepted": True,
        "benchmark": benchmark,
        "kind": kind,
        "stored": "your note",
        "file_uploaded": False,
        "weights_trained": False,
        "weights_mastered": False,
        "score_changed": False,
        "reason": "The note is the lesson. The benchmark stays unknown until a real run passes the hidden question.",
    }


if __name__ == "__main__":
    movie = assign("benchmark-tracker.yml", "movie", "the scene explains a test split", False, "what was held out")
    assert movie["accepted"] is False
    short = assign("benchmark-tracker.yml", "text", "too short", True, "what was held out")
    assert short["accepted"] is False
    good = assign(
        "benchmark-tracker.yml",
        "reel",
        "I learned to keep one question out of the study notes.",
        True,
        "which question stays hidden",
    )
    assert good["accepted"] and good["weights_mastered"] is False and good["file_uploaded"] is False
    print(json.dumps(good))
