"""
DreamCo OS — PR Review Agent
==============================

Automatically reviews pull requests using Claude/GPT.
Posts review comments with: code quality, security issues, test coverage gaps,
and compliance with DreamCo bot standards.

Usage::

    agent = PRReviewAgent()
    review = await agent.run()  # reads PR context from env
"""

from __future__ import annotations

import os
from typing import Any

from python_bots.core.base_bot import DreamCoBot


class PRReviewAgent(DreamCoBot):
    """AI-powered PR review agent.

    Environment Variables
    ---------------------
    GITHUB_TOKEN         — GitHub API token
    GITHUB_REPOSITORY    — e.g. DreamCo-Technologies/Dreamcobots
    PR_NUMBER            — Pull request number to review
    OPENAI_API_KEY       — For GPT-4 review
    ANTHROPIC_API_KEY    — For Claude review
    """

    REVIEW_SYSTEM_PROMPT = """You are an expert code reviewer for DreamCo OS, an AI bot operating system.
Review the provided diff and provide feedback on:
1. Code quality and readability
2. Security vulnerabilities (prompt injection, CVEs, hardcoded secrets)
3. DreamCoBot compliance (must inherit DreamCoBot, implement run/analyze/monetize/report)
4. Test coverage gaps
5. Performance concerns
6. Documentation completeness
Be concise, actionable, and constructive."""

    async def run(self) -> dict[str, Any]:
        pr_number = os.getenv("PR_NUMBER", "")
        repo = os.getenv("GITHUB_REPOSITORY", "")
        if not pr_number or not repo:
            return {"skipped": True, "reason": "No PR context — set PR_NUMBER and GITHUB_REPOSITORY"}

        diff = await self._fetch_diff(repo, pr_number)
        if not diff:
            return {"skipped": True, "reason": "Could not fetch PR diff"}

        review = await self._generate_review(diff)
        await self._post_review(repo, pr_number, review)
        await self.memory.event("pr_reviewed", {"pr": pr_number, "repo": repo})
        return {"pr_number": pr_number, "review_posted": True, "length": len(review)}

    async def analyze(self) -> dict[str, Any]:
        return {"agent": "pr_review", "status": "ready"}

    async def monetize(self) -> dict[str, Any]:
        return {"value": "automated_review_cost_savings"}

    async def report(self) -> dict[str, Any]:
        history = self.memory.structured.get_run_history(limit=10)
        return {"recent_runs": len(history), "agent": "pr_review"}

    async def _fetch_diff(self, repo: str, pr_number: str) -> str:
        token = os.getenv("GITHUB_TOKEN", "")
        if not token:
            return ""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files",
                    headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"},
                )
                resp.raise_for_status()
                files = resp.json()
                return "\n\n".join(
                    f"--- {f['filename']} ---\n{f.get('patch', '')}" for f in files[:20]
                )
        except Exception:  # noqa: BLE001
            return ""

    async def _generate_review(self, diff: str) -> str:
        if not diff:
            return "No diff available for review."
        from python_bots.core.model_router import ModelRouter
        router = ModelRouter()
        return await router.complete(
            prompt=f"Review this pull request diff:\n\n{diff[:8000]}",
            system=self.REVIEW_SYSTEM_PROMPT,
            max_tokens=1500,
        )

    async def _post_review(self, repo: str, pr_number: str, body: str) -> None:
        token = os.getenv("GITHUB_TOKEN", "")
        if not token:
            return
        try:
            import httpx
            async with httpx.AsyncClient(timeout=15) as client:
                await client.post(
                    f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews",
                    headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"},
                    json={"body": f"## 🤖 DreamCo AI Review\n\n{body}", "event": "COMMENT"},
                )
        except Exception:  # noqa: BLE001
            pass
