#!/usr/bin/env python3
"""Validate Pages connection index; never replace invalid data with a fake success."""
import json
import sys
from pathlib import Path
from urllib.parse import unquote

def validate(path: Path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"invalid or unreadable JSON: {exc}"]
    errors = []
    if not isinstance(data, dict) or not isinstance(data.get("files"), list):
        return ["expected object with files array"]
    base = data.get("source_base")
    if base is not None and base != "https://github.com/DreamCo-Technologies/Dreamcobots/blob/main/":
        errors.append("unrecognized source_base")
    seen = set()
    for i, row in enumerate(data["files"]):
        if not isinstance(row, dict):
            errors.append(f"row {i}: expected object")
            continue
        name, source = row.get("path"), row.get("source")
        if not isinstance(name, str) or not name or name.startswith("/") or ".." in Path(name).parts:
            errors.append(f"row {i}: invalid path")
            continue
        if name in seen:
            errors.append(f"row {i}: duplicate path")
        seen.add(name)
        if not isinstance(source, str):
            errors.append(f"row {i}: missing source")
        elif base is not None and unquote(source) != name:
            errors.append(f"row {i}: source mismatch")
        elif base is None and source != "https://github.com/DreamCo-Technologies/Dreamcobots/blob/main/" + name.replace(" ", "%20"):
            errors.append(f"row {i}: source URL mismatch")
    if len(data["files"]) < 1000:
        errors.append("unexpectedly small file inventory")
    return errors

if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("website/data/pages-connection-index.json")
    failures = validate(target)
    if failures:
        for message in failures[:30]:
            print("ERROR:", message, file=sys.stderr)
        sys.exit(1)
    print("Pages connection index valid")
