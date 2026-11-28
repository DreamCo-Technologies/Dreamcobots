"""Buddy media package with lazy public exports.

Keep lightweight policy modules importable on CPU-only control-plane runners without
loading audio/image/model dependencies. Heavy media runtime modules load on demand.
"""
from __future__ import annotations

from importlib import import_module

__all__ = ["BuddyMedia", "MediaResult", "ConsentRegistry", "ConsentError"]

def __getattr__(name: str):
    if name in {"ConsentRegistry", "ConsentError"}:
        module = import_module(".consent", __name__)
        return getattr(module, name)
    if name in {"BuddyMedia", "MediaResult"}:
        module = import_module(".core", __name__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
