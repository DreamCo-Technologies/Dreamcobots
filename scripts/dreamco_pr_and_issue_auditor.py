"""Audit an untrusted pull-request patch without executing PR code."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SECRET_PATTERNS = {
    "HF_TOKEN": re.compile(r"\bhf_[A-Za-z0-9]{20,}\b"),
    "GITHUB_TOKEN": re.compile(r"\b(?:ghp|gho|ghu|ghs|github_pat)_[A-Za-z0-9_]{20,}\b"),
    "OPENAI_STYLE_KEY": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    "AWS_ACCESS_KEY": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "PRIVATE_KEY": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}
VANITY_PATTERNS = {
    "GUARANTEED_PERFORMANCE": re.compile(r"\b100%\s+guaranteed\b", re.I),
    "UNBEATABLE": re.compile(r"\bunbeatable\b", re.I),
    "AGI_ACHIEVED": re.compile(r"\bAGI\s+achieved\b", re.I),
    "ZERO_LATENCY": re.compile(r"\bzero\s+latency\b", re.I),
}
QUARANTINE_PARTS = ("staging_quarantine/", "staging-quarantine/", "resource_staging/")
EVIDENCE_NAMES = {"evidence_stamp.json", "model_evidence.json", "release_candidate.json"}
SHA256_PATTERN = re.compile(r"\b[a-fA-F0-9]{64}\b")


def fp(code, path, message):
    return hashlib.sha256(f"{code}\0{path}\0{message}".encode()).hexdigest()[:12]


def _set_change_path(changes, files, current, new_path):
    if not new_path or new_path == current:
        return current
    info = changes.pop(current, {"status": "modified", "old_path": current})
    info["new_path"] = new_path
    changes[new_path] = info
    if current in files:
        files[files.index(current)] = new_path
    return new_path


def parse_patch(patch):
    """Return changed paths, added hunk lines, and per-path change metadata.

    Hunk state matters because an added source line may itself begin with
    multiple plus characters. File headers are interpreted only outside hunks.
    """
    files, additions, changes = [], [], {}
    current = None
    new_line = 0
    in_hunk = False

    for line in patch.splitlines():
        if line.startswith("diff --git "):
            in_hunk = False
            match = re.match(r"diff --git a/(.+) b/(.+)$", line)
            if not match:
                current = None
                continue
            old_path, new_path = match.groups()
            current = new_path
            files.append(new_path)
            changes[new_path] = {
                "status": "modified",
                "old_path": old_path,
                "new_path": new_path,
            }
            continue

        if current is None:
            continue

        if not in_hunk and line.startswith("new file mode "):
            changes[current]["status"] = "added"
        elif not in_hunk and line.startswith("deleted file mode "):
            changes[current]["status"] = "deleted"
        elif not in_hunk and line.startswith("rename from "):
            changes[current]["status"] = "renamed"
            changes[current]["old_path"] = line[len("rename from "):]
        elif not in_hunk and line.startswith("rename to "):
            new_path = line[len("rename to "):]
            current = _set_change_path(changes, files, current, new_path)
        elif line.startswith("@@"):
            in_hunk = True
            match = re.search(r"\+(\d+)(?:,(\d+))?", line)
            new_line = int(match.group(1)) if match else 0
        elif not in_hunk and line.startswith("--- "):
            old_path = line[4:]
            if old_path == "/dev/null":
                changes[current]["status"] = "added"
            elif old_path.startswith("a/"):
                changes[current]["old_path"] = old_path[2:]
        elif not in_hunk and line.startswith("+++ "):
            new_path = line[4:]
            if new_path == "/dev/null":
                changes[current]["status"] = "deleted"
            elif new_path.startswith("b/"):
                current = _set_change_path(changes, files, current, new_path[2:])
        elif in_hunk:
            if line.startswith("+"):
                additions.append((current, line[1:], new_line))
                new_line += 1
            elif line.startswith("-"):
                continue
            elif line.startswith(" "):
                new_line += 1
            elif line.startswith("\\"):
                continue

    return sorted(set(files)), additions, changes


def finding(gate, code, severity, path, line, message):
    return {
        "gate": gate,
        "code": code,
        "severity": severity,
        "path": path,
        "line": line or None,
        "message": message,
        "fingerprint": fp(code, path, message),
    }


def _is_quarantine(path):
    normalized = str(path or "").replace("\\", "/").lower()
    return any(part in normalized for part in QUARANTINE_PARTS)


def _checkpoint_scope(path):
    parts = Path(path).parts
    return "/".join(parts[:2]) if len(parts) > 1 else (parts[0] if parts else "")


def _evidence_binds_checkpoint(evidence_text, checkpoint_path):
    """Require changed evidence lines to bind the exact path to a SHA-256."""
    for match in re.finditer(re.escape(checkpoint_path), evidence_text):
        before = evidence_text[max(0, match.start() - 512):match.start()]
        after = evidence_text[match.end():match.end() + 512]
        window = before + after
        if re.search(r"(?:sha256|hash)[\"']?\s*[:=]\s*[\"']?", window, re.I) and SHA256_PATTERN.search(window):
            return True
    return False


def audit(patch, pr_number=None):
    files, additions, changes = parse_patch(patch)
    findings, issues = [], []
    additions_by_path = {}

    for path, added_text, line in additions:
        additions_by_path.setdefault(path, []).append(added_text)
        for code, pattern in SECRET_PATTERNS.items():
            if pattern.search(added_text):
                findings.append(finding(
                    "Code Trust Gate", code, "BLOCKER", path, line,
                    "Possible credential material appears in added PR content. Revoke/rotate the credential and remove it from repository history.",
                ))
        for code, pattern in VANITY_PATTERNS.items():
            if pattern.search(added_text):
                findings.append(finding(
                    "Frontier Claim Trust Gate", code, "BLOCKER", path, line,
                    "Unverified absolute performance claim. Replace it with a bounded, reproducible claim linked to benchmark evidence.",
                ))
        if added_text.startswith(("<<<<<<< ", "=======", ">>>>>>> ")):
            issues.append({
                "issue_type": "MERGE_CONFLICT_MARKER",
                "priority": "CRITICAL",
                "auto_fixable": False,
                "file": path,
                "line": line or None,
                "remediation": "Resolve conflict markers manually and rerun the complete test suite.",
                "fingerprint": fp("MERGE_CONFLICT_MARKER", path, "Conflict marker in added lines"),
            })

    # Check added/modified/renamed paths even when there is no text hunk,
    # including empty and binary files. Deleted paths do not count as commits.
    for path, change in changes.items():
        if change.get("status") == "deleted":
            continue
        touched = [path, change.get("old_path")]
        if any(_is_quarantine(candidate) for candidate in touched):
            findings.append(finding(
                "Clean-Room IP Gate", "QUARANTINE_COMMIT", "BLOCKER", path, 0,
                "A changed path touches quarantined source material. Quarantine must remain outside committed application, training, and release artifacts.",
            ))

    checkpoint_paths = []
    for path, change in changes.items():
        if change.get("status") == "deleted":
            continue
        for candidate in (path, change.get("old_path")):
            normalized_candidate = candidate.replace("\\\\", "/") if candidate else ""
            if normalized_candidate.startswith("checkpoints/") and Path(normalized_candidate).name not in EVIDENCE_NAMES:
                checkpoint_paths.append(normalized_candidate)

    for checkpoint_path in sorted(set(checkpoint_paths)):
        scope = _checkpoint_scope(checkpoint_path)
        evidence_paths = [
            path for path, change in changes.items()
            if change.get("status") != "deleted"
            and Path(path).name in EVIDENCE_NAMES
            and _checkpoint_scope(path) == scope
        ]
        bound = any(
            _evidence_binds_checkpoint(
                "\n".join(additions_by_path.get(evidence_path, [])),
                checkpoint_path,
            )
            for evidence_path in evidence_paths
        )
        if not bound:
            code = "CHECKPOINT_EVIDENCE_NOT_BOUND" if evidence_paths else "CHECKPOINT_WITHOUT_EVIDENCE"
            message = (
                "Changed checkpoint evidence must be added or modified in the same checkpoint scope and bind this exact artifact path to a SHA-256."
                if evidence_paths else
                "Checkpoint artifacts changed without a new or modified evidence manifest in the same checkpoint scope. Bind exact weights, tokenizer, data hashes, and training run."
            )
            findings.append(finding("Evidence Gate", code, "BLOCKER", checkpoint_path, 0, message))

    for path in [p for p in files if p.endswith("competitor_registry.json")]:
        for changed_path, value, line in additions:
            if changed_path == path and re.search(
                r'"(?:pinned_revision|revision)"\s*:\s*"(?:main|master|latest|HEAD)"',
                value,
                re.I,
            ):
                findings.append(finding(
                    "Baseline Reproducibility Gate", "UNPINNED_COMPETITOR_REVISION", "BLOCKER", path, line,
                    "Competitor baseline revisions must be immutable commit SHAs, not branch names or moving tags.",
                ))

    status = "CHANGES_REQUESTED" if any(x["severity"] == "BLOCKER" for x in findings) or issues else "REVIEW_REQUIRED"
    report = {
        "schema": "dreamco.pr_audit_report.v1",
        "system": "DreamCo PR Review & MR Issue Triage",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "pull_request": pr_number,
        "review_status": status,
        "files_reviewed": len(files),
        "changed_files": files,
        "gate_findings": findings,
        "mr_issues_queue": issues,
        "execution_policy": "PR code was not checked out or executed by this trusted audit.",
    }
    report["review_sha256"] = hashlib.sha256(
        json.dumps(report, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return report


def render(report):
    lines = [
        f"## DreamCo Automated PR Review — {report['review_status']}",
        f"- Files reviewed: **{report['files_reviewed']}**",
        f"- Review report SHA-256: {report['review_sha256']}",
        "",
        "### Trust and contract findings",
    ]
    if not report["gate_findings"]:
        lines.append("- No configured patch-level blocker was detected. This is not a full approval; CI and independent reviews remain required.")
    for item in report["gate_findings"]:
        location = f" ({item['path']}:{item['line']})" if item["line"] else f" ({item['path']})"
        lines.append(f"- **{item['severity']} · {item['gate']} · {item['code']}**{location}: {item['message']} [fingerprint {item['fingerprint']}]")
    lines.extend(["", "### MR issue queue"])
    if not report["mr_issues_queue"]:
        lines.append("- No patch-level merge-marker issue detected.")
    for item in report["mr_issues_queue"]:
        lines.append(f"- **{item['priority']} · {item['issue_type']}** ({item['file']}:{item['line']}): {item['remediation']} [fingerprint {item['fingerprint']}]")
    lines.extend([
        "",
        "> This patch scan does not approve a PR, prove clean-room originality, establish legal rights, or replace tests, CodeQL, human review, or branch protection.",
    ])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--diff-file", required=True, type=Path)
    parser.add_argument("--pr-number", type=int)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/pr-audit"))
    args = parser.parse_args()
    report = audit(args.diff_file.read_text(encoding="utf-8", errors="replace"), args.pr_number)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (args.output_dir / "comment.md").write_text(render(report), encoding="utf-8")
    print(json.dumps({
        "review_status": report["review_status"],
        "files_reviewed": report["files_reviewed"],
        "findings": len(report["gate_findings"]),
        "mr_issues": len(report["mr_issues_queue"]),
        "report_sha256": report["review_sha256"],
    }, indent=2))
    return 1 if report["review_status"] == "CHANGES_REQUESTED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
