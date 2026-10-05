"""Strategy analysis team. It checks that a section exists.

A live run is a file check. It does not call a model or invent a score.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IDEAS = ["name the section", "count the files", "link the folder", "record a missing score", "keep the run local", "require approval", "do not invent a winner"]


def analyze() -> dict:
    sections = sorted(path.name for path in ROOT.iterdir() if path.is_dir() and not path.name.startswith(".") and path.name != "node_modules")
    rows = [{"section": name, "files": sum(1 for item in (ROOT / name).rglob("*") if item.is_file()), "score": None, "model_called": False} for name in sections]
    return {"team": ["recorder", "checker", "reporter"], "ideas": IDEAS, "sections": rows, "winner": None}


def main() -> int:
    report = analyze()
    (ROOT / "reports" / "STRATEGY_ANALYSIS.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"sections": len(report["sections"]), "winner": None}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
