"""
DreamCo Repo Bot — Repository Activity Tracker

Monitors repository activity (open issues and pull requests) and
converts detected needs into concrete action items.  In ENTERPRISE
mode it can also auto-generate bot-template stubs to address open
repository tickets.

Key features
------------
* Scan open issues and pull requests (tier-limited).
* Categorise issues/PRs by type (bug, feature, bot-request, …).
* Generate prioritised action items based on detected repo needs.
* Auto-create bot template stubs for bot-request issues (ENTERPRISE).
* Emit structured, enhanced log entries for every scan.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import logging
import os
import re
import sys
from datetime import datetime, timezone
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))
from tiers import Tier, get_tier_config  # noqa: E402

from bots.repo_bot.tiers import BOT_FEATURES, get_bot_tier_info  # noqa: E402
from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Issue/PR scan limits per tier
# ---------------------------------------------------------------------------

ISSUE_SCAN_LIMITS: dict[Tier, int | None] = {
    Tier.FREE: 10,
    Tier.PRO: 50,
    Tier.ENTERPRISE: None,  # unlimited
}

PR_SCAN_LIMITS: dict[Tier, int | None] = {
    Tier.FREE: 5,
    Tier.PRO: 25,
    Tier.ENTERPRISE: None,
}

# ---------------------------------------------------------------------------
# Category keywords
# ---------------------------------------------------------------------------

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "bug": ["bug", "error", "crash", "fail", "broken", "fix", "issue", "exception"],
    "feature": ["feature", "enhancement", "improve", "upgrade", "add", "new", "request"],
    "bot_request": ["bot", "scraper", "automation", "agent", "crawler"],
    "documentation": ["docs", "readme", "document", "example", "guide", "typo"],
    "performance": ["slow", "performance", "speed", "optimise", "optimize", "memory"],
    "security": ["security", "vulnerability", "auth", "token", "secret", "password"],
}


class RepoActivityTrackerTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class RepoActivityTracker:
    """
    Repository activity tracker for the DreamCo Repo Bot.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling feature availability.
    repo_name : str
        Human-readable identifier for the repository being monitored.
    """

    def __init__(
        self,
        tier: Tier = Tier.FREE,
        repo_name: str = "ireanjordan24/Dreamcobots",
    ) -> None:
        self.tier = tier
        self.config = get_tier_config(tier)
        self.repo_name = repo_name
        self._scan_log: list[dict[str, Any]] = []

        # GLOBAL AI SOURCES FLOW — mandatory pipeline
        self._flow = GlobalAISourcesFlow(bot_name="RepoActivityTracker")

        logger.info(
            "RepoActivityTracker initialised (tier=%s, repo=%s)",
            tier.value,
            repo_name,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> str:
        """Run one full activity scan and return a human-readable summary."""
        result = self.scan_activity()
        issues = result["issues_scanned"]
        prs = result["prs_scanned"]
        items = len(result["action_items"])
        summary = (
            f"📋 Scanned {issues} issues, {prs} PRs → {items} action items generated"
        )
        logger.info(summary)
        return summary

    def categorise_item(self, title: str, body: str = "") -> str:
        """
        Categorise an issue or PR based on its title and body text.

        Returns the best-matching category key from ``CATEGORY_KEYWORDS``
        or ``"general"`` if no keyword matches.
        """
        text = (title + " " + body).lower()
        scores: dict[str, int] = {cat: 0 for cat in CATEGORY_KEYWORDS}
        for cat, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    scores[cat] += 1
        best = max(scores, key=lambda k: scores[k])
        return best if scores[best] > 0 else "general"

    def scan_issues(
        self,
        raw_issues: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Scan open issues and return enriched issue records.

        Parameters
        ----------
        raw_issues : list[dict], optional
            Pre-fetched issue data (e.g. from the GitHub API).  Each dict
            must contain at least ``"number"`` (int) and ``"title"`` (str).
            When omitted the method returns a populated mock dataset so the
            bot can run without a live API connection.

        Returns
        -------
        list[dict]
            Enriched issue records with ``number``, ``title``, ``category``,
            and ``priority`` keys added.
        """
        limit = ISSUE_SCAN_LIMITS[self.tier]

        if raw_issues is None:
            raw_issues = _mock_issues()

        if limit is not None:
            raw_issues = raw_issues[:limit]

        enriched: list[dict[str, Any]] = []
        for issue in raw_issues:
            title = issue.get("title", "")
            body = issue.get("body", "")
            category = self.categorise_item(title, body)
            priority = _derive_priority(category, issue.get("labels", []))
            enriched.append(
                {
                    **issue,
                    "category": category,
                    "priority": priority,
                }
            )

        logger.debug("Scanned %d issues (tier=%s)", len(enriched), self.tier.value)
        return enriched

    def scan_pull_requests(
        self,
        raw_prs: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Scan open pull requests and return enriched PR records.

        Parameters
        ----------
        raw_prs : list[dict], optional
            Pre-fetched PR data.  Each dict must contain at least
            ``"number"`` (int) and ``"title"`` (str).
            When omitted the method returns a populated mock dataset.

        Returns
        -------
        list[dict]
            Enriched PR records with ``number``, ``title``, ``category``,
            ``priority``, and ``review_status`` keys added.
        """
        limit = PR_SCAN_LIMITS[self.tier]

        if raw_prs is None:
            raw_prs = _mock_pull_requests()

        if limit is not None:
            raw_prs = raw_prs[:limit]

        enriched: list[dict[str, Any]] = []
        for pr in raw_prs:
            title = pr.get("title", "")
            body = pr.get("body", "")
            category = self.categorise_item(title, body)
            priority = _derive_priority(category, pr.get("labels", []))
            enriched.append(
                {
                    **pr,
                    "category": category,
                    "priority": priority,
                    "review_status": pr.get("review_status", "pending"),
                }
            )

        logger.debug(
            "Scanned %d pull requests (tier=%s)", len(enriched), self.tier.value
        )
        return enriched

    def generate_action_items(
        self,
        issues: list[dict[str, Any]],
        prs: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Generate a prioritised list of action items from scanned issues and PRs.

        High-priority items are listed first.  Each action item contains:
        - ``type``        : ``"issue"`` or ``"pull_request"``
        - ``number``      : issue / PR number
        - ``title``       : issue / PR title
        - ``category``    : detected category
        - ``priority``    : ``"high"``, ``"medium"``, or ``"low"``
        - ``action``      : recommended next step (human-readable)
        """
        items: list[dict[str, Any]] = []

        for issue in issues:
            action = _recommend_action("issue", issue["category"], issue["priority"])
            items.append(
                {
                    "type": "issue",
                    "number": issue.get("number"),
                    "title": issue.get("title", ""),
                    "category": issue["category"],
                    "priority": issue["priority"],
                    "action": action,
                }
            )

        for pr in prs:
            action = _recommend_action("pull_request", pr["category"], pr["priority"])
            items.append(
                {
                    "type": "pull_request",
                    "number": pr.get("number"),
                    "title": pr.get("title", ""),
                    "category": pr["category"],
                    "priority": pr["priority"],
                    "action": action,
                }
            )

        # Sort: high → medium → low
        priority_order = {"high": 0, "medium": 1, "low": 2}
        items.sort(key=lambda x: priority_order.get(x["priority"], 3))
        return items

    def auto_create_bot_stubs(
        self,
        issues: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Auto-generate bot template stubs for bot-request issues.

        Available on ENTERPRISE tier only.

        Parameters
        ----------
        issues : list[dict]
            Enriched issues as returned by :meth:`scan_issues`.

        Returns
        -------
        list[dict]
            Records describing each generated stub, with ``issue_number``,
            ``bot_name``, and ``stub_content`` keys.
        """
        if self.tier != Tier.ENTERPRISE:
            raise RepoActivityTrackerTierError(
                "auto_create_bot_stubs requires ENTERPRISE tier."
            )

        stubs: list[dict[str, Any]] = []
        for issue in issues:
            if issue.get("category") != "bot_request":
                continue

            bot_name = _derive_bot_name(issue.get("title", ""))
            stub = _generate_bot_stub(bot_name, issue.get("title", ""))
            stubs.append(
                {
                    "issue_number": issue.get("number"),
                    "bot_name": bot_name,
                    "stub_content": stub,
                }
            )
            logger.info(
                "Generated bot stub '%s' for issue #%s",
                bot_name,
                issue.get("number"),
            )

        return stubs

    def scan_activity(
        self,
        raw_issues: list[dict[str, Any]] | None = None,
        raw_prs: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Run a complete scan: issues + PRs → action items.

        Parameters
        ----------
        raw_issues : list[dict], optional
        raw_prs : list[dict], optional

        Returns
        -------
        dict with keys: ``issues``, ``pull_requests``, ``action_items``,
        ``issues_scanned``, ``prs_scanned``, ``timestamp``.
        """
        issues = self.scan_issues(raw_issues)
        prs = self.scan_pull_requests(raw_prs)
        action_items = self.generate_action_items(issues, prs)

        result: dict[str, Any] = {
            "repo": self.repo_name,
            "tier": self.tier.value,
            "issues": issues,
            "pull_requests": prs,
            "action_items": action_items,
            "issues_scanned": len(issues),
            "prs_scanned": len(prs),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        self._scan_log.append(
            {
                "issues_scanned": len(issues),
                "prs_scanned": len(prs),
                "action_items": len(action_items),
                "timestamp": result["timestamp"],
            }
        )
        return result

    def get_scan_log(self) -> list[dict[str, Any]]:
        """Return the history of scan runs."""
        return list(self._scan_log)

    def get_tier_info(self) -> dict:
        """Return tier capabilities."""
        return get_bot_tier_info(self.tier)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _derive_priority(category: str, labels: list) -> str:
    """Derive item priority from category and any attached labels."""
    label_names = [
        (lb.get("name", "") if isinstance(lb, dict) else str(lb)).lower()
        for lb in labels
    ]
    if "critical" in label_names or "urgent" in label_names:
        return "high"
    if category in ("bug", "security", "performance"):
        return "high"
    if category in ("feature", "bot_request"):
        return "medium"
    return "low"


def _recommend_action(item_type: str, category: str, priority: str) -> str:
    """Return a concise recommended action string."""
    if category == "bug":
        return "Investigate and patch the bug, add regression test."
    if category == "security":
        return "Escalate immediately — security review required."
    if category == "performance":
        return "Profile the hot path and optimize the slow step."
    if category == "bot_request":
        if item_type == "issue":
            return "Create a new bot to automate the requested workflow."
        return "Review bot implementation and merge if tests pass."
    if category == "feature":
        return "Add the requested feature with tests and documentation."
    if category == "documentation":
        return "Update documentation or README as described."
    return "Review and triage this item."


def _derive_bot_name(title: str) -> str:
    """Derive a snake_case bot name from an issue title."""
    slug = re.sub(r"[^a-z0-9\s]", "", title.lower())
    parts = slug.split()[:4]
    return "_".join(parts) + "_bot" if parts else "new_bot"


def _generate_bot_stub(bot_name: str, description: str) -> str:
    """Generate a minimal bot stub string for a bot-request issue."""
    class_name = "".join(word.capitalize() for word in bot_name.split("_"))
    return f'''\
"""
{class_name} — auto-generated stub from repository issue.

Description: {description}

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))
from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)


class {class_name}:
    """Auto-generated bot with a runnable baseline entry point."""

    def __init__(self) -> None:
        self._flow = GlobalAISourcesFlow(bot_name="{class_name}")

    def run(self) -> str:
        return "{class_name} executed repository activity tracking baseline."
'''


# ---------------------------------------------------------------------------
# Mock datasets (used when no live API connection is available)
# ---------------------------------------------------------------------------

def _mock_issues() -> list[dict[str, Any]]:
    return [
        {
            "number": 101,
            "title": "Fix bug in lead scraper — crashes on empty results",
            "body": "The lead scraper throws an exception when the results list is empty.",
            "labels": [{"name": "bug"}],
            "state": "open",
        },
        {
            "number": 102,
            "title": "Add new bot for LinkedIn automation",
            "body": "We need a bot that automates LinkedIn connection requests.",
            "labels": [],
            "state": "open",
        },
        {
            "number": 103,
            "title": "Improve documentation for CRM manager bot",
            "body": "The README for the CRM manager needs clearer setup instructions.",
            "labels": [],
            "state": "open",
        },
        {
            "number": 104,
            "title": "Performance issue — decision engine is slow under load",
            "body": "The decision engine takes over 2 s per cycle when 1 000+ bots are active.",
            "labels": [],
            "state": "open",
        },
        {
            "number": 105,
            "title": "Security: rotate SERPAPI_KEY and update secret scanning",
            "body": "The API key may have been exposed in a recent commit.",
            "labels": [{"name": "urgent"}],
            "state": "open",
        },
    ]


def _mock_pull_requests() -> list[dict[str, Any]]:
    return [
        {
            "number": 201,
            "title": "Add weighted decision engine to ai_brain",
            "body": "Replaces random.choice() with a data-driven weighted algorithm.",
            "labels": [{"name": "feature"}],
            "state": "open",
            "review_status": "approved",
        },
        {
            "number": 202,
            "title": "Fix crash in maps_scraper when results are empty",
            "body": "Adds a guard clause for empty API responses.",
            "labels": [{"name": "bug"}],
            "state": "open",
            "review_status": "changes_requested",
        },
        {
            "number": 203,
            "title": "Update README with bot architecture overview",
            "body": "Adds a diagram and step-by-step setup guide.",
            "labels": [],
            "state": "open",
            "review_status": "pending",
        },
    ]
