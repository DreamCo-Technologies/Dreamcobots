#!/usr/bin/env python3
"""Refresh Buddy's open-vocabulary AI and technology discovery radar.

The collector preserves historical observations, computes all counts from data,
and never treats a discovered listing as a verified capability or income claim.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urldefrag, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config/buddy/technology-discovery-policy.json"
OUTPUT_PATH = ROOT / "config/generated/buddy-technology-radar.json"
WEB_OUTPUT_PATH = ROOT / "website/data/buddy-technology-radar.json"
POLICY_MIRROR_PATH = ROOT / "website/data/technology-discovery-policy.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_date(value: Any) -> str | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(value, timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        except (OverflowError, OSError, ValueError):
            return None
    raw = str(value).strip()
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    except ValueError:
        try:
            parsed = parsedate_to_datetime(raw)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        except (TypeError, ValueError, OverflowError):
            return None


def clean_text(value: Any) -> str:
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False)
    value = html.unescape(re.sub(r"<[^>]+>", " ", str(value or "")))
    return re.sub(r"\s+", " ", value).strip()


def get_path(value: Any, path: str | None) -> Any:
    if not path:
        return value
    current = value
    for part in path.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        else:
            return None
    return current


def safe_url(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    clean, _ = urldefrag(raw)
    parsed = urlparse(clean)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        return ""
    return clean


def parse_feed(content: bytes) -> list[dict[str, Any]]:
    root = ET.fromstring(content)
    entries = []
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1].lower() not in {"item", "entry"}:
            continue
        fields: dict[str, Any] = {}
        for child in list(node):
            key = child.tag.rsplit("}", 1)[-1].lower()
            if key == "link":
                fields["link"] = child.attrib.get("href") or (child.text or "")
            elif key in {"title", "description", "summary", "content", "pubdate", "published", "updated", "date", "id"}:
                fields[key] = " ".join(child.itertext()).strip()
        entries.append({
            "title": fields.get("title", ""),
            "url": fields.get("link") or fields.get("id", ""),
            "summary": fields.get("description") or fields.get("summary") or fields.get("content", ""),
            "published_at": fields.get("pubdate") or fields.get("published") or fields.get("updated") or fields.get("date"),
            "external_id": fields.get("id"),
        })
    return entries


def collection_items(payload: Any, path: str | None) -> list[Any]:
    rows = get_path(payload, path)
    if isinstance(rows, list):
        return rows
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict) and not row.get("legal")]
    return []


def normalize_item(source: dict[str, Any], raw: dict[str, Any], observed_at: str, policy: dict[str, Any]) -> dict[str, Any] | None:
    title = clean_text(raw.get("title") or raw.get("name") or raw.get("full_name"))
    url = safe_url(raw.get("url"))
    summary = clean_text(raw.get("summary"))
    external_id = str(raw.get("external_id") or "")
    if not title:
        return None
    identity = url or external_id or title.casefold()
    record_id = hashlib.sha256(f"{source['id']}|{identity}".encode("utf-8")).hexdigest()
    haystack = f"{title} {summary} {url}".casefold()
    matched = []
    for lens in policy.get("priority_lenses", []):
        if any(str(term).casefold() in haystack for term in lens.get("terms", [])):
            matched.append(lens.get("id"))
    return {
        "id": record_id,
        "title": title,
        "url": url or None,
        "summary": summary[:3000],
        "record_kind": source.get("record_kind", "discovery"),
        "source_id": source["id"],
        "source_name": source.get("name", source["id"]),
        "source_url": source["url"],
        "source_trust_tier": source.get("trust_tier", "unclassified"),
        "external_id": external_id or None,
        "published_at": parse_date(raw.get("published_at")),
        "first_seen_at": observed_at,
        "last_seen_at": observed_at,
        "last_checked_at": observed_at,
        "status": "active",
        "priority_lenses": matched,
        "evidence_class": "discovery_lead_not_verified",
        "verified_capability": False,
        "income_claim_verified": False,
    }


class HtmlMetaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.description = ""
        self.in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag.lower() == "title":
            self.in_title = True
        if tag.lower() == "meta":
            key = (values.get("name") or values.get("property") or "").lower()
            if key in {"description", "og:description", "twitter:description"} and not self.description:
                self.description = clean_text(values.get("content") or "")

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False


def extract_source(source: dict[str, Any], content: bytes, observed_at: str, policy: dict[str, Any]) -> list[dict[str, Any]]:
    if source["kind"] == "rss":
        raw_items = parse_feed(content)
    elif source["kind"] == "html_page":
        parser = HtmlMetaParser()
        parser.feed(content.decode("utf-8", errors="replace"))
        raw_items = [{
            "title": " ".join("".join(parser.title_parts).split()) or source.get("name", source["id"]),
            "url": source["url"], "summary": parser.description,
            "published_at": None, "external_id": source["id"],
        }]
    elif source["kind"] == "json_collection":
        payload = json.loads(content.decode("utf-8"))
        raw_items = []
        for item in collection_items(payload, source.get("collection_path")):
            if not isinstance(item, dict):
                continue
            title = get_path(item, source.get("title_field"))
            url = get_path(item, source.get("url_field")) if source.get("url_field") else None
            if source.get("url_template") and not url:
                url = source["url_template"].replace("{" + source.get("title_field", "") + "}", str(title or ""))
                if "{id}" in url:
                    url = url.replace("{id}", str(get_path(item, source.get("id_field")) or ""))
            summary = get_path(item, source.get("summary_field")) if source.get("summary_field") else ""
            published = get_path(item, source.get("date_field")) if source.get("date_field") else None
            external_id = get_path(item, source.get("id_field")) if source.get("id_field") else None
            raw_items.append({"title": title, "url": url, "summary": summary, "published_at": published, "external_id": external_id})
    else:
        raise ValueError(f"Unsupported source kind: {source.get('kind')}")
    output = []
    for raw in raw_items:
        if not isinstance(raw, dict):
            continue
        normalized = normalize_item(source, raw, observed_at, policy)
        if normalized:
            output.append(normalized)
    return output


def fetch_source(source: dict[str, Any], policy: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    observed_at = now_iso()
    headers = {
        "User-Agent": policy.get("refresh_policy", {}).get("user_agent", "DreamCo-Buddy-Technology-Radar/1.0"),
        "Accept": "application/rss+xml, application/atom+xml, application/json, text/xml, */*",
    }
    if source["url"].startswith("https://api.github.com/"):
        headers["Accept"] = "application/vnd.github+json"
    request = Request(source["url"], headers=headers)
    try:
        max_bytes = int(policy.get("refresh_policy", {}).get("maximum_response_bytes", 12000000))
        with urlopen(request, timeout=int(policy.get("refresh_policy", {}).get("request_timeout_seconds", 25))) as response:  # noqa: S310 - URLs are policy-controlled
            content = response.read(max_bytes + 1)
        if len(content) > max_bytes:
            raise ValueError("source response exceeded configured byte budget")
        records = extract_source(source, content, observed_at, policy)
        return records, {
            "source_id": source["id"], "status": "success", "record_count": len(records),
            "checked_at": observed_at, "error": None,
        }
    except Exception as exc:  # keep the previous source snapshot when one provider is unavailable
        return [], {
            "source_id": source["id"], "status": "failed", "record_count": 0,
            "checked_at": observed_at, "error": f"{type(exc).__name__}: {str(exc)[:500]}",
        }


def merge_catalog(existing: dict[str, Any], discovered: list[dict[str, Any]], source_runs: list[dict[str, Any]], generated_at: str) -> dict[str, Any]:
    records = {item["id"]: item for item in existing.get("records", []) if item.get("id")}
    seen_by_source: dict[str, set[str]] = {}
    new_count = 0
    updated_count = 0
    for item in discovered:
        prior = records.get(item["id"])
        if prior:
            item["first_seen_at"] = prior.get("first_seen_at") or item["first_seen_at"]
            updated_count += 1
        else:
            new_count += 1
        records[item["id"]] = item
        seen_by_source.setdefault(item["source_id"], set()).add(item["id"])
    successful_sources = {run["source_id"] for run in source_runs if run["status"] == "success"}
    for record in records.values():
        if record.get("source_id") in successful_sources and record["id"] not in seen_by_source.get(record.get("source_id"), set()):
            record["status"] = "stale_not_seen_in_latest_successful_refresh"
            record["last_checked_at"] = generated_at
    ordered = sorted(records.values(), key=lambda item: (item.get("published_at") or item.get("last_seen_at") or "", item["id"]), reverse=True)
    counts_by_kind: dict[str, int] = {}
    counts_by_status: dict[str, int] = {}
    counts_by_lens: dict[str, int] = {}
    for record in ordered:
        counts_by_kind[record.get("record_kind", "unknown")] = counts_by_kind.get(record.get("record_kind", "unknown"), 0) + 1
        counts_by_status[record.get("status", "unknown")] = counts_by_status.get(record.get("status", "unknown"), 0) + 1
        for lens in record.get("priority_lenses", []):
            counts_by_lens[lens] = counts_by_lens.get(lens, 0) + 1
    return {
        "schema": "dreamco.buddy.technology_radar.v1",
        "generated_at": generated_at,
        "catalog_policy": "open_vocabulary_append_only_versioned_observations",
        "summary": {
            "records_total": len(ordered), "records_new_this_refresh": new_count,
            "records_seen_or_updated_this_refresh": updated_count,
            "records_by_kind": dict(sorted(counts_by_kind.items())),
            "records_by_status": dict(sorted(counts_by_status.items())),
            "records_by_priority_lens": dict(sorted(counts_by_lens.items())),
            "sources_total": len(source_runs),
            "sources_succeeded": sum(run["status"] == "success" for run in source_runs),
            "sources_failed": sum(run["status"] == "failed" for run in source_runs),
            "sources_pending": sum(run["status"] not in {"success", "failed"} for run in source_runs),
        },
        "source_runs": source_runs,
        "records": ordered,
        "truth_boundary": "This is a living discovery index. Counts are computed, categories are open-vocabulary, historical records are preserved, and discovery does not prove quality, integration, job legitimacy, earnings, or production capability.",
    }


def validate_catalog(catalog: dict[str, Any]) -> None:
    if catalog.get("schema") != "dreamco.buddy.technology_radar.v1":
        raise ValueError("unexpected technology radar schema")
    records = catalog.get("records")
    if not isinstance(records, list):
        raise ValueError("records must be an array")
    ids = [item.get("id") for item in records]
    if any(not item for item in ids) or len(ids) != len(set(ids)):
        raise ValueError("record IDs must be present and unique")
    summary = catalog.get("summary", {})
    if summary.get("records_total") != len(records):
        raise ValueError("summary.records_total does not match the current record list")
    if summary.get("sources_total") != len(catalog.get("source_runs", [])):
        raise ValueError("summary.sources_total does not match source run records")
    if summary.get("sources_succeeded") != sum(run.get("status") == "success" for run in catalog.get("source_runs", [])):
        raise ValueError("summary.sources_succeeded is stale")
    if summary.get("sources_failed") != sum(run.get("status") == "failed" for run in catalog.get("source_runs", [])):
        raise ValueError("summary.sources_failed is stale")
    if summary.get("sources_pending") != sum(run.get("status") not in {"success", "failed"} for run in catalog.get("source_runs", [])):
        raise ValueError("summary.sources_pending is stale")
    for item in records:
        if item.get("evidence_class") != "discovery_lead_not_verified":
            raise ValueError(f"unsupported evidence class for {item.get('id')}")
        if item.get("verified_capability") is not False or item.get("income_claim_verified") is not False:
            raise ValueError(f"unverified record cannot claim capability or income proof: {item.get('id')}")
        if item.get("status") not in {"active", "stale_not_seen_in_latest_successful_refresh"}:
            raise ValueError(f"invalid lifecycle state for {item.get('id')}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--refresh", action="store_true", help="fetch configured public sources and update the living index")
    mode.add_argument("--check", action="store_true", help="validate existing index and published mirror without network calls")
    args = parser.parse_args()
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    if args.refresh:
        existing = json.loads(OUTPUT_PATH.read_text(encoding="utf-8")) if OUTPUT_PATH.exists() else {
            "schema": "dreamco.buddy.technology_radar.v1", "records": []
        }
        discovered: list[dict[str, Any]] = []
        source_runs = []
        for source in policy.get("sources", []):
            records, run = fetch_source(source, policy)
            discovered.extend(records)
            source_runs.append(run)
        catalog = merge_catalog(existing, discovered, source_runs, now_iso())
        validate_catalog(catalog)
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        WEB_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        WEB_OUTPUT_PATH.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        POLICY_MIRROR_PATH.parent.mkdir(parents=True, exist_ok=True)
        POLICY_MIRROR_PATH.write_text(json.dumps(policy, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        if not OUTPUT_PATH.exists() or not WEB_OUTPUT_PATH.exists():
            raise SystemExit("technology radar output or Pages mirror is missing; run --refresh")
        catalog = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        mirror = json.loads(WEB_OUTPUT_PATH.read_text(encoding="utf-8"))
        if catalog != mirror:
            raise SystemExit("technology radar Pages mirror is stale")
        if not POLICY_MIRROR_PATH.exists() or json.loads(POLICY_MIRROR_PATH.read_text(encoding="utf-8")) != policy:
            raise SystemExit("technology discovery policy Pages mirror is stale")
        validate_catalog(catalog)
    print(json.dumps({"ok": True, **catalog["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
