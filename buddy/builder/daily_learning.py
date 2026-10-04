"""Daily learning tracker. A study file is not a learned result.

The teach list is every study pack and bot file without a recorded score.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ["movie", "lecture", "ebook", "book", "course", "lab", "podcast", "video", "paper", "model card", "dataset note", "manual", "simulation", "game", "commercial", "osha", "union course", "college catalog", "audio lesson", "worksheet", "exam note", "syllabus", "code repo", "issue thread", "pull request", "benchmark row", "counterexample", "user note"]


def scan() -> dict:
    packs = sorted(path.relative_to(ROOT).as_posix() for path in (ROOT / "study_packs").rglob("*") if path.is_file())
    bots = sorted(path.stem for path in (ROOT / "bots").glob("*.md"))
    return {
        "sources": SOURCES,
        "study_files": len(packs),
        "bots": len(bots),
        "learned": [],
        "needs_teaching": packs[:50] + bots[:50],
        "needs_teaching_count": len(packs) + len(bots),
        "recursive": "daily rescan, no score invented",
        "production_ready": 0,
    }


def main() -> int:
    report = scan()
    (ROOT / "reports" / "DAILY_LEARNING.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"study_files": report["study_files"], "bots": report["bots"], "learned": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
