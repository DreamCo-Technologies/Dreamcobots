"""Validated storyboard primitives."""
from __future__ import annotations
from typing import Any

def validate_storyboard(shots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(shots, list) or not shots:
        raise ValueError("A storyboard requires at least one shot.")
    normalized = []
    seen = set()
    for index, shot in enumerate(shots, 1):
        if not isinstance(shot, dict):
            raise ValueError("Each storyboard shot must be an object.")
        shot_id = str(shot.get("shot_id") or f"shot-{index:03d}")
        if shot_id in seen:
            raise ValueError(f"Duplicate shot_id: {shot_id}")
        seen.add(shot_id)
        description = str(shot.get("description") or "").strip()
        if len(description) < 12:
            raise ValueError(f"{shot_id} requires a descriptive visual direction.")
        duration = shot.get("duration_seconds", 5)
        if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not 0.5 <= duration <= 120:
            raise ValueError(f"{shot_id} duration must be between 0.5 and 120 seconds.")
        normalized.append({
            "shot_id": shot_id, "description": description[:2000],
            "duration_seconds": float(duration),
            "character_ids": list(shot.get("character_ids") or []),
            "asset_ids": list(shot.get("asset_ids") or []),
            "dialogue": str(shot.get("dialogue") or "")[:4000],
            "audio_cues": list(shot.get("audio_cues") or []),
        })
    return normalized
