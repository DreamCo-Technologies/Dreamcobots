"""Per-bot learning scan. A file is scanned. A score is not invented."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def scan() -> dict:
    bots = sorted(path.stem for path in (ROOT / "bots").glob("*.md"))
    original = json.loads((ROOT / "original-bots" / "STATUS.json").read_text())["bots"]
    buddy = sorted(path.relative_to(ROOT).as_posix() for path in (ROOT / "buddy").rglob("*") if path.is_file() and path.suffix == ".py")
    rows = [{"name": name, "scanned": True, "learned": False} for name in bots]
    rows.extend({"name": row["id"], "scanned": True, "learned": False, "state": row.get("state")} for row in original)
    return {"bots": rows, "bot_count": len(rows), "buddy_files": len(buddy), "learned": 0}


def main() -> int:
    report = scan()
    (ROOT / "reports" / "BOT_LEARNING_SCAN.json").write_text(json.dumps({"bot_count": report["bot_count"], "buddy_files": report["buddy_files"], "learned": 0, "sample": report["bots"][:5]}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"bot_count": report["bot_count"], "buddy_files": report["buddy_files"], "learned": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
