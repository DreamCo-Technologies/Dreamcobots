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
FLEET_E2E = WEBSITE / "data" / "bot-fleet-e2e.json"
CALCULATORS = ROOT / "config" / "generated" / "bot_calculators.json"
SITE_STATUS = WEBSITE / "data" / "buddy-site-status.json"
TEST_REGISTRY = ROOT / "config" / "generated" / "repository_test_registry.json"

SECRET_FILE_PATTERN = re.compile(
    r"(^|/)(\.env($|\.)|id_rsa|id_ed25519|.*\.(pem|p12|pfx|key|keystore)$)", re.IGNORECASE
)
SECRET_VALUE_PATTERNS = {
    "GitHub token": re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    "GitHub installation token": re.compile(r"ghs_[A-Za-z0-9_]{40,}"),
    "Stripe live key": re.compile(r"(?:sk|rk)_live_[A-Za-z0-9]{16,}"),
    "Private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}
LEGACY_PROVIDER_NAME = re.compile("r" + "eplit", re.IGNORECASE)
FORBIDDEN_PUBLIC_NAMES = re.compile(r"(?:r[e]plit|\bi[b]m\b|w[a]tson)", re.IGNORECASE)
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
    fleet_e2e = read_json(FLEET_E2E)
    calculators = read_json(CALCULATORS)
    site_status = read_json(SITE_STATUS)
    test_registry = read_json(TEST_REGISTRY)

    registry_summary = master.get("summary", {})
    fleet_e2e_summary = fleet_e2e.get("summary", {})
    capability_bot_count = int(registry_summary.get("per_bot_sandbox_blueprints", 0))
    site_summary = site_status.get("summary", {})
    test_summary = test_registry.get("summary", {})
    enabled_tools = int(test_summary.get("locally_testable_suites", 0))
    approval_tools = int(test_registry.get("route_classifications", {}).get("external_or_destructive_gate", 0))

    divisions = [
        {
            "id": item.get("name", "").lower().replace(" ", "-"),
            "name": item.get("name", "Unnamed division"),
            "mission": f"Routes {int(item.get('profile_count', 0))} specialist profiles through Buddy's governed shared runtime.",
            "registered_bots": int(item.get("profile_count", 0)),
            "money_actions_require_approval": True,
        }
        for item in master.get("divisions", [])
    ]

    library_rows = [
        {"id": "capabilities", "name": "Capability contracts", "count": int(registry_summary.get("declared_capability_slots", 0)), "description": "Declared capabilities mapped to Buddy routes and repository-controlled sandbox checks."},
        {"id": "sandboxes", "name": "Per-bot sandbox blueprints", "count": int(registry_summary.get("per_bot_sandbox_blueprints", 0)), "description": "Synthetic or owner-supplied fixtures with no live external writes."},
        {"id": "business", "name": "Business blueprints", "count": int(registry_summary.get("per_bot_business_blueprints", 0)), "description": "Per-profile product, customer, workflow, and approval planning contracts."},
        {"id": "leads", "name": "Governed lead systems", "count": int(registry_summary.get("per_bot_governed_lead_systems", 0)), "description": "Permission-aware discovery and follow-up plans that stop before outreach."},
        {"id": "calculators", "name": "ROI calculators", "count": int(calculators.get("summary", {}).get("roi_calculators", 0)), "description": "Bounded local estimates using user-entered assumptions, never guaranteed outcomes."},
        {"id": "identities", "name": "Bot identities", "count": int(registry_summary.get("per_bot_logo_identities", 0)), "description": "Stable bot IDs, emoji identities, prospectus links, and catalog records."},
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
            "registered_bots": int(registry_summary.get("profiles", 0)),
            "registered_divisions": int(registry_summary.get("divisions", 0)),
            "readiness_records": int(fleet_e2e_summary.get("profilesTested", 0)),
            "native_runnable_candidates": int(site_summary.get("native_runnable_candidates", 0)),
            "completion_queue": completion_queue,
            "capability_blueprints": int(registry_summary.get("declared_capability_slots", 0)),
            "bots_with_capability_blueprints": capability_bot_count,
            "per_bot_libraries": len(library_rows),
            "enabled_tool_contracts": enabled_tools,
            "approval_gated_tool_contracts": approval_tools,
            "api_route_registrations": int(test_summary.get("literal_api_routes", 0)),
            "test_suites": int(test_summary.get("test_suites", 0)),
            "files_scanned": int(test_summary.get("files_scanned", 0)),
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
                f"{int(registry_summary.get('profiles', 0)):,} bot records across "
                f"{int(registry_summary.get('divisions', 0))} governed divisions.",
                "config/master_bot_registry.json",
            ),
            system_status(
                "generated",
                "Capabilities and libraries",
                f"{int(fleet_e2e_summary.get('sandboxCapabilityTestsPassed', 0)):,} declared capability contracts pass the repository-controlled sandbox flow.",
                "website/data/bot-fleet-e2e.json",
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
                "ready" if int(test_summary.get("blocked_suites", 0)) == 0 else "in_progress",
                "Repository Test Center",
                f"{int(test_summary.get('test_suites', 0))} governed suites map "
                f"{int(test_summary.get('files_scanned', 0)):,} files and "
                f"{int(test_summary.get('literal_api_routes', 0))} literal API routes to evidence and runtime boundaries.",
                "config/generated/repository_test_registry.json",
            ),
            system_status(
                "approval_required",
                "Payments and external actions",
                "No public page moves money, posts content, contacts people, or changes accounts without a configured backend and approval.",
                "config/generated/repository_test_registry.json",
            ),
        ],
        "libraries": library_rows,
        "library_coverage": {item["id"]: item["count"] for item in library_rows},
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
        WEBSITE / "buddy.css",
        WEBSITE / "buddy.js",
        WEBSITE / "buddy-site-sync.js",
        WEBSITE / "search.html",
        WEBSITE / "dream-search.css",
        WEBSITE / "dream-search.js",
        WEBSITE / "calculator.html",
        WEBSITE / "calculator.css",
        WEBSITE / "calculator-engine.js",
        WEBSITE / "calculator.js",
        WEBSITE / "install.html",
        WEBSITE / "install.css",
        WEBSITE / "install.js",
        WEBSITE / "leads.html",
        WEBSITE / "leads.css",
        WEBSITE / "leads.js",
        WEBSITE / "connections.html",
        WEBSITE / "connections.js",
        WEBSITE / "crypto.html",
        WEBSITE / "crypto.css",
        WEBSITE / "crypto.js",
        WEBSITE / "government.html",
        WEBSITE / "government.css",
        WEBSITE / "government.js",
        WEBSITE / "data-control.html",
        WEBSITE / "data-control.css",
        WEBSITE / "data-control.js",
        WEBSITE / "nav.js",
        WEBSITE / "manifest.webmanifest",
        WEBSITE / "platform.html",
        WEBSITE / "platform.css",
        WEBSITE / "platform.js",
        WEBSITE / "studio.html",
        WEBSITE / "studio.css",
        WEBSITE / "studio.js",
        WEBSITE / "models.html",
        WEBSITE / "models.css",
        WEBSITE / "models.js",
        WEBSITE / "open-model-lab.html",
        WEBSITE / "open-model-lab.css",
        WEBSITE / "open-model-lab.js",
        WEBSITE / "test-center.html",
        WEBSITE / "test-center.css",
        WEBSITE / "test-center.js",
        WEBSITE / "service-worker.js",
        WEBSITE / "styles.css",
        WEBSITE / "system-map.html",
        WEBSITE / "data" / "buddy-site-status.json",
        WEBSITE / "data" / "buddy-routing-index.js",
        WEBSITE / "data" / "dreamco-search-index.js",
        WEBSITE / "data" / "buddy-model-router.js",
        WEBSITE / "data" / "buddy-model-benchmarks.js",
        WEBSITE / "data" / "buddy-open-model-coding-lab.js",
        WEBSITE / "data" / "repository-test-registry.json",
        WEBSITE / "data" / "buddy-fleet-quality-program.js",
        WEBSITE / "data" / "buddy-capability-certifications.js",
        WEBSITE / "data" / "buddy-connection-catalog.json",
        WEBSITE / "data" / "buddy-specialized-hubs.js",
        WEBSITE / "data" / "bot-calculators.json",
        WEBSITE / "data" / "buddy-distribution-catalog.json",
        WEBSITE / "assets" / "images" / "buddy-icon-192.png",
        WEBSITE / "assets" / "images" / "buddy-icon-512.png",
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

    buddy_parser = parsers.get(WEBSITE / "buddy.html")
    buddy_script = (WEBSITE / "buddy.js").read_text(encoding="utf-8") if (WEBSITE / "buddy.js").exists() else ""
    required_buddy_controls = {
        "buddy-input", "buddy-send", "model-free", "model-premium", "premium-panel",
        "premium-provider", "premium-model-id", "premium-approval", "specialist-open",
        "specialist-dialog", "specialist-search", "specialist-results", "specialist-close",
        "local-open", "local-dialog", "local-close", "local-status", "local-status-detail",
        "local-status-dot", "local-pause", "local-audit", "local-search", "local-app-open",
    }
    if buddy_parser:
        for control_id in sorted(required_buddy_controls - buddy_parser.ids):
            errors.append(f"Missing Buddy interaction control: #{control_id}")
        for control_id in sorted(required_buddy_controls):
            if f"getElementById('{control_id}')" not in buddy_script:
                errors.append(f"Buddy control is not bound in buddy.js: #{control_id}")

    search_parser = parsers.get(WEBSITE / "search.html")
    search_script = (WEBSITE / "dream-search.js").read_text(encoding="utf-8") if (WEBSITE / "dream-search.js").exists() else ""
    required_search_controls = {
        "dream-search-form", "dream-search-input", "dream-search-submit",
        "search-mode-dreamco", "search-mode-web", "search-mode-note",
        "search-type-filter", "search-division-filter", "search-evidence-filter",
        "search-sort", "search-clear-filters", "search-index-count",
        "search-index-detail", "search-result-label", "search-result-count",
        "search-results", "search-empty", "search-load-more", "search-ask-buddy",
        "dreamco-results-view", "web-results-view", "web-title", "web-provider-links",
        "web-ask-buddy", "web-local-provider", "web-local-approval",
        "web-local-open", "web-local-status",
    }
    if search_parser:
        for control_id in sorted(required_search_controls - search_parser.ids):
            errors.append(f"Missing DreamSearch interaction control: #{control_id}")
        for control_id in sorted(required_search_controls):
            if f"byId('{control_id}')" not in search_script:
                errors.append(f"DreamSearch control is not bound in dream-search.js: #{control_id}")

    studio_parser = parsers.get(WEBSITE / "studio.html")
    studio_script = (WEBSITE / "studio.js").read_text(encoding="utf-8") if (WEBSITE / "studio.js").exists() else ""
    required_studio_controls = {
        "record-voice", "stop-voice", "download-voice", "start-camera", "take-photo",
        "stop-camera", "download-image", "download-consent", "clear-media", "academy-track", "academy-use",
        "actor-controls", "actor-mode", "actor-description", "simulation-controls",
        "simulation-model-source", "simulation-fidelity", "simulation-model-ref",
        "simulation-rights-ref", "simulation-paint", "simulation-additions", "simulation-to-game",
    }
    if studio_parser:
        for control_id in sorted(required_studio_controls - studio_parser.ids):
            errors.append(f"Missing Studio interaction control: #{control_id}")
        for control_id in sorted(required_studio_controls):
            if f"getElementById('{control_id}')" not in studio_script:
                errors.append(f"Studio control is not bound in studio.js: #{control_id}")

    crypto_parser = parsers.get(WEBSITE / "crypto.html")
    crypto_script = (WEBSITE / "crypto.js").read_text(encoding="utf-8") if (WEBSITE / "crypto.js").exists() else ""
    required_crypto_controls = {
        "wallet-plan-form", "wallet-network", "wallet-approval", "mining-plan-form",
        "mining-approval", "dreamcoin-plan-form", "dreamcoin-approval", "crypto-network-grid",
    }
    if crypto_parser:
        for control_id in sorted(required_crypto_controls - crypto_parser.ids):
            errors.append(f"Missing Crypto Lab interaction control: #{control_id}")
        for control_id in sorted(required_crypto_controls):
            if f"byId('{control_id}')" not in crypto_script:
                errors.append(f"Crypto Lab control is not bound in crypto.js: #{control_id}")

    government_parser = parsers.get(WEBSITE / "government.html")
    government_script = (WEBSITE / "government.js").read_text(encoding="utf-8") if (WEBSITE / "government.js").exists() else ""
    required_government_controls = {
        "government-plan-form", "government-query", "government-category", "government-jurisdiction",
        "government-approval", "government-source-search", "government-source-grid", "government-ask-buddy",
    }
    if government_parser:
        for control_id in sorted(required_government_controls - government_parser.ids):
            errors.append(f"Missing Government Hub interaction control: #{control_id}")
        for control_id in sorted(required_government_controls):
            if f"byId('{control_id}')" not in government_script:
                errors.append(f"Government Hub control is not bound in government.js: #{control_id}")

    model_parser = parsers.get(WEBSITE / "models.html")
    model_script = (WEBSITE / "models.js").read_text(encoding="utf-8") if (WEBSITE / "models.js").exists() else ""
    required_model_controls = {
        "model-search", "model-tier", "model-category", "select-visible", "clear-selection",
        "run-catalog-audit", "prepare-live-plan", "benchmark-budget", "benchmark-network",
        "benchmark-paid", "download-benchmark-plan", "model-detail", "model-detail-close",
    }
    if model_parser:
        for control_id in sorted(required_model_controls - model_parser.ids):
            errors.append(f"Missing Model Lab interaction control: #{control_id}")
        for control_id in sorted(required_model_controls):
            if f"byId('{control_id}')" not in model_script:
                errors.append(f"Model Lab control is not bound in models.js: #{control_id}")

    open_lab_parser = parsers.get(WEBSITE / "open-model-lab.html")
    open_lab_script = (WEBSITE / "open-model-lab.js").read_text(encoding="utf-8") if (WEBSITE / "open-model-lab.js").exists() else ""
    required_open_lab_controls = {
        "open-model-search", "open-region-filter", "open-access-filter", "open-model-grid",
        "open-task-options", "open-runtime", "open-repetitions", "open-network", "open-budget",
        "open-paid-approval", "prepare-open-comparison", "download-open-comparison",
        "open-source-form", "source-kind", "source-url", "source-revision", "source-license",
        "source-objective", "source-rights", "source-network", "prepare-source-plan",
        "download-source-plan", "frontier-target-options", "sandbox-learner-level",
        "sandbox-contribution-mode", "repository-tracker-form", "tracker-url",
        "tracker-revision", "tracker-license", "tracker-cadence", "tracker-rights",
        "add-repository-tracker", "repository-tracker-list", "browser-support-status",
    }
    if open_lab_parser:
        for control_id in sorted(required_open_lab_controls - open_lab_parser.ids):
            errors.append(f"Missing Open Model Lab interaction control: #{control_id}")
        for control_id in sorted(required_open_lab_controls):
            if f"byId('{control_id}')" not in open_lab_script:
                errors.append(f"Open Model Lab control is not bound in open-model-lab.js: #{control_id}")

    data_control_parser = parsers.get(WEBSITE / "data-control.html")
    data_control_script = (WEBSITE / "data-control.js").read_text(encoding="utf-8") if (WEBSITE / "data-control.js").exists() else ""
    required_data_control_controls = {
        "export-data-center", "delete-buddy-memory", "clear-data-center", "memory-form", "memory-retention",
        "memory-personalization", "memory-style", "memory-training", "data-source-form",
        "data-source-name", "data-source-url", "data-acquisition", "data-source-category",
        "data-source-retention", "data-source-rights", "privacy-request-form", "privacy-company",
        "privacy-url", "privacy-jurisdiction", "privacy-verification", "data-package-form",
        "package-name", "package-source", "package-category", "package-recipient", "package-terms",
        "package-ownership-evidence", "package-resale-evidence", "package-consent-receipt", "package-provenance",
        "package-owner-created", "package-resale-rights", "package-opt-in",
    }
    if data_control_parser:
        for control_id in sorted(required_data_control_controls - data_control_parser.ids):
            errors.append(f"Missing Data Control interaction control: #{control_id}")
        for control_id in sorted(required_data_control_controls):
            if f"byId('{control_id}')" not in data_control_script:
                errors.append(f"Data Control is not bound in data-control.js: #{control_id}")

    test_center_parser = parsers.get(WEBSITE / "test-center.html")
    test_center_script = (WEBSITE / "test-center.js").read_text(encoding="utf-8") if (WEBSITE / "test-center.js").exists() else ""
    required_test_center_controls = {
        "test-files-count", "test-routes-count", "test-pages-count", "test-tests-count",
        "test-suites-count", "test-blocked-count", "test-scan-id", "test-suite-search",
        "test-level-filter", "select-local-tests", "clear-test-selection", "test-suite-list",
        "selected-test-count", "test-mode-options", "test-network", "test-external-approval",
        "test-budget", "prepare-test-plan", "test-plan-output", "copy-test-command",
        "download-test-plan", "send-test-plan-to-buddy", "test-route-search", "test-route-list",
        "quality-profile-count", "quality-capability-count", "quality-contract-count",
        "quality-live-count", "quality-production-count", "quality-review-status",
        "quality-search", "quality-status-filter", "quality-result-count", "quality-bot-list",
        "quality-detail", "quality-detail-division", "quality-detail-title", "quality-detail-close",
        "quality-detail-body", "quality-download-plan", "quality-send-buddy",
    }
    if test_center_parser:
        for control_id in sorted(required_test_center_controls - test_center_parser.ids):
            errors.append(f"Missing Test Center interaction control: #{control_id}")
        for control_id in sorted(required_test_center_controls):
            if f"byId('{control_id}')" not in test_center_script:
                errors.append(f"Test Center control is not bound in test-center.js: #{control_id}")

    skipped_roots = {".git", "node_modules", "dist", "logs"}
    branding_hits: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in skipped_roots for part in path.relative_to(ROOT).parts):
            continue
        relative = path.relative_to(ROOT).as_posix()
        if LEGACY_PROVIDER_NAME.search(relative):
            branding_hits.append(relative)
            continue
        if path.suffix.lower() not in {".css", ".html", ".js", ".json", ".md", ".nix", ".py", ".ts", ".tsx", ".txt", ".yaml", ".yml"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if LEGACY_PROVIDER_NAME.search(text):
            branding_hits.append(relative)
    if branding_hits:
        errors.append("Legacy provider branding remains in project files: " + ", ".join(sorted(set(branding_hits))[:25]))

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
