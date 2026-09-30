"""Local image likeness or style cloning.

clone_image() requires a consent record for the first reference image.
The local backend is SDXL plus IP-Adapter. Nothing is downloaded on import.
A sexual, violent, or defamatory prompt is refused even when consent exists.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Sequence

import numpy as np

from .consent_gate import require_consent
from .watermark import watermark_image

logger = logging.getLogger(__name__)
_BASE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
_IP_ADAPTER_REPO = "h94/IP-Adapter"
_IP_ADAPTER_WEIGHT = "ip-adapter_sdxl.bin"
_pipe_singleton = None
_BLOCKED = ("nude", "naked", "sexual", "porn", "kill", "murder", "defame")


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


def _load_pipeline():
    global _pipe_singleton
    if _pipe_singleton is None:
        import torch
        from diffusers import StableDiffusionXLPipeline

        device = _device()
        dtype = torch.float16 if device in ("mps", "cuda") else torch.float32
        pipe = StableDiffusionXLPipeline.from_pretrained(_BASE_MODEL, torch_dtype=dtype)
        pipe.load_ip_adapter(_IP_ADAPTER_REPO, subfolder="sdxl_models", weight_name=_IP_ADAPTER_WEIGHT)
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
    paid: bool = False,
    use_remote: bool = False,
    remote_client=None,
) -> Path:
    """Generate one watermarked image from reference images and a prompt."""
    if paid:
        raise RuntimeError("A paid likeness run is not enabled. Confirm the model license first.")
    if not reference_image_paths:
        raise ValueError("reference_image_paths must contain at least one image")
    _refuse_prompt(prompt)
    reference_image_paths = [Path(path) for path in reference_image_paths]
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    record = require_consent(reference_image_paths[0], "image_clone", consent_record_path)
    logger.info("consent verified for '%s'", record.subject_name)
    if use_remote:
        if remote_client is None:
            raise ValueError("use_remote=True requires a remote_client callable supplied by the caller")
        pixels = remote_client(
            reference_image_paths,
            prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
        )
    else:
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
        pixels = np.array(result.images[0])
    pixels = watermark_image(np.asarray(pixels), metadata={"subject": record.subject_name})
    from PIL import Image as PILImage

    PILImage.fromarray(pixels).save(output_path)
    return output_path
