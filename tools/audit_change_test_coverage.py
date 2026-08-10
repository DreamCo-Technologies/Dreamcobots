#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / "config/change-impact-test-policy.json").read_text())
EXEMPT = json.loads((ROOT / "config/change-impact-test-exemptions.json").read_text()).get("exemptions", [])
OUT = ROOT / "config/generated/change-impact-test-coverage.json"


def git_lines(*args: str) -> list[str]:
    proc = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if proc.returncode:
        raise SystemExit(proc.stderr)
    return [line.rstrip("\n") for line in proc.stdout.splitlines()]


def changed_name_status(base: str, head: str) -> list[tuple[str, str]]:
    rows = []
    for line in git_lines("diff", "--name-status", base, head):
        parts = line.split("\t")
        if len(parts) >= 2:
            status = parts[0]
            path = parts[-1]
            rows.append((status, path))
    return rows


def valid_exemption(path: str):
    for row in EXEMPT:
        if row.get("path") == path and row.get("reason") and row.get("owner") and row.get("expires", "") >= date.today().isoformat():
            return row
    return None


def tokenise(path: str) -> set[str]:
    stem = Path(path).stem.lower()
    parent = Path(path).parent.name.lower()
    tokens = set(re.split(r"[^a-z0-9]+", f"{stem} {parent}"))
    generic = set(POLICY.get("generic_source_tokens", []))
    return {token for token in tokens if len(token) >= 3 and token not in generic}


def relevant_tests_for(path: str, tests: list[str]) -> list[str]:
    tokens = tokenise(path)
    if not tokens:
        return tests
    matches = []
    for test in tests:
        lower = test.lower()
        if any(token in lower for token in tokens):
            matches.append(test)
    return matches


def focused_tests_for(path: str, tests: list[str]) -> list[str]:
    changed_tests = set(tests)
    matches = []
    for mapping in POLICY.get("focused_test_mappings", []):
        if path not in mapping.get("sources", []):
            continue
        matches.extend(test for test in mapping.get("tests", []) if test in changed_tests)
    return sorted(set(matches))


def high_risk_matches(path: str) -> list[str]:
    lower = path.lower()
    return [word for word in POLICY["high_risk_path_keywords"] if word in lower]


def high_risk_test_evidence(words: list[str], tests: list[str]) -> list[str]:
    if not words:
        return []
    aliases = POLICY.get("high_risk_test_aliases", {})
    wanted = set()
    for word in words:
        wanted.update(aliases.get(word, [word]))
    return [test for test in tests if any(alias in test.lower() for alias in wanted)]


def added_skip_markers(base: str, head: str) -> list[str]:
    proc = subprocess.run(["git", "diff", "--unified=0", base, head, "--", "tests/"], cwd=ROOT, capture_output=True, text=True)
    if proc.returncode:
        raise SystemExit(proc.stderr)
    markers = POLICY.get("skip_markers", [])
    hits = []
    for line in proc.stdout.splitlines():
        if not line.startswith("+") or line.startswith("+++"):
            continue
        if any(marker in line for marker in markers):
            hits.append(line[1:].strip()[:300])
    return hits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    args = parser.parse_args()

    status_rows = changed_name_status(args.base, args.head)
    changed = [path for _status, path in status_rows]
    exts = set(POLICY["executable_extensions"])
    test_paths = POLICY["test_paths"]
    tests = [path for status, path in status_rows if status != "D" and any(path.startswith(prefix) for prefix in test_paths)]
    deleted_tests = [path for status, path in status_rows if status == "D" and any(path.startswith(prefix) for prefix in test_paths)]
    executable = [path for status, path in status_rows if status != "D" and Path(path).suffix in exts and not any(path.startswith(prefix) for prefix in test_paths)]
    skip_hits = added_skip_markers(args.base, args.head) if executable else []

    rows = []
    blockers = []
    for path in executable:
        risk_words = high_risk_matches(path)
        high = bool(risk_words)
        shared = any(path.startswith(prefix) for prefix in POLICY["shared_core_prefixes"])
        exemption = valid_exemption(path)
        heuristic_tests = relevant_tests_for(path, tests)
        focused_tests = focused_tests_for(path, tests)
        relevant = sorted(set(heuristic_tests + focused_tests))
        high_tests = high_risk_test_evidence(risk_words, tests)
        evidence = []
        if relevant:
            evidence.append("relevant_changed_test")
        if focused_tests:
            evidence.append("focused_test_mapping")
        if shared:
            evidence.append("broad_repository_verification_required")
        if high:
            evidence += ["domain_relevant_negative_security_integration_evidence_required", "rollback_review_when_applicable"]
        covered = bool(relevant or exemption)
        if high and not high_tests and not exemption:
            covered = False
            blockers.append(f"{path}: high-risk change lacks domain-relevant changed test evidence")
        elif not covered:
            blockers.append(f"{path}: no relevant changed test evidence or valid exemption")
        rows.append({
            "path": path,
            "risk": "high" if high else "normal",
            "risk_keywords": risk_words,
            "shared_core": shared,
            "relevant_tests": relevant,
            "focused_tests": focused_tests,
            "high_risk_tests": high_tests,
            "evidence": evidence,
            "exemption": exemption,
            "covered": covered,
        })

    if executable and deleted_tests and not tests:
        blockers.append(f"test files deleted without replacement evidence: {', '.join(deleted_tests[:10])}")
    if executable and skip_hits:
        blockers.append(f"new test skip markers added: {len(skip_hits)}")

    payload = {
        "schema": "dreamco.change_impact_test_coverage.v2",
        "base": args.base,
        "head": args.head,
        "changed_file_count": len(changed),
        "changed_test_file_count": len(tests),
        "deleted_test_file_count": len(deleted_tests),
        "changed_executable_file_count": len(executable),
        "new_skip_marker_count": len(skip_hits),
        "deleted_tests": deleted_tests,
        "new_skip_markers": skip_hits,
        "files": rows,
        "release_blockers": blockers,
        "ok": not blockers,
        "truth_boundary": POLICY["truth_rule"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({
        "ok": not blockers,
        "changed": len(changed),
        "executable": len(executable),
        "tests": len(tests),
        "deleted_tests": len(deleted_tests),
        "new_skip_markers": len(skip_hits),
        "blockers": blockers,
    }, indent=2))
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
