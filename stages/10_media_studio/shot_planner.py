"""Deterministic shot planning and continuity checks."""
from __future__ import annotations
from typing import Any
from .storyboard import validate_storyboard

def plan_shots(shots: list[dict[str, Any]]) -> dict[str, Any]:
    normalized = validate_storyboard(shots)
    previous_characters: set[str] = set()
    planned = []
    for index, shot in enumerate(normalized, 1):
        characters = set(str(value) for value in shot["character_ids"])
        planned.append({**shot, "sequence": index,
                        "continuity_in": sorted(previous_characters),
                        "continuity_out": sorted(characters),
                        "generation_mode": "keyframe_first",
                        "render_status": "not_rendered"})
        previous_characters = characters
    return {"schema": "dreamco.media.shot_plan.v1", "shot_count": len(planned),
            "duration_seconds": sum(item["duration_seconds"] for item in planned), "shots": planned}
