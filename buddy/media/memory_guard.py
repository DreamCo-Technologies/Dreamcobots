"""One heavy model in memory at a time. Essential on 8 GB unified memory."""
from __future__ import annotations

import gc


def free_accelerator() -> None:
    gc.collect()
    try:
        import torch

        if hasattr(torch, "mps") and torch.backends.mps.is_available():
            torch.mps.empty_cache()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except Exception:
        pass


def available_gb() -> float | None:
    try:
        import psutil

        return psutil.virtual_memory().available / 1e9
    except Exception:
        return None


class ModelSlot:
    def __init__(self, min_free_gb: float = 2.0):
        self.min_free_gb = min_free_gb
        self._backend = None

    @property
    def loaded(self):
        return self._backend

    def acquire(self, backend):
        if self._backend is backend:
            return backend
        self.release()
        free = available_gb()
        if free is not None and free < self.min_free_gb:
            raise MemoryError(
                f"Only {free:.1f} GB free (< {self.min_free_gb} GB). Close the dev stack "
                "(Redis, Node, Vite, browsers) or route this job to a cloud GPU."
            )
        backend.load()
        self._backend = backend
        return backend

    def release(self) -> None:
        if self._backend is not None:
            try:
                self._backend.unload()
            finally:
                self._backend = None
                free_accelerator()
