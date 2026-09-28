"""Image cloning (likeness/style) with Stable Diffusion 1.5 + IP-Adapter. No training needed; fits 8 GB alone."""
from __future__ import annotations

from typing import Optional

from PIL import Image

from .voice import pick_device


class IPAdapterBackend:
    name = "sd15-ip-adapter"
    model = "stable-diffusion-v1-5 + h94/IP-Adapter"

    def __init__(self, mode: str = "style", device: Optional[str] = None,
                 base_model: str = "stable-diffusion-v1-5/stable-diffusion-v1-5"):
        assert mode in ("style", "face")
        self.mode = mode
        self.device = device or pick_device()
        self.base_model = base_model
        self._pipe = None

    def load(self) -> None:
        import torch
        from diffusers import StableDiffusionPipeline

        dtype = torch.float16 if self.device in ("mps", "cuda") else torch.float32
        # The default safety checker stays ON.
        pipe = StableDiffusionPipeline.from_pretrained(self.base_model, torch_dtype=dtype)
        weight = "ip-adapter-full-face_sd15.bin" if self.mode == "face" else "ip-adapter_sd15.bin"
        pipe.load_ip_adapter("h94/IP-Adapter", subfolder="models", weight_name=weight)
        pipe.to(self.device)
        pipe.enable_attention_slicing()
        self._pipe = pipe

    def unload(self) -> None:
        self._pipe = None

    def generate(self, prompt: str, reference: Image.Image, strength: float = 0.6, steps: int = 25,
                 guidance: float = 7.5, size: int = 512, seed: Optional[int] = None,
                 negative_prompt: str = "blurry, deformed, low quality") -> Image.Image:
        import torch

        self._pipe.set_ip_adapter_scale(strength)
        gen = torch.Generator("cpu").manual_seed(seed) if seed is not None else None
        return self._pipe(
            prompt=prompt, negative_prompt=negative_prompt, ip_adapter_image=reference.convert("RGB"),
            num_inference_steps=steps, guidance_scale=guidance, height=size, width=size, generator=gen,
        ).images[0]
