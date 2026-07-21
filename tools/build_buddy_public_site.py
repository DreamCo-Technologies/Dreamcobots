#!/usr/bin/env python3
"""Build and validate the public-safe Buddy static website payload."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
WEBSITE = ROOT / "website"
PUBLIC_MAP = WEBSITE / "data" / "repository-system-map.json"

MASTER_REGISTRY = ROOT / "config" / "master_bot_registry.json"
READINESS = ROOT / "config" / "generated" / "bot_end_to_end_readiness" / "index.json"
CAPABILITIES = ROOT / "config" / "generated" / "capabilities_library" / "index.json"
SYSTEM_LIBRARIES = ROOT / "config" / "generated" / "system_libraries" / "index.json"
SITE_STATUS = WEBSITE / "data" / "buddy-site-status.json"
TOOL_REGISTRY = ROOT / "config" / "buddy-mcp-tool-registry.json"

SECRET_FILE_PATTERN = re.compile(
    r"(^|/)(\.env($|\.)|id_rsa|id_ed25519|.*\.(pem|p12|pfx|key|keystore)$)", re.IGNORECASE
)
SECRET_VALUE_PATTERNS = {
    "GitHub token": re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    "GitHub installation token": re.compile(r"ghs_[A-Za-z0-9_]{40,}"),
    "Stripe live key": re.compile(r"(?:sk|rk)_live_[A-Za-z0-9]{16,}"),
    "Private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}
FORBIDDEN_PUBLIC_NAMES = re.compile(r"(?:replit|\bibm\b|watson)", re.IGNORECASE)
PUBLIC_EXTENSIONS = {
    ".css",
    ".gif",
    ".html",
    ".ico",
    ".jpeg",
    ".jpg",
    ".js",
    ".json",
    ".png",
    ".svg",
    ".txt",
    ".webmanifest",
    ".webp",
    ".woff",
    ".woff2",
    ".xml",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Required generated input is missing: {path.relative_to(ROOT)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"Expected a JSON object: {path.relative_to(ROOT)}")
    return payload


def system_status(status: str, label: str, detail: str, source: str) -> dict[str, str]:
    return {"status": status, "label": label, "detail": detail, "source": source}


def build_public_map() -> dict[str, Any]:
    master = read_json(MASTER_REGISTRY)
    readiness = read_json(READINESS)
    capabilities = read_json(CAPABILITIES)
    libraries = read_json(SYSTEM_LIBRARIES)
    site_status = read_json(SITE_STATUS)
    tools = read_json(TOOL_REGISTRY)

    registry_summary = master.get("summary", {})
    readiness_totals = readiness.get("totals", {})
    capability_bot_count = int(capabilities.get("bot_count", 0))
    library_coverage = libraries.get("coverage", {})
    site_summary = site_status.get("summary", {})
    tool_rows = tools.get("tools", [])
    enabled_tools = sum(1 for item in tool_rows if item.get("enabled") is True)
    approval_tools = sum(1 for item in tool_rows if item.get("requiresApproval") is True)

    divisions = [
        {
            "id": item.get("id", ""),
            "name": item.get("name", "Unnamed division"),
            "mission": item.get("mission", ""),
            "registered_bots": int(item.get("bot_count", 0)),
            "money_actions_require_approval": bool(
                item.get("governance", {}).get("human_approval_required_for_revenue_actions", True)
            ),
        }
        for item in master.get("divisions", [])
    ]

    library_rows = [
        {
            "id": item.get("id", ""),
            "name": item.get("name", "Unnamed library"),
            "count": int(item.get("count", 0)),
            "description": item.get("description", ""),
        }
        for item in libraries.get("libraries", [])
    ]

    completion_queue = int(site_summary.get("completion_queue", 0))
    runtime_detail = (
        f"{completion_queue:,} product bot records remain in the generated completion queue."
        if completion_queue
        else "No product bot records are currently listed in the generated completion queue."
    )

    return {
        "schema": "dreamco.public_repository_system_map.v1",
        "generated_at": utc_now(),
        "repository": {
            "name": "DreamCo-Technologies/Dreamcobots",
            "default_branch": "main",
            "public_site_source": "website/",
            "deployment": "GitHub Pages",
        },
        "summary": {
            "registered_bots": int(registry_summary.get("bot_count", 0)),
            "registered_divisions": int(registry_summary.get("division_count", 0)),
            "readiness_records": int(readiness_totals.get("bots", 0)),
            "native_runnable_candidates": int(site_summary.get("native_runnable_candidates", 0)),
            "completion_queue": completion_queue,
            "capability_blueprints": int(capabilities.get("total_capability_slots", 0)),
            "bots_with_capability_blueprints": capability_bot_count,
            "per_bot_libraries": len(library_rows),
            "enabled_tool_contracts": enabled_tools,
            "approval_gated_tool_contracts": approval_tools,
            "autonomous_cash_enabled": bool(registry_summary.get("autonomous_cash_enabled", False)),
        },
        "systems": [
            system_status(
                "ready",
                "Public website",
                "Static Buddy, Studio, dashboard, division, and catalog pages pass deployment preflight.",
                "website/",
            ),
            system_status(
                "cataloged",
                "Bot registry",
                f"{int(registry_summary.get('bot_count', 0)):,} bot records across "
                f"{int(registry_summary.get('division_count', 0))} governed divisions.",
                "config/master_bot_registry.json",
            ),
            system_status(
                "generated",
                "Capabilities and libraries",
                f"{capability_bot_count:,} bot records have 100-slot capability blueprints and per-bot library contracts.",
                "config/generated/capabilities_library/index.json",
            ),
            system_status(
                "in_progress" if completion_queue else "candidate_ready",
                "Native runtimes",
                runtime_detail,
                "website/data/buddy-site-status.json",
            ),
            system_status(
                "prototype",
                "Buddy command interface",
                "The public page creates local task packets. Server-side execution is not exposed from the static site.",
                "website/buddy.html",
            ),
            system_status(
                "prototype",
                "Creative Studio",
                "Browser-based project packets, recording, consent checks, and local previews are available; rendering engines are optional.",
                "website/studio.html",
            ),
            system_status(
                "approval_required",
                "Payments and external actions",
                "No public page moves money, posts content, contacts people, or changes accounts without a configured backend and approval.",
                "config/buddy-mcp-tool-registry.json",
            ),
        ],
        "libraries": library_rows,
        "library_coverage": {
            key: int(value)
            for key, value in library_coverage.items()
            if isinstance(value, int) and not isinstance(value, bool)
        },
        "divisions": divisions,
        "public_contract": {
            "site_mode": "repository_preview",
            "verified_live_revenue": False,
            "public_payment_processing": False,
            "public_bot_execution": False,
            "data_policy": "Only generated counts, readiness labels, missions, and governance summaries are published.",
            "excluded": ["secrets", "credentials", "personal data", "private reports", "raw logs"],
        },
    }


class SiteHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[tuple[str, str]] = []
        self.ids: set[str] = set()
        self.has_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "title":
            self.has_title = True
        if values.get("id"):
            self.ids.add(values["id"] or "")
        for attribute in ("href", "src"):
            if values.get(attribute):
                self.references.append((attribute, values[attribute] or ""))


def load_html_parsers() -> dict[Path, SiteHTMLParser]:
    parsers: dict[Path, SiteHTMLParser] = {}
    for path in sorted(WEBSITE.rglob("*.html")):
        parser = SiteHTMLParser()
        parser.feed(path.read_text(encoding="utf-8"))
        parsers[path] = parser
    return parsers


def resolve_reference(source: Path, raw: str) -> tuple[Path | None, str]:
    value = raw.strip()
    if not value or value.startswith(("#", "data:", "mailto:", "tel:", "javascript:")):
        return None, ""
    split = urlsplit(value)
    if split.scheme or split.netloc:
        return None, ""
    reference_path = unquote(split.path)
    if not reference_path:
        return source, split.fragment
    if reference_path.startswith("/"):
        target = WEBSITE / reference_path.lstrip("/")
    else:
        target = source.parent / reference_path
    return target.resolve(), split.fragment


def validate_site() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    parsers = load_html_parsers()
    website_root = WEBSITE.resolve()

    required_files = [
        WEBSITE / ".nojekyll",
        WEBSITE / "404.html",
        WEBSITE / "index.html",
        WEBSITE / "buddy.html",
        WEBSITE / "buddy-site-sync.js",
        WEBSITE / "nav.js",
        WEBSITE / "studio.html",
        WEBSITE / "studio.js",
        WEBSITE / "styles.css",
        WEBSITE / "system-map.html",
        WEBSITE / "data" / "buddy-site-status.json",
        PUBLIC_MAP,
    ]
    for path in required_files:
        if not path.exists():
            errors.append(f"Missing required public file: {path.relative_to(ROOT)}")

    for path in sorted(WEBSITE.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(WEBSITE).as_posix()
        if SECRET_FILE_PATTERN.search(relative):
            errors.append(f"Secret-like file must not be deployed: website/{relative}")
        if path.suffix and path.suffix.lower() not in PUBLIC_EXTENSIONS:
            errors.append(f"Unsupported public artifact type: website/{relative}")
        if path.stat().st_size > 8 * 1024 * 1024:
            warnings.append(f"Large public file: website/{relative} ({path.stat().st_size:,} bytes)")
        if path.suffix.lower() in {".html", ".js", ".json", ".txt", ".xml", ".webmanifest"}:
            text = path.read_text(encoding="utf-8")
            if FORBIDDEN_PUBLIC_NAMES.search(text):
                errors.append(f"Disallowed outside-builder name detected in website/{relative}")
            for label, pattern in SECRET_VALUE_PATTERNS.items():
                if pattern.search(text):
                    errors.append(f"{label} detected in website/{relative}")

    for source, parser in parsers.items():
        if not parser.has_title:
            errors.append(f"Missing title element: {source.relative_to(ROOT)}")
        for attribute, raw in parser.references:
            target, fragment = resolve_reference(source, raw)
            if target is None:
                continue
            if website_root not in target.parents and target != website_root:
                errors.append(f"Reference escapes website/: {source.name} {attribute}={raw!r}")
                continue
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                errors.append(f"Broken reference: {source.relative_to(WEBSITE)} -> {raw}")
                continue
            if fragment and target.suffix.lower() == ".html" and target in parsers:
                if fragment not in parsers[target].ids:
                    warnings.append(
                        f"Missing fragment target: {source.relative_to(WEBSITE)} -> {raw}"
                    )

    if errors:
        raise SystemExit("Buddy public-site preflight failed:\n- " + "\n- ".join(errors))

    return {
        "ok": True,
        "html_pages": len(parsers),
        "public_files": sum(1 for path in WEBSITE.rglob("*") if path.is_file()),
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate without rewriting public data.")
    args = parser.parse_args()

    if not args.check:
        PUBLIC_MAP.parent.mkdir(parents=True, exist_ok=True)
        PUBLIC_MAP.write_text(
            json.dumps(build_public_map(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    result = validate_site()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
