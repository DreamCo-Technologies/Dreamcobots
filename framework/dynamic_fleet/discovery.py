"""Filesystem discovery for reusable bot/module assets.

Discovery is intentionally best-effort: malformed assets are reported instead
of preventing healthy assets from being discovered. Counts are never capped.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .action_control_plane import Module


def discover_json_modules(root: str | Path) -> tuple[list[Module], list[dict[str, Any]]]:
    base = Path(root)
    modules: list[Module] = []
    errors: list[dict[str, Any]] = []
    if not base.exists():
        return modules, [{"path": str(base), "error": "root_not_found"}]

    for path in sorted(base.rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("JSON root must be an object")
            module_id = str(data.get("module_id") or data.get("bot_id") or data.get("id") or path.stem)
            raw_caps = data.get("capabilities", data.get("skills", []))
            if isinstance(raw_caps, str):
                raw_caps = [raw_caps]
            capabilities = {str(x) for x in raw_caps if x is not None}
            modules.append(Module(module_id=module_id, capabilities=capabilities, metadata={"source": str(path)}))
        except Exception as exc:  # discovery must not hide other valid assets
            errors.append({"path": str(path), "error": type(exc).__name__, "message": str(exc)})
    return modules, errors
