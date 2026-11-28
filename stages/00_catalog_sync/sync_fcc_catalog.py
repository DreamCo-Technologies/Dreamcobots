"""Compatibility entry point for the policy-gated FreeCodeCamp metadata delta sync."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CATALOG_MODULE_PATH = Path(__file__).with_name("catalog_sync.py")
SOURCE_ID = "freecodecamp"
SOURCE_URL = "https://www.youtube.com/@freecodecamp"


def _load_catalog_module():
    spec = importlib.util.spec_from_file_location("dreamco_catalog_sync", CATALOG_MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Stage 00 catalog sync module could not be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sync_fcc_catalog(
    *,
    ledger: Path | None = None,
    policy_path: Path | None = None,
    enumerator: Any = None,
) -> dict[str, Any]:
    """Delta-sync official FreeCodeCamp channel metadata; never fetch media/transcripts."""
    module = _load_catalog_module()
    kwargs: dict[str, Any] = {}
    if enumerator is not None:
        kwargs["enumerator"] = enumerator
    return module.sync_sources(
        [{"source_id": SOURCE_ID, "url": SOURCE_URL}],
        ledger=ledger or module.DEFAULT_LEDGER,
        policy_path=policy_path or module.DEFAULT_POLICY,
        **kwargs,
    )


if __name__ == "__main__":
    import json
    print(json.dumps(sync_fcc_catalog(), indent=2))
