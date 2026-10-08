"""Voice and image cloning for Buddy.

Every public entry point requires a verified consent record. There is no
parameter that skips that check. Speech and pictures are Buddy's own code.
They stay on this machine. They do not call Chatterbox or Stable Diffusion.
"""
from .consent_gate import ConsentError, ConsentRecord, require_consent


def __getattr__(name):
    """Consent/schema checks do not require the optional image/audio stack."""
    if name == "clone_image":
        from .image_clone import clone_image
        return clone_image
    if name == "clone_voice":
        from .voice_clone import clone_voice
        return clone_voice
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "ConsentError",
    "ConsentRecord",
    "require_consent",
    "clone_voice",
    "clone_image",
]
