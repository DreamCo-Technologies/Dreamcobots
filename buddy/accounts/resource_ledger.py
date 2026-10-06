"""Resource ledger. A site is sandboxed, not mastered.

GitHub, Grok, and ChatGPT are labels. No login is stored, and a gap stays
open until a measured run exists.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESOURCES = ["github", "grok", "chatgpt", "huggingface", "pages", "actions", "codecademy", "youtube", "ebook", "lecture", "movie", "benchmark", "goal-list", "bot-file"]


def ledger() -> dict:
    rows = [{"name": name, "sandboxed": True, "mastered": False, "benchmark_score": None, "gap": "no measured run", "profile": "label only"} for name in RESOURCES]
    return {"resources": rows, "count": len(rows), "logged_in": False, "mastered": 0, "production_ready": 0}


def main() -> int:
    report = ledger()
    (ROOT / "reports" / "RESOURCE_LEDGER.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"count": report["count"], "mastered": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
