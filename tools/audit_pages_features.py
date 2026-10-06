#!/usr/bin/env python3
"""Check that every GitHub Pages page's advertised features link to real code, data or routes.

For each ``website/**/*.html`` page the auditor collects its features and checks them statically:

* ``script``   -- every local ``<script src>`` exists;
* ``style``    -- every local stylesheet exists;
* ``data``     -- every literal ``fetch('…')`` / data URL used by the page's own scripts exists in website/;
* ``api``      -- ``/api/…`` calls need the DreamCo server; static Pages cannot serve them (``server-only``);
* ``control``  -- every ``<button id>`` / ``<form id>`` is referenced by the page's scripts or has an inline
                  handler; unreferenced ones are ``dead`` (the control does nothing);
* ``text``     -- "coming soon", "not yet implemented", "lorem ipsum", "under construction" in visible text.

Verdict per page: ``broken`` (missing script/data), ``stub`` (dead controls, stub text, or only
server-only data), ``partial`` (some server-only features), ``working``. Output:
``website/data/pages-feature-audit.json`` (read by ``page-truth.js``, which labels stub features on the
page itself) and ``reports/PAGES_FEATURE_AUDIT.md``. ``--check`` fails on drift; ``--check-regressions``
fails if a page got worse than ``config/bots/pages-feature-baseline.json``.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "website"
OUT = SITE / "data" / "pages-feature-audit.json"
REPORT = ROOT / "reports" / "PAGES_FEATURE_AUDIT.md"
BASELINE = ROOT / "config" / "bots" / "pages-feature-baseline.json"
SHARED_SCRIPTS = {"nav.js", "theme.js", "page-actions.js", "repository-actions.js", "page-truth.js"}
FETCH_RE = re.compile(r"""fetch\(\s*(['"])([^'"$`]+)\1""")
FETCH_TPL_RE = re.compile(r"""fetch\(\s*`([^`$]+)`""")
DATA_URL_RE = re.compile(r"""['"]((?:\./)?data/[\w./-]+\.(?:json|jsonl|csv|txt))['"]""")
API_RE = re.compile(r"""['"`](/api/[\w./-]*)""")
STUB_TEXT_RE = re.compile(r"\b(coming soon|not yet implemented|lorem ipsum|under construction|placeholder page)\b", re.I)
VERDICT_RANK = {"working": 0, "partial": 1, "stub": 2, "broken": 3}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.scripts: list[str] = []
        self.styles: list[str] = []
        self.inline: list[str] = []
        self.controls: list[dict[str, Any]] = []
        self.text: list[str] = []
        self._in_script = False
        self._skip = 0
        self._forms: list[dict[str, Any]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k: (v or "") for k, v in attrs}
        if tag == "script":
            self._in_script = True
            if a.get("src"):
                self.scripts.append(a["src"])
        elif tag == "style":
            self._skip += 1
        elif tag == "link" and "stylesheet" in a.get("rel", "") and a.get("href"):
            self.styles.append(a["href"])
        if tag == "form":
            self._forms.append({"id": a.get("id", ""), "action": bool(a.get("action")),
                                "inline": any(k.startswith("on") for k in a)})
        if tag in {"button", "form"} and a.get("id"):
            inline = any(k.startswith("on") for k in a)
            form = self._forms[-1] if (tag == "button" and self._forms and a.get("type", "submit") == "submit") else None
            self.controls.append({"tag": tag, "id": a["id"], "inline_handler": inline, "type": a.get("type", ""),
                                  "has_action": bool(a.get("action")), "label": "", "form": form})

    def handle_endtag(self, tag: str) -> None:
        if tag == "form" and self._forms:
            self._forms.pop()
        if tag == "script":
            self._in_script = False
        elif tag == "style":
            self._skip = max(0, self._skip - 1)

    def handle_data(self, data: str) -> None:
        if self._in_script:
            self.inline.append(data)
        elif not self._skip:
            self.text.append(data)
            if self.controls and not self.controls[-1]["label"] and data.strip():
                self.controls[-1]["label"] = data.strip()[:60]


def local(ref: str) -> str | None:
    if not ref or "://" in ref or ref.startswith(("//", "data:", "mailto:", "#", "javascript:")):
        return None
    return ref.split("?")[0].split("#")[0]


def resolve(page: Path, ref: str) -> Path:
    if ref.startswith("/"):
        return SITE / ref.lstrip("/")
    return (page.parent / ref).resolve()


def audit_page(page: Path) -> dict[str, Any]:
    html = page.read_text(encoding="utf-8", errors="replace")
    parser = PageParser()
    try:
        parser.feed(html)
    except Exception:  # malformed HTML: audit what was parsed
        pass
    rel = page.relative_to(SITE).as_posix()
    features: list[dict[str, Any]] = []
    js_texts = list(parser.inline)
    for src in parser.scripts:
        ref = local(src)
        if not ref:
            continue
        target = resolve(page, ref)
        ok = target.is_file()
        features.append({"kind": "script", "target": ref, "status": "ok" if ok else "missing"})
        if ok and PurePosixPath(ref).name not in SHARED_SCRIPTS:
            js_texts.append(target.read_text(encoding="utf-8", errors="replace"))
    for href in parser.styles:
        ref = local(href)
        if ref:
            features.append({"kind": "style", "target": ref, "status": "ok" if resolve(page, ref).is_file() else "missing"})
    js = "\n".join(js_texts)
    data_refs = {m.group(2) for m in FETCH_RE.finditer(js)} | {m.group(1) for m in FETCH_TPL_RE.finditer(js)} | set(DATA_URL_RE.findall(js))
    for ref in sorted(data_refs):
        if ref.startswith("/api/") or ref.startswith("api/"):
            continue
        r = local(ref)
        if not r or not re.search(r"\.(json|jsonl|csv|txt|md|html)$", r):
            continue
        features.append({"kind": "data", "target": r, "status": "ok" if resolve(page, r).is_file() else "missing"})
    for api in sorted(set(API_RE.findall(js))):
        features.append({"kind": "api", "target": api, "status": "server-only"})
    def referenced(ident: str) -> bool:
        if not ident:
            return False
        cid = re.escape(ident)
        return re.search(rf"""(['"`#]){cid}(['"`\s.\[:,)])|\b{cid}\b\s*[.=]""", js) is not None

    for c in parser.controls:
        form = c.get("form")
        via_form = bool(form) and (form["action"] or form["inline"] or referenced(form["id"]))
        ok = referenced(c["id"]) or c["inline_handler"] or c["has_action"] or via_form
        features.append({"kind": "control", "target": f"{c['tag']}#{c['id']}", "label": c["label"],
                         "status": "ok" if ok else "dead"})
    visible = " ".join(parser.text)
    for m in sorted({m.group(1).lower() for m in STUB_TEXT_RE.finditer(visible)}):
        features.append({"kind": "text", "target": m, "status": "stub-text"})
    statuses = [f["status"] for f in features]
    if "missing" in statuses:
        verdict = "broken"
    elif "dead" in statuses or "stub-text" in statuses:
        verdict = "stub"
    elif "server-only" in statuses:
        data_ok = any(f["kind"] == "data" and f["status"] == "ok" for f in features)
        verdict = "partial" if data_ok else "stub"
    else:
        verdict = "working"
    return {"page": rel, "verdict": verdict, "has_page_truth": "nav.js" in " ".join(parser.scripts),
            "counts": {s: statuses.count(s) for s in sorted(set(statuses))},
            "issues": [f for f in features if f["status"] != "ok"]}


def build() -> dict[str, Any]:
    pages = sorted(p for p in SITE.rglob("*.html") if "node_modules" not in p.parts)
    rows = [audit_page(p) for p in pages]
    summary: dict[str, int] = {v: 0 for v in VERDICT_RANK}
    for r in rows:
        summary[r["verdict"]] += 1
    return {
        "schema": "dreamco.pages_feature_audit.v1",
        "generator": "tools/audit_pages_features.py",
        "truth_boundary": "Static check: scripts, styles and data a page uses exist; controls are wired to code; /api calls need the DreamCo server and cannot work on static Pages. A 'working' page can still have logic bugs; this proves wiring, not behaviour.",
        "pages": len(rows), "summary": summary, "rows": rows,
    }


def render_report(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lines = ["# Pages Feature Audit", "", "_Generated by `tools/audit_pages_features.py`. Do not hand-edit._", "",
             payload["truth_boundary"], "", "| Verdict | Pages |", "|---|---:|"]
    lines += [f"| {k} | {v} |" for k, v in s.items()]
    lines += [f"| **Total** | **{payload['pages']}** |", "",
              "Pages that load `nav.js` show these findings on the page itself (`page-truth.js` labels dead controls and "
              "server-only features as **stub**).", "", "## Pages that are not fully working", ""]
    for r in payload["rows"]:
        if r["verdict"] == "working":
            continue
        issues = "; ".join(f"{i['kind']} `{i['target']}` {i['status']}" for i in r["issues"][:8])
        more = f" (+{len(r['issues']) - 8} more)" if len(r["issues"]) > 8 else ""
        lines.append(f"- **{r['page']}** — {r['verdict']}: {issues}{more}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--check-regressions", action="store_true")
    parser.add_argument("--write-baseline", action="store_true")
    args = parser.parse_args(argv)
    payload = build()
    text = json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n"
    report = render_report(payload)
    rc = 0
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text or not REPORT.exists() or REPORT.read_text(encoding="utf-8") != report:
            print("pages feature audit is stale. Run: python3 tools/audit_pages_features.py", file=sys.stderr)
            rc = 1
    if args.check_regressions:
        base = json.loads(BASELINE.read_text(encoding="utf-8")).get("pages", {}) if BASELINE.exists() else {}
        worse = [f"{r['page']}: {base[r['page']]} -> {r['verdict']}" for r in payload["rows"]
                 if r["page"] in base and VERDICT_RANK[r["verdict"]] > VERDICT_RANK[base[r["page"]]]]
        new_bad = [f"{r['page']}: new page is {r['verdict']}" for r in payload["rows"]
                   if r["page"] not in base and r["verdict"] in {"broken"}]
        if worse or new_bad:
            print("Pages feature regressions:\n  " + "\n  ".join(worse + new_bad), file=sys.stderr)
            rc = 1
    if not (args.check or args.check_regressions):
        OUT.write_text(text, encoding="utf-8")
        REPORT.write_text(report, encoding="utf-8")
    if args.write_baseline:
        BASELINE.write_text(json.dumps({"schema": "dreamco.pages_feature_baseline.v1",
                                        "policy": "CI fails when a page's verdict gets worse or a new page is broken. Raise the baseline when pages improve.",
                                        "pages": {r["page"]: r["verdict"] for r in payload["rows"]}}, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"pages": payload["pages"], **payload["summary"]}))
    return rc


if __name__ == "__main__":
    sys.exit(main())
