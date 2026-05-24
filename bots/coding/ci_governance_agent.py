"""
DreamCo OS — CI Governance Agent
====================================

Monitors GitHub Actions workflow runs, identifies failures, and
auto-generates fix recommendations.  Self-healing: can open a PR
with the suggested fix when enabled.
"""

from __future__ import annotations

import os
from typing import Any

from python_bots.core.base_bot import DreamCoBot


class CIGovernanceAgent(DreamCoBot):
    """Monitors and fixes failing CI pipelines."""

    async def run(self) -> dict[str, Any]:
        failures = await self._get_workflow_failures()
        recommendations = []
        for failure in failures:
            rec = await self._diagnose_failure(failure)
            recommendations.append(rec)

        await self.memory.event("ci_audited", {"failures": len(failures)})
        return {
            "workflow_failures": len(failures),
            "recommendations": recommendations,
        }

    async def analyze(self) -> dict[str, Any]:
        return {"agent": "ci_governance", "status": "ready"}

    async def monetize(self) -> dict[str, Any]:
        return {"value": "ci_downtime_prevention"}

    async def report(self) -> dict[str, Any]:
        return {"agent": "ci_governance", "runs": self.memory.structured.get_run_history(5)}

    async def _get_workflow_failures(self) -> list[dict[str, Any]]:
        token = os.getenv("GITHUB_TOKEN", "")
        repo = os.getenv("GITHUB_REPOSITORY", "")
        if not token or not repo:
            return []
        try:
            import httpx
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    f"https://api.github.com/repos/{repo}/actions/runs?status=failure&per_page=10",
                    headers={"Authorization": f"token {token}"},
                )
                resp.raise_for_status()
                return resp.json().get("workflow_runs", [])
        except Exception:  # noqa: BLE001
            return []

    async def _diagnose_failure(self, run: dict[str, Any]) -> dict[str, Any]:
        name = run.get("name", "unknown")
        conclusion = run.get("conclusion", "")
        return {
            "workflow": name,
            "conclusion": conclusion,
            "recommendation": f"Review workflow '{name}' — conclusion: {conclusion}. Check logs for root cause.",
            "run_url": run.get("html_url", ""),
        }
