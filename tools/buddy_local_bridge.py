#!/usr/bin/env python3
"""Loopback-only, approval-gated bridge between Buddy and this computer."""

from __future__ import annotations

import argparse
import json
import re
import secrets
import subprocess
import sys
import threading
import webbrowser
from dataclasses import dataclass, field
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, quote_plus, urlparse


ROOT = Path(__file__).resolve().parents[1]
WEBSITE = ROOT / "website"
MAX_BODY_BYTES = 32 * 1024
MAX_AUDIT_EVENTS = 50
MAX_SECRET_WRITES_PER_SESSION = 20

SEARCH_ENGINES = {
    "duckduckgo": "https://duckduckgo.com/?q={query}",
    "google": "https://www.google.com/search?q={query}",
    "bing": "https://www.bing.com/search?q={query}",
    "brave": "https://search.brave.com/search?q={query}",
}

BROWSERS = {
    "system": None,
    "safari": "Safari",
    "chrome": "Google Chrome",
    "firefox": "Firefox",
    "edge": "Microsoft Edge",
    "brave": "Brave Browser",
    "arc": "Arc",
}

SAFE_APPS = {
    "finder": "Finder",
    "notes": "Notes",
    "calendar": "Calendar",
    "mail": "Mail",
    "safari": "Safari",
    "chrome": "Google Chrome",
    "firefox": "Firefox",
    "edge": "Microsoft Edge",
    "brave": "Brave Browser",
    "arc": "Arc",
}


class LocalBridgeError(ValueError):
    """Raised when a local action violates the bridge policy."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_url(raw: str) -> str:
    if not isinstance(raw, str) or len(raw) > 2_048:
        raise LocalBridgeError("Use a normal web address under 2,048 characters.")
    parsed = urlparse(raw.strip())
    is_loopback_http = parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost", "::1"}
    if parsed.scheme != "https" and not is_loopback_http:
        raise LocalBridgeError("Only HTTPS or loopback HTTP addresses can be opened.")
    if parsed.username or parsed.password or not parsed.hostname:
        raise LocalBridgeError("Addresses cannot contain embedded credentials.")
    return parsed.geturl()


def search_url(query: str, engine: str) -> str:
    normalized = " ".join(str(query).split())
    if not 2 <= len(normalized) <= 500:
        raise LocalBridgeError("Search text must be between 2 and 500 characters.")
    template = SEARCH_ENGINES.get(engine)
    if not template:
        raise LocalBridgeError("Choose a supported search engine.")
    return template.format(query=quote_plus(normalized))


def require_approval(payload: dict[str, Any]) -> None:
    if payload.get("approved") is not True:
        raise LocalBridgeError("Approve this one local action before Buddy opens anything.")


def validate_secret_locator(provider: Any, account: Any) -> tuple[str, str]:
    provider_id = str(provider or "").strip().lower()
    account_name = str(account or "").strip()
    if not re.fullmatch(r"[a-z][a-z0-9-]{1,63}", provider_id):
        raise LocalBridgeError("Use a short lowercase provider id.")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.:/-]{2,127}", account_name):
        raise LocalBridgeError("Use a credential-free secret reference name.")
    return provider_id, account_name


def validate_secret_value(value: Any) -> str:
    if not isinstance(value, str) or not 8 <= len(value) <= 16_384:
        raise LocalBridgeError("The secret must be between 8 and 16,384 characters.")
    if any(character in value for character in ("\x00", "\r", "\n")):
        raise LocalBridgeError("Secrets cannot contain null bytes or line breaks.")
    return value


def store_macos_keychain_secret(provider: Any, account: Any, value: Any) -> str:
    provider_id, account_name = validate_secret_locator(provider, account)
    secret_value = validate_secret_value(value)
    if sys.platform != "darwin":
        raise LocalBridgeError("Secure local key intake currently requires the macOS Keychain bridge.")
    service = f"dreamco.buddy.{provider_id}"
    command = [
        "/usr/bin/security", "add-generic-password", "-U",
        "-a", account_name,
        "-s", service,
        "-D", "application password",
        "-j", "Stored by the owner through Buddy's loopback-only key intake",
        "-T", "",
        "-w",
    ]
    try:
        result = subprocess.run(
            command,
            input=f"{secret_value}\n",
            text=True,
            capture_output=True,
            timeout=15,
            check=False,
        )
    finally:
        secret_value = ""
    if result.returncode:
        raise LocalBridgeError("macOS Keychain did not accept the secret. No browser copy was retained.")
    return f"os_keychain:{service}/{account_name}"


def launch_url(url: str, browser: str) -> None:
    if browser not in BROWSERS:
        raise LocalBridgeError("Choose a supported browser.")
    app = BROWSERS[browser]
    if app is None:
        if not webbrowser.open(url, new=2):
            raise LocalBridgeError("The system browser did not accept the request.")
        return
    result = subprocess.run(["/usr/bin/open", "-a", app, url], check=False, capture_output=True, text=True)
    if result.returncode:
        raise LocalBridgeError(f"{app} is not installed or could not be opened.")


def launch_app(app_id: str) -> str:
    app = SAFE_APPS.get(app_id)
    if not app:
        raise LocalBridgeError("Choose an approved local app.")
    result = subprocess.run(["/usr/bin/open", "-a", app], check=False, capture_output=True, text=True)
    if result.returncode:
        raise LocalBridgeError(f"{app} is not installed or could not be opened.")
    return app


def workspace_targets(apps: Any, urls: Any) -> tuple[list[str], list[str]]:
    if not isinstance(apps, list) or not isinstance(urls, list):
        raise LocalBridgeError("Workspace apps and addresses must be lists.")
    app_ids = list(dict.fromkeys(str(item) for item in apps))
    safe_urls = list(dict.fromkeys(safe_url(str(item)) for item in urls))
    if not app_ids and not safe_urls:
        raise LocalBridgeError("Choose at least one app or approved web address.")
    if len(app_ids) + len(safe_urls) > 6:
        raise LocalBridgeError("A local workspace can open at most six visible targets at once.")
    if any(app_id not in SAFE_APPS for app_id in app_ids):
        raise LocalBridgeError("Every workspace app must be on the approved local app list.")
    return app_ids, safe_urls


@dataclass
class BridgeState:
    token: str
    paused: bool = False
    audit: list[dict[str, Any]] = field(default_factory=list)
    secret_writes: int = 0
    lock: threading.Lock = field(default_factory=threading.Lock)

    def add_audit(self, action: str, target: str, status: str = "approved") -> None:
        with self.lock:
            self.audit.insert(0, {"at": utc_now(), "action": action, "target": target, "status": status})
            del self.audit[MAX_AUDIT_EVENTS:]


class BuddyLocalHandler(SimpleHTTPRequestHandler):
    server_version = "BuddyLocalBridge/1.1"

    @property
    def state(self) -> BridgeState:
        return self.server.bridge_state  # type: ignore[attr-defined]

    def log_message(self, format: str, *args: Any) -> None:
        sys.stdout.write(f"[buddy-local] {self.address_string()} {format % args}\n")
        sys.stdout.flush()

    def _authorized(self) -> bool:
        supplied = self.headers.get("Authorization", "")
        expected = f"Bearer {self.state.token}"
        return secrets.compare_digest(supplied, expected)

    def _json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _payload(self) -> dict[str, Any]:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as error:
            raise LocalBridgeError("Invalid request length.") from error
        if length < 1 or length > MAX_BODY_BYTES:
            raise LocalBridgeError("Request body is empty or too large.")
        try:
            value = json.loads(self.rfile.read(length))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise LocalBridgeError("Request body must be valid JSON.") from error
        if not isinstance(value, dict):
            raise LocalBridgeError("Request body must be a JSON object.")
        return value

    def _require_session(self) -> bool:
        if self._authorized():
            return True
        self._json(HTTPStatus.UNAUTHORIZED, {"ok": False, "error": "Local session token required."})
        return False

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/local/health":
            if not self._require_session():
                return
            self._json(HTTPStatus.OK, {
                "ok": True,
                "schema": "dreamco.buddy_local_bridge.v1",
                "connected": True,
                "paused": self.state.paused,
                "host": "127.0.0.1",
                "retention": "memory_only_last_50_events",
                "capabilities": ["browser_search", "https_open", "approved_app_launch", "approved_workspace_launch", "action_planning", "secure_keychain_intake"],
                "limits": ["no arbitrary clicking or typing", "raw secrets accepted only by the explicit local keychain dialog", "no background takeover"],
                "audit": self.state.audit,
            })
            return
        if path == "/":
            self.path = "/buddy.html"
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        if not self._require_session():
            return
        try:
            payload = self._payload()
            path = urlparse(self.path).path
            if path == "/api/local/pause":
                require_approval(payload)
                self.state.paused = bool(payload.get("paused", True))
                self.state.add_audit("bridge_pause", "local_bridge", "paused" if self.state.paused else "active")
                self._json(HTTPStatus.OK, {"ok": True, "paused": self.state.paused})
                return
            if self.state.paused:
                self._json(HTTPStatus.LOCKED, {"ok": False, "error": "Local actions are paused."})
                return
            if path == "/api/local/secrets/store":
                require_approval(payload)
                if self.state.secret_writes >= MAX_SECRET_WRITES_PER_SESSION:
                    raise LocalBridgeError("Secret write limit reached. Restart the local bridge before adding more keys.")
                provider, account = validate_secret_locator(payload.get("provider"), payload.get("account"))
                try:
                    reference = store_macos_keychain_secret(provider, account, payload.get("secret"))
                finally:
                    payload["secret"] = ""
                self.state.secret_writes += 1
                self.state.add_audit("keychain_secret_store", f"{provider}:{account}", "stored")
                self._json(HTTPStatus.CREATED, {
                    "ok": True,
                    "stored": True,
                    "provider": "os_keychain",
                    "reference": reference,
                    "secretReturned": False,
                    "browserRetention": "cleared_after_request",
                })
                return
            if path == "/api/local/browser/search":
                require_approval(payload)
                engine = str(payload.get("engine", "duckduckgo"))
                browser = str(payload.get("browser", "system"))
                url = search_url(str(payload.get("query", "")), engine)
                launch_url(url, browser)
                self.state.add_audit("browser_search", f"{browser}:{engine}")
                self._json(HTTPStatus.OK, {"ok": True, "opened": True, "browser": browser, "engine": engine})
                return
            if path == "/api/local/browser/open":
                require_approval(payload)
                browser = str(payload.get("browser", "system"))
                url = safe_url(str(payload.get("url", "")))
                launch_url(url, browser)
                self.state.add_audit("browser_open", f"{browser}:{urlparse(url).hostname}")
                self._json(HTTPStatus.OK, {"ok": True, "opened": True, "browser": browser, "host": urlparse(url).hostname})
                return
            if path == "/api/local/apps/open":
                require_approval(payload)
                app_id = str(payload.get("app", ""))
                app = launch_app(app_id)
                self.state.add_audit("app_open", app_id)
                self._json(HTTPStatus.OK, {"ok": True, "opened": True, "app": app})
                return
            if path == "/api/local/workspaces/open":
                require_approval(payload)
                title = " ".join(str(payload.get("title", "")).split())
                if not 2 <= len(title) <= 120:
                    raise LocalBridgeError("Name the workspace in 2 to 120 characters.")
                browser = str(payload.get("browser", "system"))
                if browser not in BROWSERS:
                    raise LocalBridgeError("Choose a supported browser.")
                app_ids, urls = workspace_targets(payload.get("apps", []), payload.get("urls", []))
                opened: list[dict[str, str]] = []
                errors: list[dict[str, str]] = []
                for app_id in app_ids:
                    try:
                        opened.append({"type": "app", "target": launch_app(app_id)})
                    except LocalBridgeError as error:
                        errors.append({"type": "app", "target": app_id, "error": str(error)})
                for url in urls:
                    try:
                        launch_url(url, browser)
                        opened.append({"type": "url", "target": urlparse(url).hostname or "loopback"})
                    except LocalBridgeError as error:
                        errors.append({"type": "url", "target": urlparse(url).hostname or "unknown", "error": str(error)})
                self.state.add_audit("workspace_open", f"{title}:{len(opened)}_opened", "partial" if errors else "approved")
                self._json(HTTPStatus.OK, {
                    "ok": not errors,
                    "status": "opened_with_errors" if errors else "opened",
                    "title": title,
                    "opened": opened,
                    "errors": errors,
                    "controlGranted": False,
                })
                return
            if path == "/api/local/actions/plan":
                objective = " ".join(str(payload.get("objective", "")).split())
                if not 5 <= len(objective) <= 1_000:
                    raise LocalBridgeError("Describe the local task in 5 to 1,000 characters.")
                self._json(HTTPStatus.OK, {
                    "ok": True,
                    "status": "preview_ready",
                    "objective": objective,
                    "executionPermitted": False,
                    "steps": [
                        "Choose an installed app or official HTTPS destination.",
                        "Start read-only and show the exact intended action.",
                        "Request approval for one visible action.",
                        "Record a minimal redacted receipt and return control to the owner.",
                    ],
                })
                return
            self._json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "Unknown local bridge route."})
        except LocalBridgeError as error:
            self._json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(error)})
        except Exception:
            self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"ok": False, "error": "Local bridge action failed safely."})


def serve(host: str, port: int, token: str, open_page: bool) -> int:
    handler = lambda *args, **kwargs: BuddyLocalHandler(*args, directory=str(WEBSITE), **kwargs)
    server = ThreadingHTTPServer((host, port), handler)
    server.bridge_state = BridgeState(token=token)  # type: ignore[attr-defined]
    url = f"http://{host}:{port}/buddy.html#buddy-local-token={token}"
    print(json.dumps({
        "ok": True,
        "url": url,
        "host": host,
        "port": port,
        "security": "loopback_only_ephemeral_token",
        "retention": "memory_only",
    }), flush=True)
    if open_page:
        webbrowser.open(url, new=2)
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve Buddy through an approval-gated local laptop bridge.")
    parser.add_argument("--host", default="127.0.0.1", choices=["127.0.0.1", "localhost"])
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--open", action="store_true", help="Open Buddy in the default browser.")
    parser.add_argument("--token", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if not 1_024 <= args.port <= 65_535:
        parser.error("Port must be between 1024 and 65535.")
    token = args.token or secrets.token_urlsafe(32)
    return serve(args.host, args.port, token, args.open)


if __name__ == "__main__":
    raise SystemExit(main())
