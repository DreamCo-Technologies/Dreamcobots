"""HashiCorp Vault wrapper with AppRole auth, TTL cache, and env fallback."""

from __future__ import annotations

import os
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable

import requests


@dataclass
class CacheEntry:
    value: dict[str, Any]
    expires_at: float

    def valid(self) -> bool:
        return time.time() < self.expires_at


class VaultClient:
    """Lightweight Vault KV v2 client used by DreamCo services."""

    def __init__(
        self,
        *,
        address: str | None = None,
        role_id: str | None = None,
        secret_id: str | None = None,
        mount: str = "secret",
        cache_ttl_seconds: int = 300,
        timeout: int = 10,
    ) -> None:
        self.address = address or os.getenv("VAULT_ADDR", "")
        self.role_id = role_id or os.getenv("VAULT_ROLE_ID", "")
        self.secret_id = secret_id or os.getenv("VAULT_SECRET_ID", "")
        self.mount = mount
        self.cache_ttl_seconds = cache_ttl_seconds
        self.timeout = timeout
        self.session = requests.Session()
        self._token: str | None = None
        self._token_lease_seconds = 0
        self._token_acquired_at = 0.0
        self._cache: dict[str, CacheEntry] = {}
        self._lock = threading.RLock()

    def _using_env_fallback(self) -> bool:
        return not bool(self.address)

    def _cache_get(self, path: str) -> dict[str, Any] | None:
        entry = self._cache.get(path)
        return entry.value if entry and entry.valid() else None

    def _cache_put(self, path: str, value: dict[str, Any]) -> dict[str, Any]:
        self._cache[path] = CacheEntry(value=value, expires_at=time.time() + self.cache_ttl_seconds)
        return value

    def _headers(self) -> dict[str, str]:
        self._renew_token_if_needed()
        return {"X-Vault-Token": self._token or ""}

    def _renew_token_if_needed(self) -> None:
        if self._using_env_fallback():
            return
        with self._lock:
            if not self._token:
                self._authenticate()
                return
            age = time.time() - self._token_acquired_at
            if self._token_lease_seconds and age > self._token_lease_seconds * 0.75:
                self.session.post(
                    f"{self.address}/v1/auth/token/renew-self",
                    headers={"X-Vault-Token": self._token},
                    timeout=self.timeout,
                )
                self._token_acquired_at = time.time()

    def _authenticate(self) -> None:
        if self._using_env_fallback():
            return
        payload = {"role_id": self.role_id, "secret_id": self.secret_id}
        response = self.session.post(
            f"{self.address}/v1/auth/approle/login",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        auth = response.json()["auth"]
        self._token = auth["client_token"]
        self._token_lease_seconds = int(auth.get("lease_duration", 3600))
        self._token_acquired_at = time.time()

    def get_secret(self, path: str) -> dict[str, Any]:
        """Fetch a secret from Vault KV v2 or environment variables."""
        cached = self._cache_get(path)
        if cached is not None:
            return cached
        if self._using_env_fallback():
            prefix = path.upper().replace("/", "_")
            value = {k[len(prefix) + 1 :]: v for k, v in os.environ.items() if k.startswith(prefix + "_")}
            return self._cache_put(path, value)
        response = self.session.get(
            f"{self.address}/v1/{self.mount}/data/{path}",
            headers=self._headers(),
            timeout=self.timeout,
        )
        response.raise_for_status()
        value = response.json()["data"]["data"]
        return self._cache_put(path, value)

    def put_secret(self, path: str, value: dict[str, Any]) -> dict[str, Any]:
        """Write a KV v2 secret and refresh local cache."""
        if self._using_env_fallback():
            for key, item in value.items():
                os.environ[f"{path.upper().replace('/', '_')}_{key.upper()}"] = str(item)
            return self._cache_put(path, value)
        response = self.session.post(
            f"{self.address}/v1/{self.mount}/data/{path}",
            headers=self._headers(),
            json={"data": value},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return self._cache_put(path, value)

    def rotate_secret(self, path: str, generator: Callable[[dict[str, Any]], dict[str, Any]] | None = None) -> dict[str, Any]:
        """Rotate a secret using a supplied generator or a default timestamped value."""
        current = self.get_secret(path)
        next_value = generator(current) if callable(generator) else {
            **current,
            "rotated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "version": str(int(time.time())),
        }
        return self.put_secret(path, next_value)

    def list_secrets(self, path: str = "") -> list[str]:
        """List secrets from Vault metadata API or derive from environment prefixes."""
        if self._using_env_fallback():
            prefix = path.upper().replace("/", "_")
            matches = set()
            for key in os.environ:
                if prefix and not key.startswith(prefix):
                    continue
                matches.add(key.split("_")[0].lower())
            return sorted(matches)
        response = self.session.request(
            "LIST",
            f"{self.address}/v1/{self.mount}/metadata/{path}".rstrip("/"),
            headers=self._headers(),
            timeout=self.timeout,
        )
        response.raise_for_status()
        return sorted(response.json().get("data", {}).get("keys", []))
