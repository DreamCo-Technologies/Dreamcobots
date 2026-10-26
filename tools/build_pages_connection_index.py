#!/usr/bin/env python3
"""Index tracked paths and Pages reachability with a compact, verifiable source base."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "website/data/pages-connection-index.json"


def build(root: Path = ROOT) -> dict:
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=root).decode().split("\0")
    rows = []
    for name in sorted(set(tracked) - {""}):
        path = root / name
        if not path.is_file():
            continue
        served = name.startswith("website/")
        page = served and path.suffix == ".html"
        rows.append({"path": name, "kind": "page" if page else "asset" if served else "repository_source",
                     "source": quote(name, safe="/"),
                     "page": name[len("website/"):] if page else None})
    return {"schema": "dreamco.pages_connection_index.v1", "source_base": "https://github.com/DreamCo-Technologies/Dreamcobots/blob/main/", "files": rows,
            "counts": {"tracked_files": len(rows), "pages": sum(r["kind"] == "page" for r in rows)},
            "scope": "Tracked paths only; source visibility and page reachability do not prove runtime behavior.",
            "evidence": {"features": "data/pages-feature-audit.json", "runtime": "data/fleet-runtime-status.json"}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(build(), separators=(",", ":")) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != content:
            print("Pages connection index is stale; run python3 tools/build_pages_connection_index.py")
            return 1
    else:
        OUTPUT.write_text(content)
    print(json.dumps(build()["counts"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
