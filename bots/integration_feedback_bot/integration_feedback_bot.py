"""
Integration Feedback Bot — DreamCo integration tracking and notification system.

Tracks integration tasks for platforms such as WordPress, Wix, Streamlit,
MySQL, Docker, Terraform, and more.  Logs each event (success or failure)
with timestamps and reasons to ``data/integration_log.json``, and sends
real-time notifications via Slack or Discord.

Sub-systems
-----------
  • IntegrationLogger     — appends structured events to the JSON log
  • SlackNotifier         — dispatches Slack messages via incoming webhooks (PRO+)
  • DiscordNotifier       — dispatches Discord messages via incoming webhooks (PRO+)
  • AutoHealAdvisor       — suggests remediation steps for failed integrations (PRO+)
                           Supports: WordPress, Wix, Streamlit, Stripe, GitHub Actions,
                           MySQL, Docker, Terraform
  • IntegrationAnalytics  — computes success rates and failure summaries (PRO+)
                           Supports daily/weekly/monthly period filtering

Tier access
-----------
  FREE:       Track up to 10 integrations, basic status logging.
  PRO:        Unlimited tracking, Slack/Discord notifications, CSV export,
              auto-heal, period analytics.
  ENTERPRISE: All PRO features + signed webhook delivery, email alerts, analytics.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.

Usage
-----
    from bots.integration_feedback_bot import IntegrationFeedbackBot, Tier

    bot = IntegrationFeedbackBot(tier=Tier.PRO)
    bot.log_integration(
        platform="WordPress",
        status="success",
        details="Plugin v2.3 deployed to production.",
    )
    print(bot.get_summary())
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)
from bots.integration_feedback_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
    FEATURE_BASIC_TRACKING,
    FEATURE_SLACK_NOTIFY,
    FEATURE_EXPORT_CSV,
    FEATURE_AUTO_HEAL,
    FEATURE_WEBHOOK,
    FEATURE_EMAIL_ALERTS,
    FEATURE_ANALYTICS,
)

# ---------------------------------------------------------------------------
# Known platforms and auto-heal suggestions
# ---------------------------------------------------------------------------

_PLATFORMS = [
    "WordPress",
    "Wix",
    "Streamlit",
    "Shopify",
    "HubSpot",
    "Stripe",
    "Twilio",
    "Zapier",
    "Salesforce",
    "GitHub Actions",
    "MySQL",
    "Docker",
    "Terraform",
    "Custom",
]

_AUTO_HEAL_SUGGESTIONS: Dict[str, List[str]] = {
    "WordPress": [
        "Verify SFTP/SSH credentials in the deployment workflow.",
        "Check WordPress REST API authentication token (wp-json auth).",
        "Ensure the plugin zip is well-formed and contains a valid plugin header.",
        "Confirm wp-config.php ABSPATH is accessible from the CI runner.",
    ],
    "Wix": [
        "Confirm the Wix API key has not expired in the Wix Developer Console.",
        "Ensure Velo backend code matches the expected schema.",
        "Check if Wix site is in Maintenance Mode, which blocks API calls.",
        "Validate that Wix Blocks CLI version matches the site's platform version.",
    ],
    "Streamlit": [
        "Verify secrets.toml or st.secrets entries match the cloud app settings.",
        "Confirm the requirements.txt lists all dependencies at compatible versions.",
        "Check the app entrypoint path in Community Cloud matches the repo file.",
        "Ensure no syntax errors are present by running `python -m py_compile app.py`.",
    ],
    "Stripe": [
        "Check that the Stripe API key secret is correctly set in the environment.",
        "Confirm webhook signing secret matches the live endpoint configuration.",
        "Review Stripe event logs at dashboard.stripe.com/events for error details.",
        "Ensure idempotency keys are used for retry logic to avoid duplicate charges.",
    ],
    "GitHub Actions": [
        "Review the failed job logs for the specific step that errored.",
        "Confirm all referenced secrets (SLACK_WEBHOOK_URL, etc.) are set in Settings > Secrets.",
        "Check that the runner OS and Python version match requirements.txt constraints.",
        "Inspect the GITHUB_TOKEN permissions — ensure `contents: write` is granted.",
    ],
    "MySQL": [
        "Verify the database host, port, username, and password in the connection string.",
        "Check that the MySQL user has the required GRANT privileges for the target schema.",
        "Inspect the MySQL error log (`/var/log/mysql/error.log`) for connection refusals.",
        "Ensure the MySQL service is running: `systemctl status mysql` or `docker ps`.",
    ],
    "Docker": [
        "Run `docker logs <container_id>` to inspect the container's stderr output.",
        "Confirm the image tag exists in the registry: `docker pull <image>:<tag>`.",
        "Check available disk space — Docker build failures often stem from full disks.",
        "Validate the Dockerfile syntax and ensure all COPY/ADD source paths exist.",
    ],
    "Terraform": [
        "Run `terraform validate` to catch syntax and reference errors before applying.",
        "Check provider credentials: ensure AWS_ACCESS_KEY_ID / ARM_CLIENT_SECRET are set.",
        "Review the state file lock — another process may hold the lock; run `terraform force-unlock`.",
        "Inspect `terraform plan` output to identify resource diffs causing the failure.",
    ],
    "default": [
        "Review the platform's official documentation for updated API/auth requirements.",
        "Inspect the raw error message and search the platform's community forums.",
        "Retry the operation after a brief delay — transient outages are common.",
        "Contact DreamCo support if the issue persists across multiple retry attempts.",
    ],
}

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

_REPO_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
DEFAULT_LOG_PATH = os.path.join(_REPO_ROOT, "data", "integration_log.json")


# ===========================================================================
# IntegrationLogger
# ===========================================================================


class IntegrationLogger:
    """Reads and writes ``data/integration_log.json``."""

    def __init__(self, log_path: str = DEFAULT_LOG_PATH) -> None:
        self.log_path = log_path

    def load(self) -> Dict[str, Any]:
        if not os.path.exists(self.log_path):
            return {"last_updated": None, "total_entries": 0, "entries": []}
        with open(self.log_path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    def save(self, store: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        with open(self.log_path, "w", encoding="utf-8") as fh:
            json.dump(store, fh, indent=2)

    def append(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Append *entry* to the log and return the updated store."""
        store = self.load()
        entries: List[Dict[str, Any]] = store.get("entries", [])
        entries.append(entry)
        store["entries"] = entries
        store["total_entries"] = len(entries)
        store["last_updated"] = datetime.now(tz=timezone.utc).isoformat()
        self.save(store)
        return store

    def get_all(self) -> List[Dict[str, Any]]:
        return self.load().get("entries", [])

    def get_by_platform(self, platform: str) -> List[Dict[str, Any]]:
        return [e for e in self.get_all()
                if e.get("platform", "").lower() == platform.lower()]

    def get_by_status(self, status: str) -> List[Dict[str, Any]]:
        return [e for e in self.get_all()
                if e.get("status", "").lower() == status.lower()]

    def export_csv(self, output_path: str) -> str:
        import csv
        entries = self.get_all()
        if not entries:
            return output_path
        fieldnames = list(entries[0].keys())
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(entries)
        return output_path


# ===========================================================================
# SlackNotifier
# ===========================================================================


class SlackNotifier:
    """Sends integration feedback notifications to Slack."""

    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url

    def send(self, entry: Dict[str, Any], suggestions: Optional[List[str]] = None) -> bool:
        """
        Post a Slack message for *entry*.  Returns True on HTTP 200.
        """
        try:
            import urllib.request

            platform = entry.get("platform", "Unknown")
            status = entry.get("status", "unknown").upper()
            details = entry.get("details", "")
            ts = entry.get("timestamp", "")
            emoji = ":white_check_mark:" if status == "SUCCESS" else ":x:"

            text = (
                f"{emoji} *Integration {status}* — {platform}\n"
                f"> {details}\n"
                f"> _Logged at {ts}_"
            )

            if status != "SUCCESS" and suggestions:
                sugg_list = "\n".join(f"  • {s}" for s in suggestions[:3])
                text += f"\n\n*Auto-Heal Suggestions:*\n{sugg_list}"

            payload = json.dumps({"text": text}).encode()
            req = urllib.request.Request(
                self.webhook_url,
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status == 200
        except Exception:
            return False


# ===========================================================================
# DiscordNotifier  (PRO+)
# ===========================================================================


class DiscordNotifier:
    """
    Sends integration feedback notifications to a Discord channel via
    an incoming webhook URL (``DISCORD_WEBHOOK_URL``).

    Discord webhooks accept ``{"content": "..."}`` or ``{"embeds": [...]}``
    payloads.  This notifier uses ``embeds`` for rich formatting.
    """

    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url

    def send(self, entry: Dict[str, Any], suggestions: Optional[List[str]] = None) -> bool:
        """
        Post a Discord embed for *entry*.  Returns True on HTTP 204 (Discord's
        success response for webhook posts).
        """
        try:
            import urllib.request

            platform = entry.get("platform", "Unknown")
            status = entry.get("status", "unknown").upper()
            details = entry.get("details", "")
            ts = entry.get("timestamp", "")
            colour = 0x2ECC71 if status == "SUCCESS" else 0xE74C3C  # green / red

            description = details
            if status != "SUCCESS" and suggestions:
                sugg_lines = "\n".join(f"• {s}" for s in suggestions[:3])
                description += f"\n\n**Auto-Heal Suggestions:**\n{sugg_lines}"

            embed = {
                "title": f"Integration {status} — {platform}",
                "description": description,
                "color": colour,
                "footer": {"text": f"DreamCo Integration Feedback • {ts}"},
            }

            payload = json.dumps({"embeds": [embed]}).encode()
            req = urllib.request.Request(
                self.webhook_url,
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status in (200, 204)
        except Exception:
            return False


# ===========================================================================
# AutoHealAdvisor  (PRO+)
# ===========================================================================


class AutoHealAdvisor:
    """
    Suggests remediation steps for failed integrations (PRO+).

    Returns a platform-specific list of actionable fixes, falling back to
    generic suggestions when no platform-specific guide exists.
    """

    def suggest(self, platform: str, reason: str = "") -> List[str]:
        """Return up to 4 remediation steps for *platform*."""
        steps = _AUTO_HEAL_SUGGESTIONS.get(platform, _AUTO_HEAL_SUGGESTIONS["default"])
        return list(steps[:4])


# ===========================================================================
# IntegrationAnalytics  (PRO+)
# ===========================================================================


class IntegrationAnalytics:
    """Computes success rates and failure summaries across logged integrations (PRO+)."""

    _PERIOD_DAYS: Dict[str, int] = {
        "daily": 1,
        "weekly": 7,
        "monthly": 30,
    }

    def _filter_by_period(
        self,
        entries: List[Dict[str, Any]],
        period: Optional[str],
    ) -> List[Dict[str, Any]]:
        """Return *entries* that fall within the requested *period*.

        Parameters
        ----------
        period : str | None
            ``"daily"``, ``"weekly"``, ``"monthly"``, or ``None`` (all time).
        """
        if period is None:
            return entries
        days = self._PERIOD_DAYS.get(period.lower())
        if days is None:
            raise ValueError(
                f"Unknown period '{period}'. "
                f"Valid values: {list(self._PERIOD_DAYS.keys())}"
            )
        cutoff = datetime.now(tz=timezone.utc) - timedelta(days=days)
        result = []
        for e in entries:
            ts_str = e.get("timestamp", "")
            try:
                ts = datetime.fromisoformat(ts_str)
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                if ts >= cutoff:
                    result.append(e)
            except (ValueError, TypeError):
                result.append(e)  # include entries with unparseable timestamps
        return result

    def compute(
        self,
        entries: List[Dict[str, Any]],
        period: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Return analytics computed from *entries*.

        Parameters
        ----------
        entries : list[dict]
            Raw integration log entries.
        period : str | None
            Time window to restrict analysis to: ``"daily"``, ``"weekly"``,
            ``"monthly"``, or ``None`` for all time.

        Keys returned
        -------------
        period : str | None
        total_integrations : int
        success_count : int
        failure_count : int
        success_rate_pct : float
        by_platform : dict[str, dict]
            Per-platform success/failure counts and rate.
        recent_failures : list
            The 5 most recent failure entries.
        """
        scoped = self._filter_by_period(entries, period)
        total = len(scoped)
        success = sum(1 for e in scoped if e.get("status", "").lower() == "success")
        failure = total - success

        by_platform: Dict[str, Dict[str, Any]] = {}
        for entry in scoped:
            p = entry.get("platform", "Unknown")
            if p not in by_platform:
                by_platform[p] = {"success": 0, "failure": 0}
            if entry.get("status", "").lower() == "success":
                by_platform[p]["success"] += 1
            else:
                by_platform[p]["failure"] += 1

        for p, stats in by_platform.items():
            t = stats["success"] + stats["failure"]
            stats["total"] = t
            stats["success_rate_pct"] = round(100 * stats["success"] / t, 1) if t else 0.0

        recent_failures = [
            e for e in reversed(scoped) if e.get("status", "").lower() != "success"
        ][:5]

        return {
            "period": period,
            "total_integrations": total,
            "success_count": success,
            "failure_count": failure,
            "success_rate_pct": round(100 * success / total, 1) if total else 0.0,
            "by_platform": by_platform,
            "recent_failures": recent_failures,
        }


# ===========================================================================
# IntegrationFeedbackBot  (main orchestrator)
# ===========================================================================


class IntegrationFeedbackBot:
    """
    DreamCo Integration Feedback Bot.

    Tracks deployment and integration events, logs them to
    ``data/integration_log.json``, and sends Slack and/or Discord notifications.

    Parameters
    ----------
    tier : Tier
        Subscription tier that governs feature access.
    log_path : str
        Path to the integration log JSON file.
    slack_webhook_url : str | None
        Slack incoming webhook URL.
    discord_webhook_url : str | None
        Discord incoming webhook URL.
    webhook_signing_secret : str | None
        HMAC-SHA256 secret for signing outbound webhook payloads (ENTERPRISE+).
    """

    SUPPORTED_PLATFORMS = _PLATFORMS

    def __init__(
        self,
        tier: Tier = Tier.FREE,
        log_path: str = DEFAULT_LOG_PATH,
        slack_webhook_url: Optional[str] = None,
        discord_webhook_url: Optional[str] = None,
        webhook_signing_secret: Optional[str] = None,
    ) -> None:
        self.tier = tier
        self._config = get_tier_config(tier)
        self._logger = IntegrationLogger(log_path)
        self._advisor = AutoHealAdvisor()
        self._analytics = IntegrationAnalytics()
        self._slack_url = slack_webhook_url or os.getenv("SLACK_WEBHOOK_URL", "")
        self._discord_url = discord_webhook_url or os.getenv("DISCORD_WEBHOOK_URL", "")
        self._signing_secret = webhook_signing_secret or os.getenv(
            "WEBHOOK_SIGNING_SECRET", ""
        )
        self._session_entries: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Tier helpers
    # ------------------------------------------------------------------

    def _enforce_tier(self, required_feature: str) -> None:
        if not self._config.has_feature(required_feature):
            upgrade = get_upgrade_path(self.tier)
            hint = f" Upgrade to {upgrade.name}." if upgrade else ""
            raise PermissionError(
                f"Feature '{required_feature}' is not available on the "
                f"{self.tier.value.upper()} tier." + hint
            )

    def _check_tracking_limit(self) -> None:
        limit = self._config.max_integrations
        if limit is not None:
            total = len(self._logger.get_all())
            if total >= limit:
                raise RuntimeError(
                    f"Integration log limit ({limit}) reached on the "
                    f"{self.tier.value.upper()} tier. Upgrade to log more."
                )

    # ------------------------------------------------------------------
    # Webhook signing (ENTERPRISE+)
    # ------------------------------------------------------------------

    def sign_payload(self, payload: bytes) -> str:
        """
        Return an HMAC-SHA256 hex digest of *payload* using the configured
        signing secret.  Used to authenticate outbound webhook deliveries.

        Raises
        ------
        PermissionError
            If the current tier does not support webhook delivery.
        ValueError
            If no signing secret has been configured.
        """
        self._enforce_tier(FEATURE_WEBHOOK)
        if not self._signing_secret:
            raise ValueError(
                "WEBHOOK_SIGNING_SECRET is not configured. "
                "Set the 'webhook_signing_secret' parameter or the "
                "WEBHOOK_SIGNING_SECRET environment variable."
            )
        return hmac.new(
            self._signing_secret.encode(), payload, hashlib.sha256
        ).hexdigest()

    # ------------------------------------------------------------------
    # Core logging
    # ------------------------------------------------------------------

    def log_integration(
        self,
        platform: str,
        status: str,
        details: str = "",
        reason: str = "",
        version: Optional[str] = None,
        triggered_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Log an integration event.

        Parameters
        ----------
        platform : str
            Target platform (e.g. ``"WordPress"``, ``"Streamlit"``).
        status : str
            ``"success"`` or ``"failure"``.
        details : str
            Human-readable description of what happened.
        reason : str
            Root cause (for failures).
        version : str | None
            Artifact/plugin/app version deployed.
        triggered_by : str | None
            Actor that triggered this event (e.g. ``"GitHub Actions"``).

        Returns
        -------
        dict with keys: ``entry``, ``slack_sent``, ``discord_sent``, ``suggestions``
        """
        self._enforce_tier(FEATURE_BASIC_TRACKING)
        self._check_tracking_limit()

        ts = datetime.now(tz=timezone.utc).isoformat()
        entry: Dict[str, Any] = {
            "platform": platform,
            "status": status.lower(),
            "details": details,
            "reason": reason,
            "version": version,
            "triggered_by": triggered_by or "manual",
            "timestamp": ts,
        }

        self._logger.append(entry)
        self._session_entries.append(entry)

        suggestions: List[str] = []
        if status.lower() != "success" and self._config.has_feature(FEATURE_AUTO_HEAL):
            suggestions = self._advisor.suggest(platform, reason)
            entry["auto_heal_suggestions"] = suggestions

        slack_sent = False
        if self._config.has_feature(FEATURE_SLACK_NOTIFY) and self._slack_url:
            notifier = SlackNotifier(self._slack_url)
            slack_sent = notifier.send(entry, suggestions if suggestions else None)

        discord_sent = False
        if self._config.has_feature(FEATURE_SLACK_NOTIFY) and self._discord_url:
            discord_notifier = DiscordNotifier(self._discord_url)
            discord_sent = discord_notifier.send(
                entry, suggestions if suggestions else None
            )

        return {
            "entry": entry,
            "slack_sent": slack_sent,
            "discord_sent": discord_sent,
            "suggestions": suggestions,
        }

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_log(
        self,
        platform: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Return log entries, optionally filtered by platform and/or status."""
        if platform:
            entries = self._logger.get_by_platform(platform)
        else:
            entries = self._logger.get_all()

        if status:
            entries = [e for e in entries if e.get("status", "").lower() == status.lower()]
        return entries

    def get_analytics(self, period: Optional[str] = None) -> Dict[str, Any]:
        """Return integration success/failure analytics (PRO+).

        Parameters
        ----------
        period : str | None
            ``"daily"``, ``"weekly"``, ``"monthly"``, or ``None`` for all time.
        """
        self._enforce_tier(FEATURE_ANALYTICS)
        return self._analytics.compute(self._logger.get_all(), period=period)

    def export_csv(self, output_path: str = "data/integration_log_export.csv") -> str:
        """Export the integration log to CSV (PRO+)."""
        self._enforce_tier(FEATURE_EXPORT_CSV)
        return self._logger.export_csv(output_path)

    def get_suggestions(self, platform: str) -> List[str]:
        """Return auto-heal suggestions for a platform (PRO+)."""
        self._enforce_tier(FEATURE_AUTO_HEAL)
        return self._advisor.suggest(platform)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def get_summary(self) -> Dict[str, Any]:
        """Return a summary of this session's activity."""
        all_entries = self._logger.get_all()
        success = sum(1 for e in all_entries if e.get("status") == "success")
        failure = len(all_entries) - success
        return {
            "bot": "IntegrationFeedbackBot",
            "tier": self.tier.value,
            "entries_this_session": len(self._session_entries),
            "total_logged": len(all_entries),
            "success_count": success,
            "failure_count": failure,
            "success_rate_pct": round(100 * success / len(all_entries), 1) if all_entries else 0.0,
            "supported_platforms": self.SUPPORTED_PLATFORMS,
            "features_enabled": list(self._config.features),
            "generated_by": "GLOBAL AI SOURCES FLOW",
        }


__all__ = [
    "IntegrationFeedbackBot",
    "IntegrationLogger",
    "SlackNotifier",
    "DiscordNotifier",
    "AutoHealAdvisor",
    "IntegrationAnalytics",
]
