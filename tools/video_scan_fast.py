"""Fast, dependency-light video inventory for Buddy's video mastery pipeline.

This intentionally performs cheap metadata discovery first. Expensive vision/audio
models should be plugged into later stages so large collections can be scanned
incrementally, cached, checkpointed, and resumed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"}


def sha256_prefix(path: Path, size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        h.update(f.read(size))
    return h.hexdigest()


def ffprobe(path: Path) -> dict:
    cmd = [
        "ffprobe", "-v", "error", "-show_format", "-show_streams",
        "-of", "json", str(path)
    ]
    try:
        raw = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)
        return json.loads(raw)
    except (FileNotFoundError, subprocess.CalledProcessError, json.JSONDecodeError):
        return {"error": "ffprobe_unavailable_or_failed"}


def scan(root: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    existing = {}
    if output.exists():
        for line in output.read_text().splitlines():
            try:
                row = json.loads(line)
                existing[row["path"]] = row
            except (ValueError, KeyError):
                continue

    with output.open("w") as out:
        for path in sorted(p for p in root.rglob("*") if p.suffix.lower() in VIDEO_EXTENSIONS):
            key = str(path.resolve())
            if key in existing:
                out.write(json.dumps(existing[key], ensure_ascii=False) + "\n")
                continue
            stat = path.stat()
            row = {
                "schema": "dreamco.video.inventory.v1",
                "path": key,
                "size_bytes": stat.st_size,
                "modified_ns": stat.st_mtime_ns,
                "content_hash_prefix": sha256_prefix(path),
                "ffprobe": ffprobe(path),
                "analysis_state": "inventory_complete",
                "next_stage": "scene_change_and_adaptive_sampling",
            }
            out.write(json.dumps(row, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path, default=Path("artifacts/video_inventory.jsonl"))
    args = parser.parse_args()
    scan(args.root, args.output)
