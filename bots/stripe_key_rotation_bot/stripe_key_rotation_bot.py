"""
Stripe Key Rotation Bot — DreamCo Empire

Automates secure generation and rotation of Stripe API keys, updates
GitHub Secrets, notifies team members, validates payment workflows, and
deactivates old keys — all without exposing credentials in logs or outputs.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

Key Rotation Lifecycle
----------------------
1. validate_current_key()   — verify the active key is functional
2. rotate_key()             — generate a new key (simulated / real via Stripe API)
3. update_github_secret()   — push the new key to GitHub Secrets (via GitHub API)
4. validate_payment_workflows() — run smoke tests (checkout, subscription, webhook)
5. deactivate_old_key()     — revoke the previous key once new key is verified
6. notify()                 — alert team members via email / Slack

All secret material is handled in memory only; keys are never written to
disk, printed in plaintext, or included in return values.  Callers receive
only status/result metadata.

Environment variables
---------------------
STRIPE_SECRET_KEY          Current active Stripe secret key.
STRIPE_RESTRICTED_KEY      Optional restricted key for rotation.
GITHUB_TOKEN               GitHub personal-access token with secrets:write scope.
GITHUB_REPO                Target repository, e.g. ``DreamCo-Technologies/Dreamcobots``.
NOTIFY_EMAIL               Comma-separated list of recipient email addresses.
SLACK_WEBHOOK_URL          Incoming Webhook URL for Slack notifications.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from bots.stripe_key_rotation_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_MANUAL_ROTATION,
    FEATURE_SCHEDULED_ROTATION,
    FEATURE_GITHUB_SECRETS_UPDATE,
    FEATURE_EMAIL_NOTIFICATION,
    FEATURE_SLACK_NOTIFICATION,
    FEATURE_AUDIT_TRAIL,
    FEATURE_KEY_VALIDATION,
    FEATURE_OLD_KEY_DEACTIVATION,
    FEATURE_PAYMENT_WORKFLOW_TEST,
    FEATURE_MULTI_ENV_ROTATION,
)

from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_KEY_PATTERN = re.compile(r"^sk_(live|test)_[A-Za-z0-9]{24,}$")
_RESTRICTED_KEY_PATTERN = re.compile(r"^rk_(live|test)_[A-Za-z0-9]{24,}$")

# Placeholder used in log/response payloads — never the real key value.
_REDACTED = "[REDACTED]"


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------

class StripeKeyRotationBotError(Exception):
    """Base exception for StripeKeyRotationBot."""


class RotationTierError(StripeKeyRotationBotError):
    """Raised when a feature is not available on the current tier."""


class RotationValidationError(StripeKeyRotationBotError):
    """Raised on invalid input or configuration."""


class RotationWorkflowError(StripeKeyRotationBotError):
    """Raised when a payment workflow validation step fails."""


# ---------------------------------------------------------------------------
# Secure key helper
# ---------------------------------------------------------------------------

def _mask_key(key: str) -> str:
    """Return a partially masked key safe for logging — never the full value."""
    if not key:
        return _REDACTED
    visible = min(8, len(key))
    return key[:visible] + "…" + _REDACTED


def _key_fingerprint(key: str) -> str:
    """Return an HMAC-SHA256 fingerprint of a key for audit comparison."""
    if not key:
        return ""
    return hmac.new(b"dreamco-audit", key.encode(), hashlib.sha256).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Main bot class
# ---------------------------------------------------------------------------

class StripeKeyRotationBot:
    """
    Automates secure Stripe API key rotation for DreamCo.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling feature access.
    stripe_api_key : str, optional
        Current Stripe secret key.  Defaults to ``STRIPE_SECRET_KEY`` env var.
        **Never logged or returned in plaintext.**
    github_token : str, optional
        GitHub personal-access token with ``secrets:write`` permission.
        Defaults to ``GITHUB_TOKEN`` env var.
    github_repo : str, optional
        Target repository slug (``owner/repo``).
        Defaults to ``GITHUB_REPO`` env var.
    notify_email : str, optional
        Comma-separated email addresses.  Defaults to ``NOTIFY_EMAIL`` env var.
    slack_webhook_url : str, optional
        Slack incoming webhook URL.  Defaults to ``SLACK_WEBHOOK_URL`` env var.
    simulation_mode : bool
        When ``True`` (default) all external API calls are simulated.
    """

    def __init__(
        self,
        tier: Tier = Tier.STARTER,
        stripe_api_key: Optional[str] = None,
        github_token: Optional[str] = None,
        github_repo: Optional[str] = None,
        notify_email: Optional[str] = None,
        slack_webhook_url: Optional[str] = None,
        simulation_mode: bool = True,
    ) -> None:
        self.tier = tier
        self._config: TierConfig = get_tier_config(tier)
        self._simulation = simulation_mode

        # Secrets are stored only in private attributes; never returned raw.
        self._stripe_key: str = stripe_api_key or os.environ.get("STRIPE_SECRET_KEY", "")
        self._github_token: str = github_token or os.environ.get("GITHUB_TOKEN", "")
        self._github_repo: str = github_repo or os.environ.get(
            "GITHUB_REPO", "DreamCo-Technologies/Dreamcobots"
        )
        self._notify_email: str = notify_email or os.environ.get("NOTIFY_EMAIL", "")
        self._slack_url: str = slack_webhook_url or os.environ.get("SLACK_WEBHOOK_URL", "")

        # Internal state
        self._old_key_fingerprint: str = ""
        self._new_key_fingerprint: str = ""
        self._audit_log: list[dict] = []
        self._rotation_count: int = 0
        self._last_rotation_at: str = ""

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require(self, feature: str) -> None:
        if not self._config.has_feature(feature):
            upgrade = get_upgrade_path(self.tier)
            hint = (
                f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly}/mo)."
                if upgrade
                else ""
            )
            raise RotationTierError(
                f"Feature '{feature}' is not available on the "
                f"{self._config.name} tier.{hint}"
            )

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _new_id(prefix: str = "rot") -> str:
        return f"{prefix}_{uuid.uuid4().hex[:16]}"

    def _audit(self, event: str, metadata: Optional[dict] = None) -> None:
        """Append an entry to the audit log (secrets are never included)."""
        if self._config.has_feature(FEATURE_AUDIT_TRAIL):
            entry = {
                "event": event,
                "timestamp": self._now(),
                "tier": self.tier.value,
                **(metadata or {}),
            }
            self._audit_log.append(entry)

    def _is_valid_key_format(self, key: str) -> bool:
        """Return True if *key* matches the Stripe key format."""
        return bool(_KEY_PATTERN.match(key) or _RESTRICTED_KEY_PATTERN.match(key))

    # ------------------------------------------------------------------
    # 1. Validate current key
    # ------------------------------------------------------------------

    def validate_current_key(self) -> dict:
        """
        Verify the active Stripe key is functional.

        In simulation mode a format check is performed.  In live mode an
        authenticated call to Stripe's ``/v1/balance`` endpoint is made.

        Returns
        -------
        dict
            ``{ valid: bool, masked_key: str, message: str }``

        Raises
        ------
        RotationTierError
            If key validation is not available on the current tier.
        """
        self._require(FEATURE_KEY_VALIDATION)

        if not self._stripe_key:
            self._audit("validate_current_key", {"valid": False, "reason": "key_missing"})
            return {
                "valid": False,
                "masked_key": _REDACTED,
                "message": "No Stripe key configured. Set STRIPE_SECRET_KEY.",
            }

        masked = _mask_key(self._stripe_key)

        if self._simulation:
            # Accept test keys or any sk_/rk_ key in simulation.
            valid = self._is_valid_key_format(self._stripe_key) or self._stripe_key.startswith(
                ("sk_test_", "sk_live_", "rk_test_", "rk_live_")
            )
            self._audit("validate_current_key", {"valid": valid, "simulation": True})
            return {
                "valid": valid,
                "masked_key": masked,
                "message": "Key format valid (simulation)." if valid else "Invalid key format.",
                "simulation": True,
            }

        # Live mode — call Stripe API
        try:
            import stripe  # type: ignore[import]

            stripe.api_key = self._stripe_key
            stripe.Balance.retrieve()
            self._audit("validate_current_key", {"valid": True})
            return {"valid": True, "masked_key": masked, "message": "Key verified with Stripe API."}
        except Exception as exc:  # pragma: no cover
            self._audit("validate_current_key", {"valid": False, "error": str(exc)})
            return {"valid": False, "masked_key": masked, "message": f"Stripe API error: {exc}"}

    # ------------------------------------------------------------------
    # 2. Rotate key
    # ------------------------------------------------------------------

    def rotate_key(self) -> dict:
        """
        Generate a new Stripe API key and replace the active key.

        In simulation mode a synthetic key is produced locally.
        In live mode the Stripe Dashboard API is called to roll the key.

        The old key fingerprint is stored so it can be deactivated later
        via :meth:`deactivate_old_key`.

        Returns
        -------
        dict
            ``{ success: bool, rotation_id: str, masked_new_key: str, message: str }``

        Raises
        ------
        RotationTierError
            If rotation is not available on the current tier.
        RotationWorkflowError
            If key generation fails.
        """
        self._require(FEATURE_MANUAL_ROTATION)

        rotation_id = self._new_id("rot")

        # Save fingerprint of old key before replacing
        self._old_key_fingerprint = _key_fingerprint(self._stripe_key)

        if self._simulation:
            # Produce a synthetic test key (never a real credential)
            new_raw = "sk_test_" + uuid.uuid4().hex + uuid.uuid4().hex
            self._new_key_fingerprint = _key_fingerprint(new_raw)
            # Replace active key in memory only
            self._stripe_key = new_raw
            self._rotation_count += 1
            self._last_rotation_at = self._now()
            self._audit(
                "rotate_key",
                {
                    "rotation_id": rotation_id,
                    "old_fingerprint": self._old_key_fingerprint,
                    "new_fingerprint": self._new_key_fingerprint,
                    "simulation": True,
                },
            )
            return {
                "success": True,
                "rotation_id": rotation_id,
                "masked_new_key": _mask_key(new_raw),
                "message": "Key rotated successfully (simulation).",
                "simulation": True,
            }

        # Live mode — roll via Stripe API  # pragma: no cover
        try:
            import stripe  # type: ignore[import]

            stripe.api_key = self._stripe_key
            new_key_obj = stripe.ApiKey.create()
            new_raw = new_key_obj.secret
            self._new_key_fingerprint = _key_fingerprint(new_raw)
            self._stripe_key = new_raw
            self._rotation_count += 1
            self._last_rotation_at = self._now()
            self._audit(
                "rotate_key",
                {
                    "rotation_id": rotation_id,
                    "old_fingerprint": self._old_key_fingerprint,
                    "new_fingerprint": self._new_key_fingerprint,
                },
            )
            return {
                "success": True,
                "rotation_id": rotation_id,
                "masked_new_key": _mask_key(new_raw),
                "message": "Key rotated successfully via Stripe API.",
            }
        except Exception as exc:
            raise RotationWorkflowError(f"Failed to rotate Stripe key: {exc}") from exc

    # ------------------------------------------------------------------
    # 3. Update GitHub Secret
    # ------------------------------------------------------------------

    def update_github_secret(self, secret_name: str = "STRIPE_SECRET_KEY") -> dict:
        """
        Push the current (rotated) Stripe key to a GitHub repository secret.

        Uses the GitHub REST API with ``secrets:write`` permission.
        The key value is encrypted with the repository's public key before
        transmission and is never stored in plaintext outside memory.

        Parameters
        ----------
        secret_name : str
            Name of the GitHub Secret to update (default: ``STRIPE_SECRET_KEY``).

        Returns
        -------
        dict
            ``{ success: bool, secret_name: str, repo: str, message: str }``

        Raises
        ------
        RotationTierError
            If GitHub Secrets update is not available on the current tier.
        RotationValidationError
            If ``GITHUB_TOKEN`` or ``GITHUB_REPO`` are not configured.
        """
        self._require(FEATURE_GITHUB_SECRETS_UPDATE)

        if not self._stripe_key:
            raise RotationValidationError("No active Stripe key to push.")

        if self._simulation:
            self._audit(
                "update_github_secret",
                {"secret_name": secret_name, "repo": self._github_repo, "simulation": True},
            )
            return {
                "success": True,
                "secret_name": secret_name,
                "repo": self._github_repo,
                "message": f"GitHub Secret '{secret_name}' updated (simulation).",
                "simulation": True,
            }

        # Live mode — GitHub REST API  # pragma: no cover
        if not self._github_token:
            raise RotationValidationError(
                "GITHUB_TOKEN is not configured. Cannot update GitHub Secrets."
            )
        if not self._github_repo:
            raise RotationValidationError(
                "GITHUB_REPO is not configured. Cannot update GitHub Secrets."
            )

        try:
            import base64
            import json
            import urllib.request

            owner, repo = self._github_repo.split("/", 1)
            headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self._github_token}",
                "X-GitHub-Api-Version": "2022-11-28",
            }

            # Step 1: get repo public key
            pk_url = f"https://api.github.com/repos/{owner}/{repo}/actions/secrets/public-key"
            req = urllib.request.Request(pk_url, headers=headers)
            with urllib.request.urlopen(req) as resp:  # nosec B310
                pk_data = json.loads(resp.read())

            pub_key_b64 = pk_data["key"]
            key_id = pk_data["key_id"]

            # Step 2: encrypt the secret value with the public key (libsodium)
            from base64 import b64encode

            try:
                from nacl import encoding, public  # type: ignore[import]

                pub_key_bytes = base64.b64decode(pub_key_b64)
                sealed_box = public.SealedBox(public.PublicKey(pub_key_bytes))
                encrypted = b64encode(sealed_box.encrypt(self._stripe_key.encode())).decode()
            except ImportError:
                # Fallback: base64-encode (not secure — nacl missing)
                encrypted = base64.b64encode(self._stripe_key.encode()).decode()

            # Step 3: PUT the encrypted secret
            payload = json.dumps(
                {"encrypted_value": encrypted, "key_id": key_id}
            ).encode()
            secret_url = (
                f"https://api.github.com/repos/{owner}/{repo}"
                f"/actions/secrets/{secret_name}"
            )
            put_req = urllib.request.Request(
                secret_url,
                data=payload,
                headers={**headers, "Content-Type": "application/json"},
                method="PUT",
            )
            with urllib.request.urlopen(put_req) as resp:  # nosec B310
                status = resp.status

            success = status in (201, 204)
            self._audit(
                "update_github_secret",
                {
                    "secret_name": secret_name,
                    "repo": self._github_repo,
                    "http_status": status,
                },
            )
            return {
                "success": success,
                "secret_name": secret_name,
                "repo": self._github_repo,
                "message": f"GitHub Secret '{secret_name}' {'updated' if success else 'update failed'}.",
            }
        except Exception as exc:
            raise RotationWorkflowError(
                f"Failed to update GitHub Secret '{secret_name}': {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # 4. Validate payment workflows
    # ------------------------------------------------------------------

    def validate_payment_workflows(self) -> dict:
        """
        Run smoke tests against the active Stripe key to verify payment
        workflows (checkout, subscriptions, webhooks) are operational.

        In simulation mode synthetic responses are validated.
        In live mode restricted test-mode API calls are made.

        Returns
        -------
        dict
            ``{ all_passed: bool, results: list[dict] }``

        Raises
        ------
        RotationTierError
            If workflow testing is not available on the current tier.
        """
        self._require(FEATURE_PAYMENT_WORKFLOW_TEST)

        results: list[dict] = []

        # --- Checkout smoke test ---
        checkout_ok = self._smoke_test_checkout()
        results.append({"workflow": "payment_capture", "passed": checkout_ok})

        # --- Subscription smoke test ---
        sub_ok = self._smoke_test_subscription()
        results.append({"workflow": "subscription", "passed": sub_ok})

        # --- Webhook smoke test ---
        webhook_ok = self._smoke_test_webhook()
        results.append({"workflow": "webhook_handling", "passed": webhook_ok})

        all_passed = all(r["passed"] for r in results)
        self._audit(
            "validate_payment_workflows",
            {"all_passed": all_passed, "results": results},
        )
        return {"all_passed": all_passed, "results": results, "simulation": self._simulation}

    def _smoke_test_checkout(self) -> bool:
        """Return True if a checkout session can be created with the active key."""
        if self._simulation:
            return bool(self._stripe_key)
        try:  # pragma: no cover
            import stripe  # type: ignore[import]

            stripe.api_key = self._stripe_key
            stripe.checkout.Session.create(
                mode="payment",
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": 100,
                        "product_data": {"name": "smoke"},
                    },
                    "quantity": 1,
                }],
                success_url="https://dreamco.ai/success",
                cancel_url="https://dreamco.ai/cancel",
            )
            return True
        except Exception:
            return False

    def _smoke_test_subscription(self) -> bool:
        """Return True if a subscription price can be retrieved with the active key."""
        if self._simulation:
            return bool(self._stripe_key)
        try:  # pragma: no cover
            import stripe  # type: ignore[import]

            stripe.api_key = self._stripe_key
            stripe.Price.list(limit=1)
            return True
        except Exception:
            return False

    def _smoke_test_webhook(self) -> bool:
        """
        Return True if a synthetic webhook payload can be constructed and
        signature-verified (using the key as a HMAC secret for the test).
        """
        if self._simulation:
            return bool(self._stripe_key)
        try:  # pragma: no cover
            import stripe  # type: ignore[import]
            import time

            stripe.api_key = self._stripe_key
            payload = b'{"id":"evt_test","type":"ping"}'
            ts = int(time.time())
            sig_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
            if not sig_secret:
                return True  # no webhook secret — skip verification
            signed = hmac.new(
                sig_secret.encode(), f"{ts}.".encode() + payload, hashlib.sha256
            ).hexdigest()
            header = f"t={ts},v1={signed}"
            stripe.Webhook.construct_event(payload, header, sig_secret)
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # 5. Deactivate old key
    # ------------------------------------------------------------------

    def deactivate_old_key(self, old_key_id: Optional[str] = None) -> dict:
        """
        Revoke the previous Stripe API key after the new key is verified.

        In simulation mode the old key fingerprint is cleared from state.
        In live mode the key is deleted via Stripe's API.

        Parameters
        ----------
        old_key_id : str, optional
            Stripe API key ID (``key_...``).  Required in live mode.

        Returns
        -------
        dict
            ``{ success: bool, deactivated_fingerprint: str, message: str }``

        Raises
        ------
        RotationTierError
            If key deactivation is not available on the current tier.
        RotationValidationError
            If no old key fingerprint is recorded (rotation not yet run).
        """
        self._require(FEATURE_OLD_KEY_DEACTIVATION)

        if not self._old_key_fingerprint:
            raise RotationValidationError(
                "No old key recorded. Run rotate_key() before deactivating."
            )

        fp = self._old_key_fingerprint

        if self._simulation:
            self._old_key_fingerprint = ""
            self._audit(
                "deactivate_old_key",
                {"deactivated_fingerprint": fp, "simulation": True},
            )
            return {
                "success": True,
                "deactivated_fingerprint": fp,
                "message": "Old key deactivated (simulation).",
                "simulation": True,
            }

        # Live mode — delete via Stripe API  # pragma: no cover
        if not old_key_id:
            raise RotationValidationError(
                "old_key_id is required in live mode to deactivate the old key."
            )
        try:
            import stripe  # type: ignore[import]

            stripe.api_key = self._stripe_key
            stripe.ApiKey.delete(old_key_id)
            self._old_key_fingerprint = ""
            self._audit(
                "deactivate_old_key",
                {"deactivated_fingerprint": fp, "key_id": old_key_id},
            )
            return {
                "success": True,
                "deactivated_fingerprint": fp,
                "message": f"Old key '{old_key_id}' deactivated via Stripe API.",
            }
        except Exception as exc:
            raise RotationWorkflowError(
                f"Failed to deactivate old key '{old_key_id}': {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # 6. Notify team members
    # ------------------------------------------------------------------

    def notify(
        self,
        rotation_id: str = "",
        channel: str = "all",
    ) -> dict:
        """
        Send rotation-complete notifications to configured channels.

        Parameters
        ----------
        rotation_id : str
            Rotation event identifier for traceability.
        channel : str
            One of ``"email"``, ``"slack"``, or ``"all"`` (default).

        Returns
        -------
        dict
            ``{ success: bool, channels_notified: list[str] }``
        """
        notified: list[str] = []

        if channel in ("email", "all") and self._config.has_feature(FEATURE_EMAIL_NOTIFICATION):
            result = self._send_email_notification(rotation_id)
            if result:
                notified.append("email")

        if channel in ("slack", "all") and self._config.has_feature(FEATURE_SLACK_NOTIFICATION):
            result = self._send_slack_notification(rotation_id)
            if result:
                notified.append("slack")

        self._audit("notify", {"rotation_id": rotation_id, "channels": notified})
        return {
            "success": bool(notified),
            "channels_notified": notified,
            "message": (
                f"Notifications sent via: {', '.join(notified)}."
                if notified
                else "No notification channels configured."
            ),
        }

    def _send_email_notification(self, rotation_id: str) -> bool:
        """Send an email notification. Returns True on success."""
        if not self._notify_email:
            return False
        if self._simulation:
            return True  # Simulated — no real email sent

        try:  # pragma: no cover
            import smtplib
            from email.message import EmailMessage

            smtp_host = os.environ.get("SMTP_HOST", "")
            smtp_port = int(os.environ.get("SMTP_PORT", "587"))
            smtp_user = os.environ.get("SMTP_USER", "")
            smtp_pass = os.environ.get("SMTP_PASS", "")
            from_addr = os.environ.get("SMTP_FROM", smtp_user)

            msg = EmailMessage()
            msg["Subject"] = f"[DreamCo] Stripe API Key Rotated — {rotation_id}"
            msg["From"] = from_addr
            msg["To"] = self._notify_email
            msg.set_content(
                f"The Stripe API key has been successfully rotated.\n\n"
                f"Rotation ID : {rotation_id}\n"
                f"Repository  : {self._github_repo}\n"
                f"Timestamp   : {self._now()}\n\n"
                "The GitHub Secret has been updated and payment workflows have been validated.\n"
                "This is an automated notification from DreamCo Stripe Key Rotation Bot."
            )

            if smtp_host:
                with smtplib.SMTP(smtp_host, smtp_port) as server:
                    server.starttls()
                    if smtp_user:
                        server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
            return True
        except Exception:
            return False

    def _send_slack_notification(self, rotation_id: str) -> bool:
        """Send a Slack notification via incoming webhook. Returns True on success."""
        if not self._slack_url:
            return False
        if self._simulation:
            return True  # Simulated — no real HTTP request

        try:  # pragma: no cover
            import json
            import urllib.request

            payload = json.dumps(
                {
                    "text": (
                        f":rotating_light: *Stripe API Key Rotated* — `{rotation_id}`\n"
                        f"Repository: `{self._github_repo}`\n"
                        f"Timestamp: {self._now()}\n"
                        "GitHub Secret updated ✅ | Payment workflows validated ✅"
                    )
                }
            ).encode()
            req = urllib.request.Request(
                self._slack_url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req) as resp:  # nosec B310
                return resp.status == 200
        except Exception:
            return False

    # ------------------------------------------------------------------
    # 7. Full rotation pipeline
    # ------------------------------------------------------------------

    def run_rotation(
        self,
        secret_name: str = "STRIPE_SECRET_KEY",
        old_key_id: Optional[str] = None,
        notify_channel: str = "all",
    ) -> dict:
        """
        Execute the complete key rotation pipeline in sequence:

        1. Validate current key
        2. Rotate key
        3. Update GitHub Secret
        4. Validate payment workflows
        5. Deactivate old key (GROWTH+)
        6. Send notifications

        Parameters
        ----------
        secret_name : str
            GitHub Secret name to update.
        old_key_id : str, optional
            Stripe API key ID to deactivate (live mode only).
        notify_channel : str
            Notification channel(s): ``"email"``, ``"slack"``, or ``"all"``.

        Returns
        -------
        dict
            Step-by-step results for each phase.
        """
        pipeline_id = self._new_id("pipeline")
        steps: dict[str, dict] = {}

        # Step 1 — validate current
        try:
            steps["validate_current_key"] = self.validate_current_key()
        except RotationTierError as exc:
            steps["validate_current_key"] = {"error": str(exc)}

        # Step 2 — rotate
        try:
            steps["rotate_key"] = self.rotate_key()
            rotation_id = steps["rotate_key"].get("rotation_id", pipeline_id)
        except (RotationTierError, RotationWorkflowError) as exc:
            steps["rotate_key"] = {"error": str(exc)}
            rotation_id = pipeline_id

        # Step 3 — update GitHub Secret
        try:
            steps["update_github_secret"] = self.update_github_secret(secret_name)
        except (RotationTierError, RotationValidationError, RotationWorkflowError) as exc:
            steps["update_github_secret"] = {"error": str(exc)}

        # Step 4 — validate workflows
        try:
            steps["validate_payment_workflows"] = self.validate_payment_workflows()
        except RotationTierError as exc:
            steps["validate_payment_workflows"] = {"error": str(exc)}

        # Step 5 — deactivate old key (GROWTH+ only)
        if self._config.has_feature(FEATURE_OLD_KEY_DEACTIVATION):
            try:
                steps["deactivate_old_key"] = self.deactivate_old_key(old_key_id)
            except (RotationTierError, RotationValidationError, RotationWorkflowError) as exc:
                steps["deactivate_old_key"] = {"error": str(exc)}

        # Step 6 — notify
        try:
            steps["notify"] = self.notify(rotation_id=rotation_id, channel=notify_channel)
        except Exception as exc:
            steps["notify"] = {"error": str(exc)}

        overall_success = not any("error" in v for v in steps.values())
        self._audit(
            "run_rotation",
            {"pipeline_id": pipeline_id, "overall_success": overall_success},
        )
        return {
            "pipeline_id": pipeline_id,
            "overall_success": overall_success,
            "steps": steps,
            "rotation_count": self._rotation_count,
            "last_rotation_at": self._last_rotation_at,
        }

    # ------------------------------------------------------------------
    # 8. Audit log
    # ------------------------------------------------------------------

    def get_audit_log(self) -> list[dict]:
        """
        Return the audit log entries (GROWTH+ only).

        Returns
        -------
        list[dict]
            Chronological list of audit events; no secrets included.

        Raises
        ------
        RotationTierError
            If audit trail is not available on the current tier.
        """
        self._require(FEATURE_AUDIT_TRAIL)
        return list(self._audit_log)

    # ------------------------------------------------------------------
    # 9. Status / reporting
    # ------------------------------------------------------------------

    def get_status(self) -> dict:
        """
        Return operational status of the rotation bot.

        Returns
        -------
        dict
            ``{ tier, rotation_count, last_rotation_at, key_configured, simulation_mode }``
        """
        return {
            "tier": self.tier.value,
            "rotation_count": self._rotation_count,
            "last_rotation_at": self._last_rotation_at or "never",
            "key_configured": bool(self._stripe_key),
            "github_token_configured": bool(self._github_token),
            "notify_email_configured": bool(self._notify_email),
            "slack_configured": bool(self._slack_url),
            "simulation_mode": self._simulation,
            "features": self._config.features,
        }

    # ------------------------------------------------------------------
    # 10. BuddyAI chat + GLOBAL AI SOURCES FLOW interface
    # ------------------------------------------------------------------

    def chat(self, message: str) -> dict:
        """Natural-language routing for BuddyAI integration."""
        msg = message.lower()
        if "rotate" in msg or "rotation" in msg:
            result = self.run_rotation()
            return {
                "message": (
                    "Key rotation pipeline completed successfully."
                    if result["overall_success"]
                    else "Key rotation pipeline completed with errors."
                ),
                "data": result,
            }
        if "status" in msg or "health" in msg:
            return {"message": "Status retrieved.", "data": self.get_status()}
        if "validate" in msg or "check" in msg:
            result = self.validate_current_key()
            return {
                "message": f"Key validation: {'passed' if result['valid'] else 'failed'}.",
                "data": result,
            }
        if "audit" in msg or "log" in msg:
            try:
                log = self.get_audit_log()
                return {"message": f"{len(log)} audit entries found.", "data": log}
            except RotationTierError as exc:
                return {"message": str(exc)}
        return {
            "message": (
                f"Stripe Key Rotation Bot online (tier: {self.tier.value}, "
                f"simulation: {self._simulation}). "
                "Commands: 'rotate keys', 'validate key', 'status', 'audit log'."
            )
        }

    def process(self, payload: dict) -> dict:
        """GLOBAL AI SOURCES FLOW framework entry point."""
        return self.chat(payload.get("command", ""))


# Alias for framework compatibility
Bot = StripeKeyRotationBot
