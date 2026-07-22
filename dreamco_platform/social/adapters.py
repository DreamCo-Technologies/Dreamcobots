"""Concrete local and HTTPS adapters for governed social publishing."""

from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.request
import uuid
from pathlib import Path
from urllib.parse import urlsplit

from .manager import SocialManagerError


class LocalSocialOutboxPublisher:
    """Write approved posts to a private local outbox without publishing."""

    name = "buddy-local-social-outbox"

    def __init__(self, platform: str, outbox_dir: Path) -> None:
        self.platform = platform
        self.outbox_dir = outbox_dir.resolve()
        self.outbox_dir.mkdir(parents=True, exist_ok=True, mode=0o700)

    def publish(self, *, account_ref: str, content: str, media_refs: tuple[str, ...]) -> str:
        post_id = f"local-post-{uuid.uuid4().hex[:16]}"
        output = self.outbox_dir / f"{post_id}.json"
        output.write_text(
            json.dumps(
                {
                    "schema": "dreamco.local_social_outbox.v1",
                    "post_id": post_id,
                    "platform": self.platform,
                    "account_ref": account_ref,
                    "content": content,
                    "media_refs": list(media_refs),
                    "live_external_action_taken": False,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        output.chmod(0o600)
        return f"local-social-outbox:{post_id}"


class WebhookSocialPublisher:
    """Publish an approved post through a user-owned HTTPS webhook."""

    name = "buddy-secure-social-webhook"

    def __init__(self, platform: str, endpoint: str, secret_reference: str = "", timeout: int = 15) -> None:
        parsed = urlsplit(endpoint)
        if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
            raise SocialManagerError("Social webhook must be an HTTPS URL without embedded credentials.")
        if secret_reference and not re.fullmatch(r"[A-Z][A-Z0-9_]{2,127}", secret_reference):
            raise SocialManagerError("Social webhook secrets must use an environment-variable reference.")
        self.platform = platform
        self.endpoint = endpoint
        self.secret_reference = secret_reference
        self.timeout = min(max(timeout, 2), 60)

    def publish(self, *, account_ref: str, content: str, media_refs: tuple[str, ...]) -> str:
        secret = os.environ.get(self.secret_reference) if self.secret_reference else ""
        if self.secret_reference and not secret:
            raise SocialManagerError(f"Secret reference {self.secret_reference} is not configured.")
        fingerprint = hashlib.sha256(
            json.dumps([self.platform, account_ref, content, list(media_refs)], separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        payload = json.dumps(
            {
                "schema": "dreamco.social_publish_webhook.v1",
                "platform": self.platform,
                "account_ref": account_ref,
                "content": content,
                "media_refs": list(media_refs),
                "idempotency_key": fingerprint,
            }
        ).encode("utf-8")
        headers = {"Content-Type": "application/json", "Idempotency-Key": fingerprint}
        if secret:
            headers["Authorization"] = f"Bearer {secret}"
        request = urllib.request.Request(self.endpoint, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read(1_000_001)
                if len(body) > 1_000_000:
                    raise SocialManagerError("Social webhook response exceeded 1 MB.")
                parsed_body = json.loads(body.decode("utf-8")) if body else {}
        except SocialManagerError:
            raise
        except Exception as error:
            raise SocialManagerError(f"Social webhook failed: {error}") from error
        return str(parsed_body.get("post_ref") or parsed_body.get("id") or f"webhook:{fingerprint[:16]}")
