#!/usr/bin/env python3
"""Study YouTube or a book from ten views, then write your own line.

The video or book is not downloaded or copied into a model.
"""
from __future__ import annotations

import json

KINDS = {"text", "video", "movie", "reel", "notes", "book"}
STUDY = {
    "owned",
    "youtube",
    "bought-book",
    "bought-to-watch",
    "free-to-watch",
    "public-domain",
    "license-allows-training",
    "bought-with-training-license",
}
STOLEN = (
    "distill",
    "copy the video",
    "copy the book",
    "full transcript",
    "download the video",
    "paste the page",
)


def perspectives(source: str, kind: str, views: list[str], own: str) -> dict:
    source = (source or "").strip().lower()
    kind = (kind or "").strip().lower()
    own_line = " ".join((own or "").split())
    notes = []
    for view in views or []:
        line = " ".join(str(view).split())
        if line and line not in notes:
            notes.append(line[:500])
    blob = " ".join(notes + [own_line, source]).lower()
    blocked = {
        "accepted": False,
        "downloaded": False,
        "file_uploaded": False,
        "weights_trained": False,
        "copied": False,
    }
    if source == "found-online":
        return {**blocked, "reason": "A file you found online is not stored. Write your own views instead."}
    if kind not in KINDS or source not in STUDY:
        return {**blocked, "reason": "Choose a book, a video, or YouTube, then write ten views."}
    for phrase in STOLEN:
        if phrase in blob:
            return {**blocked, "reason": "Do not distill, download, or copy the source. Write your own view."}
    if len(notes) < 10:
        return {**blocked, "reason": "Write 10 different views before your own line. One view is not enough."}
    if any(len(line) < 20 for line in notes[:10]):
        return {**blocked, "reason": "Each view needs a real sentence, not a title."}
    if len(own_line) < 20 or own_line in notes:
        return {**blocked, "reason": "Your own line has to be new. It cannot repeat one of the ten views."}
    return {
        "accepted": True,
        "source": source,
        "kind": kind,
        "views": 10,
        "stored": "your ten views and your own line",
        "downloaded": False,
        "file_uploaded": False,
        "weights_trained": False,
        "copied": False,
        "reason": "YouTube or a book can teach you. What is stored is your perspective, not the video or the book.",
    }


if __name__ == "__main__":
    views = [f"View {n} says something different about this lesson." for n in range(1, 11)]
    blocked = perspectives("youtube", "video", views, "download the video and copy the book")
    assert blocked["accepted"] is False and blocked["downloaded"] is False
    short = perspectives("youtube", "video", views[:3], "My own take is different from those three views.")
    assert short["accepted"] is False
    good = perspectives("youtube", "video", views, "My own take is that I would try a new example and not replay the clip.")
    assert good["accepted"] and good["copied"] is False and good["weights_trained"] is False
    book = perspectives("bought-book", "book", views, "After the book, I would explain the idea with my own example.")
    assert book["accepted"] is True
    assert perspectives("found-online", "video", views, "My own take is long enough to count here.")["accepted"] is False
    print(json.dumps(good))
