"""Local skills for the plugin gaps. Each one is Buddy's own tool.

The result is a sandbox receipt. It does not call ChatGPT, GitHub, Grok, or Claude.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILLS = [
    "draft a prompt", "summarize a note", "compare two answers", "open an issue",
    "read a public repo", "run a free workflow", "publish Pages", "scan a repo",
    "write a report", "rank a model list", "review a diff", "explain an error",
    "draft a test", "study a free lesson with permission", "save the user's own note",
]


def run_skill(name: str, text: str) -> dict:
    if name not in SKILLS:
        raise ValueError(f"unknown skill: {name}")
    return {"skill": name, "button": name, "output": text.strip()[:240], "third_party_called": False, "secret_stored": False}


def main() -> int:
    report = {"skills": [run_skill(name, name) for name in SKILLS], "third_party_called": False}
    (ROOT / "reports" / "OWN_SKILLS.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (ROOT / "website" / "data" / "own-skills.json").write_text(json.dumps({"skills": SKILLS}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"skills": len(SKILLS), "third_party_called": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
