# Pull Request Learning Bot

import sys
import os
import json
import re
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from framework import GlobalAISourcesFlow  # noqa: F401 — GLOBAL AI SOURCES FLOW


class PullRequestLearningBot:
    def __init__(self):
        self._flow = GlobalAISourcesFlow(bot_name="PullRequestLearningBot")
        self._learned_patterns: list = []
        self._response_templates: dict = {
            "feature": "Thank you for this feature addition! The changes look well-structured.",
            "bugfix": "Great catch! This bug fix improves system stability.",
            "refactor": "Clean refactoring — the code is more maintainable now.",
            "docs": "Documentation improvements are always appreciated.",
            "test": "Excellent — more test coverage strengthens the codebase.",
            "default": "Thanks for your contribution! The PR has been reviewed.",
        }

    def learn_from_pr(self, pr_data: dict) -> dict:
        """Extract and store patterns from pull request data for future decisions."""
        if not pr_data:
            return {"learned": False, "reason": "empty pr_data"}

        title = pr_data.get("title", "")
        description = pr_data.get("description", pr_data.get("body", ""))
        files_changed = pr_data.get("files_changed", pr_data.get("changed_files", []))
        additions = pr_data.get("additions", 0)
        deletions = pr_data.get("deletions", 0)

        # Classify the PR type from title/description keywords
        pr_type = self._classify_pr(title, description)

        # Extract file extension patterns
        ext_counts: dict = {}
        for f in (files_changed if isinstance(files_changed, list) else []):
            fname = f if isinstance(f, str) else f.get("filename", "")
            ext = os.path.splitext(fname)[-1].lower()
            if ext:
                ext_counts[ext] = ext_counts.get(ext, 0) + 1

        pattern = {
            "pr_type": pr_type,
            "title": title,
            "additions": additions,
            "deletions": deletions,
            "file_extensions": ext_counts,
            "files_changed_count": len(files_changed) if isinstance(files_changed, list) else 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._learned_patterns.append(pattern)
        return {"learned": True, "pattern": pattern, "total_patterns": len(self._learned_patterns)}

    def generate_response(self, pr_data: dict) -> str:
        """Generate a contextual review response based on the pull request data."""
        if not pr_data:
            return self._response_templates["default"]

        title = pr_data.get("title", "")
        description = pr_data.get("description", pr_data.get("body", ""))
        pr_type = self._classify_pr(title, description)

        # Build a richer response using learned patterns
        base = self._response_templates.get(pr_type, self._response_templates["default"])
        additions = pr_data.get("additions", 0)
        deletions = pr_data.get("deletions", 0)
        files_changed = pr_data.get("files_changed", pr_data.get("changed_files", []))
        file_count = len(files_changed) if isinstance(files_changed, list) else 0

        size_note = ""
        if additions + deletions > 500:
            size_note = " This is a large PR — consider breaking it into smaller chunks for easier review."
        elif additions + deletions < 10:
            size_note = " Small, focused change — easy to review."

        scope_note = f" Touches {file_count} file(s)." if file_count else ""
        return f"{base}{scope_note}{size_note}"

    def get_learned_patterns(self) -> list:
        """Return all patterns learned from past PRs."""
        return list(self._learned_patterns)

    def get_stats(self) -> dict:
        """Return summary statistics about learned patterns."""
        if not self._learned_patterns:
            return {"total_prs_learned": 0}
        type_counts: dict = {}
        for p in self._learned_patterns:
            t = p.get("pr_type", "default")
            type_counts[t] = type_counts.get(t, 0) + 1
        return {
            "total_prs_learned": len(self._learned_patterns),
            "pr_type_distribution": type_counts,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _classify_pr(self, title: str, description: str) -> str:
        text = (title + " " + description).lower()
        if re.search(r"\bfix\b|\bbug\b|\bpatch\b|\bresolve\b", text):
            return "bugfix"
        if re.search(r"\brefactor\b|\bclean\b|\bimprove\b|\boptimiz", text):
            return "refactor"
        if re.search(r"\btest\b|\bspec\b|\bunit\b|\bcoverage\b", text):
            return "test"
        if re.search(r"\bdoc\b|\breadme\b|\bcomment\b|\bchangelog\b", text):
            return "docs"
        if re.search(r"\bfeat\b|\bfeature\b|\badd\b|\bnew\b|\bimplement\b", text):
            return "feature"
        return "default"


# Example usage:
if __name__ == '__main__':
    bot = PullRequestLearningBot()
    sample = {
        "title": "feat: add user authentication flow",
        "body": "Implements JWT-based login and registration endpoints.",
        "additions": 120,
        "deletions": 5,
        "changed_files": ["auth/login.py", "auth/register.py", "tests/test_auth.py"],
    }
    result = bot.learn_from_pr(sample)
    print("Learned:", result)
    response = bot.generate_response(sample)
    print("Response:", response)
