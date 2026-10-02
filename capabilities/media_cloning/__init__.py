"""Voice and image cloning for Buddy.

Every public entry point requires a verified consent record. There is no
parameter that skips that check. Speech and pictures are Buddy's own code.
They stay on this machine. They do not call Chatterbox or Stable Diffusion.
"""
from .consent_gate import ConsentError, ConsentRecord, require_consent
from .image_clone import clone_image
from .voice_clone import clone_voice

__all__ = [
    "ConsentError",
    "ConsentRecord",
    "require_consent",
    "clone_voice",
    "clone_image",
]
