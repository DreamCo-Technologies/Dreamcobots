"""Self-training session. It starts only when the user turns it on.

A lesson is the user's own note. No weights are downloaded, no secret is
stored, and the session does not mark a model production ready.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def start(note: str, enabled: bool) -> dict:
    if not enabled:
        raise PermissionError("self-training is off until the user turns it on")
    if not note.strip():
        raise ValueError("a lesson needs the user's note")
    if "sk_live" in note or "api_key" in note.lower():
        raise PermissionError("a secret cannot be a lesson")
    return {"enabled": True, "started": True, "note": note.strip()[:240], "weights_downloaded": False, "production_ready": False, "frontier_claim": False}


def main() -> int:
    report = start("practice note", True)
    (ROOT / "reports" / "SELF_TRAINING.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    html = '''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Self-training | Buddy</title><link rel="stylesheet" href="styles.css?v=41"><link rel="stylesheet" href="actions.css?v=4"></head>
<body><div id="nav-placeholder"></div><script src="nav.js"></script><main class="actions-shell">
<header class="actions-header"><div><p class="actions-kicker">Your model</p><h1>Self-training</h1><p>Turn it on, then save your own note. No weights are downloaded.</p></div></header>
<section class="actions-review"><button class="btn btn-primary" id="enable" type="button">Turn self-training on</button> <label>Lesson <input id="note" value=""></label> <button class="btn btn-outline" id="save" type="button">Save lesson</button><p id="status">Self-training is off.</p></section>
</main>
<script>
document.getElementById("enable").addEventListener("click", () => { localStorage.setItem("dreamco.self-training", "on"); document.getElementById("status").textContent = "Self-training is on. No weights downloaded."; });
document.getElementById("save").addEventListener("click", () => { if (localStorage.getItem("dreamco.self-training") !== "on") { document.getElementById("status").textContent = "Turn it on first."; return; } const note = document.getElementById("note").value.trim(); if (!note) return; localStorage.setItem("dreamco.self-training.note", note.slice(0, 240)); document.getElementById("status").textContent = "Lesson saved in this browser."; });
</script>
</body></html>
'''
    (ROOT / "website" / "self-training.html").write_text(html)
    print(json.dumps({"started": report["started"], "weights_downloaded": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
