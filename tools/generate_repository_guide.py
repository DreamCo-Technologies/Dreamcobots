#!/usr/bin/env python3
"""Build the owner directory from the canonical repository inventory, without copying file contents."""
import argparse
from collections import Counter
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote
from generate_dreamco_repository_master_map import build_payload

ROOT = Path(__file__).resolve().parents[1]
REPO = "https://github.com/DreamCo-Technologies/Dreamcobots"

class Title(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside = False
        self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag == "title": self.inside = True
    def handle_endtag(self, tag):
        if tag == "title": self.inside = False
    def handle_data(self, data):
        if self.inside: self.parts.append(data)

def render(root):
    inventory = build_payload(root)
    paths = [row["path"] for row in inventory["files"]]
    pages = sorted(p for p in paths if p.startswith("website/") and p.endswith(".html"))
    docs = sorted(p for p in paths if p.startswith("docs/") and p.endswith(".md"))
    areas = Counter(p.split("/")[0] for p in paths if "/" in p)
    def link(href, label):
        return '<a href="' + escape(href, quote=True) + '">' + escape(label) + '</a>'
    def source(path, folder=False):
        return REPO + ("/tree/main/" if folder else "/blob/main/") + quote(path, safe="/")
    page_rows = []
    for path in pages:
        parser = Title()
        parser.feed((root / path).read_text(encoding="utf-8"))
        label = " ".join("".join(parser.parts).split()) or Path(path).stem
        relative = path.removeprefix("website/")
        page_rows.append('<li>' + link(quote(relative, safe="/"), label) + ' <small>' + escape(relative) + ' · ' + link(source(path), "Source") + '</small></li>')
    area_rows = ['<li>' + link(source(area, True), area + "/") + ' <small>' + str(count) + ' scanned files</small></li>' for area, count in sorted(areas.items())]
    doc_rows = ['<li>' + link(source(path), Path(path).stem.replace("_", " ")) + ' <small>' + escape(path) + '</small></li>' for path in docs]
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>What DreamCo Has | Repository Guide</title><link rel="stylesheet" href="styles.css"><link rel="stylesheet" href="repository-guide.css"></head>
<body><div id="nav-placeholder"></div><script src="nav.js"></script><main class="repo-guide">
<header><p class="eyebrow">DREAMCO · START HERE</p><h1>Know what you have.<br>Find what comes next.</h1>
<p>Your website, source code, and documentation in one directory. A listed file means it exists; it does not prove a service is running.</p>
<nav aria-label="Guide sections"><a href="#have">What is here</a><a href="#gaps">What needs setup</a><a href="#pages">All pages</a><a href="#areas">Source folders</a><a href="#docs">Documentation</a></nav></header>
<section id="have"><h2>What is here</h2><div class="guide-cards">
<article><h3>A public website</h3><p>Buddy, dashboards, calculators, resource catalogs, and browser interfaces.</p><a href="buddy.html">Open Buddy</a> · <a href="system-map.html">System map</a></article>
<article><h3>Bot profiles and shared code</h3><p>Specialist profiles, routing policies, shared contracts, and backend source. Profiles are not independently running workers.</p><a href="bots.html">Bot catalog</a> · <a href="build.html">Readiness</a></article>
<article><h3>Tests and automation</h3><p>Test files, generators, and GitHub Actions workflows exist. Check the actual run before calling a feature verified.</p><a href="test-center.html">Test center</a> · <a href="https://github.com/DreamCo-Technologies/Dreamcobots/actions">Live workflow results</a></article></div></section>
<section id="gaps"><h2>What still needs setup or proof</h2><ul>
<li><strong>Hosted backend:</strong> GitHub Pages serves static files. Server routes, database operations, private model calls, and background workers need a separate running service.</li>
<li><strong>Provider connections:</strong> A connector catalog is not an authorized account connection. Configure and verify each provider through the backend. <a href="setup-center.html">Setup center</a> · <a href="resource-connection-center.html">Connection center</a></li>
<li><strong>Production evidence:</strong> No repository inventory proves live payments, customer delivery, revenue, or that every specialist is running. Those need explicit deployment and end-to-end evidence.</li>
<li><strong>One consistent Pages publisher:</strong> Two workflows currently publish different artifact contents. Choose a canonical publisher after verifying coverage; a later deployment can replace the previous site's files.</li>
<li><strong>ChatGPT project imports:</strong> Project conversations and uploaded files are not automatically synchronized into this repository. This directory includes repository files only.</li></ul>
<p><a href="https://github.com/DreamCo-Technologies/Dreamcobots/blob/main/docs/REPOSITORY_OWNER_GUIDE.md">Read the owner guide and next steps</a></p></section>
<section id="pages"><h2>All website pages</h2><p>Links open the website page; Source opens its code. These are discovered pages, not a certification of their features.</p>
<label for="page-filter">Find a page</label><input id="page-filter" type="search" placeholder="Try Buddy, payments, learning, memory…"><p id="page-count" role="status"></p>
<ul id="page-list" class="guide-list">""" + "\n".join(page_rows) + """</ul><p id="page-empty" hidden>No pages match your search.</p></section>
<section id="areas"><h2>Source folders</h2><p>Open a folder in GitHub. Files retain their existing locations so imports and automation keep working. Counts use the canonical scan exclusions.</p><ul class="guide-list">""" + "\n".join(area_rows) + """</ul></section>
<section id="docs"><h2>Documentation</h2><p>Plans and instructions provide context; they are not runtime verification.</p><ul class="guide-list">""" + "\n".join(doc_rows) + """</ul></section>
<footer>Generated by tools/generate_repository_guide.py from repository files. Rebuild after adding pages or documentation. <a href="https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages">About GitHub Pages</a></footer>
</main><script src="repository-guide.js" defer></script></body></html>
"""

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = ROOT / "website/repository-guide.html"
    # Include the output in its own directory on the first generation too.
    if not output.exists() and not args.check:
        output.write_text('<title>What DreamCo Has | Repository Guide</title>', encoding="utf-8")
    content = render(ROOT)
    if args.check:
        if not output.exists() or output.read_text(encoding="utf-8") != content:
            raise SystemExit("Repository guide is stale; run python3 tools/generate_repository_guide.py")
        print("Repository guide is current")
    else:
        output.write_text(content, encoding="utf-8")
        print("Generated website/repository-guide.html")

if __name__ == "__main__": main()
