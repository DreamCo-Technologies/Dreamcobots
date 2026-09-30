"""Draw with Buddy's own picture code.

clone_image() requires an adult consent record. It does not call Stable
Diffusion or any other service. The picture is an original drawing tinted
from the reference file hash. It does not reproduce a person's face.
A sexual, violent, or defamatory prompt is refused even when consent exists.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Sequence

from buddy.picture.draw import draw

from .consent_gate import require_consent

logger = logging.getLogger(__name__)
_BLOCKED = ("nude", "naked", "sexual", "porn", "kill", "murder", "defame")
USES = {"personal", "business", "social"}


def _refuse_prompt(prompt: str) -> None:
    text = " ".join(prompt.lower().split())
    if any(word in text.split() for word in _BLOCKED):
        raise ValueError("refusing a sexual, violent, or defamatory depiction")


def clone_image(
    reference_image_paths: Sequence[str | Path],
    prompt: str,
    consent_record_path: str | Path,
    output_path: str | Path,
    negative_prompt: str = "",
    num_inference_steps: int = 25,
    guidance_scale: float = 6.0,
    width: int = 1024,
    height: int = 1024,
    use: str = "personal",
) -> Path:
    """Draw one original picture for personal, business, or social use."""
    if use not in USES:
        raise ValueError("use must be personal, business, or social")
    if not reference_image_paths:
        raise ValueError("reference_image_paths must contain at least one image")
    _refuse_prompt(prompt)
    reference_image_paths = [Path(path) for path in reference_image_paths]
    output_path = Path(output_path)
    record = require_consent(reference_image_paths[0], "image_clone", consent_record_path)
    logger.info(
        "consent verified for '%s' (%s). Owned drawing, not a likeness model. steps=%s scale=%s size=%sx%s negative=%s",
        record.subject_name, use, num_inference_steps, guidance_scale, width, height, bool(negative_prompt),
    )
    return draw(prompt, reference_image_paths[0], output_path)