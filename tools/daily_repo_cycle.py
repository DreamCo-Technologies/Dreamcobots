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
    return {
        "scan": scan(),
        "build": {"status": "planned", "erased": False},
        "train": {"status": "planned", "weights_downloaded": False},
        "bootcamp": {"courses": len(courses["courses"]), "ran": True, "certified": False},
        "green": False,
    }


def main() -> int:
    report = cycle()
    path = ROOT / "reports" / "DAILY_REPO_CYCLE.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"bootcamp": report["bootcamp"]["courses"], "green": False, "train": report["train"]["status"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
