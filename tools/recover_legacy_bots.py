#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "config" / "legacy-bot-recovery-program.json"
OUT = ROOT / "config" / "generated" / "legacy-bot-recovery-manifest.json"
REPORT = ROOT / "reports" / "LEGACY_BOT_RECOVERY.md"

TEXT_EXTS = {".json", ".py", ".js", ".ts", ".tsx", ".md", ".txt", ".yml", ".yaml"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", "coverage", ".buddy-local"}
BOT_WORD = re.compile(r"bot|agent|assistant|worker|scout|engine|manager|planner|optimizer|analyst|builder", re.I)


def slugify(value: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", value)
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value


def canonical_bots() -> dict[str, dict]:
    rows = {}
    base = ROOT / "App_bots"
    if not base.exists():
        return rows
    for path in sorted(base.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        division = payload.get("division") or path.stem
        for bot in payload.get("bots", []):
            slug = slugify(str(bot.get("slug") or bot.get("displayName") or ""))
            if slug:
                rows[slug] = {"division": division, "category": bot.get("category"), "capabilities": bot.get("capabilities", []), "source": str(path.relative_to(ROOT))}
    return rows


def extract_python(path: Path, text: str) -> dict:
    names, funcs, classes = [], [], []
    try:
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
                if BOT_WORD.search(node.name): names.append(node.name)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                funcs.append(node.name)
    except Exception:
        pass
    return {"candidate_names": names, "classes": classes[:100], "functions": funcs[:200]}


def extract_generic(path: Path, text: str) -> dict:
    names = []
    for pattern in [r"class\s+([A-Za-z_][A-Za-z0-9_]*)", r"name\s*[:=]\s*[\"']([^\"']+)", r"displayName\s*[:=]\s*[\"']([^\"']+)"]:
        for match in re.finditer(pattern, text):
            value = match.group(1).strip()
            if BOT_WORD.search(value): names.append(value)
    return {"candidate_names": list(dict.fromkeys(names))[:50], "classes": [], "functions": []}


def extract_json(path: Path, text: str) -> dict:
    names, capabilities, category, division = [], [], None, None
    try:
        data = json.loads(text)
        def visit(obj):
            nonlocal category, division
            if isinstance(obj, dict):
                for key in ("slug", "name", "displayName", "bot_name"):
                    value = obj.get(key)
                    if isinstance(value, str) and BOT_WORD.search(value): names.append(value)
                if isinstance(obj.get("capabilities"), list): capabilities.extend(str(x) for x in obj["capabilities"][:100])
                category = category or obj.get("category")
                division = division or obj.get("division")
                for value in obj.values(): visit(value)
            elif isinstance(obj, list):
                for value in obj: visit(value)
        visit(data)
    except Exception:
        return extract_generic(path, text)
    return {"candidate_names": list(dict.fromkeys(names))[:50], "capabilities": list(dict.fromkeys(capabilities))[:200], "category": category, "division": division, "classes": [], "functions": []}


def main() -> int:
    program = json.loads(PROGRAM.read_text(encoding="utf-8"))
    canonical = canonical_bots()
    items = []
    states = Counter()
    candidate_slugs = Counter()
    for root_name in program["source_roots"]:
        base = ROOT / root_name
        if not base.exists():
            items.append({"source_root": root_name, "state": "invalid_or_unreadable", "reason": "source root missing"})
            states["invalid_or_unreadable"] += 1
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
                continue
            rel = str(path.relative_to(ROOT))
            ext = path.suffix.lower()
            record = {"source_root": root_name, "path": rel, "size_bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            if root_name == "App_bots":
                record.update({"state": "canonical_existing", "reason": "canonical source"}); states["canonical_existing"] += 1; items.append(record); continue
            if ext not in TEXT_EXTS:
                record.update({"state": "supporting_asset", "reason": "non-text legacy/supporting asset"}); states["supporting_asset"] += 1; items.append(record); continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except Exception as exc:
                record.update({"state": "invalid_or_unreadable", "reason": str(exc)}); states["invalid_or_unreadable"] += 1; items.append(record); continue
            extracted = extract_json(path, text) if ext == ".json" else extract_python(path, text) if ext == ".py" else extract_generic(path, text)
            names = extracted.get("candidate_names", [])
            slugs = [slugify(name) for name in names if slugify(name)]
            for slug in slugs: candidate_slugs[slug] += 1
            exact = [slug for slug in slugs if slug in canonical]
            if exact:
                state = "legacy_duplicate"
                reason = f"matches canonical bot(s): {', '.join(exact[:10])}"
            elif slugs:
                state = "recoverable_new_bot"
                reason = "bot-like identity found with no exact canonical slug match"
            else:
                state = "supporting_asset"
                reason = "no bot identity detected; retain as legacy/supporting knowledge"
            record.update({"state": state, "reason": reason, "candidate_names": names, "candidate_slugs": slugs, "canonical_matches": exact, "extracted": {k:v for k,v in extracted.items() if k != "candidate_names"}})
            states[state] += 1
            items.append(record)

    duplicate_legacy_candidates = [slug for slug, count in candidate_slugs.items() if count > 1]
    recoverable = [row for row in items if row.get("state") == "recoverable_new_bot"]
    payload = {
        "schema": "dreamco.legacy_bot_recovery_manifest.v1",
        "canonical_bot_count": len(canonical),
        "source_roots": program["source_roots"],
        "file_count": len(items),
        "state_counts": dict(states),
        "recoverable_candidate_file_count": len(recoverable),
        "duplicate_legacy_candidate_slugs": duplicate_legacy_candidates,
        "items": items,
        "promotion_gate": program["promotion_gate"],
        "truth_boundary": program["truth_rule"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True); REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = ["# Legacy Bot Recovery", "", f"- Canonical bots: **{len(canonical)}**", f"- Files inventoried: **{len(items)}**", f"- Recoverable candidate files: **{len(recoverable)}**", f"- Duplicate legacy candidate slugs: **{len(duplicate_legacy_candidates)}**", "", "## State counts", ""]
    for key, value in sorted(states.items()): lines.append(f"- {key}: {value}")
    lines += ["", "## Recoverable candidates", ""]
    for row in recoverable[:500]: lines.append(f"- `{row['path']}` → {', '.join(row.get('candidate_slugs',[])[:8]) or 'unnamed'}")
    REPORT.write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(json.dumps({"ok": True, "canonical_bots": len(canonical), "files": len(items), "states": dict(states), "recoverable_candidate_files": len(recoverable), "output": str(OUT.relative_to(ROOT))}, indent=2))
    return 0

if __name__ == "__main__": raise SystemExit(main())
