#!/usr/bin/env python3
"""Turn one subject into a draft for each social network. Do not publish it."""
from __future__ import annotations

import json
from pathlib import Path

FORMATS = json.loads((Path(__file__).resolve().parents[2] / "website/data/social-formats.json").read_text(encoding="utf-8"))


def _clip(text: str, limit: int) -> str:
    clean = " ".join(text.split())
    if len(clean) <= limit:
        return clean
    room = clean[: max(0, limit - 1)].rsplit(" ", 1)[0]
    return (room or clean[: limit - 1]).rstrip() + "…"


def formats() -> dict:
    return {
        "platforms": len(FORMATS["platforms"]),
        "weights_trained": False,
        "posted": False,
        "note": FORMATS["note"],
    }


def packet(subject: str, when: str = "", link: str = "") -> dict:
    topic = " ".join((subject or "").split())[:160]
    base = {"posted": False, "video_generated": False, "reaches_instagram": False}
    if len(topic) < 3:
        return {**base, "accepted": False, "reason": "Name the content."}
    schedule = " ".join((when or "").split())[:80] or "Pick a time. Buddy does not know when your audience is online."
    clean_link = " ".join((link or "").split())[:200]
    body = f"{topic}. One step. Not posted until you post it."
    if clean_link:
        body = f"{body} {clean_link}"
    drafts = []
    for item in FORMATS["platforms"]:
        room = item["limit"]
        if item["id"] == "x" and clean_link:
            room = max(40, item["limit"] - 24)
        draft = {"id": item["id"], "name": item["name"], "shape": item["shape"], "limit": item["limit"], "within_limit": True}
        if "title_limit" in item:
            draft["title"] = _clip(topic, item["title_limit"])
            draft["text"] = _clip(body, room)
        else:
            draft["text"] = _clip(body, room)
        draft["within_limit"] = len(draft["text"]) <= item["limit"] and len(draft.get("title", "")) <= item.get("title_limit", 10**6)
        drafts.append(draft)
    return {
        **base,
        "accepted": True,
        "platforms": drafts,
        "learned": formats(),
        "angles": [
            f"Open on the problem in {topic}.",
            "Show one step a viewer can copy.",
            "Show the result, then how you got there.",
        ],
        "shots": [
            "Three seconds on the problem, tight on the work.",
            "One step, close enough to copy.",
            "The result, then the line you want remembered.",
        ],
        "lines": [
            f"This is {topic}, in one step.",
            "Do this part first.",
            "That is the whole piece.",
        ],
        "caption": _clip(body, 2200),
        "schedule": schedule,
        "link": clean_link,
        "reason": "Buddy wrote one draft per network from public format rules. It did not train a model, render a video, or publish a post.",
    }


if __name__ == "__main__":
    made = packet("how to frost a cake", "Friday 6pm", "https://example.com/recipe")
    assert made["accepted"] and made["posted"] is False and made["video_generated"] is False and made["reaches_instagram"] is False
    assert made["learned"]["platforms"] == 12 and made["learned"]["weights_trained"] is False
    assert all(row["within_limit"] for row in made["platforms"])
    assert packet("no")["accepted"] is False
    print(json.dumps({"platforms": len(made["platforms"]), "posted": False, "weights_trained": False}))
