"""Verify actual render files and their hashes before delivery certification."""
from __future__ import annotations
import hashlib
from pathlib import Path
from typing import Any

def verify_render_outputs(records: list[dict[str, Any]], output_root: Path) -> dict[str, Any]:
    if not isinstance(records, list) or not records:
        return {"passed": False, "verified_count": 0, "errors": ["No rendered outputs were supplied."]}
    root = output_root.resolve()
    errors = []
    verified = 0
    for row in records:
        relative = Path(str(row.get("relative_path") or ""))
        if relative.is_absolute() or ".." in relative.parts:
            errors.append("Output path is unsafe.")
            continue
        path = (root / relative).resolve()
        if root not in path.parents or not path.is_file():
            errors.append(f"Rendered output is missing or outside the output root: {relative}")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != row.get("sha256"):
            errors.append(f"Rendered output hash mismatch: {relative}")
            continue
        if not row.get("shot_id"):
            errors.append(f"Rendered output is missing shot provenance: {relative}")
            continue
        verified += 1
    return {"passed": not errors and verified == len(records), "verified_count": verified, "errors": errors}
