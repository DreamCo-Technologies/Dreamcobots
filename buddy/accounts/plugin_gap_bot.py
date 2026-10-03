"""Gap bot. It compares plugin actions with Buddy files.

A gap is work that is not done. This scan does not download weights and does
not claim a frontier model.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from buddy.accounts.plugin_manager import FREE


def scan() -> dict:
    buddy_files = [path.relative_to(ROOT).as_posix() for path in (ROOT / "buddy").rglob("*.py")]
    gaps = []
    for provider, actions in FREE.items():
        for action in actions:
            gaps.append({"provider": provider, "action": action, "covered": False, "reason": "named action has no executed plugin run"})
    return {
        "buddy_files": len(buddy_files),
        "plugin_actions": sum(len(rows) for rows in FREE.values()),
        "gaps": gaps,
        "sources": ["github", "hugging-face", "frontier"],
        "weights_downloaded": False,
        "frontier_claim": False,
        "plan": ["study model cards", "score tasks before routing", "fill one plugin gap with a tested sandbox", "keep secrets on the host"],
    }


def main() -> int:
    report = scan()
    path = ROOT / "reports" / "PLUGIN_GAP_BOT.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"gaps": len(report["gaps"]), "frontier_claim": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
