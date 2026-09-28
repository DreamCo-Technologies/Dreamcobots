#!/usr/bin/env python3
"""Turn a subject into a content packet. Do not publish it or render a video."""
from __future__ import annotations

import json


def packet(subject: str, when: str = "", link: str = "") -> dict:
    topic = " ".join((subject or "").split())[:160]
    base = {"posted": False, "video_generated": False, "reaches_instagram": False}
    if len(topic) < 3:
        return {**base, "accepted": False, "reason": "Name the content."}
    schedule = " ".join((when or "").split())[:80]
    return {
        **base,
        "accepted": True,
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
        "caption": f"{topic}. One step. Not posted until you post it.",
        "schedule": schedule or "Pick a time. Buddy does not know when your audience is online.",
        "link": " ".join((link or "").split())[:200],
        "reason": "Buddy wrote the idea, the shots, and the caption. It did not render a video or publish the post.",
    }


if __name__ == "__main__":
    made = packet("how to frost a cake", "Friday 6pm", "https://example.com/recipe")
    assert made["accepted"] and made["posted"] is False and made["video_generated"] is False and made["reaches_instagram"] is False
    assert packet("no")["accepted"] is False
    print(json.dumps({"accepted": True, "posted": False, "video_generated": False}))
