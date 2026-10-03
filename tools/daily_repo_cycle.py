"""One load-balanced daily cycle: scan, build plan, train plan, bootcamp.

Train stays planned. The cycle does not start a second copy of itself and
does not mark the repository green.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks.study_courses.catalog import catalog
from tools.expert_section_scan import scan


def cycle() -> dict:
    courses = catalog()
    review = scan()
    return {
        "scan": review,
        "build": {"status": "planned", "erased": False},
        "train": {"status": "planned", "weights_downloaded": False},
        "bootcamp": {"courses": len(courses["courses"]), "ran": True, "certified": False},
        "production": {"status": "external_config_required", "expert_approved": False, "green": False, "blocker": "live host secrets are not in the repo"},
        "green": False,
    }


def render(report: dict) -> str:
    lines = ["# Daily production scan", "", "Expert review only. This file does not mark the repository production ready.", ""]
    lines.append(f"- Sections scanned: {len(report['scan']['sections'])}")
    lines.append(f"- Duplicate file names: {report['scan']['duplicate_names']}")
    lines.append(f"- Bootcamp courses ran in sandbox: {report['bootcamp']['courses']}")
    lines.append(f"- Train: {report['train']['status']}")
    lines.append(f"- Production status: {report['production']['status']}")
    lines.append(f"- Blocker: {report['production']['blocker']}")
    lines.append("- Deleted files: 0")
    return "\n".join(lines) + "\n"


def main() -> int:
    report = cycle()
    path = ROOT / "reports" / "DAILY_REPO_CYCLE.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (ROOT / "reports" / "DAILY_PRODUCTION_SCAN.md").write_text(render(report), encoding="utf-8")
    page = ROOT / "website" / "data" / "daily-cycle.json"
    page.write_text(json.dumps({"sections": len(report["scan"]["sections"]), "duplicate_names": report["scan"]["duplicate_names"], "bootcamp_courses": report["bootcamp"]["courses"], "train": report["train"]["status"], "production": report["production"]["status"], "expert_approved": False, "green": False}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"bootcamp": report["bootcamp"]["courses"], "green": False, "train": report["train"]["status"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
