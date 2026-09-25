#!/usr/bin/env python3
"""Turn any note into ten views and one original line. Do not store the source."""
from __future__ import annotations

import json

STOLEN = ("distill", "copy the video", "copy the book", "full transcript", "download the video")


def from_any(text: str) -> dict:
    clean = " ".join((text or "").split())
    blocked = {"accepted": False, "source_stored": False, "weights_trained": False, "copied": False}
    if any(phrase in clean.lower() for phrase in STOLEN):
        return {**blocked, "reason": "Do not distill or copy the source. Write from the comparison."}
    if len(clean) < 20:
        return {**blocked, "reason": "Give a real note. One word is not enough to compare."}
    topic = " ".join(clean.split()[:4])
    views = [
        f"Teacher: ask what {topic} is for, then answer on a new example.",
        f"Book: {topic} is one reading, not the whole subject.",
        f"Beginner: start with one fact from {topic} and say it another way.",
        f"Practitioner: use {topic} on a fresh case, not the case in the note.",
        f"Critic: {topic} does not prove the task is mastered.",
        "Measurer: learned means a hidden question passes. A reread does not.",
        "Safety: do not copy the source, spend money, or keep a secret from it.",
        "Neighbor: doing the task without rereading the note is a different view.",
        f"Subject: {topic} belongs to the subject of the note and nowhere else yet.",
        f"Examiner: what will you do differently on a new task after reading about {topic}?",
    ]
    if len(set(views)) != 10:
        return {**blocked, "reason": "The ten views were not different."}
    own = f"Our line: after ten views of {topic}, practice on a new example and do not repeat the source."
    if own in views or own == clean or clean in own:
        return {**blocked, "reason": "The own line copied the source."}
    return {
        "accepted": True,
        "views": views,
        "own": own,
        "source_stored": False,
        "weights_trained": False,
        "copied": False,
        "reason": "Compared ten ways. Kept our line. Did not keep the source and did not train a weight.",
    }


if __name__ == "__main__":
    bad = from_any("please download the video and copy the book into the model")
    assert bad["accepted"] is False and bad["copied"] is False
    good = from_any("Sort support mail into three piles and write a short reply for each pile.")
    assert good["accepted"] and len(good["views"]) == 10 and good["source_stored"] is False
    assert good["own"] not in good["views"]
    print(json.dumps({"accepted": True, "views": 10, "weights_trained": False}))
