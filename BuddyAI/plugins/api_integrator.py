"""
ApiIntegrator plugin for Buddy.

Provides compatibility with public APIs:
  - HTTP GET / POST requests to arbitrary URLs
  - Response parsing (JSON and plain text)
  - Simple caching of repeated requests

Register with the TaskEngine via ``register(engine)``.
"""

import json
import logging
import time
from typing import Any, Dict, Optional, Tuple
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError

logger = logging.getLogger(__name__)

_CACHE: Dict[str, Tuple[float, Any]] = {}
_CACHE_TTL_SECONDS = 60


# ---------------------------------------------------------------------------
# Core HTTP helpers (stdlib only – no external dependencies)
# ---------------------------------------------------------------------------


def _http_get(url: str, timeout: int = 10) -> Tuple[int, str]:
    """Perform an HTTP GET and return ``(status_code, body_text)``."""
    try:
        with urllib_request.urlopen(url, timeout=timeout) as resp:  # noqa: S310
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        return exc.code, str(exc.reason)
    except URLError as exc:
        return 0, str(exc.reason)


def _http_post(url: str, payload: Dict[str, Any], timeout: int = 10) -> Tuple[int, str]:
    """Perform an HTTP POST with a JSON body and return ``(status_code, body_text)``."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib_request.Request(  # noqa: S310
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib_request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        return exc.code, str(exc.reason)
    except URLError as exc:
        return 0, str(exc.reason)


def _parse_response(body: str) -> Any:
    """Try to parse *body* as JSON; fall back to raw string."""
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return body


# ---------------------------------------------------------------------------
# Task handlers
# ---------------------------------------------------------------------------


def handle_fetch_api(params: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch data from a URL (HTTP GET).

    Params:
        url (str): Target URL.
        use_cache (bool): Whether to use the local cache (default True).
    """
    url = params.get("url", "").strip()
    if not url:
        return {"success": False, "message": "No URL provided."}

    use_cache = params.get("use_cache", True)

    # Check cache
    if use_cache and url in _CACHE:
        cached_at, cached_data = _CACHE[url]
        if time.time() - cached_at < _CACHE_TTL_SECONDS:
            logger.info("Cache hit for URL: %s", url)
            return {
                "success": True,
                "message": f"Data fetched from cache for {url}.",
                "data": cached_data,
                "cached": True,
            }

    status, body = _http_get(url)
    if status == 0:
        return {"success": False, "message": f"Request failed: {body}"}

    parsed = _parse_response(body)

    if use_cache:
        _CACHE[url] = (time.time(), parsed)

    return {
        "success": status < 400,
        "message": f"HTTP {status} from {url}.",
        "data": parsed,
        "status_code": status,
        "cached": False,
    }


def handle_post_api(params: Dict[str, Any]) -> Dict[str, Any]:
    """Post data to a URL (HTTP POST).

    Params:
        url (str): Target URL.
        payload (dict): JSON payload to send.
    """
    url = params.get("url", "").strip()
    payload = params.get("payload", {})
    if not url:
        return {"success": False, "message": "No URL provided."}

    status, body = _http_post(url, payload)
    if status == 0:
        return {"success": False, "message": f"Request failed: {body}"}

    parsed = _parse_response(body)
    return {
        "success": status < 400,
        "message": f"HTTP {status} from {url}.",
        "data": parsed,
        "status_code": status,
    }


def handle_clear_cache(params: Dict[str, Any]) -> Dict[str, Any]:
    """Clear the API response cache."""
    count = len(_CACHE)
    _CACHE.clear()
    return {"success": True, "message": f"Cleared {count} cached response(s)."}


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register(engine: Any) -> None:
    """Register API integrator capabilities with *engine*.

    Args:
        engine: :class:`~BuddyAI.task_engine.TaskEngine` instance.
    """
    engine.register_capability("fetch_api", handle_fetch_api)
    engine.register_capability("post_api", handle_post_api)
    engine.register_capability("clear_api_cache", handle_clear_cache)
    logger.info("ApiIntegrator plugin registered.")
