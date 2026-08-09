#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "notes-to-code-program.json"
OUT = ROOT / "config" / "generated" / "notes-to-code-backlog.json"

EXCLUDED = {"node_modules", ".git", ".buddy-local", "dist", "build", "coverage"}
ACTION_WORDS = re.compile(r"\b(add|build|create|implement|fix|repair|connect|integrate|test|benchmark|support|make|ensure|generate|upgrade|improve|move|scan|audit|deploy|automate|train)\b", re.I)
CHECKBOX = re.compile(r"^\s*[-*]\s*\[( |x|X)\]\s+(.+)$")
HEADING = re.compile(r"^#{1,6}\s+(.+)$")


def note_files() -> list[Path]:
    rows = []
    for pattern in ("*.md", "*.txt"):
        for path in ROOT.rglob(pattern):
            if any(part in EXCLUDED for part in path.parts):
                continue
            if path == OUT:
                continue
            rows.append(path)
    return sorted(set(rows))


def classify(text: str) -> str:
    lower = text.lower()
    if any(word in lower for word in ("bug", "broken", "fail", "error", "fix", "repair")):
        return "bug"
    if any(word in lower for word in ("benchmark", "competitor", "gap", "parity")):
        return "benchmark_gap"
    if any(word in lower for word in ("architecture", "system", "infrastructure", "shared")):
        return "architecture"
    if ACTION_WORDS.search(text):
        return "capability"
    return "documentation"


def stable_id(path: Path, line: int, text: str) -> str:
    digest = hashlib.sha256(f"{path.relative_to(ROOT)}|{line}|{text}".encode()).hexdigest()[:12]
    return f"note-{digest}"


def main() -> int:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    backlog = []
    scanned = 0
    actionable = 0
    for path in note_files():
        heading = None
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception:
            continue
        scanned += 1
        for lineno, raw in enumerate(lines, 1):
            match = HEADING.match(raw)
            if match:
                heading = match.group(1).strip()
                continue
            checkbox = CHECKBOX.match(raw)
            text = checkbox.group(2).strip() if checkbox else raw.strip()
            if len(text) < 12:
                continue
            kind = classify(text)
            is_actionable = bool(checkbox and checkbox.group(1).strip().lower() != "x") or (kind != "documentation" and bool(ACTION_WORDS.search(text)))
            if not is_actionable:
                continue
            actionable += 1
            backlog.append({
                "note_id": stable_id(path, lineno, text),
                "source": str(path.relative_to(ROOT)),
                "line": lineno,
                "heading": heading,
                "text": text[:1200],
                "classification": kind,
                "status": "needs_review",
                "repository_search_required": True,
                "dedupe_required": True,
                "canonical_owner_required": True,
                "acceptance_tests_required": True,
                "sandbox_requirements_required": True,
                "code_candidate_status": "not_generated_until_existing_implementation_checked",
            })
    payload = {
        "schema": "dreamco.notes_to_code_backlog.v1",
        "source_program": str(CONFIG.relative_to(ROOT)),
        "files_scanned": scanned,
        "actionable_note_count": actionable,
        "items": backlog,
        "pipeline": cfg["pipeline"],
        "truth_boundary": cfg["truth_rule"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "files_scanned": scanned, "actionable_notes": actionable, "output": str(OUT.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
