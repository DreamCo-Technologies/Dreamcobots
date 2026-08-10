#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPLACEMENTS = {
    "server/fleet-runtime.ts": [
        ("z.record(z.unknown())", "z.record(z.string(), z.unknown())"),
    ],
    "server/media-quality-lab.ts": [
        ("z.record(z.number().min(0).max(1))", "z.record(z.string(), z.number().min(0).max(1))"),
        ("z.record(z.boolean())", "z.record(z.string(), z.boolean())"),
        (
            "const scorecard = catalog.scorecards[modality];",
            "const scorecard = catalog.scorecards[modality] as { dimensions: Record<string, number>; release_threshold: number };",
        ),
    ],
    "server/routes.ts": [
        ("error.errors", "error.issues"),
    ],
}


def main() -> int:
    changed = []
    for rel, replacements in REPLACEMENTS.items():
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        original = text
        for old, new in replacements:
            if old not in text:
                raise SystemExit(f"Expected migration pattern not found in {rel}: {old}")
            text = text.replace(old, new)
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed.append(rel)
    print({"ok": True, "changed": changed})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
