"""Account and plugin catalog. Secrets stay on the host.

A connected name is a label. This file does not log in, and a free action is
a description Buddy can read, not a claim the action already ran.
"""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).with_name("free_actions.md")
ACCOUNTS = {
    "chatgpt": ["custom GPTs", "plugins or apps", "memory", "file upload", "canvas"],
    "github": ["issues", "pull requests", "actions", "pages", "codespaces free quota", "dependabot"],
    "grok": ["chat", "connected tools", "image generation", "file preview"],
    "claude": ["projects", "artifacts", "code tool", "file upload"],
    "codecademy": ["free lessons", "course notes", "practice exercises"],
    "user-added": [],
}
FREE = {
    "chatgpt": ["draft a prompt", "summarize a note", "compare two answers"],
    "github": ["open an issue", "read a public repo", "run a free workflow", "publish Pages"],
    "grok": ["scan a repo", "write a report", "rank a model list"],
    "claude": ["review a diff", "explain an error", "draft a test"],
    "codecademy": ["study a free lesson with permission", "save the user's own note"],
}


def catalog(extra: list[str] | None = None) -> dict:
    accounts = dict(ACCOUNTS)
    if extra:
        accounts["user-added"] = extra
    return {"accounts": accounts, "free_actions": FREE, "secrets_stored": False, "logged_in": False}


def render(report: dict) -> str:
    lines = ["# Free actions Buddy can use", "", "No logins are stored. A row is available only after you connect that account.", ""]
    for name, actions in report["free_actions"].items():
        lines.append(f"## {name}")
        lines.extend(f"- {action}" for action in actions)
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    report = catalog()
    path = Path(__file__).resolve().parents[2] / "reports" / "FREE_ACTIONS.md"
    path.write_text(render(report), encoding="utf-8")
    print(json.dumps({"accounts": len(report["accounts"]), "secrets_stored": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
