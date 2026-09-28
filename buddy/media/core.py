"""BuddyMedia: Buddy's own voice + image cloning engine.

Flow for every job: consent gate -> memory slot -> generate -> watermark -> save -> manifest -> ledger.
"""
from __future__ import annotations

import hashlib
import os
import secrets
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import soundfile as sf
from PIL import Image
from PIL.PngImagePlugin import PngInfo

from . import provenance as prov
from .consent import ConsentRegistry
from .memory_guard import ModelSlot
from .voice import ChatterboxBackend, prepare_reference, synthesize_long


@dataclass
class MediaResult:
    path: Path
    manifest_path: Path
    consent_id: str
    kind: str


class BuddyMedia:
    def __init__(self, root="buddy/media/store", voice_backend=None, image_backend=None, min_free_gb: float = 2.0):
        self.root = Path(root)
        (self.root / "outputs").mkdir(parents=True, exist_ok=True)
        self.consents = ConsentRegistry(self.root / "consents.json")
        self.ledger = self.root / "ledger.jsonl"
        self.slot = ModelSlot(min_free_gb=min_free_gb)
        self._voice = voice_backend
        self._image = image_backend
        self._wm_key = self._load_key()

    # -- setup helpers --
    def _load_key(self) -> str:
        env = os.environ.get("BUDDY_MEDIA_WATERMARK_KEY")
        if env:
            return env
        kp = self.root / "watermark.key"
        if not kp.exists():
            kp.write_text(secrets.token_hex(32))
            os.chmod(kp, 0o600)
        return kp.read_text().strip()

    def _voice_backend(self):
        self._voice = self._voice or ChatterboxBackend()
        return self._voice

    def _image_backend(self, mode: str):
        if self._image is None or getattr(self._image, "mode", mode) != mode:
            from .image import IPAdapterBackend

            self.slot.release()
            self._image = IPAdapterBackend(mode=mode)
        return self._image

    def register_consent(self, reference_path, subject_name, kind, granted_by, attestation, scope=("personal",), ttl_days=None):
        return self.consents.register(reference_path, subject_name, kind, granted_by, attestation, scope, ttl_days)

    def _base_info(self, kind, consent, backend, ref_path, text_or_prompt):
        return {
            "kind": kind,
            "consent_id": consent.consent_id,
            "subject_name": consent.subject_name,
            "reference_sha256": consent.reference_sha256,
            "backend": backend.name,
            "model": backend.model,
            "input_sha256": hashlib.sha256(text_or_prompt.encode()).hexdigest(),
            "input_chars": len(text_or_prompt),
            "created_at": time.time(),
            "watermark": {"scheme": f"keyed-spread-spectrum-{kind}", "key_id": prov.key_id(self._wm_key)},
        }

    # -- voice --
    def clone_voice(self, text: str, reference, purpose: str = "personal", out=None, **kw) -> MediaResult:
        consent = self.consents.require(reference, "voice", purpose)  # gate BEFORE any model loads
        backend = self._voice_backend()
        prepared = prepare_reference(reference, out_dir=self.root / "tmp")
        self.slot.acquire(backend)
        wav, sr = synthesize_long(backend, text, prepared, **kw)
        wav = prov.watermark_audio(wav, self._wm_key)
        out = Path(out or self.root / "outputs" / f"voice_{int(time.time())}_{uuid.uuid4().hex[:6]}.wav")
        sf.write(str(out), wav, sr)
        manifest = prov.write_manifest(out, self._base_info("voice", consent, backend, reference, text))
        prov.append_ledger(self.ledger, {**manifest, "purpose": purpose})
        return MediaResult(out, prov.manifest_path(out), consent.consent_id, "voice")

    # -- image --
    def clone_image(self, prompt: str, reference, purpose: str = "personal", mode: str = "style",
                    out=None, seed: Optional[int] = None, **kw) -> MediaResult:
        consent = self.consents.require(reference, "image", purpose)
        backend = self._image_backend(mode)
        self.slot.acquire(backend)
        ref_img = Image.open(reference)
        img = backend.generate(prompt, ref_img, seed=seed, **kw)
        arr = prov.watermark_image(np.array(img.convert("RGB")), self._wm_key)
        out = Path(out or self.root / "outputs" / f"image_{int(time.time())}_{uuid.uuid4().hex[:6]}.png")
        info = self._base_info("image", consent, backend, reference, prompt)
        meta = PngInfo()
        meta.add_text("ai_generated", "true")
        meta.add_text("buddy_consent_id", consent.consent_id)
        Image.fromarray(arr).save(out, pnginfo=meta)
        manifest = prov.write_manifest(out, info)
        prov.append_ledger(self.ledger, {**manifest, "purpose": purpose})
        return MediaResult(out, prov.manifest_path(out), consent.consent_id, "image")

    # -- verification --
    def verify(self, path) -> dict:
        path = Path(path)
        if path.suffix.lower() in (".wav", ".flac"):
            x, _ = sf.read(str(path), dtype="float32", always_2d=True)
            found, z = prov.detect_audio_watermark(x.mean(axis=1), self._wm_key)
        else:
            found, z = prov.detect_image_watermark(np.array(Image.open(path).convert("RGB")), self._wm_key)
        mp = prov.manifest_path(path)
        return {"watermark_found": bool(found), "z_score": round(z, 2), "manifest_present": mp.exists()}

    def status(self) -> dict:
        # Honest by construction: nothing here claims verification. Those stages need recorded evidence.
        return {
            "voice_clone": {"stage": "implemented", "sandbox_verified": False, "benchmark_verified": False},
            "image_clone": {"stage": "implemented", "sandbox_verified": False, "benchmark_verified": False},
            "loaded_model": getattr(self.slot.loaded, "name", None),
        }

    def close(self) -> None:
        self.slot.release()
