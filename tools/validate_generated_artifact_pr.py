"""Fail-closed validator for generated-artifact review PRs.

Inspects only a bounded Git diff. It never executes candidate code.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys

ALLOWED_PREFIXES = (
    "config/bots/",
    "config/generated/",
    "config/buddy/",
    "website/data/",
    "reports/",
)
BLOCKED_PARTS = {".github", "security", "policy", "secrets", "credentials", "credential", "host-secrets", "workflows", "migrations"}
BLOCKED_NAMES = {".env", ".env.example", "credentials.json", "secrets.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "poetry.lock", "Pipfile.lock"}
MAX_FILES = 20
MAX_CHANGED_LINES = 1500
MAX_DIFF_BYTES = 5 * 1024 * 1024

SECRET_PATTERNS = (
    re.compile(r"(?i)\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"""(?i)["']?(?:api[_-]?key|client[_-]?secret|secret|password|access[_-]?token)["']?\s*[:=]\s*["'][^"'\r\n]+["']"""),
    re.compile(r"""(?i)(?:api[_-]?key|client[_-]?secret|secret|password|access[_-]?token)\s*[:=]\s*[A-Za-z0-9_./+=-]{20,}"""),
)


def validate_changes(name_status: str, diff_text: str) -> list[str]:
    errors = []
    entries = [line.split("\t") for line in name_status.splitlines() if line.strip()]
    if len(entries) > MAX_FILES:
        errors.append(f"Generated change set exceeds the {MAX_FILES}-file limit.")
    if len(diff_text.encode("utf-8")) > MAX_DIFF_BYTES:
        errors.append(f"Generated diff exceeds the {MAX_DIFF_BYTES // (1024 * 1024)} MiB review limit.")
    if "GIT binary patch" in diff_text or re.search(r"(?m)^Binary files .+ differ$", diff_text):
        errors.append("Binary generated artifacts are not reviewable and are blocked.")

    statuses = {}
    for entry in entries:
        if len(entry) != 2 or entry[0] not in {"A", "M"}:
            errors.append(f"Only added or modified generated files are allowed: {entry!r}")
            continue
        path = entry[1]
        if path in statuses:
            errors.append(f"Duplicate generated-file metadata: {path}")
        statuses[path] = entry[0]
        parts = path.split("/")
        basename = parts[-1]
        if path.startswith("/") or "\\" in path or any(part in {"", ".", ".."} for part in parts):
            errors.append(f"Unsafe or non-normalized generated path: {path}")
        if not path.startswith(ALLOWED_PREFIXES):
            errors.append(f"Generated path is outside the artifact allowlist: {path}")
        if any(part in BLOCKED_PARTS for part in parts):
            errors.append(f"Protected path cannot be changed: {path}")
        if basename in BLOCKED_NAMES or path.endswith((".lock", ".pem", ".key")):
            errors.append(f"Protected or credential-bearing file cannot be changed: {path}")

    diff_paths = []
    current_path = None
    in_hunk = False
    changed_lines = 0
    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            in_hunk = False
            match = re.fullmatch(r"diff --git a/(\S+) b/(\S+)", line)
            if not match:
                errors.append("Diff contains an unsupported or ambiguously quoted file path.")
                current_path = None
                continue
            old_path, new_path = match.groups()
            if old_path != new_path:
                errors.append(f"Renames are not allowed: {old_path} -> {new_path}")
            current_path = new_path
            diff_paths.append(new_path)
            if new_path not in statuses:
                errors.append(f"Diff contains a file absent from changed-file metadata: {new_path}")
            continue
        if line.startswith(("old mode ", "new mode ", "deleted file mode ")):
            errors.append("File mode changes are not allowed.")
        elif line.startswith("new file mode ") and line != "new file mode 100644":
            errors.append("Only regular non-executable generated files may be added.")
        elif line.startswith(("--- ", "+++ ")) and current_path:
            marker_path = line[4:]
            if marker_path not in ("/dev/null", f"a/{current_path}", f"b/{current_path}"):
                errors.append(f"Diff header does not match its file section: {current_path}")
        if line.startswith("@@"):
            in_hunk = True
            continue
        if not in_hunk:
            continue
        if line.startswith(("+", "-")):
            changed_lines += 1
        if line.startswith("+") and any(pattern.search(line[1:]) for pattern in SECRET_PATTERNS):
            errors.append("Added generated content appears to contain a credential.")

    if len(diff_paths) != len(set(diff_paths)):
        errors.append("Diff contains duplicate generated-file sections.")
    missing = sorted(set(statuses) - set(diff_paths))
    if missing:
        errors.append("Generated-file metadata has no corresponding inspected diff section: " + ", ".join(missing))
    if changed_lines > MAX_CHANGED_LINES:
        errors.append(f"Generated change set exceeds the {MAX_CHANGED_LINES:,}-line review limit.")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--paths", nargs="+", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"(?:origin/)?[A-Za-z0-9][A-Za-z0-9._/-]{0,127}", args.base) or ".." in args.base:
        parser.error("--base must be a valid bounded Git ref.")
    for path in args.paths:
        if (path.startswith("/") or "\\" in path or ".." in path.split("/")
                or not path.startswith(ALLOWED_PREFIXES)):
            parser.error("--paths must be repository-relative generated artifact paths.")
    name_status = subprocess.run(
        ["git", "diff", "--name-status", "--no-renames", args.base, "--", *args.paths],
        check=True, capture_output=True, text=True,
    ).stdout
    diff_text = subprocess.run(
        ["git", "diff", "--no-ext-diff", "--unified=0", args.base, "--", *args.paths],
        check=True, capture_output=True, text=True,
    ).stdout
    errors = validate_changes(name_status, diff_text)
    if errors:
        for error in errors:
            print(f"BLOCKED: {error}", file=sys.stderr)
        return 2
    if not name_status.strip():
        print("No generated artifact changes found; no PR is needed.")
        return 0
    print("Generated artifact diff passed structural safety checks. Human review and CI are still required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
