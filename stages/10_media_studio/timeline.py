"""Create an ordered, deterministic media timeline from a shot plan."""
from __future__ import annotations
from typing import Any

def build_timeline(shot_plan: dict[str, Any]) -> dict[str, Any]:
    shots = shot_plan.get("shots")
    if not isinstance(shots, list) or not shots:
        raise ValueError("A non-empty shot plan is required.")
    cursor = 0.0
    timeline = []
    for shot in shots:
        duration = float(shot["duration_seconds"])
        if duration <= 0:
            raise ValueError("Timeline shot durations must be positive.")
        timeline.append({"shot_id": shot["shot_id"], "start_seconds": round(cursor, 3),
                         "end_seconds": round(cursor + duration, 3), "duration_seconds": duration,
                         "dialogue": shot.get("dialogue", ""), "audio_cues": shot.get("audio_cues", [])})
        cursor += duration
    return {"schema": "dreamco.media.timeline.v1", "duration_seconds": round(cursor, 3),
            "shots": timeline, "rendered": False}
