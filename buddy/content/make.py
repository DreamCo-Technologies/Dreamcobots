#!/usr/bin/env python3
"""Turn one subject into a draft for each social network. Do not publish it."""
from __future__ import annotations

import json
from pathlib import Path

FORMATS = json.loads((Path(__file__).resolve().parents[2] / "website/data/social-formats.json").read_text(encoding="utf-8"))
TYPES = json.loads((Path(__file__).resolve().parents[2] / "website/data/social-types.json").read_text(encoding="utf-8"))
BY_ID = {item["id"]: item for item in TYPES["types"]}


def _clip(text: str, limit: int) -> str:
    clean = " ".join(text.split())
    if len(clean) <= limit:
        return clean
    room = clean[: max(0, limit - 1)].rsplit(" ", 1)[0]
    return (room or clean[: limit - 1]).rstrip() + "…"


def formats() -> dict:
    return {
        "platforms": len(FORMATS["platforms"]),
        "types": len(TYPES["types"]),
        "weights_trained": False,
        "posted": False,
        "note": FORMATS["note"],
    }


def beats(group: str, name: str, topic: str) -> list[str]:
    if group == "poem" or name in {"Poem", "Haiku", "Spoken word", "Original verse"}:
        return [
            f"{topic}, kept small and near.",
            "One step, then the next is clear.",
            "The hands do what the line has said.",
            "Stop before a borrowed thread.",
        ]
    if group == "commercial":
        return [
            f"Open on the problem in {topic}.",
            "Show one step. Do not invent a price or a review.",
            f"End on the result. This {name} is a script, not a finished ad.",
        ]
    if group == "music":
        return [
            f"{name} for {topic}: a picture, then a line you wrote.",
            "Do not use someone else's recording unless you have the right.",
            "Cut back to the result. No video file is rendered.",
        ]
    if group == "long":
        return [
            f"{name}: why {topic} matters in the first minute.",
            "One example a viewer can check.",
            "Close with what to do next. This is an outline, not a filmed show.",
        ]
    if group == "note":
        return [
            f"{name}: {topic}.",
            "Say only what you can stand behind.",
            "Leave the post unpublished until you send it.",
        ]
    return [
        f"{name}: open on {topic}.",
        "Show one step a viewer can copy.",
        "Close on the result. Not posted until you post it.",
    ]


def cost() -> dict:
    return {
        "usd": 0,
        "charged": False,
        "paid_api": False,
        "voice_clone_trained": False,
        "image_clone_trained": False,
        "reason": "Written on this machine. Buddy does not bill you and does not call a paid model.",
    }


def clone(kind: str, mine: bool, consent: bool) -> dict:
    base = {"kind": kind, "trained": False, "charged": False, "usd": 0, "copied_another_person": False}
    if kind not in {"voice", "image"}:
        return {**base, "accepted": False, "reason": "Choose voice or image."}
    if mine is not True or consent is not True:
        return {**base, "accepted": False, "reason": "Buddy will not copy a voice or a face unless it is yours and you agree. It still will not train a clone."}
    return {**base, "accepted": True, "reason": "This is a note that the sample is yours. No voice model and no face model is trained."}


def lineup(subject: str) -> dict:
    topic = " ".join((subject or "").split())[:160]
    if len(topic) < 3:
        return {"accepted": False, "posted": False, "video_generated": False, "reason": "Name the content."}
    rows = [{"id": item["id"], "name": item["name"], "line": beats(item["group"], item["name"], topic)[0]} for item in TYPES["types"]]
    return {"accepted": True, "posted": False, "video_generated": False, "weights_trained": False, "count": len(rows), "rows": rows}


def packet(subject: str, when: str = "", link: str = "", kind: str = "feed-post") -> dict:
    topic = " ".join((subject or "").split())[:160]
    base = {"posted": False, "video_generated": False, "reaches_instagram": False}
    if len(topic) < 3:
        return {**base, "accepted": False, "reason": "Name the content."}
    chosen = BY_ID.get(kind)
    if chosen is None:
        return {**base, "accepted": False, "reason": "That content type is not in the list."}
    script = beats(chosen["group"], chosen["name"], topic)
    schedule = " ".join((when or "").split())[:80] or "Pick a time. Buddy does not know when your audience is online."
    clean_link = " ".join((link or "").split())[:200]
    body = " ".join(script)
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
        "kind": chosen["id"],
        "script": script,
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
        "cost": cost(),
        "schedule": schedule,
        "link": clean_link,
        "reason": f"Buddy wrote a {chosen['name']} and one draft per network. It did not film, render, or publish it.",
    }


if __name__ == "__main__":
    made = packet("how to frost a cake", "Friday 6pm", "https://example.com/recipe")
    assert made["accepted"] and made["posted"] is False and made["video_generated"] is False and made["reaches_instagram"] is False
    assert made["learned"]["platforms"] == 12 and made["learned"]["types"] == 118 and made["learned"]["weights_trained"] is False
    assert all(row["within_limit"] for row in made["platforms"])
    assert len(made["script"]) == 3
    board = lineup("how to frost a cake")
    assert board["count"] == 118 and board["video_generated"] is False
    poem = packet("how to frost a cake", kind="poem")
    assert poem["accepted"] and "borrowed thread" in poem["script"][-1]
    assert packet("how to frost a cake", kind="nope")["accepted"] is False
    assert packet("no")["accepted"] is False
    assert made["cost"]["usd"] == 0 and made["cost"]["charged"] is False and made["cost"]["paid_api"] is False
    own = clone("voice", True, True)
    other = clone("image", False, True)
    assert own["accepted"] and own["trained"] is False and other["accepted"] is False and other["copied_another_person"] is False
    print(json.dumps({"platforms": len(made["platforms"]), "types": board["count"], "usd": 0, "clone_trained": False}))
