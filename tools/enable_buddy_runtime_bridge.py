#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUDDY_HTML = ROOT / "website" / "buddy.html"
BRIDGE_JS = ROOT / "website" / "buddy-runtime-bridge.js"
SCRIPT_TAG = '  <script src="buddy-runtime-bridge.js?v=1" defer></script>\n'
ANCHOR = '  <script src="buddy.js?v=28" defer></script>\n'


def enable_bridge(html: str) -> str:
    if SCRIPT_TAG.strip() in html:
        return html
    if ANCHOR not in html:
        raise ValueError("Buddy page script anchor was not found.")
    return html.replace(ANCHOR, ANCHOR + SCRIPT_TAG, 1)


def main() -> int:
    if not BRIDGE_JS.exists() or BRIDGE_JS.stat().st_size < 500:
        raise SystemExit("Buddy runtime bridge JavaScript is missing or unexpectedly small.")
    original = BUDDY_HTML.read_text(encoding="utf-8")
    updated = enable_bridge(original)
    BUDDY_HTML.write_text(updated, encoding="utf-8")
    print({"ok": True, "changed": updated != original, "bridge": str(BRIDGE_JS.relative_to(ROOT))})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
