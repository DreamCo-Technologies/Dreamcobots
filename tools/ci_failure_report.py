"""Create a small, sanitized CI failure report without uploading raw logs."""
from __future__ import annotations
import argparse
import json
import os
import re
from pathlib import Path

REDACTIONS = (
    (re.compile(r"(?i)(authorization:\s*bearer\s+)[^\s]+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)([?&](?:access_token|api_key|apikey|token|secret|password)=)[^&\s]+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"), "[REDACTED_TOKEN]"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "[REDACTED_AWS_KEY]"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"), "[REDACTED_API_KEY]"),
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"), "[REDACTED_PRIVATE_KEY]"),
    (re.compile(r"(?i)\b([A-Z0-9._%+-]+)@([A-Z0-9.-]+\.[A-Z]{2,})\b"), "[REDACTED_EMAIL]"),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[REDACTED_SSN]"),
    (re.compile(r"(?<!\d)(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)"), "[REDACTED_PHONE]"),
)
def sanitize(value: str) -> str:
    for pattern, replacement in REDACTIONS:
        value = pattern.sub(replacement, value)
    return value

def build_report(log_text: str, exit_code: int, *, commit: str = "", run_id: str = "") -> dict:
    excerpt = "\n".join(sanitize(log_text).splitlines()[-100:])[-12000:]
    return {
        "schema_version": "dreamco.ci_failure_report.v1",
        "status": "PASS" if exit_code == 0 else "FAIL",
        "exit_code": int(exit_code),
        "commit": commit[:40],
        "run_id": run_id[:40],
        "raw_log_included": False,
        "failure_excerpt": excerpt if exit_code else "",
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--exit-code", required=True, type=int)
    args = parser.parse_args()
    report = build_report(
        Path(args.log).read_text(encoding="utf-8", errors="replace"),
        args.exit_code,
        commit=os.environ.get("GITHUB_SHA", ""),
        run_id=os.environ.get("GITHUB_RUN_ID", ""),
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
