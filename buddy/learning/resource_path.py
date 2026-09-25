#!/usr/bin/env python3
"""Attach a resource you may train from. Watching is not a training right."""
from __future__ import annotations

import json

KINDS = {"text", "video", "movie", "reel", "notes"}
ALLOWED = {"owned", "bought-with-training-license", "public-domain", "license-allows-training"}
REFUSED = {
    "youtube": "A YouTube page lets people watch. It does not let you download the video or train on it. This page will not download it.",
    "free-to-watch": "Free to watch is not free to train.",
    "bought-to-watch": "Buying a copy you can watch is not a license to train.",
    "found-online": "Finding a file online is not a training right.",
}


def assign(benchmark: str, kind: str, note: str, rights: bool, hidden_test: str, source: str) -> dict:
    benchmark = (benchmark or "").strip()
    kind = (kind or "").strip().lower()
    source = (source or "").strip().lower()
    note = " ".join((note or "").split())
    hidden_test = " ".join((hidden_test or "").split())
    blocked = {
        "accepted": False,
        "file_uploaded": False,
        "weights_trained": False,
        "downloaded": False,
    }
    if source in REFUSED:
        return {**blocked, "reason": REFUSED[source]}
    if not benchmark or kind not in KINDS or source not in ALLOWED:
        return {**blocked, "reason": "Use text, video, movie, reel, or notes that you own, bought with a training license, or that are public domain or licensed for training."}
    if not rights:
        return {**blocked, "reason": "Confirm that this source allows training, not only watching."}
    if len(note) < 20:
        return {**blocked, "reason": "Write what you learned in your own words. The file itself is not uploaded."}
    if len(hidden_test) < 10:
        return {**blocked, "reason": "Keep one question the note does not answer."}
    return {
        "accepted": True,
        "benchmark": benchmark,
        "kind": kind,
        "source": source,
        "stored": "your note",
        "file_uploaded": False,
        "downloaded": False,
        "weights_trained": False,
        "weights_mastered": False,
        "score_changed": False,
        "reason": "The note can be a lesson. Training still happens on a machine you control, and only if that license allows it.",
    }


if __name__ == "__main__":
    assert assign("benchmark-tracker.yml", "movie", "a note that is long enough here", True, "which question stays hidden", "youtube")["accepted"] is False
    assert assign("benchmark-tracker.yml", "movie", "a note that is long enough here", True, "which question stays hidden", "free-to-watch")["accepted"] is False
    assert assign("benchmark-tracker.yml", "movie", "a note that is long enough here", True, "which question stays hidden", "bought-to-watch")["downloaded"] is False
    good = assign(
        "benchmark-tracker.yml",
        "movie",
        "I learned to keep one question out of the study notes.",
        True,
        "which question stays hidden",
        "owned",
    )
    assert good["accepted"] and good["weights_trained"] is False and good["downloaded"] is False
    public = assign("benchmark-tracker.yml", "text", "I learned to keep one question out of the study notes.", True, "which question stays hidden", "public-domain")
    assert public["accepted"] is True
    print(json.dumps(good))
