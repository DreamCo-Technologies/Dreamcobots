"""
DevOps Bot — Auto-Commit + Auto-Push System

Detects new bots created or changes to existing files and automatically
commits and pushes them to the GitHub repository.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)


class DevOpsBot:
    """Automatically stages, commits, and pushes repository changes to GitHub.

    Detects new bots or modified files via ``git add .`` and creates a
    timestamped commit before pushing to the remote origin.
    """

    def run(self) -> str:
        """Stage all changes, commit, and push to GitHub.

        Returns
        -------
        str
            Status message describing the result of the operation.
        """
        os.system("git add .")
        commit_rc = os.system('git commit -m "🤖 Auto-update from DreamCo"')
        if commit_rc != 0:
            return "⚠️ Nothing to commit or commit failed"
        push_rc = os.system("git push")
        if push_rc != 0:
            return "❌ Push failed — check remote configuration"
        return "🚀 Changes pushed to GitHub"

    def process(self, payload: dict | None = None) -> dict:
        """GLOBAL AI SOURCES FLOW framework entry point."""
        result = self.run()
        return {"status": result}


# Backwards-compatible alias expected by the control center / test harness.
Bot = DevOpsBot
