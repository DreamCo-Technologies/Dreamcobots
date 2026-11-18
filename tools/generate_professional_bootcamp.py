#!/usr/bin/env python3
"""Validate and publish the professional Bootcamp contract for GitHub Pages."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "config/buddy-professional-bootcamp.json"
OUTPUT = ROOT / "website/data/professional-bootcamp.json"
REPORT = ROOT / "reports/PROFESSIONAL_BOOTCAMP.md"


def build() -> tuple[str, str]:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    if data.get("schema") != "dreamco.buddy_professional_bootcamp.v1":
        raise ValueError("unexpected Bootcamp schema")
    required = {"software", "reverse_engineering", "research", "invention", "business", "education", "science", "robotics", "biology", "personal"}
    ids = {track.get("id") for track in data.get("tracks", [])}
    if ids != required:
        raise ValueError(f"Bootcamp tracks differ from required set: {sorted(required ^ ids)}")
    if data["task_learning"]["default"] != "off" or data["task_learning"]["capture"] != "per_task_opt_in":
        raise ValueError("task learning must be opt-in")
    if data["truth"]["trained_weight_artifacts"] != 0:
        raise ValueError("repository has no verified trained weight artifact")
    rendered = json.dumps(data, indent=2, sort_keys=True) + "\n"
    report = "\n".join([
        "# Buddy Professional Bootcamp",
        "",
        f"- Tracks: {len(data['tracks'])}",
        f"- Benchmark dimensions: {len(data['benchmarks']['dimensions'])}",
        f"- Training methods: {len(data['weight_training']['methods'])}",
        f"- Gesture commands: {len(data['gesture_control']['commands'])}",
        "- Verified weight-training runs: 0",
        "- Verified professional deployments: 0",
        "",
        "This contract connects consented task demonstrations to redacted examples, repeated benchmarks, hidden holdouts and optional training handoffs. It does not capture users, run apps, access a camera, rent GPUs or train weights by itself.",
        "",
    ])
    return rendered, report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered, report = build()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"stale generated file: {OUTPUT.relative_to(ROOT)}")
        if not REPORT.exists() or REPORT.read_text(encoding="utf-8") != report:
            raise SystemExit(f"stale generated file: {REPORT.relative_to(ROOT)}")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered, encoding="utf-8")
    REPORT.write_text(report, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
