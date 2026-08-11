#!/usr/bin/env python3
"""Build and validate repo-wide user-facing page coverage for GitHub Pages.

The public Pages artifact has two layers:
1. `website/*.html` and nested static pages.
2. The full React client compiled to `website/app/` in GitHub Pages mode.

This script inventories both and writes an evidence manifest plus a human-readable
coverage page. It intentionally distinguishes static availability from backend
runtime availability; a static build does not make protected APIs or secrets live.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEBSITE = ROOT / "website"
APP_SOURCE = ROOT / "client" / "src" / "App.tsx"
PAGES_DIR = ROOT / "client" / "src" / "pages"
APP_BUILD = WEBSITE / "app"
DATA_FILE = WEBSITE / "data" / "public-page-coverage.json"
REPORT_FILE = WEBSITE / "page-coverage.html"

LAZY_IMPORT = re.compile(
    r'const\s+(?P<name>[A-Za-z0-9_]+)\s*=\s*lazy\(\(\)\s*=>\s*import\("@/pages/(?P<path>[^"]+)"\)\);'
)
ROUTE_COMPONENT = re.compile(
    r'<Route\s+path="(?P<route>[^"]+)"\s+component=\{wrap\((?P<component>[A-Za-z0-9_]+),\s*"(?P<label>[^"]+)"\)\}\s*/>'
)
ROUTE_BLOCK = re.compile(r'<Route\s+path="(?P<route>[^"]+)"\s*>')


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_source_path(import_path: str) -> Path:
    base = PAGES_DIR / import_path
    candidates = [base.with_suffix(ext) for ext in (".tsx", ".ts", ".jsx", ".js")]
    candidates.extend([base / f"index{ext}" for ext in (".tsx", ".ts", ".jsx", ".js")])
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def route_link(route: str) -> str:
    if ":" in route:
        return "app/#/"
    if route == "/":
        return "app/#/"
    return f"app/#{route}"


def collect() -> tuple[dict, list[str]]:
    errors: list[str] = []
    source = APP_SOURCE.read_text(encoding="utf-8")

    imports = {m.group("name"): m.group("path") for m in LAZY_IMPORT.finditer(source)}
    routes = []
    routed_components: set[str] = set()
    for match in ROUTE_COMPONENT.finditer(source):
        component = match.group("component")
        routed_components.add(component)
        import_path = imports.get(component)
        source_path = normalize_source_path(import_path) if import_path else None
        if import_path is None:
            errors.append(f"Route component {component} has no lazy page import")
        elif source_path and not source_path.exists():
            errors.append(f"Missing page source for {component}: {source_path.relative_to(ROOT)}")
        route = match.group("route")
        routes.append({
            "route": route,
            "label": match.group("label"),
            "component": component,
            "source": source_path.relative_to(ROOT).as_posix() if source_path and source_path.exists() else import_path,
            "pages_url": route_link(route),
            "dynamic": ":" in route,
            "availability": "static_ui_available_backend_may_be_required",
        })

    convenience_routes = [m.group("route") for m in ROUTE_BLOCK.finditer(source)]
    explicit_route_paths = {item["route"] for item in routes}
    for route in convenience_routes:
        if route not in explicit_route_paths:
            routes.append({
                "route": route,
                "label": "Redirect / convenience route",
                "component": None,
                "source": "client/src/App.tsx",
                "pages_url": route_link(route),
                "dynamic": ":" in route,
                "availability": "redirect_or_convenience_route",
            })

    page_files = sorted(
        path for path in PAGES_DIR.rglob("*")
        if path.is_file() and path.suffix in {".tsx", ".ts", ".jsx", ".js"}
    )
    imported_files: set[Path] = set()
    for import_path in imports.values():
        resolved = normalize_source_path(import_path)
        if resolved.exists():
            imported_files.add(resolved.resolve())

    unrouted_sources = []
    for path in page_files:
        if path.resolve() not in imported_files:
            unrouted_sources.append(path.relative_to(ROOT).as_posix())

    # NotFound is imported and intentionally has no explicit path; all other imported pages
    # must appear in a route component.
    for component, import_path in imports.items():
        if component == "NotFound":
            continue
        if component not in routed_components:
            errors.append(f"Imported page {component} ({import_path}) is not bound to an explicit route")

    static_pages = []
    for path in sorted(WEBSITE.rglob("*.html")):
        if APP_BUILD in path.parents:
            continue
        static_pages.append({
            "path": path.relative_to(WEBSITE).as_posix(),
            "source": path.relative_to(ROOT).as_posix(),
            "pages_url": path.relative_to(WEBSITE).as_posix(),
        })

    app_index = APP_BUILD / "index.html"
    app_built = app_index.exists()
    if not app_built:
        errors.append("React GitHub Pages build missing: website/app/index.html")

    payload = {
        "schema": "dreamco.public_page_coverage.v1",
        "generated_at": utc_now(),
        "summary": {
            "static_html_pages": len(static_pages),
            "react_routes": len(routes),
            "react_page_source_files": len(page_files),
            "unrouted_page_source_files": len(unrouted_sources),
            "app_built": app_built,
        },
        "deployment_contract": {
            "static_site_source": "website/",
            "react_app_publish_path": "website/app/",
            "react_pages_mode": "hash routing",
            "backend_runtime_on_github_pages": False,
            "note": "Every routed React screen is published as UI. API-, secret-, database-, payment-, or server-dependent operations remain disconnected unless a separately deployed backend is configured.",
        },
        "static_pages": static_pages,
        "react_routes": sorted(routes, key=lambda item: item["route"]),
        "unrouted_page_sources": unrouted_sources,
    }
    return payload, errors


def render_report(payload: dict) -> str:
    summary = payload["summary"]
    static_rows = "\n".join(
        f'<tr><td>{html.escape(item["path"])}</td><td><a href="{html.escape(item["pages_url"])}">Open</a></td><td>{html.escape(item["source"])}</td></tr>'
        for item in payload["static_pages"]
    )
    react_rows = "\n".join(
        f'<tr><td>{html.escape(item["route"])}</td><td>{html.escape(item["label"])}</td><td><a href="{html.escape(item["pages_url"])}">Open UI</a></td><td>{html.escape(str(item["source"]))}</td><td>{html.escape(item["availability"])}</td></tr>'
        for item in payload["react_routes"]
    )
    warning = (
        "<p class=\"warning\"><strong>Runtime boundary:</strong> GitHub Pages is static. The full React UI is published, but server/API/database/payment controls still require the deployed DreamCo backend and authorized credentials.</p>"
    )
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>DreamCo Public Page Coverage</title>
<style>body{{font-family:system-ui,sans-serif;max-width:1400px;margin:auto;padding:24px;background:#0b1020;color:#eef2ff}}a{{color:#8ab4ff}}table{{width:100%;border-collapse:collapse;margin:18px 0 36px}}th,td{{border:1px solid #334155;padding:8px;text-align:left;vertical-align:top}}th{{background:#172033}}.cards{{display:flex;gap:12px;flex-wrap:wrap}}.card{{background:#172033;padding:12px 16px;border-radius:10px}}.warning{{background:#3b2a12;padding:14px;border-radius:10px}}</style></head>
<body><h1>DreamCo GitHub Pages — Full Page Coverage</h1>
<p>Generated {html.escape(payload["generated_at"])} from repository sources.</p>
<div class="cards"><div class="card"><strong>{summary["static_html_pages"]}</strong><br>static HTML pages</div><div class="card"><strong>{summary["react_routes"]}</strong><br>React routes</div><div class="card"><strong>{summary["react_page_source_files"]}</strong><br>React page source files</div><div class="card"><strong>{summary["unrouted_page_source_files"]}</strong><br>unrouted page files</div></div>
{warning}
<h2>React application pages</h2><table><thead><tr><th>Route</th><th>Page</th><th>GitHub Pages</th><th>Source</th><th>Status</th></tr></thead><tbody>{react_rows}</tbody></table>
<h2>Static website pages</h2><table><thead><tr><th>Page</th><th>GitHub Pages</th><th>Source</th></tr></thead><tbody>{static_rows}</tbody></table>
</body></html>'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if page coverage is incomplete")
    args = parser.parse_args()

    payload, errors = collect()
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    REPORT_FILE.write_text(render_report(payload), encoding="utf-8")

    if payload["unrouted_page_sources"]:
        errors.append("Unrouted page source files: " + ", ".join(payload["unrouted_page_sources"]))

    print(json.dumps(payload["summary"], indent=2))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1 if args.check else 0
    print("All discovered user-facing page sources are represented in the GitHub Pages artifact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
