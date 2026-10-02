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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--site", default=str(ROOT / "website"))
    args = parser.parse_args(argv)
    site = Path(args.site).resolve()
    if not site.is_dir():
        print(f"site folder not found: {site}", file=sys.stderr)
        return 2
    result = check(site)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
