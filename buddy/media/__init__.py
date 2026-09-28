"""Buddy media: consent-gated voice and image cloning that runs locally (8 GB Apple silicon friendly)."""
from .consent import ConsentError, ConsentRegistry
from .core import BuddyMedia, MediaResult

__all__ = ["BuddyMedia", "MediaResult", "ConsentRegistry", "ConsentError"]
