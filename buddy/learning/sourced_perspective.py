#!/usr/bin/env python3
"""Ten sourced views, then our own line. The pages are not downloaded."""
from __future__ import annotations

import json
from urllib.parse import urlparse

STOLEN = ("distill", "copy the page", "download the page", "full transcript")


def _url_ok(url: str) -> bool:
    parsed = urlparse((url or "").strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def sourced(views: list[dict], own: str) -> dict:
    notes = []
    for view in views or []:
        text = " ".join(str(view.get("text", "")).split())
        url = str(view.get("source", "")).strip()
        if text and url and (text, url) not in [(item["text"], item["source"]) for item in notes]:
            notes.append({"text": text[:400], "source": url})
    own_line = " ".join((own or "").split())
    blob = " ".join(item["text"] for item in notes) + " " + own_line
    blocked = {"accepted": False, "downloaded": False, "copied": False, "weights_trained": False}
    if any(phrase in blob.lower() for phrase in STOLEN):
        return {**blocked, "reason": "Do not copy or download the page. Cite it and write your own line."}
    if len(notes) < 10:
        return {**blocked, "reason": "Each of 10 views needs its own sentence and its own source link."}
    if any(len(item["text"]) < 20 or not _url_ok(item["source"]) for item in notes[:10]):
        return {**blocked, "reason": "Use a real sentence and an http source link for every view."}
    if len(own_line) < 20 or own_line in [item["text"] for item in notes]:
        return {**blocked, "reason": "Your own line has to be new. It cannot repeat a view."}
    return {
        "accepted": True,
        "views": notes[:10],
        "own": own_line,
        "sources": [item["source"] for item in notes[:10]],
        "downloaded": False,
        "copied": False,
        "weights_trained": False,
        "reason": "Each point keeps its source. The page was not downloaded, and no weight was trained.",
    }


if __name__ == "__main__":
    views = [
        {"text": f"View {n} says something different about this free note.", "source": f"https://example.com/note-{n}"}
        for n in range(1, 11)
    ]
    assert sourced(views[:2], "My own take is long enough to count.")["accepted"] is False
    bad_url = [dict(view, source="javascript:alert(1)") for view in views]
    assert sourced(bad_url, "My own take is long enough to count here.")["accepted"] is False
    good = sourced(views, "My own take is to try a new example and cite the ten links.")
    assert good["accepted"] and len(good["sources"]) == 10 and good["downloaded"] is False
    print(json.dumps({"accepted": True, "sources": 10, "downloaded": False}))
