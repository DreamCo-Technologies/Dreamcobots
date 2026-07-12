"""Local-first runtime for GitHub Cost Saver Bot.

The bot reduces GitHub spend through compliant alternatives: local execution,
self-hosted runners, artifact retention limits, workflow throttling, and budget
alerts. It never bypasses billing, quotas, permissions, or product terms.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json
import re
from typing import Any


RUNNER_RATES_USD = {
    "ubuntu": 0.006,
    "ubuntu-slim": 0.002,
    "windows": 0.010,
    "macos": 0.062,
}


@dataclass(frozen=True)
class CostFinding:
    """One safe savings opportunity found in the repository."""

    category: str
    severity: str
    path: str
    title: str
    why_it_costs: str
    safe_replacement: str
    estimated_monthly_savings_usd: float = 0.0
    requires_approval: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "severity": self.severity,
            "path": self.path,
            "title": self.title,
            "why_it_costs": self.why_it_costs,
            "safe_replacement": self.safe_replacement,
            "estimated_monthly_savings_usd": round(self.estimated_monthly_savings_usd, 2),
            "requires_approval": self.requires_approval,
        }


@dataclass
class GitHubCostSaverRuntime:
    """Deterministic, local-first cost-control bot for GitHub usage."""

    slug: str = "github-cost-saver"
    name: str = "GitHub Cost Saver Bot"
    division: str = "DreamFinance"
    category: str = "developer-cost-optimization"
    description: str = (
        "Scans repository automation and produces safe savings actions for "
        "GitHub Actions, Pages, Packages, Codespaces, and AI-assisted review spend."
    )
    capabilities: tuple[str, ...] = (
        "GitHub Actions minute risk scan",
        "Artifact and cache retention review",
        "Packages storage cost review",
        "Codespaces local-first replacement plan",
        "Copilot and AI review spend guardrails",
        "Self-hosted runner migration guidance",
        "GitHub Pages free hosting readiness",
        "Budget alert checklist",
        "Pull-request-safe workflow patch planning",
        "Local automation replacement recommendations",
    )
    risk_level: str = "standard"
    approval_required: bool = True
    events: list[dict[str, Any]] = field(default_factory=list)

    def describe(self) -> dict[str, Any]:
        return {
            "slug": self.slug,
            "name": self.name,
            "division": self.division,
            "category": self.category,
            "description": self.description,
            "capabilities": list(self.capabilities),
            "risk_level": self.risk_level,
            "approval_required": self.approval_required,
            "storage_policy": self.storage_policy(),
            "billing_policy": self.billing_policy(),
        }

    def storage_policy(self) -> dict[str, Any]:
        return {
            "mode": "local_first",
            "network_default": "disabled_until_configured",
            "secrets": "environment_or_vault_only",
            "retention": "operator_defined",
            "audit_log": True,
        }

    def billing_policy(self) -> dict[str, Any]:
        return {
            "bypass_billing": False,
            "bypass_terms": False,
            "live_external_action_taken": False,
            "allowed_automatic_actions": [
                "scan_local_repository",
                "estimate_cost_risk",
                "write_local_report",
                "prepare_reviewable_patch_plan",
            ],
            "approval_required_for": [
                "deleting_remote_artifacts",
                "changing_repository_settings",
                "changing_org_budgets",
                "disabling_paid_products",
                "pushing workflow edits",
            ],
        }

    def scan_repository(self, repo_path: str | Path = ".") -> dict[str, Any]:
        root = Path(repo_path).resolve()
        workflows = sorted((root / ".github" / "workflows").glob("*.yml"))
        workflows += sorted((root / ".github" / "workflows").glob("*.yaml"))

        findings: list[CostFinding] = []
        for workflow in workflows:
            text = workflow.read_text(encoding="utf-8", errors="ignore")
            findings.extend(self._scan_workflow(workflow.relative_to(root), text))

        if (root / ".devcontainer").exists() or any(root.glob("**/devcontainer.json")):
            findings.append(
                CostFinding(
                    category="codespaces",
                    severity="medium",
                    path=".devcontainer",
                    title="Codespaces/devcontainer config present",
                    why_it_costs="Cloud dev environments can accrue compute and storage while active or retained.",
                    safe_replacement="Prefer local VS Code/devcontainer runs for daily work; keep Codespaces for client demos only.",
                    estimated_monthly_savings_usd=15.0,
                )
            )

        if any(root.glob("**/Dockerfile")):
            findings.append(
                CostFinding(
                    category="packages",
                    severity="low",
                    path="repository",
                    title="Container image publishing may create package storage",
                    why_it_costs="GitHub Packages shares storage allowance with Actions artifacts.",
                    safe_replacement="Use local image builds by default, prune old package versions, and publish only release images.",
                    estimated_monthly_savings_usd=3.0,
                )
            )

        findings.append(
            CostFinding(
                category="budgets",
                severity="high",
                path="GitHub billing settings",
                title="Set budget alerts before enabling metered products",
                why_it_costs="Actions, storage, Codespaces, and AI usage can continue until a budget or payment block stops it.",
                safe_replacement="Set soft budgets and email alerts at 50%, 75%, 90%, and 100% for the account or organization.",
                estimated_monthly_savings_usd=25.0,
                requires_approval=True,
            )
        )

        summary = self._summarize(findings)
        return {
            "bot": self.slug,
            "repo_path": str(root),
            "scanned_at": datetime.now(timezone.utc).isoformat(),
            "workflow_count": len(workflows),
            "findings": [finding.as_dict() for finding in findings],
            "summary": summary,
            "recommendations": self.recommendations(findings),
            "live_external_action_taken": False,
        }

    def _scan_workflow(self, relative_path: Path, text: str) -> list[CostFinding]:
        findings: list[CostFinding] = []
        path = str(relative_path)
        lowered = text.lower()

        runners = re.findall(r"runs-on:\s*([^\n#]+)", text)
        for runner in runners:
            runner_value = runner.strip().strip("'\"").lower()
            if "macos" in runner_value:
                findings.append(
                    CostFinding(
                        category="actions_minutes",
                        severity="high",
                        path=path,
                        title="macOS runner detected",
                        why_it_costs="macOS GitHub-hosted runners have a much higher minute rate than Linux.",
                        safe_replacement="Run routine checks on ubuntu-latest or a self-hosted Mac only when macOS is required.",
                        estimated_monthly_savings_usd=16.8,
                    )
                )
            elif "windows" in runner_value:
                findings.append(
                    CostFinding(
                        category="actions_minutes",
                        severity="medium",
                        path=path,
                        title="Windows runner detected",
                        why_it_costs="Windows GitHub-hosted runners cost more per minute than Linux.",
                        safe_replacement="Move non-Windows-specific jobs to ubuntu-latest or local preflight checks.",
                        estimated_monthly_savings_usd=2.4,
                    )
                )
            elif "larger" in runner_value or "arc" in runner_value:
                findings.append(
                    CostFinding(
                        category="actions_minutes",
                        severity="high",
                        path=path,
                        title="Larger/custom runner label detected",
                        why_it_costs="Larger runners can be billed even when standard runner minutes are available.",
                        safe_replacement="Use standard runners or self-hosted runners unless the job needs extra capacity.",
                        estimated_monthly_savings_usd=20.0,
                    )
                )

        if "schedule:" in lowered:
            cron_count = lowered.count("cron:")
            if cron_count >= 1:
                findings.append(
                    CostFinding(
                        category="actions_minutes",
                        severity="medium",
                        path=path,
                        title="Scheduled workflow consumes recurring minutes",
                        why_it_costs="Scheduled runs execute whether or not client-facing work changed.",
                        safe_replacement="Gate schedules with path checks, reduce frequency, or run local nightly scans.",
                        estimated_monthly_savings_usd=6.0 * cron_count,
                    )
                )

        if "upload-artifact" in lowered and "retention-days" not in lowered:
            findings.append(
                CostFinding(
                    category="actions_storage",
                    severity="high",
                    path=path,
                    title="Artifact upload without retention-days",
                    why_it_costs="Artifacts accrue storage charges until they expire or are deleted.",
                    safe_replacement="Set retention-days to 1-7 for diagnostics and 14-30 only for release evidence.",
                    estimated_monthly_savings_usd=5.0,
                )
            )

        if "actions/cache" in lowered and "restore-keys" in lowered:
            findings.append(
                CostFinding(
                    category="actions_cache",
                    severity="low",
                    path=path,
                    title="Broad cache restore keys can grow cache usage",
                    why_it_costs="Cache storage above included per-repository allowance can become billable.",
                    safe_replacement="Use narrow cache keys, dependency lockfile hashes, and periodic cache cleanup.",
                    estimated_monthly_savings_usd=1.5,
                )
            )

        if "copilot" in lowered and ("review" in lowered or "pull_request" in lowered):
            findings.append(
                CostFinding(
                    category="ai_review",
                    severity="high",
                    path=path,
                    title="AI code review workflow may consume credits and minutes",
                    why_it_costs="AI review can consume AI credits and, for private repositories, Actions minutes.",
                    safe_replacement="Use local lint/test review first; run AI review only on ready-for-review pull requests.",
                    estimated_monthly_savings_usd=12.0,
                )
            )

        return findings

    def _summarize(self, findings: list[CostFinding]) -> dict[str, Any]:
        by_category: dict[str, int] = {}
        for finding in findings:
            by_category[finding.category] = by_category.get(finding.category, 0) + 1
        return {
            "finding_count": len(findings),
            "high_severity": sum(1 for finding in findings if finding.severity == "high"),
            "estimated_monthly_savings_usd": round(
                sum(finding.estimated_monthly_savings_usd for finding in findings),
                2,
            ),
            "by_category": by_category,
        }

    def recommendations(self, findings: list[CostFinding]) -> list[dict[str, Any]]:
        actions = [
            {
                "priority": 1,
                "action": "Use GitHub Pages for static client previews before paid hosting.",
                "owner": "Buddy",
                "approval_required": False,
            },
            {
                "priority": 2,
                "action": "Run heavy test suites locally or on self-hosted runners before GitHub-hosted CI.",
                "owner": "Buddy",
                "approval_required": False,
            },
            {
                "priority": 3,
                "action": "Set artifact retention-days on every upload-artifact step.",
                "owner": "Buddy",
                "approval_required": True,
            },
            {
                "priority": 4,
                "action": "Turn off paid AI/code review automation except on final PR review passes.",
                "owner": "Owner",
                "approval_required": True,
            },
        ]
        if any(finding.category == "codespaces" for finding in findings):
            actions.append(
                {
                    "priority": 5,
                    "action": "Use laptop-local dev servers for everyday work and reserve cloud dev environments for demos.",
                    "owner": "Buddy",
                    "approval_required": False,
                }
            )
        return sorted(actions, key=lambda item: item["priority"])

    def write_report(self, repo_path: str | Path = ".", output_path: str | Path | None = None) -> dict[str, Any]:
        scan = self.scan_repository(repo_path)
        root = Path(repo_path).resolve()
        target = Path(output_path) if output_path else root / "reports" / "github_cost_saver_report.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(scan, indent=2), encoding="utf-8")
        event = {
            "type": "github_cost_saver.write_report",
            "at": datetime.now(timezone.utc).isoformat(),
            "path": str(target),
            "estimated_monthly_savings_usd": scan["summary"]["estimated_monthly_savings_usd"],
        }
        self.events.append(event)
        return {**scan, "report_path": str(target)}

    def run(self, objective: str = "scan repository for GitHub cost savings", context: dict[str, Any] | None = None) -> dict[str, Any]:
        context = context or {}
        repo_path = context.get("repo_path", ".")
        write_report = bool(context.get("write_report", False))
        result = self.write_report(repo_path) if write_report else self.scan_repository(repo_path)
        result["objective"] = objective
        result["evaluation"] = self.evaluate(result)
        return result

    def evaluate(self, result: dict[str, Any]) -> dict[str, Any]:
        checks = {
            "has_summary": bool(result.get("summary")),
            "has_recommendations": bool(result.get("recommendations")),
            "no_live_external_action": result.get("live_external_action_taken") is False,
            "billing_bypass_disabled": self.billing_policy()["bypass_billing"] is False,
        }
        return {
            "bot": self.slug,
            "ready_for_smoke_test": all(checks.values()),
            "checks": checks,
        }


def create_bot() -> GitHubCostSaverRuntime:
    return GitHubCostSaverRuntime()
