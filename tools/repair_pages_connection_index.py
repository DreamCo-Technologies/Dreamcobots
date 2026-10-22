#!/usr/bin/env python3
"""Fail-closed validation and optional regeneration of the Pages connection index.

Run: python tools/repair_pages_connection_index.py --check
     python tools/repair_pages_connection_index.py --repair
Never hides unrelated JSON failures or changes other repository files.
"""
import argparse
import json
from pathlib import Path
from tools.build_pages_connection_index import build, OUTPUT, ROOT

def verify(path: Path = OUTPUT) -> tuple[bool, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return False, f"invalid JSON: {exc}"
    if not isinstance(payload, dict) or payload.get("schema") != "dreamco.pages_connection_index.v1":
        return False, "unexpected schema"
    if not isinstance(payload.get("files"), list):
        return False, "missing files list"
    return True, f"valid index ({len(payload['files'])} records)"

def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--repair", action="store_true")
    args = parser.parse_args()
    ok, message = verify()
    if args.check:
        print(message)
        return 0 if ok else 1
    if ok:
        print("Index already valid; no overwrite")
        return 0
    # Regenerate only from tracked paths. No user content is indexed.
    payload = build(ROOT)
    if not payload["files"]:
        print("Refusing to overwrite index with empty inventory")
        return 1
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")
    ok, message = verify()
    print(message)
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
