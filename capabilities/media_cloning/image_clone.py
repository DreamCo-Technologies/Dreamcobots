"""Local image likeness or style cloning.

clone_image() requires a consent record for the first reference image.
The local backend is SDXL plus IP-Adapter, loaded only from folders already
on this machine. There is no remote call and no download. A sexual, violent,
or defamatory prompt is refused even when consent exists.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Sequence

import numpy as np

from .consent_gate import require_consent
from .watermark import watermark_image

logger = logging.getLogger(__name__)
_pipe_singleton = None
_BLOCKED = ("nude", "naked", "sexual", "porn", "kill", "murder", "defame")
USES = {"personal", "business", "social"}


def _device() -> str:
    try:
        import torch
    except ImportError:
        return "cpu"
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def _refuse_prompt(prompt: str) -> None:
    text = " ".join(prompt.lower().split())
    if any(word in text.split() for word in _BLOCKED):
        raise ValueError("refusing a sexual, violent, or defamatory depiction")


def _local_image_weights() -> tuple[Path, Path]:
    folder = Path(os.environ.get("DREAMCO_SDXL_DIR", ""))
    adapter = Path(os.environ.get("DREAMCO_IP_ADAPTER", ""))
    if not (folder / "model_index.json").is_file() or not adapter.is_file():
        raise RuntimeError(
            "Local image weights are not on this machine. Set DREAMCO_SDXL_DIR to a folder "
            "that already contains model_index.json and DREAMCO_IP_ADAPTER to the adapter file. "
            "This package will not download weights and will not send the picture anywhere."
        )
    return folder, adapter


def _load_pipeline():
    global _pipe_singleton
    folder, adapter = _local_image_weights()
    if _pipe_singleton is None:
        import torch
        from diffusers import StableDiffusionXLPipeline

        device = _device()
        dtype = torch.float16 if device in ("mps", "cuda") else torch.float32
        logger.info("loading local SDXL on %s", device)
        pipe = StableDiffusionXLPipeline.from_pretrained(str(folder), torch_dtype=dtype, local_files_only=True)
        pipe.load_ip_adapter(str(adapter.parent), subfolder="", weight_name=adapter.name)
        pipe.set_ip_adapter_scale(0.6)
        pipe.to(device)
        if device == "mps":
            pipe.enable_attention_slicing()
        _pipe_singleton = pipe
    return _pipe_singleton


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
    """Generate one watermarked image for personal, business, or social use."""
    if use not in USES:
        raise ValueError("use must be personal, business, or social")
    if not reference_image_paths:
        raise ValueError("reference_image_paths must contain at least one image")
    _refuse_prompt(prompt)
    reference_image_paths = [Path(path) for path in reference_image_paths]
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    record = require_consent(reference_image_paths[0], "image_clone", consent_record_path)
    logger.info("consent verified for '%s'", record.subject_name)
    _local_image_weights()
    pipe = _load_pipeline()
    from PIL import Image

    references = [Image.open(path).convert("RGB") for path in reference_image_paths]
    result = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        ip_adapter_image=references,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
        width=width,
        height=height,
    )
    pixels = watermark_image(np.asarray(result.images[0]), metadata={"subject": record.subject_name})
    from PIL import Image as PILImage

    PILImage.fromarray(pixels).save(output_path)
    return output_path