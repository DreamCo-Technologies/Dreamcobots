"""Bounded adapters for explicitly configured public JSON feeds.

Only HTTPS on port 443 is accepted. Private, loopback, link-local, reserved,
and non-global DNS results are rejected. Redirects are disabled to avoid
redirect-based SSRF. Authenticated vendor integrations should be separate
adapters backed by a secret manager, never inline rule values.
"""
from __future__ import annotations

import http.client
import ipaddress
import json
import socket
import ssl
import urllib.error
from typing import Any
from urllib.parse import urlsplit

from .engine import Observation, WatchRule

MAX_RESPONSE_BYTES = 2 * 1024 * 1024
DEFAULT_TIMEOUT_SECONDS = 10


def _resolve_public_https_url(url: str) -> tuple[Any, list[str]]:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("JSON feed targets must be absolute HTTPS URLs.")
    if parsed.username or parsed.password or parsed.fragment:
        raise ValueError("Feed URLs cannot contain credentials or fragments.")
    if parsed.port not in (None, 443):
        raise ValueError("Only the standard HTTPS port is allowed.")
    host = parsed.hostname.rstrip(".").lower()
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
        raise ValueError("Local network targets are blocked.")
    try:
        literal = ipaddress.ip_address(host)
        addresses = [str(literal)]
    except ValueError:
        try:
            addresses = sorted({row[4][0] for row in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)})
        except OSError as exc:
            raise ValueError("Feed hostname could not be resolved.") from exc
    parsed_addresses = [ipaddress.ip_address(address) for address in addresses]
    if not parsed_addresses or any(not address.is_global for address in parsed_addresses):
        raise ValueError("Feed host resolves to a non-public network address.")
    return parsed, addresses


def validate_public_https_url(url: str) -> None:
    """Validate a feed URL and reject any non-public DNS/IP result."""
    _resolve_public_https_url(url)


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    """Connect to a prevalidated IP while retaining hostname TLS verification."""

    def __init__(self, hostname: str, address: str, timeout: int):
        super().__init__(hostname, port=443, timeout=timeout, context=ssl.create_default_context())
        self._pinned_address = address

    def connect(self) -> None:
        raw = socket.create_connection((self._pinned_address, 443), self.timeout)
        self.sock = self._context.wrap_socket(raw, server_hostname=self.host)






class JsonFeedAdapter:
    def __init__(self, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS, max_bytes: int = MAX_RESPONSE_BYTES):
        if not 1 <= timeout_seconds <= 30:
            raise ValueError("timeout_seconds must be between 1 and 30.")
        if not 1024 <= max_bytes <= MAX_RESPONSE_BYTES:
            raise ValueError("max_bytes must be between 1 KiB and 2 MiB.")
        self.timeout_seconds = timeout_seconds
        self.max_bytes = max_bytes
        self._opener = urllib.request.build_opener(_NoRedirect)

    def fetch(self, rule: WatchRule) -> list[Observation]:
        rule.validate()
        if rule.adapter != "json_feed":
            raise ValueError("JsonFeedAdapter only supports json_feed rules.")
        parsed, addresses = _resolve_public_https_url(rule.target)
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query
        body = None
        last_error = None
        for address in addresses:
            connection = _PinnedHTTPSConnection(parsed.hostname, address, self.timeout_seconds)
            try:
                connection.request(
                    "GET",
                    path,
                    headers={"Accept": "application/json", "User-Agent": "DreamCo-Watchtower/1.0"},
                )
                response = connection.getresponse()
                if 300 <= response.status < 400:
                    raise ValueError("Feed redirects are disabled.")
                if response.status < 200 or response.status >= 300:
                    raise ValueError(f"Feed returned HTTP status {response.status}.")
                content_type = response.getheader("Content-Type", "").split(";", 1)[0].strip().lower()
                if content_type not in {"application/json", "application/problem+json"}:
                    raise ValueError(f"Unsupported feed content type: {content_type}")
                body = response.read(self.max_bytes + 1)
                break
            except (OSError, http.client.HTTPException) as exc:
                last_error = exc
            finally:
                connection.close()
        if body is None:
            raise ValueError("Could not retrieve the public JSON feed.") from last_error
        if len(body) > self.max_bytes:
            raise ValueError("Feed response exceeded the configured byte limit.")
        try:
            payload: Any = json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("Feed response was not valid JSON.") from exc
        rows = payload.get("items", []) if isinstance(payload, dict) else payload
        if not isinstance(rows, list):
            raise ValueError("JSON feed must be an array or an object with an items array.")
        observations = []
        for row in rows[: rule.max_items]:
            if not isinstance(row, dict):
                continue
            normalized = dict(row)
            normalized.setdefault("source", rule.name)
            if not normalized.get("item_id"):
                normalized["item_id"] = normalized.get("id") or normalized.get("url") or normalized.get("title")
            if normalized.get("item_id") and normalized.get("title"):
                observations.append(Observation.from_dict(normalized))
        return observations
