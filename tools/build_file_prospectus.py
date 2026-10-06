#!/usr/bin/env python3
"""Generate a prospectus for every file in the repository.

Output: ``config/generated/file-prospectus/index.json`` plus one compact,
columnar shard per top-level folder (``config/generated/file-prospectus/<shard>.json``).
The data lives outside website/ to keep the Pages site under its size budget;
website/files.html reads it from raw.githubusercontent.com (main).
No per-file Markdown is written. For each file:

* ``path``, ``type`` (from the extension / location);
* ``purpose`` from the file's own header (module docstring, leading comment,
  Markdown heading, HTML <title>/meta description, JSON description/purpose/title
  key, workflow ``name:``); otherwise the nearest README; otherwise a heuristic
  marked ``auto-summary``. ``purpose_source`` says which;
* ``owner``: the bot (bots/<slug>.md and manifest sources) or division
  (App_bots/<division>.json), else a folder heuristic (``owner_source``);
* ``used_by``: files that import or reference it (Python imports, JS/TS
  imports/require incl. tsconfig aliases, HTML src/href, and literal repo-path
  mentions in code, workflows and configs), capped at 6 with a total count;
* ``tests``: test files that import/reference it or are named after it;
* ``readiness``: bot state from the fleet auditor, workflow static status from
  the Actions health report, or the audited code-folder verdict; else ``unknown``.

Owner-approved overrides from ``/buddy customize file:<path>`` live in
``config/files/prospectus-overrides.json`` (purpose / owner only).

``--check`` regenerates in memory and fails on drift.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

OUT_DIR = ROOT / "config" / "generated" / "file-prospectus"
OVERRIDES = ROOT / "config" / "files" / "prospectus-overrides.json"
FLEET_STATUS = ROOT / "website" / "data" / "fleet-runtime-status.json"
ACTIONS_HEALTH = ROOT / "website" / "data" / "actions-health-report.json"
MAX_READ = 400_000
COLUMNS = ["path", "type", "purpose", "purpose_source", "owner", "owner_source", "used_by", "used_by_count", "tests", "readiness"]
# Low-cardinality columns are stored as indexes into index.json "enums" to keep the Pages site small.
ENUM_COLUMNS = ("type", "purpose_source", "owner", "owner_source", "readiness")
USED_BY_SHOWN = 2
TESTS_SHOWN = 3

TYPE_BY_EXT = {
    ".py": "python", ".ts": "typescript", ".tsx": "typescript-react", ".js": "javascript", ".mjs": "javascript-module",
    ".cjs": "javascript", ".jsx": "javascript-react", ".json": "json", ".jsonl": "jsonl", ".yml": "yaml", ".yaml": "yaml",
    ".md": "markdown", ".mdx": "markdown", ".html": "html", ".css": "css", ".sh": "shell", ".txt": "text",
    ".toml": "toml", ".ini": "config", ".cfg": "config", ".csv": "csv", ".svg": "image-svg", ".png": "image",
    ".jpg": "image", ".jpeg": "image", ".gif": "image", ".webp": "image", ".ico": "image", ".pdf": "pdf",
    ".sql": "sql", ".prisma": "prisma-schema", ".lock": "lockfile", ".xml": "xml", ".webmanifest": "web-manifest",
}
FOLDER_OWNER = {
    ".github": "Actions (repository automation)", "buddy": "Buddy core runtime", "buddy_os": "Buddy OS governance",
    "website": "GitHub Pages site", "server": "API server", "client": "Web client", "shared": "Shared types (client+server)",
    "tools": "Repository tooling", "tests": "Test suite", "docs": "Documentation", "reports": "Generated reports",
    "config": "Configuration and generated registries", "benchmarks": "Benchmarks", "eval": "Evaluation harness",
    "framework": "Bot framework", "dreamco_platform": "DreamCo platform", "runtime": "Compiled bot runtime",
    "money_os": "Money OS (money: never triggerable)", "DreamPayments": "Payments (money: never triggerable)",
    "money": "Money (never triggerable)", "marketplace": "Marketplace", "systems": "Systems", "study_packs": "Study packs",
    "attached_assets": "Attached assets (owner uploads)", "original-bots": "Original bots", "data": "Data",
    "evidence": "Evidence records", "capabilities": "Capabilities", "command-center": "Command center",
    "huggingface": "Hugging Face study", "schemas": "Schemas", "plans": "Plans", "foundry": "Foundry",
}
CODE_FOLDER_READINESS_KEYS = {"buddy", "buddy_os", "server", "client", "website", "benchmarks", "eval", "framework",
                              "dreamco_platform", "runtime", "money_os", "marketplace", "systems"}
SECRET_RE = re.compile(r"(?<![A-Za-z0-9])(sk-[A-Za-z0-9_-]{8,}|gh[pousr]_[A-Za-z0-9]{20,}|xox[abp]-[A-Za-z0-9-]+|AKIA[0-9A-Z]{12,})")
PY_IMPORT_RE = re.compile(r"^\s*(?:from\s+(\.*[\w.]*)\s+import\s+([\w*, ()]+)|import\s+([\w., ]+))", re.M)
JS_IMPORT_RE = re.compile(r"""(?:import\s[^'"]*?from\s*|import\s*\(\s*|require\s*\(\s*|import\s+|export\s[^'"]*?from\s*)['"]([^'"]+)['"]""")
HTML_REF_RE = re.compile(r"""(?:src|href)\s*=\s*["']([^"'#?]+)""", re.I)
PATH_TOKEN_RE = re.compile(r"""(?<![\w/.-])((?:\.github/|[A-Za-z0-9_][\w.-]*/)[\w./-]*\.[A-Za-z0-9]{1,10})""")
JS_EXTS = (".ts", ".tsx", ".js", ".mjs", ".cjs", ".jsx", ".json")
TS_ALIASES = {"@/": "client/src/", "@shared/": "shared/"}
TEXTLIKE = {"python", "typescript", "typescript-react", "javascript", "javascript-module", "javascript-react", "json",
            "yaml", "markdown", "html", "css", "shell", "text", "toml", "config", "sql", "prisma-schema", "xml", "web-manifest", "jsonl"}
# Generated indexes that list every path would make every file "used by" them.
NO_REFERENCE_SCAN = ("config/generated/file-prospectus/", "website/data/run-prospectus", "website/data/fleet-runtime-status.json",
                     "config/bots/bot-manifests.generated.json", "config/generated/", "website/data/actions-health-report.json",
                     "config/buddy/run-with-buddy.generated.json", "reports/")
INDEX_THRESHOLD = 120
REFERENCE_SCAN_TYPES = {"python", "typescript", "typescript-react", "javascript", "javascript-module", "javascript-react",
                        "json", "yaml", "html", "shell", "toml"}


def list_files() -> list[str]:
    out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    files = sorted({p for p in out.split("\0") if p and (ROOT / p).is_file()})
    return files


def file_type(path: str) -> str:
    p = PurePosixPath(path)
    if path.startswith(".github/workflows/"):
        return "workflow"
    if p.name in {"package.json", "package-lock.json", "tsconfig.json", "pyproject.toml", "requirements.txt"} or p.name.startswith("requirements"):
        return "manifest/" + p.name
    if p.name.lower().startswith("readme"):
        return "readme"
    if p.name == "Dockerfile" or p.suffix == ".dockerfile":
        return "dockerfile"
    if re.search(r"(^|/)(test_[^/]+\.py|[^/]+\.test\.[a-z]+|[^/]+\.spec\.[a-z]+)$", path):
        return "test/" + TYPE_BY_EXT.get(p.suffix.lower(), "other")
    return TYPE_BY_EXT.get(p.suffix.lower(), "other" if p.suffix else "extensionless")


def read_text(path: str) -> str | None:
    full = ROOT / path
    try:
        if full.stat().st_size > MAX_READ * 5:
            with open(full, "rb") as handle:
                data = handle.read(MAX_READ)
        else:
            data = full.read_bytes()
    except OSError:
        return None
    if b"\0" in data[:4096]:
        return None
    return data.decode("utf-8", errors="replace")


def clean(text: str, limit: int = 140) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[`*_#>|]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip(" -:=")
    text = SECRET_RE.sub("[redacted]", text)
    if len(text) > limit:
        cut = text[:limit]
        text = (cut[: cut.rfind(" ")] if " " in cut[60:] else cut).rstrip(" ,;:") + "…"
    return text


def first_sentence(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    m = re.match(r"(.{12,}?[.!?])(\s|$)", text)
    return m.group(1) if m else text


def comment_header(text: str, styles: tuple[str, ...]) -> str:
    lines = text.splitlines()
    i = 0
    while i < len(lines) and (lines[i].startswith("#!") or not lines[i].strip() or lines[i].strip().startswith(("'use strict'", '"use strict"', "// @ts-", "/* eslint", "// eslint"))):
        i += 1
    if i < len(lines) and "/*" in styles and lines[i].strip().startswith("/*"):
        block = []
        for line in lines[i:i + 40]:
            block.append(line.strip().lstrip("/*").rstrip("*/").strip(" *"))
            if "*/" in line:
                break
        return " ".join(b for b in block if b and not b.startswith("@"))
    out = []
    for line in lines[i:i + 20]:
        s = line.strip()
        prefix = next((p for p in styles if p != "/*" and s.startswith(p)), None)
        if not prefix:
            break
        body = s[len(prefix):].strip()
        if body.startswith(("-*-", "type:", "noqa", "pylint", "eslint", "@ts-")):
            continue
        out.append(body)
    return " ".join(out)


def header_purpose(path: str, ftype: str, text: str) -> tuple[str, str] | None:
    try:
        base = ftype.split("/")[-1]
        if base == "python":
            try:
                doc = ast.get_docstring(ast.parse(text))
            except (SyntaxError, ValueError):
                doc = None
            if doc:
                return first_sentence(doc), "docstring"
            head = comment_header(text, ("#",))
            return (first_sentence(head), "header") if head else None
        if base in {"typescript", "typescript-react", "javascript", "javascript-module", "javascript-react", "css"}:
            head = comment_header(text, ("/*", "//"))
            return (first_sentence(head), "header") if head else None
        if ftype == "workflow":
            m = re.search(r"^name:\s*[\"']?(.+?)[\"']?\s*$", text, re.M)
            head = comment_header(text, ("#",))
            parts = [p for p in ((m.group(1) if m else ""), first_sentence(head) if head else "") if p]
            return (" — ".join(parts), "header") if parts else None
        if base in {"yaml", "shell", "toml", "config", "dockerfile", "text"}:
            head = comment_header(text, ("#",))
            if head:
                return first_sentence(head), "header"
            if base == "yaml":
                m = re.search(r"^(?:description|purpose|title|name):\s*[\"']?(.+?)[\"']?\s*$", text, re.M)
                return (m.group(1), "header") if m else None
            if base == "text":
                line = next((l for l in text.splitlines() if l.strip()), "")
                return (first_sentence(line), "header") if len(line.strip()) > 8 else None
            return None
        if base in {"markdown", "readme"}:
            title = re.search(r"^#{1,3}\s+(.+)$", text, re.M)
            body = ""
            for para in re.split(r"\n\s*\n", text):
                p = re.sub(r"^(?:#{1,6} [^\n]*\n)+", "", para.strip() + "\n").strip()
                lines = [l for l in p.splitlines() if l.strip()]
                keyvals = sum(bool(re.match(r"^[-*\s]*\**[\w /]{2,30}\**\s*:\**\s", l)) for l in lines)
                if lines and keyvals * 2 >= len(lines):
                    continue
                if p and not p.startswith(("#", "|", "```", "<", ">", "---", "!", "[!", "- ", "* ")) and len(p) > 20:
                    body = first_sentence(p)
                    break
            parts = [x for x in ((title.group(1) if title else ""), body) if x]
            return (": ".join(parts), "header") if parts else None
        if base == "html":
            title = re.search(r"<title>(.*?)</title>", text, re.S | re.I)
            desc = re.search(r"<meta\s+name=[\"']description[\"']\s+content=[\"']([^\"']+)", text, re.I)
            parts = [x.strip() for x in ((title.group(1) if title else ""), (desc.group(1) if desc else "")) if x and x.strip()]
            return (" — ".join(parts), "header") if parts else None
        if base in {"json", "web-manifest"} or ftype.startswith("manifest/package"):
            try:
                data = json.loads(text)
            except ValueError:
                return None
            if isinstance(data, dict):
                for key in ("description", "purpose", "summary", "title", "name", "division", "schema"):
                    val = data.get(key)
                    if isinstance(val, str) and len(val) > 3:
                        if key == "division":
                            n = len(data.get("bots") or [])
                            return f"Division manifest for {val}" + (f" ({n} bots)" if n else ""), "header"
                        return (f"{key}: {val}" if key in {"schema", "name"} else val), "header"
            return None
    except Exception:  # never let one odd file break the index
        return None
    return None


def auto_summary(path: str, ftype: str) -> str:
    p = PurePosixPath(path)
    parent = str(p.parent) if str(p.parent) != "." else "repository root"
    stem = p.stem.replace("_", " ").replace("-", " ")
    if ftype.startswith("test/"):
        target = re.sub(r"^test[_ ]|[. ]test$|[. ]spec$", "", p.stem.replace(".test", "").replace(".spec", ""))
        return f"auto-summary: tests for {target.replace('_', ' ').replace('-', ' ')}"
    if ftype.startswith("image") or ftype == "pdf":
        return f"auto-summary: {ftype} asset '{p.name}' in {parent}"
    if path.startswith("bots/"):
        return f"auto-summary: bot spec for {stem}"
    return f"auto-summary: {ftype} file '{stem}' in {parent}"


def resolve_py(module: str, importer: str, py_index: dict[str, str]) -> list[str]:
    hits = []
    if module.startswith("."):
        dots = len(module) - len(module.lstrip("."))
        base = PurePosixPath(importer).parent
        for _ in range(dots - 1):
            base = base.parent
        rest = module.lstrip(".")
        module = ".".join([*(x for x in base.parts if x), *([rest] if rest else [])])
    parts = module.split(".")
    for n in range(len(parts), 0, -1):
        key = ".".join(parts[:n])
        if key in py_index:
            hits.append(py_index[key])
            break
    return hits


def resolve_js(spec: str, importer: str, files: set[str]) -> str | None:
    for alias, target in TS_ALIASES.items():
        if spec.startswith(alias):
            spec = target + spec[len(alias):]
            base = PurePosixPath(spec)
            break
    else:
        if not spec.startswith("."):
            return None
        base = PurePosixPath(os.path.normpath(str(PurePosixPath(importer).parent / spec)))
    cand = str(base)
    options = [cand] + [cand + e for e in JS_EXTS] + [f"{cand}/index{e}" for e in JS_EXTS]
    if cand.endswith(".js"):
        options += [cand[:-3] + ".ts", cand[:-3] + ".tsx"]
    return next((o for o in options if o in files), None)


def build_references(files: list[str], types: dict[str, str], texts: dict[str, str]) -> dict[str, set[str]]:
    fileset = set(files)
    py_index: dict[str, str] = {}
    for f in files:
        if f.endswith(".py"):
            mod = f[:-3].replace("/", ".")
            if mod.endswith(".__init__"):
                mod = mod[: -len(".__init__")]
            py_index.setdefault(mod, f)
            # top-level tools/ and tests/ scripts are imported with sys.path hacks by bare name
            if f.count("/") == 1 and f.startswith(("tools/", "tests/")):
                py_index.setdefault(PurePosixPath(f).stem, f)
    used_by: dict[str, set[str]] = defaultdict(set)
    for f in files:
        text = texts.get(f)
        if text is None or f.startswith(NO_REFERENCE_SCAN):
            continue
        base = types[f].split("/")[-1]
        targets: set[str] = set()
        if base == "python":
            for m in PY_IMPORT_RE.finditer(text):
                if m.group(1) is not None:
                    mod = m.group(1)
                    targets.update(resolve_py(mod, f, py_index))
                    for name in re.split(r"[,\s()]+", m.group(2)):
                        if name and name != "*":
                            targets.update(t for t in resolve_py(f"{mod}.{name}" if mod.strip(".") else mod + name, f, py_index)
                                           if t.endswith(f"/{name}.py") or t.endswith(f"/{name}/__init__.py"))
                else:
                    for mod in m.group(3).split(","):
                        targets.update(resolve_py(mod.strip().split(" ")[0], f, py_index))
        if base in {"typescript", "typescript-react", "javascript", "javascript-module", "javascript-react"}:
            for spec in JS_IMPORT_RE.findall(text):
                hit = resolve_js(spec, f, fileset)
                if hit:
                    targets.add(hit)
        if base == "html":
            for ref in HTML_REF_RE.findall(text):
                if "://" in ref or ref.startswith(("mailto:", "data:", "javascript:")):
                    continue
                cand = os.path.normpath(str(PurePosixPath(f).parent / ref.lstrip("/"))) if not ref.startswith("/") else ref.lstrip("/")
                if cand in fileset:
                    targets.add(cand)
        if base in REFERENCE_SCAN_TYPES or types[f] == "workflow" or types[f].startswith("manifest/"):
            for token in PATH_TOKEN_RE.findall(text):
                token = token.lstrip("./")
                if token in fileset:
                    targets.add(token)
                elif f.startswith("website/") and ("website/" + token) in fileset:
                    targets.add("website/" + token)
        targets.discard(f)
        if len(targets) > INDEX_THRESHOLD and base in {"json", "jsonl", "yaml", "markdown"}:
            continue  # a catalog/index listing many paths is not a real "use"
        for t in targets:
            used_by[t].add(f)
    return used_by


def is_test(path: str, ftype: str) -> bool:
    return ftype.startswith("test/") or path.startswith("tests/")


def readiness_maps() -> tuple[dict[str, str], dict[str, str], dict[str, str], dict[str, list[str]]]:
    status = json.loads(FLEET_STATUS.read_text(encoding="utf-8")) if FLEET_STATUS.exists() else {}
    cols = status.get("bot_columns", [])
    bot_state = {row[0]: dict(zip(cols, row)).get("state", "unknown") for row in status.get("bots", [])}
    folder = {f["folder"]: f["verdict"] for f in status.get("code_folders", [])}
    health = json.loads(ACTIONS_HEALTH.read_text(encoding="utf-8")) if ACTIONS_HEALTH.exists() else {}
    workflows = {f["workflow"]: f.get("static_status", "unknown") for f in health.get("findings", [])}
    by_division: dict[str, list[str]] = defaultdict(list)
    for row in status.get("bots", []):
        r = dict(zip(cols, row))
        by_division[r.get("division", "")].append(r.get("state", "unknown"))
    return bot_state, folder, workflows, by_division


def owners_from_manifests() -> tuple[dict[str, str], set[str], set[str]]:
    from buddy.fleet_runtime.contract import load_manifests

    collection = load_manifests()
    owner: dict[str, str] = {}
    slugs, divisions = set(), set()
    per_file: dict[str, set[str]] = defaultdict(set)
    for b in collection["bots"]:
        slugs.add(b["slug"])
        divisions.add(b["division"])
        for src in b["sources"]:
            per_file[src.split("#")[0]].add(b["slug"])
    for path, bots in per_file.items():
        if path.startswith("bots/") and len(bots) == 1:
            owner[path] = "bot:" + next(iter(bots))
    for p in (ROOT / "App_bots").glob("*.json"):
        try:
            div = json.loads(p.read_text(encoding="utf-8")).get("division")
        except ValueError:
            div = None
        if div:
            owner[p.relative_to(ROOT).as_posix()] = "division:" + div
    return owner, slugs, divisions


def build(files: list[str] | None = None) -> dict[str, Any]:
    files = files if files is not None else list_files()
    types = {f: file_type(f) for f in files}
    texts = {f: t for f in files if types[f].split("/")[-1] in TEXTLIKE or types[f] in {"workflow", "readme", "dockerfile", "extensionless", "other"} or types[f].startswith("manifest/")
             for t in [read_text(f)] if t is not None}
    used_by = build_references(files, types, texts)
    manifest_owner, slugs, divisions = owners_from_manifests()
    bot_state, folder_verdict, wf_status, by_division = readiness_maps()
    overrides = json.loads(OVERRIDES.read_text(encoding="utf-8")).get("entries", {}) if OVERRIDES.exists() else {}
    readme_purpose: dict[str, str] = {}
    for f in files:
        if PurePosixPath(f).name.lower() in {"readme.md", "readme"} and f in texts:
            hp = header_purpose(f, "readme", texts[f])
            if hp:
                readme_purpose[str(PurePosixPath(f).parent)] = clean(hp[0], 90)
    tests_by_name: dict[str, list[str]] = defaultdict(list)
    for f in files:
        if is_test(f, types[f]):
            stem = re.sub(r"^test_|\.test$|\.spec$|_test$", "", PurePosixPath(f).stem.replace(".test", "").replace(".spec", ""))
            tests_by_name[stem.replace("-", "_").lower()].append(f)
    shards: dict[str, list[list[Any]]] = defaultdict(list)
    for f in files:
        ftype = types[f]
        purpose, source = None, None
        hp = header_purpose(f, ftype, texts[f]) if f in texts else None
        if hp and clean(hp[0]):
            purpose, source = clean(hp[0]), hp[1]
        else:
            parent = PurePosixPath(f).parent
            while str(parent) not in readme_purpose and str(parent) not in {".", ""}:
                parent = parent.parent
            if str(parent) in readme_purpose and str(parent) not in {".", ""}:
                purpose, source = f"part of {parent}/: {readme_purpose[str(parent)]}", "readme"
            else:
                purpose, source = auto_summary(f, ftype), "auto-summary"
        top = f.split("/")[0] if "/" in f else "(root)"
        owner = manifest_owner.get(f)
        owner_source = "manifest" if owner else "folder-heuristic"
        if not owner:
            owner = FOLDER_OWNER.get(top, "Repository root" if top == "(root)" else top)
        ov = overrides.get(f, {})
        if ov.get("purpose"):
            purpose, source = clean(ov["purpose"], 300), "owner"
        if ov.get("owner"):
            owner, owner_source = ("bot:" + ov["owner"]) if ov["owner"] in slugs else ("division:" + ov["owner"]), "owner"
        refs = sorted(used_by.get(f, ()))
        stem_key = PurePosixPath(f).stem.replace("-", "_").lower()
        tests = sorted({r for r in refs if is_test(r, types.get(r, ""))} | ({t for t in tests_by_name.get(stem_key, []) if t != f}
                                                                            if not is_test(f, ftype) else set()))
        if owner.startswith("bot:"):
            readiness = bot_state.get(owner[4:], "unknown")
        elif owner.startswith("division:"):
            states = by_division.get(owner[9:], [])
            readiness = (f"{states.count('TESTED')}/{len(states)} bots TESTED" if states else "unknown")
        elif ftype == "workflow":
            readiness = {"static_checks_passed": "CONFIGURED (static checks; runtime unknown)"}.get(wf_status.get(f, ""), wf_status.get(f, "unknown"))
        elif top in CODE_FOLDER_READINESS_KEYS and top in folder_verdict:
            readiness = f"folder {folder_verdict[top]}"
        elif is_test(f, ftype):
            readiness = "test"
        else:
            readiness = "unknown"
        shard = re.sub(r"[^A-Za-z0-9_-]+", "_", top.lstrip(".")) or "root"
        if top == "(root)":
            shard = "root"
        shards[shard].append([f, ftype, purpose, source, owner, owner_source, refs[:USED_BY_SHOWN], len(refs), tests[:TESTS_SHOWN], readiness])
    index = {
        "schema": "dreamco.file_prospectus.v1",
        "generator": "tools/build_file_prospectus.py",
        "truth_boundary": "Purposes come from each file's own header/docstring/README; 'auto-summary' marks a heuristic guess. used_by and tests are static references, not runtime proof. Readiness comes from the fleet auditor and Actions health report.",
        "columns": COLUMNS,
        "files": len(files),
        "purpose_sources": {},
        "shards": [],
    }
    counts: dict[str, int] = defaultdict(int)
    for shard, rows in sorted(shards.items()):
        for r in rows:
            counts[r[3]] += 1
        index["shards"].append({"name": shard, "url": f"{shard}.json", "files": len(rows)})
    index["purpose_sources"] = dict(sorted(counts.items()))
    positions = {c: COLUMNS.index(c) for c in ENUM_COLUMNS}
    enums = {c: sorted({r[i] for rows in shards.values() for r in rows}) for c, i in positions.items()}
    lookup = {c: {v: n for n, v in enumerate(vals)} for c, vals in enums.items()}
    index["enums"] = enums
    encoded = {}
    for name, rows in shards.items():
        out = []
        for r in sorted(rows):
            r = list(r)
            for c, i in positions.items():
                r[i] = lookup[c][r[i]]
            out.append(r)
        encoded[name] = out
    return {"index": index, "shards": encoded}


def decode_row(index: dict[str, Any], row: list[Any]) -> dict[str, Any]:
    """Expand one shard row to a dict using index.json columns + enums."""
    rec = dict(zip(index["columns"], row))
    for c, values in (index.get("enums") or {}).items():
        if isinstance(rec.get(c), int):
            rec[c] = values[rec[c]]
    return rec


def render(payload: dict[str, Any]) -> dict[Path, str]:
    out = {OUT_DIR / "index.json": json.dumps(payload["index"], indent=1, ensure_ascii=False) + "\n"}
    for name, rows in payload["shards"].items():
        body = ",\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in rows)
        out[OUT_DIR / f"{name}.json"] = '{"schema":"dreamco.file_prospectus.shard.v1","shard":' + json.dumps(name) + ',"rows":[\n' + body + "\n]}\n"
    return out


def customize(body_file: str, apply: bool) -> int:
    from buddy.fleet_runtime.customize import FILE_STORE, PatchError, _merge_store, extract_from_issue, validate_file_patch

    try:
        target, patch = extract_from_issue(Path(body_file).read_text(encoding="utf-8"))
        if not target.startswith("file:"):
            raise PatchError(["target must be file:<path>"])
        path = target[5:]
        _, slugs, divisions = owners_from_manifests()
        clean_patch = validate_file_patch(path, patch, set(list_files()), slugs | divisions)
        if apply:
            _merge_store(FILE_STORE, path, clean_patch)
    except PatchError as exc:
        print(json.dumps({"accepted": False, "errors": exc.errors}, indent=2))
        return 1
    print(json.dumps({"accepted": True, "target": target, "fields": clean_patch, "applied": apply}, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the per-file prospectus index for GitHub Pages.")
    parser.add_argument("--check", action="store_true", help="fail if the committed index is stale")
    parser.add_argument("--changed-since", metavar="REF",
                        help="with --check: only fail on rows of files changed since REF (PR gate; the daily run checks everything)")
    sub = parser.add_subparsers(dest="cmd")
    cust = sub.add_parser("customize", help="validate (and optionally apply) a /buddy customize file:<path> patch")
    cust.add_argument("--issue-body-file", required=True)
    cust.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    if args.cmd == "customize":
        return customize(args.issue_body_file, args.apply)
    payload = build()
    outputs = render(payload)
    if args.check and args.changed_since:
        diff = subprocess.run(["git", "diff", "--name-only", f"{args.changed_since}...HEAD"], cwd=ROOT, capture_output=True, text=True)
        if diff.returncode != 0:
            print(f"cannot diff against {args.changed_since}: {diff.stderr.strip()}", file=sys.stderr)
            return 2
        changed = {p for p in diff.stdout.split() if not p.startswith("config/generated/file-prospectus/")}
        fresh = {r[0]: decode_row(payload["index"], r) for rows in payload["shards"].values() for r in rows}
        committed: dict[str, Any] = {}
        index_path = OUT_DIR / "index.json"
        committed_index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else {"columns": COLUMNS}
        for shard in OUT_DIR.glob("*.json"):
            if shard.name != "index.json":
                committed.update({r[0]: decode_row(committed_index, r) for r in json.loads(shard.read_text(encoding="utf-8")).get("rows", [])})
        stale = sorted(p for p in changed if fresh.get(p) != committed.get(p))
        if stale:
            print(f"file prospectus drift for {len(stale)} file(s) changed in this branch: {stale[:10]}. "
                  "Run: python3 tools/build_file_prospectus.py", file=sys.stderr)
            return 1
        print(json.dumps({"ok": True, "changed_files_checked": len(changed)}))
        return 0
    if args.check:
        existing = {p for p in OUT_DIR.glob("*.json")} if OUT_DIR.exists() else set()
        stale = sorted(p.relative_to(ROOT).as_posix() for p, text in outputs.items()
                       if not p.exists() or p.read_text(encoding="utf-8") != text)
        extra = sorted(p.relative_to(ROOT).as_posix() for p in existing - set(outputs))
        if stale or extra:
            print(f"file prospectus drift: {len(stale)} stale shard(s) {stale[:8]}, {len(extra)} orphan(s) {extra[:5]}. "
                  "Run: python3 tools/build_file_prospectus.py", file=sys.stderr)
            return 1
        print(json.dumps({"ok": True, "files": json.loads(outputs[OUT_DIR / 'index.json'])["files"]}))
        return 0
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for stale in set(OUT_DIR.glob("*.json")) - set(outputs):
        stale.unlink()
    for path, text in outputs.items():
        path.write_text(text, encoding="utf-8")
    index = json.loads(outputs[OUT_DIR / "index.json"])
    print(json.dumps({"files": index["files"], "shards": len(index["shards"]), "purpose_sources": index["purpose_sources"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
