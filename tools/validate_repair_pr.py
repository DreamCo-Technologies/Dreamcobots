"""Fail-closed validator for manually prepared repair-PR branches.

Only Git metadata and added diff text are inspected. Candidate code is never
checked out or executed.
"""
from __future__ import annotations
import argparse
import re
import subprocess
import sys

ALLOWED_PREFIXES = ("buddy/", "server/", "client/", "shared/", "tools/")
BLOCKED_PARTS = {".github", "contracts", "security", "policy", "secrets", "host-secrets", "workflows", "migrations"}
BLOCKED_NAMES = {".env", ".env.example", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "poetry.lock", "Pipfile.lock"}
MAX_FILES = 20
MAX_CHANGED_LINES = 1500
SECRET_PATTERNS = (
    re.compile(r"(?i)\\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\\b"),
    re.compile(r"\\bAKIA[0-9A-Z]{16}\\b"),
    re.compile(r"\\bsk-[A-Za-z0-9_-]{20,}\\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)(?:api[_-]?key|secret|password|access_token)\\s*[:=]\\s*['\"]?[A-Za-z0-9_./+=-]{20,}"),
)

def validate_changes(name_status: str, diff_text: str) -> list[str]:
    errors = []
    entries = [line.split("\\t") for line in name_status.splitlines() if line.strip()]
    if not entries:
        errors.append("No changed files were found.")
    if len(entries) > MAX_FILES:
        errors.append(f"Change set exceeds the {MAX_FILES}-file limit.")
    changed_lines = 0
    for entry in entries:
        status = entry[0]
        if status not in {"A", "M"} or len(entry) != 2:
            errors.append(f"Only added or modified files are allowed: {entry!r}")
            continue
        path = entry[1]
        parts = path.split("/")
        if not path.startswith(ALLOWED_PREFIXES):
            errors.append(f"Path is outside the source-code allowlist: {path}")
        if any(part in BLOCKED_PARTS for part in parts):
            errors.append(f"Protected path cannot be changed: {path}")
        if path in BLOCKED_NAMES or path.endswith((".lock", ".pem", ".key")):
            errors.append(f"Protected or credential-bearing file cannot be changed: {path}")
        if path == "tools/validate_repair_pr.py":
            errors.append("The repair validator cannot modify itself.")
    for line in diff_text.splitlines():
        if line.startswith(("+++", "---")):
            continue
        if line.startswith(("+", "-")):
            changed_lines += 1
        if line.startswith("+") and any(pattern.search(line[1:]) for pattern in SECRET_PATTERNS):
            errors.append("Added diff content appears to contain a credential.")
    if changed_lines > MAX_CHANGED_LINES:
        errors.append(f"Change set exceeds the {MAX_CHANGED_LINES}-line limit.")
    return sorted(set(errors))

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    args = parser.parse_args()
    name_status = subprocess.run(
        ["git", "diff", "--name-status", "--no-renames", f"{args.base}...{args.head}"],
        check=True, capture_output=True, text=True,
    ).stdout
    diff_text = subprocess.run(
        ["git", "diff", "--no-ext-diff", "--unified=0", f"{args.base}...{args.head}"],
        check=True, capture_output=True, text=True,
    ).stdout
    errors = validate_changes(name_status, diff_text)
    if errors:
        for error in errors:
            print(f"BLOCKED: {error}", file=sys.stderr)
        return 2
    print("Repair branch passed structural safety checks. Human review and CI are still required.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
