"""Opt-in, metadata-only discovery from approved public software registries.

No package files, datasets or model weights are downloaded. No discovered code
is executed. Every result remains a candidate until source, version, license,
rights and security review are completed.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable
from urllib.error import URLError
from urllib.parse import quote, urlencode, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config/buddy-library-registry-adapters.json"
USER_AGENT = "DreamCo-Buddy-Library-Metadata-Discovery/1.0"


class _SameHostRedirectHandler(HTTPRedirectHandler):
    """Reject redirects to hosts outside the configured registry endpoint."""

    def __init__(self, allowed_host: str):
        super().__init__()
        self.allowed_host = allowed_host

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urlparse(newurl)
        if target.scheme != "https" or target.hostname != self.allowed_host:
            raise ValueError("registry redirect left the configured HTTPS host")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _load_config(root: Path) -> dict[str, Any]:
    config = json.loads((root / "config/buddy-library-registry-adapters.json").read_text(encoding="utf-8"))
    if config.get("schema") != "dreamco.buddy_library_registry_adapters.v1":
        raise ValueError("unsupported registry adapter config schema")
    return config


def _normalize(provider: dict[str, Any], payload: Any) -> list[dict[str, Any]]:
    parser = provider["parser"]
    if parser == "npm":
        rows = [item.get("package", {}) for item in payload.get("objects", [])]
        return [{
            "name": row.get("name"),
            "version": row.get("version"),
            "description": row.get("description"),
            "homepage": row.get("links", {}).get("npm"),
            "repository": row.get("links", {}).get("repository"),
        } for row in rows]
    if parser == "maven":
        response = payload.get("response", {})
        return [{
            "name": row.get("id"),
            "version": row.get("latestVersion"),
            "description": row.get("description"),
            "homepage": None,
            "repository": None,
            "group": row.get("g"),
            "artifact": row.get("a"),
            "packaging": row.get("p"),
            "version_count": row.get("versionCount"),
        } for row in response.get("docs", [])]
    if parser == "metacpan":
        hits = payload.get("hits", {}).get("hits", [])
        rows = []
        for hit in hits:
            row = hit.get("_source") or hit.get("fields") or {}
            resources = row.get("resources") or {}
            repository = resources.get("repository") or {}
            rows.append({
                "name": row.get("distribution") or row.get("name"),
                "version": row.get("version"),
                "description": row.get("abstract") or row.get("description"),
                "homepage": resources.get("homepage"),
                "repository": repository.get("url") if isinstance(repository, dict) else repository,
                "license": row.get("license"),
                "author": row.get("author"),
                "release_date": row.get("date"),
            })
        return rows
    if parser == "crates":
        return [{
            "name": row.get("id"),
            "version": row.get("max_version"),
            "description": row.get("description"),
            "homepage": row.get("homepage"),
            "repository": row.get("repository"),
        } for row in payload.get("crates", [])]
    if parser == "nuget":
        return [{
            "name": row.get("id"),
            "version": row.get("version"),
            "description": row.get("description"),
            "homepage": row.get("projectUrl"),
            "license_url": row.get("licenseUrl"),
        } for row in payload.get("data", [])]
    if parser == "rubygems":
        return [{
            "name": row.get("name"),
            "version": row.get("version"),
            "description": row.get("info"),
            "homepage": row.get("homepage_uri"),
            "repository": row.get("source_code_uri"),
            "licenses": row.get("licenses", []),
        } for row in payload]
    if parser == "packagist":
        return [{
            "name": row.get("name"),
            "version": None,
            "description": row.get("description"),
            "homepage": row.get("url"),
            "repository": row.get("repository"),
        } for row in payload.get("results", [])]
    if parser == "huggingface":
        return [{
            "name": row.get("id"),
            "version": row.get("sha"),
            "description": row.get("pipeline_tag") or row.get("tags", []),
            "homepage": None,
            "repository": "https://huggingface.co/" + str(row.get("id", "")),
            "downloads": row.get("downloads"),
            "likes": row.get("likes"),
            "tags": row.get("tags", []),
        } for row in payload]
    if parser == "pypi":
        info = payload.get("info", {})
        project_urls = info.get("project_urls") or {}
        return [{
            "name": info.get("name"),
            "version": info.get("version"),
            "description": info.get("summary"),
            "homepage": info.get("home_page") or project_urls.get("Documentation"),
            "repository": project_urls.get("Source") or project_urls.get("Repository"),
            "license": info.get("license"),
        }]
    raise ValueError(f"unsupported registry parser: {parser}")


def search_public_registry(
    provider_id: str,
    query: str,
    *,
    allow_network: bool = False,
    page: int = 0,
    limit: int = 50,
    root: Path = ROOT,
    opener: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Search a configured provider once; callers must explicitly opt into network."""
    if not allow_network:
        raise PermissionError("registry discovery is opt-in; pass allow_network=True after approval")
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")
    if page < 0:
        raise ValueError("page must be non-negative")
    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100")
    config = _load_config(root)
    provider = next((row for row in config.get("providers", []) if row.get("id") == provider_id), None)
    if provider is None:
        raise ValueError(f"unknown registry provider: {provider_id}")
    endpoint = provider["endpoint"]
    if provider["parser"] == "pypi":
        safe_name = query.strip()
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", safe_name):
            raise ValueError("PyPI exact lookup accepts a valid package name, not a URL or path")
        url = endpoint.replace("{query}", quote(safe_name, safe=".-_"))
    else:
        search_term = query.strip()
        if provider_id == "metacpan":
            search_term = f"status:latest AND {search_term}"
        params: dict[str, Any] = {provider["query_parameter"]: search_term}
        if provider_id == "maven-central":
            params["wt"] = "json"
        size_key = provider.get("page_size_parameter")
        if size_key:
            params[size_key] = limit
        page_key = provider.get("page_parameter")
        if page_key:
            params[page_key] = page * limit if provider_id in {"npm", "nuget", "huggingface-models", "huggingface-datasets", "maven-central", "metacpan"} else page + 1
        url = endpoint + "?" + urlencode(params)
    if urlparse(url).scheme != "https" or urlparse(url).hostname != provider["host"]:
        raise ValueError("registry URL failed the configured HTTPS host allowlist")
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    fetch = opener or build_opener(_SameHostRedirectHandler(provider["host"])).open
    try:
        response = fetch(request, timeout=int(config.get("timeout_seconds", 12)))
        with response:
            raw = response.read(int(config.get("max_response_bytes", 1048576)) + 1)
    except (URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"registry request failed for {provider_id}: {exc}") from exc
    if len(raw) > int(config.get("max_response_bytes", 1048576)):
        raise ValueError("registry response exceeded the configured size limit")
    payload = json.loads(raw.decode("utf-8"))
    rows = _normalize(provider, payload)
    candidates = []
    seen = set()
    for row in rows:
        name = str(row.get("name") or "").strip()
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        candidates.append({
            **row,
            "provider": provider_id,
            "candidate_status": "discovered_metadata_only",
            "license_review": "pending",
            "source_revision_review": "pending",
            "download_authorized": False,
            "execution_authorized": False,
            "evaluation_permission": "pending",
            "training_permission": "pending",
        })
    return {
        "schema": "dreamco.buddy_library_registry_discovery.v1",
        "provider": provider_id,
        "query": query.strip(),
        "page": page,
        "result_count": len(candidates),
        "candidates": candidates,
        "next_page": page + 1 if provider.get("supports_pagination") and len(candidates) == limit else None,
        "network_used": True,
        "metadata_only": True,
        "truth_boundary": "Registry search results are candidate metadata, not verified packages, completed guides, safe dependencies, or permissions to download, execute, evaluate or train.",
    }
