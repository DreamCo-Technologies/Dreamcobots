"""Connectors for real local models. Importing this file does not download weights."""
from __future__ import annotations

import importlib.util
from typing import Optional


class ConnectorMissing(RuntimeError):
    """The Python package for this model is not installed."""


CONNECTORS = (
    {"id": "chatterbox", "kind": "voice", "clones": True, "module": "chatterbox.tts", "model": "ResembleAI/chatterbox", "license": "MIT"},
    {"id": "f5-tts", "kind": "voice", "clones": True, "module": "f5_tts", "model": "SWivid/F5-TTS", "license": "read the model card before selling output"},
    {"id": "openvoice", "kind": "voice", "clones": True, "module": "openvoice", "model": "myshell-ai/OpenVoiceV2", "license": "MIT"},
    {"id": "kokoro", "kind": "voice", "clones": False, "module": "kokoro", "model": "hexgrad/Kokoro-82M", "license": "Apache-2.0"},
    {"id": "mlx-whisper", "kind": "transcribe", "clones": False, "module": "mlx_whisper", "model": "mlx-community/whisper-small-mlx", "license": "MIT"},
    {"id": "sd15-ip-adapter", "kind": "image", "clones": True, "module": "diffusers", "model": "stable-diffusion-v1-5 + h94/IP-Adapter", "license": "CreativeML Open RAIL-M"},
    {"id": "instantid", "kind": "image", "clones": True, "module": "diffusers", "model": "InstantX/InstantID", "license": "read the model card; too large for 8GB"},
    {"id": "mflux", "kind": "image", "clones": False, "module": "mflux", "model": "FLUX.1-schnell 4-bit", "license": "FLUX non-commercial terms may apply"},
    {"id": "huggingface-hub", "kind": "weights", "clones": False, "module": "huggingface_hub", "model": "user-selected open weights", "license": "per model card"},
)


def probe() -> list[dict]:
    rows = []
    for item in CONNECTORS:
        rows.append({
            **item,
            "package_installed": importlib.util.find_spec(item["module"].split(".")[0]) is not None,
            "weights_downloaded": False,
            "sandbox_verified": False,
        })
    return rows


def first_voice_clone():
    """Return a voice connector that can clone. Do not substitute a non-cloning voice."""
    from .voice import ChatterboxBackend

    installed = {row["id"]: row["package_installed"] for row in probe()}
    if installed["chatterbox"]:
        return ChatterboxBackend()
    if installed["f5-tts"]:
        return F5Backend()
    if installed["openvoice"]:
        return OpenVoiceBackend()
    raise ConnectorMissing("No voice-clone package is installed. Install chatterbox-tts, f5-tts, or openvoice. Kokoro is not a clone.")


class F5Backend:
    name = "f5-tts"
    model = "SWivid/F5-TTS"
    clones = True

    def __init__(self):
        self._m = None

    def load(self) -> None:
        try:
            from f5_tts.api import F5TTS
        except Exception as exc:
            raise ConnectorMissing("f5-tts is not installed") from exc
        self._m = F5TTS()

    def unload(self) -> None:
        self._m = None

    def synthesize(self, text, reference_path, ref_text: str = "", **_):
        if self._m is None:
            self.load()
        wav, sr, _spec = self._m.infer(ref_file=str(reference_path), ref_text=ref_text, gen_text=text)
        return wav, int(sr)


class OpenVoiceBackend:
    name = "openvoice"
    model = "myshell-ai/OpenVoiceV2"
    clones = True

    def __init__(self, checkpoint: Optional[str] = None):
        self.checkpoint = checkpoint
        self._converter = None

    def load(self) -> None:
        try:
            from openvoice.api import ToneColorConverter
        except Exception as exc:
            raise ConnectorMissing("openvoice is not installed") from exc
        if not self.checkpoint:
            raise ConnectorMissing("OpenVoice needs a local checkpoint path. This connector does not download one.")
        self._converter = ToneColorConverter(self.checkpoint)

    def unload(self) -> None:
        self._converter = None

    def synthesize(self, text, reference_path, **_):
        if self._converter is None:
            self.load()
        raise ConnectorMissing("OpenVoice still needs a base-speaker wav and a target embedding on this machine. Nothing was synthesized.")


class KokoroBackend:
    """Fast local speech. It does not copy a reference voice."""

    name = "kokoro"
    model = "hexgrad/Kokoro-82M"
    clones = False

    def load(self) -> None:
        try:
            import kokoro  # noqa: F401
        except Exception as exc:
            raise ConnectorMissing("kokoro is not installed") from exc

    def unload(self) -> None:
        return None

    def synthesize(self, text, reference_path, **_):
        raise ConnectorMissing("Kokoro does not clone a reference voice.")
