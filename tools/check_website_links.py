#!/usr/bin/env python3
"""Fail when a website navigation link points at a page that does not exist.

Checked sources (static, offline, no network):
- ``href: '...'`` entries and literal ``href="..."`` attributes in the shared
  nav scripts (``website/nav.js``, ``website/desk-chrome.js``), resolved
  against ``website/``.
- ``<a href>`` links inside ``<nav>...</nav>`` blocks of ``website/**/*.html``,
  resolved against the page's own folder.

External (http/https/mailto/tel/data/javascript), fragment-only, and
templated (``${...}``) links are skipped. Exit code 1 if any local nav link is
broken; a JSON summary is printed either way.

``--all`` widens the scan to every internal Pages link/route in ``website/``:
all ``href``/``src`` attributes in every HTML page, ``href:``/``href=``
literals and ``url``/``href``/``route``/``page``/``link`` keys pointing at ``*.html``
in every ``website/**/*.js`` file, plus literal ``fetch('...')`` targets,, and
``href``/``route``/``page``/``url``/``link`` values ending in ``.html`` in
``website/data/**/*.json``. ``--baseline FILE`` makes the exit code fail only
on broken links that are not already listed in the baseline (regression
mode); ``--write-baseline FILE`` records the current broken set.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAV_SCRIPTS = ("nav.js", "desk-chrome.js")
JS_HREF_RE = re.compile(r"""href\s*[:=]\s*(['"])(.*?)\1""")
NAV_BLOCK_RE = re.compile(r"<nav\b[^>]*>(.*?)</nav\s*>", re.I | re.S)
A_HREF_RE = re.compile(r"""<a\b[^>]*?\bhref\s*=\s*(['"])(.*?)\1""", re.I | re.S)
SKIP_PREFIXES = ("http://", "https://", "//", "mailto:", "tel:", "data:", "javascript:", "#")


def is_local(href: str) -> bool:
    h = href.strip()
    return bool(h) and not h.lower().startswith(SKIP_PREFIXES) and "${" not in h and "{{" not in h


def resolve(site: Path, base_dir: Path, href: str) -> Path:
    path = href.split("#", 1)[0].split("?", 1)[0]
    target = (site / path.lstrip("/")) if path.startswith("/") else (base_dir / path)
    if path.endswith("/") or target.is_dir():
        target = target / "index.html"
    return target


def check(site: Path) -> dict:
    checked, broken = 0, []

    def visit(source: Path, base_dir: Path, href: str) -> None:
        nonlocal checked
        if not is_local(href):
            return
        checked += 1
        if not resolve(site, base_dir, href).exists():
            broken.append({"source": str(source.relative_to(site.parent)), "href": href})

    for name in NAV_SCRIPTS:
        script = site / name
        if script.exists():
            for _, href in JS_HREF_RE.findall(script.read_text(encoding="utf-8", errors="replace")):
                visit(script, site, href)
    pages = sorted(site.rglob("*.html"))
    for page in pages:
        text = page.read_text(encoding="utf-8", errors="replace")
        for block in NAV_BLOCK_RE.findall(text):
            for _, href in A_HREF_RE.findall(block):
                visit(page, page.parent, href)
    return {"site": str(site.relative_to(ROOT)) if site.is_relative_to(ROOT) else str(site),
            "pages_scanned": len(pages), "nav_links_checked": checked,
            "broken_count": len(broken), "broken": broken, "ok": not broken}


ATTR_RE = re.compile(r"""\b(?:href|src)\s*=\s*(['"])(.*?)\1""", re.I | re.S)
JS_ROUTE_RE = re.compile(
    r"""["']?\b(?:url|href|route|page|link)["']?\s*[:=]\s*(['"`])([A-Za-z0-9_./-]+\.html(?:[?#][^'"`]*)?)\1""")
FETCH_RE = re.compile(r"""\bfetch\(\s*(['"`])([^'"`$]+)\1""")
CONCAT_RE = re.compile(r"""['"`]\s*\+|\+\s*['"`]""")
JSON_ROUTE_KEYS = {"href", "route", "page", "url", "link", "pages_route"}
SKIP_DIRS = {"node_modules", "vendor"}


def _json_routes(value, out: list[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in JSON_ROUTE_KEYS and isinstance(item, str) and ".html" in item:
                out.append(item)
            else:
                _json_routes(item, out)
    elif isinstance(value, list):
        for item in value:
            _json_routes(item, out)


def check_all(site: Path) -> dict:
    """Check every internal link/route in the Pages site (see module doc)."""
    checked, broken = 0, []
    seen: set[tuple[str, str]] = set()
    api_refs: set[str] = set()

    def visit(source: Path, base_dir: Path, href: str, kind: str) -> None:
        nonlocal checked
        href = href.strip()
        if not is_local(href) or href.startswith("?") or CONCAT_RE.search(href):
            return
        if href.startswith("/api/"):
            api_refs.add(href)
            return
        rel = str(source.relative_to(site.parent))
        if (rel, href) in seen:
            return
        seen.add((rel, href))
        checked += 1
        if not resolve(site, base_dir, href).exists():
            broken.append({"source": rel, "href": href, "kind": kind})

    files = [p for p in sorted(site.rglob("*")) if p.is_file() and not (set(p.relative_to(site).parts) & SKIP_DIRS)]
    for path in files:
        suffix = path.suffix.lower()
        if suffix not in {".html", ".js", ".mjs", ".json"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if suffix == ".html":
            for _, href in ATTR_RE.findall(text):
                visit(path, path.parent, href, "html")
        elif suffix in {".js", ".mjs"}:
            for _, href in JS_HREF_RE.findall(text):
                visit(path, site, href, "js-href")
            for _, href in JS_ROUTE_RE.findall(text):
                visit(path, site, href, "js-route")
            for _, href in FETCH_RE.findall(text):
                # fetch() resolves against the page URL; site pages live at the root.
                visit(path, site, href, "js-fetch")
        elif suffix == ".json":
            try:
                data = json.loads(text)
            except ValueError:
                continue
            routes: list[str] = []
            _json_routes(data, routes)
            for href in routes:
                visit(path, site, href, "json-route")
    broken.sort(key=lambda b: (b["source"], b["href"]))
    return {"site": str(site.relative_to(ROOT)) if site.is_relative_to(ROOT) else str(site),
            "mode": "all", "files_scanned": len(files), "links_checked": checked,
            "broken_count": len(broken), "broken": broken,
            "server_api_refs": sorted(api_refs),
            "server_api_note": "/api/* calls need the DreamCo server; they cannot resolve on static GitHub Pages and are listed, not counted as broken pages.",
            "ok": not broken}


def _key(item: dict) -> str:
    return f"{item['source']} -> {item['href']}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--site", default=str(ROOT / "website"))
    parser.add_argument("--all", action="store_true", help="check every internal link/route, not only navigation")
    parser.add_argument("--baseline", type=Path, help="fail only on broken links missing from this baseline")
    parser.add_argument("--write-baseline", type=Path, help="write the current broken-link set to this file")
    args = parser.parse_args(argv)
    site = Path(args.site).resolve()
    if not site.is_dir():
        print(f"site folder not found: {site}", file=sys.stderr)
        return 2
    result = check_all(site) if args.all else check(site)
    if args.write_baseline:
        args.write_baseline.parent.mkdir(parents=True, exist_ok=True)
        args.write_baseline.write_text(json.dumps({"schema": "dreamco.website_link_baseline.v1",
                                                   "mode": result.get("mode", "nav"),
                                                   "broken": sorted(_key(b) for b in result["broken"])},
                                                  indent=2) + "\n", encoding="utf-8")
    if args.baseline:
        known = set(json.loads(args.baseline.read_text(encoding="utf-8")).get("broken", []))
        new = [b for b in result["broken"] if _key(b) not in known]
        fixed = sorted(known - {_key(b) for b in result["broken"]})
        result.update({"baseline": str(args.baseline), "new_broken": new, "fixed_since_baseline": fixed,
                       "ok": not new})
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
