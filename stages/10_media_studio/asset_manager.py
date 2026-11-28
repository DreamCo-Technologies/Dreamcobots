"""Hash and register local media assets without uploading them."""
from __future__ import annotations
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def write_asset_manifest(path: Path, records: list[dict[str, Any]], output: Path) -> dict[str, Any]:
    root = path.resolve()
    assets = []
    for row in records:
        relative = Path(str(row.get("relative_path") or ""))
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Asset paths must be repository-relative and cannot traverse directories.")
        asset_path = (root / relative).resolve()
        if root not in asset_path.parents or not asset_path.is_file():
            raise ValueError(f"Asset path is missing or escapes the asset root: {relative}")
        assets.append({**row, "relative_path": relative.as_posix(),
                       "observed_sha256": sha256_file(asset_path), "size_bytes": asset_path.stat().st_size})
    payload = {"schema": "dreamco.media.asset_manifest.v1", "assets": assets}
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{output.name}.", dir=str(output.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, output)
    except Exception:
        try: os.unlink(temporary)
        except OSError: pass
        raise
    return payload
