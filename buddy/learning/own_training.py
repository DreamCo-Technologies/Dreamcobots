#!/usr/bin/env python3
"""Turn each part of a subject into your own training line. Do not store the source."""
from __future__ import annotations

import json
from urllib.parse import urlparse

STOLEN = ("distill", "copy the video", "copy the page", "download the video", "full transcript")


def company_of(url: str) -> str:
    parsed = urlparse((url or "").strip())
    host = (parsed.netloc or "").lower().removeprefix("www.")
    parts = [part for part in parsed.path.split("/") if part]
    if host == "huggingface.co" and len(parts) >= 2 and parts[0] in {"datasets", "models", "spaces"}:
        return parts[1].lower()
    if host == "github.com" and parts:
        return parts[0].lower()
    return host


def _views(rows: list[dict]) -> list[dict]:
    notes = []
    seen = set()
    for row in rows or []:
        text = " ".join(str(row.get("text", "")).split())
        source = str(row.get("source", "")).strip()
        parsed = urlparse(source)
        if len(text) < 20 or parsed.scheme != "https" or not parsed.netloc:
            continue
        key = (text, source)
        if key in seen:
            continue
        seen.add(key)
        notes.append({"text": text[:400], "source": source, "company": company_of(source)})
    return notes


def own_data(subject: str, parts: list[dict], restricted: list[str]) -> dict:
    subject = " ".join((subject or "").split())
    blocked_companies = {item.strip().lower() for item in restricted or [] if item.strip()}
    refused = {
        "accepted": False,
        "source_files_stored": False,
        "weights_trained": False,
        "training_data": "none",
    }
    if len(subject) < 3 or not parts:
        return {**refused, "reason": "Name the subject and at least one part."}
    made = []
    blob = subject
    for part in parts:
        name = " ".join(str(part.get("name", "")).split())
        kind = str(part.get("kind", "text")).strip().lower() or "text"
        notes = _views(part.get("views") or [])
        own = " ".join(str(part.get("own", "")).split())
        blob += " " + name + " " + own + " " + " ".join(item["text"] for item in notes)
        if kind not in {"text", "video", "movie", "github", "huggingface", "other"}:
            return {**refused, "reason": "Use text, video, movie, GitHub, Hugging Face, or other."}
        if len(notes) < 10:
            return {**refused, "reason": f"{name or 'A part'} needs 10 different views, each with its own https source."}
        hit = next((item["company"] for item in notes[:10] if item["company"] in blocked_companies), "")
        if hit:
            return {**refused, "reason": f"{hit} is restricted. Pick another source or remove the restriction."}
        if len(own) < 20 or own in [item["text"] for item in notes]:
            return {**refused, "reason": "Your own line has to be new. It cannot repeat a view."}
        made.append({
            "name": name or "part",
            "kind": kind,
            "own": own,
            "sources": [item["source"] for item in notes[:10]],
            "companies": sorted({item["company"] for item in notes[:10]}),
        })
    if any(phrase in blob.lower() for phrase in STOLEN):
        return {**refused, "reason": "Do not copy or download the source. Write your own line."}
    return {
        "accepted": True,
        "subject": subject,
        "parts": made,
        "training_data": "your own lines",
        "source_files_stored": False,
        "weights_trained": False,
        "restricted": sorted(blocked_companies),
        "reason": "Each part was compared ten ways. The training note is your line, not the video, movie, or repository.",
    }


def sample() -> tuple[dict, dict]:
    views = [
        {"text": f"View {n} says something different about this part of the subject.", "source": f"https://huggingface.co/datasets/example/set-{n}"}
        for n in range(1, 11)
    ]
    part = {"name": "sorting", "kind": "video", "views": views, "own": "Our line is to try a new example and cite the ten links."}
    return own_data("mail", [part], []), own_data("mail", [part], ["example"])


if __name__ == "__main__":
    good, blocked = sample()
    assert good["accepted"] and good["weights_trained"] is False and good["source_files_stored"] is False
    assert blocked["accepted"] is False
    assert company_of("https://github.com/cli/cli") == "cli"
    print(json.dumps({"accepted": True, "parts": len(good["parts"]), "weights_trained": False}))
