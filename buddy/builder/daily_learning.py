"""Daily learning tracker. A study file is not a learned result.

The teach list is every study pack and bot file without a recorded score.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ["movie", "lecture", "ebook", "book", "course", "lab", "podcast", "video", "paper", "model card", "dataset note", "manual", "simulation", "game", "commercial", "osha", "union course", "college catalog", "audio lesson", "worksheet", "exam note", "syllabus", "code repo", "issue thread", "pull request", "benchmark row", "counterexample", "user note", "official docs", "standard", "glossary", "worked example", "failure note", "second pass", "open weight card", "open source card"]


def scan() -> dict:
    packs = sorted(path.relative_to(ROOT).as_posix() for path in (ROOT / "study_packs").rglob("*") if path.is_file())
    bots = sorted(path.stem for path in (ROOT / "bots").glob("*.md"))
    benchmarks = sorted(path.relative_to(ROOT).as_posix() for path in (ROOT / "benchmarks").rglob("*") if path.is_file())
    goals = ["reports/MASSIVE_GOAL_LIST.md"] if (ROOT / "reports" / "MASSIVE_GOAL_LIST.md").exists() else []
    gaps = ["reports/PLUGIN_GAP_BOT.json"] if (ROOT / "reports" / "PLUGIN_GAP_BOT.json").exists() else []
    needs = packs + bots + benchmarks + goals + gaps
    return {
        "sources": SOURCES,
        "study_files": len(packs),
        "bots": len(bots),
        "benchmarks": len(benchmarks),
        "goals": len(goals),
        "gaps": len(gaps),
        "learned": [],
        "needs_teaching_count": len(needs),
        "needs_teaching_sample": needs[:30],
        "recursive": "one daily scan, no score invented",
        "production_ready": 0,
    }


def main() -> int:
    report = scan()
    (ROOT / "reports" / "DAILY_LEARNING.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = ["# Daily learning", "", f"Learned: {len(report['learned'])}", f"Needs teaching: {report['needs_teaching_count']}", "", "No score was invented.", ""]
    (ROOT / "reports" / "DAILY_LEARNING.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"study_files": report["study_files"], "bots": report["bots"], "benchmarks": report["benchmarks"], "learned": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
