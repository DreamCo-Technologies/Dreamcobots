"""Build the DreamCo seed candidate catalog from Buddy's existing mastery curriculum.

The result is a discovery backlog, not a verified package inventory or study
guide. It never downloads, imports, executes, evaluates or trains on a package.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("server/seed-buddy-bot.ts")
OUTPUT = Path("data/buddy-library-seed-catalog.json")
START_MARKER = "COMPLETE LIBRARY MASTERY CURRICULUM"
END_MARKER = "AUTONOMOUS AGENT ENGINE"


def _slug(value: str) -> str:
    value = value.lower().replace("c++", "cpp").replace("c#", "c-sharp").replace("f#", "f-sharp").replace(".net", "dotnet")
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def _split_top_level(value: str) -> list[str]:
    result: list[str] = []
    current: list[str] = []
    depth = 0
    for char in value:
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth = max(0, depth - 1)
        if char == "," and depth == 0:
            token = "".join(current).strip()
            if token:
                result.append(token)
            current = []
        else:
            current.append(char)
    token = "".join(current).strip()
    if token:
        result.append(token)
    return result


def build_catalog(root: Path = ROOT) -> dict[str, Any]:
    source_path = root / SOURCE
    source = source_path.read_text(encoding="utf-8")
    start = source.find(START_MARKER)
    stop = source.find(END_MARKER, start + len(START_MARKER))
    if start < 0 or stop < 0 or stop <= start:
        raise ValueError("Buddy library mastery curriculum section markers are missing")
    section = source[start:stop]
    headings = list(re.finditer(r"──\s*(.*?)\s*──", section))
    if not headings:
        raise ValueError("no library curriculum category headings were found")
    candidates: dict[str, dict[str, Any]] = {}
    raw_candidate_count = 0
    for index, heading in enumerate(headings):
        body_start = heading.end()
        body_end = headings[index + 1].start() if index + 1 < len(headings) else len(section)
        body = re.sub(r"\s*\n\s*", " ", section[body_start:body_end])
        body = re.sub(r"━+", " ", body).strip()
        category = heading.group(1).strip()
        for raw_value in _split_top_level(body):
            raw = re.sub(r"\s+", " ", raw_value).strip()
            raw = raw.lstrip("-• ").rstrip(" \t:;,.")
            if len(raw) < 2 or raw == "};" or raw.lower() == "or engagement footers":
                continue
            raw_candidate_count += 1
            name = re.split(r"\s+\(", raw, maxsplit=1)[0].strip()
            key = re.sub(r"[^a-z0-9]+", "", name.lower())
            if not key:
                continue
            candidate_id = "seed-" + _slug(name)
            item = candidates.get(key)
            if item is None:
                item = {
                    "id": candidate_id,
                    "name": name,
                    "categories": [],
                    "raw_variants": [],
                    "status": "seed_candidate_unverified",
                    "artifact_type": "unclassified_candidate",
                    "version": None,
                    "official_documentation": None,
                    "license": "unknown",
                    "rights": {
                        "download": "pending",
                        "execution": "prohibited_by_seed_catalog",
                        "evaluation": "pending",
                        "training": "pending",
                    },
                    "source": {
                        "path": SOURCE.as_posix(),
                        "section": category,
                        "source_kind": "DreamCo-curated-seed-list",
                    },
                }
                candidates[key] = item
            if category not in item["categories"]:
                item["categories"].append(category)
            if raw not in item["raw_variants"]:
                item["raw_variants"].append(raw)
    rows = list(candidates.values())
    ids = [row["id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("seed candidate slug collision; add an explicit canonical ID mapping")
    return {
        "schema": "dreamco.buddy_library_seed_catalog.v1",
        "status": "partial_unverified_seed_inventory",
        "source_path": SOURCE.as_posix(),
        "source_section": START_MARKER,
        "generated_by": "tools/build_buddy_library_seed_catalog.py",
        "raw_candidate_count": raw_candidate_count,
        "unique_candidate_count": len(rows),
        "worldwide_completeness_claimed": False,
        "rights_boundary": (
            "Names are candidate discovery seeds only. No upstream package identity, version, license, "
            "official documentation, download, execution, evaluation or training permission is established."
        ),
        "candidates": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = json.dumps(build_catalog(args.root), ensure_ascii=False, indent=2) + "\n"
    output = args.root / OUTPUT
    if args.check:
        if not output.exists() or output.read_text(encoding="utf-8") != payload:
            raise SystemExit("Buddy library seed catalog is stale; run tools/build_buddy_library_seed_catalog.py")
        print("Buddy library seed catalog: PASS")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(payload, encoding="utf-8")
    print(f"Built {json.loads(payload)['unique_candidate_count']} unverified library discovery candidates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
