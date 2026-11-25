#!/usr/bin/env python3
"""Generate an evidence-first daily production-readiness master list."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import urllib.request
import urllib.error
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts/dreamco-reconciliation"
POLICY = ROOT / "governance/dreamco-always-on-policy.json"
EVIDENCE = ROOT / "governance/dreamco-requirement-evidence.json"
REGISTRY = ROOT / "config/masterbot-65-registry.json"

# These files are curricula, bot descriptions, agent notes, or generated catalogs/audits.
# They remain available in their own validation systems, but are not product requirements.
EXCLUDED_PREFIXES = (
    ".agents/memory/", "bots/", "study_packs/", "data/",
    "buddy/bootcamp/", "buddy/frontier/", "capabilities/",
)
EXCLUDED_EXACT = {
    "reports/MARKDOWN_IMPLEMENTATION_GAP_AUDIT.md",
    "reports/BOT_ACCOUNTING_PLACEMENT_AUDIT.md",
    "reports/BOT_DIVISION_PLACEMENT_AUDIT.md",
    "docs/BUDDY_ADDITIONAL_TAXONOMY_SYSTEMS.md",
    "docs/BUDDY_TASK_AND_MARKDOWN_TAXONOMY_SYSTEMS.md",
}


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def is_requirement_source(path: Path) -> bool:
    relative = path.relative_to(ROOT).as_posix()
    return (
        relative.endswith((".md", ".mdx"))
        and relative not in EXCLUDED_EXACT
        and not any(relative.startswith(prefix) for prefix in EXCLUDED_PREFIXES)
    )


def tracked() -> list[Path]:
    try:
        rows = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    except Exception:
        rows = [path.relative_to(ROOT).as_posix() for path in ROOT.rglob("*") if path.is_file()]
    return [ROOT / row for row in rows if row and is_requirement_source(ROOT / row)]


def classify_requirement(evidence: dict) -> str:
    """A Markdown bullet is only a candidate until explicitly confirmed by a reviewer."""
    return "CONFIRMED_REQUIREMENT" if evidence.get("confirmed_requirement") is True else "UNTRIAGED_CANDIDATE"


def missing_requirement_evidence(evidence: dict) -> list[str]:
    """Only confirmed requirements create evidence obligations; candidates stay triage-only."""
    if classify_requirement(evidence) != "CONFIRMED_REQUIREMENT":
        return []
    return [key for key in ("implementation", "tests", "runtime_routes", "benchmark_evidence") if not evidence.get(key)]


def build_candidate_triage(requirements: list[dict]) -> list[dict]:
    grouped: dict[str, dict] = {}
    for item in requirements:
        source = item["source"]
        entry = grouped.setdefault(source, {"source": source, "candidate_count": 0, "sample_requirement_ids": []})
        entry["candidate_count"] += 1
        if len(entry["sample_requirement_ids"]) < 5:
            entry["sample_requirement_ids"].append(item["id"])
    return sorted(grouped.values(), key=lambda item: (-item["candidate_count"], item["source"]))


def verify_github_check(repository: str, check_id: str, current_sha: str, token: str | None) -> bool:
    """Verify a GitHub Actions run or check-run completed successfully on this exact SHA."""
    if not token or not check_id.isdigit():
        return False
    endpoints = (
        f"https://api.github.com/repos/{repository}/actions/runs/{check_id}",
        f"https://api.github.com/repos/{repository}/check-runs/{check_id}",
    )
    for url in endpoints:
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                continue
            return False
        except Exception:
            return False
        return (
            payload.get("head_sha") == current_sha
            and payload.get("status") == "completed"
            and payload.get("conclusion") == "success"
        )
    return False


def build_production_gate_records(
    policy: dict,
    evidence: dict,
    current_sha: str,
    repository: str,
    token: str | None,
    *,
    root: Path = ROOT,
    verify_check=verify_github_check,
) -> tuple[list[dict], list[dict]]:
    """Require existing evidence artifacts and a successful GitHub check on the same SHA."""
    records = []
    findings = []
    gate_evidence = evidence.get("production_gates", {})
    for gate in policy.get("production_gates", []):
        entry = gate_evidence.get(gate, {})
        refs = entry.get("evidence", []) if isinstance(entry, dict) else []
        verified_refs = []
        errors = []
        if not isinstance(refs, list) or not refs:
            errors.append("no evidence references recorded")
        else:
            for ref in refs:
                if not isinstance(ref, dict) or not all(ref.get(key) for key in ("path", "sha", "check_id")):
                    errors.append("evidence reference is missing path, sha, or check_id")
                    continue
                relative = Path(str(ref["path"]))
                if relative.is_absolute() or ".." in relative.parts:
                    errors.append("evidence path is unsafe")
                    continue
                artifact = (root / relative).resolve()
                try:
                    artifact.relative_to(root.resolve())
                except ValueError:
                    errors.append("evidence path escapes repository root")
                    continue
                if not artifact.is_file():
                    errors.append(f"evidence artifact does not exist: {relative.as_posix()}")
                    continue
                if ref["sha"] != current_sha:
                    errors.append("evidence SHA does not match the current revision")
                    continue
                if not str(ref["check_id"]).isdigit():
                    errors.append("check_id must be a GitHub Actions run or check-run ID")
                    continue
                if not verify_check(repository, str(ref["check_id"]), current_sha, token):
                    errors.append("linked GitHub check did not complete successfully on the current revision")
                    continue
                verified_refs.append(ref)

        if isinstance(entry, dict) and entry.get("status") != "VERIFIED":
            errors.append("evidence ledger entry status is not VERIFIED")
        verified = (
            isinstance(entry, dict)
            and entry.get("status") == "VERIFIED"
            and not errors
            and len(verified_refs) == len(refs)
        )
        records.append({
            "gate": gate,
            "status": "VERIFIED" if verified else "BLOCKED",
            "revision": current_sha,
            "evidence": verified_refs if verified else [],
            "verification_errors": errors,
        })
        if not verified:
            findings.append({
                "id": "GATE-" + sha(gate)[:12].upper(),
                "kind": "production_gate_unverified",
                "severity": "high",
                "production_gate": gate,
                "status": "BLOCKED",
                "verification_errors": errors,
                "next_action": f"Provide an existing artifact and a successful GitHub Actions run/check-run on the same current SHA for production gate: {gate}.",
            })
    return records, findings


def fetch_pull_requests(repository: str, token: str | None, max_pages: int = 30) -> dict:
    """Fetch all PR pages through the read-only GitHub API."""
    if not token:
        return {"status": "BLOCKED_NO_TOKEN", "pull_requests": [], "pages_fetched": 0}
    rows = []
    pages = 0
    for page in range(1, max_pages + 1):
        url = f"https://api.github.com/repos/{repository}/pulls?state=all&per_page=100&page={page}"
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                batch = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            return {"status": "BLOCKED_FETCH_FAILED", "pull_requests": rows, "pages_fetched": pages, "error_type": type(exc).__name__}
        pages += 1
        if not isinstance(batch, list):
            return {"status": "BLOCKED_INVALID_RESPONSE", "pull_requests": rows, "pages_fetched": pages}
        for pr in batch:
            rows.append({
                "number": pr.get("number"),
                "title": pr.get("title"),
                "state": pr.get("state"),
                "draft": pr.get("draft"),
                "head_ref": (pr.get("head") or {}).get("ref"),
                "head_sha": (pr.get("head") or {}).get("sha"),
                "base_ref": (pr.get("base") or {}).get("ref"),
                "updated_at": pr.get("updated_at"),
                "merged_at": pr.get("merged_at"),
                "html_url": pr.get("html_url"),
            })
        if len(batch) < 100:
            return {"status": "COMPLETE", "pull_requests": rows, "pages_fetched": pages}
    return {"status": "TRUNCATED_PAGE_LIMIT", "pull_requests": rows, "pages_fetched": pages}


def main() -> int:
    now = datetime.now(timezone.utc).isoformat()
    policy = json.loads(POLICY.read_text(encoding="utf-8")) if POLICY.exists() else {}
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8")) if EVIDENCE.exists() else {"requirements": {}, "production_gates": {}}
    mapped = evidence.get("requirements", {})
    requirements = []
    routes = []
    findings = []

    current_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() if (ROOT / ".git").exists() else "unknown"
    production_gates, gate_findings = build_production_gate_records(
        policy, evidence, current_sha, os.getenv("GITHUB_REPOSITORY", "DreamCo-Technologies/Dreamcobots"),
        os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN"),
    )
    findings.extend(gate_findings)

    for path in tracked():
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        section = ""
        for line_number, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                section = re.sub(r"^#+\s*", "", stripped)
            match = re.match(r"^(?:[-*+]\s+(?:\[[ xX]\]\s+)?|\d+[.)]\s+)(.+)$", stripped)
            if not match or len(match.group(1).strip()) < 12:
                continue
            body = match.group(1).strip()
            requirement_id = "DCO-" + sha(path.relative_to(ROOT).as_posix() + "\0" + re.sub(r"\s+", " ", body))[:14].upper()
            item_evidence = mapped.get(requirement_id, {})
            classification = classify_requirement(item_evidence)
            item = {
                "id": requirement_id,
                "source": path.relative_to(ROOT).as_posix(),
                "line": line_number,
                "section": section,
                "text": body,
                "evidence": item_evidence,
                "classification": classification,
            }
            requirements.append(item)
            if classification == "CONFIRMED_REQUIREMENT":
                missing = missing_requirement_evidence(item_evidence)
                if missing:
                    findings.append({
                        "id": "GAP-" + requirement_id,
                        "kind": "requirement_evidence_gap",
                        "severity": "high",
                        "requirement_id": requirement_id,
                        "source": item["source"],
                        "line": line_number,
                        "missing": missing,
                        "status": "BLOCKED",
                        "next_action": "Map this confirmed requirement to real code, executable tests, a runtime route, and benchmark evidence where applicable.",
                    })

    files = [
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file() and not any(part in path.parts for part in (".git", "node_modules", ".venv", "dist", "build"))
    ]
    workflows = [path for path in files if path.startswith(".github/workflows/") and path.endswith((".yml", ".yaml"))]
    tests = [path for path in files if (path.startswith("tests/") or "/tests/" in path or path.startswith("test_")) and path.endswith((".py", ".js", ".ts", ".tsx"))]

    resource_patterns = {
        "runtime_service": r"(service|server|worker|runtime)",
        "api_route": r"(routes?/|router|endpoint|openapi)",
        "integration": r"(integration|connector|mcp|webhook)",
        "database": r"(schema|migration|database|supabase|postgres)",
        "monitor": r"(monitor|observability|telemetry|alert)",
        "backup": r"(backup|restore)",
        "security_control": r"(security|auth|permission|secret|policy)",
        "benchmark": r"(benchmark|eval|holdout)",
    }
    for kind, pattern in resource_patterns.items():
        matches = [path for path in files if re.search(pattern, path, re.I)]
        routes.append({
            "resource_class": kind,
            "discovered_paths": matches[:500],
            "count": len(matches),
            "verification": "DISCOVERED_NOT_RUNTIME_VERIFIED",
        })

    for workflow in workflows:
        if not re.search(r"(test|validate|check|gate|health|ci)", workflow, re.I):
            findings.append({
                "id": "WF-" + sha(workflow)[:12],
                "kind": "workflow_test_coverage",
                "severity": "medium",
                "source": workflow,
                "status": "UNVERIFIED",
                "next_action": "Add workflow contract tests for triggers, permissions, concurrency, failure handling and artifacts.",
            })
    for resource in ("runtime_service", "api_route", "integration", "database", "monitor", "backup", "security_control", "benchmark"):
        if not any(item["resource_class"] == resource and item["count"] for item in routes):
            findings.append({
                "id": "RES-" + resource.upper(),
                "kind": "resource_inventory_gap",
                "severity": "high",
                "resource_class": resource,
                "status": "BLOCKED",
                "next_action": "Inventory this resource class and provide owner, route, test, and runtime evidence.",
            })

    try:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        bots = registry.get("masterbots") or registry.get("divisions") or []
    except Exception:
        bots = []

    pr_inventory = OUT / "pull-request-inventory.json"
    repository = os.getenv("GITHUB_REPOSITORY", "DreamCo-Technologies/Dreamcobots")
    pr_data = fetch_pull_requests(repository, os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN"))
    pr_count = len(pr_data["pull_requests"]) if pr_data["status"] == "COMPLETE" else None
    pr_inventory.parent.mkdir(parents=True, exist_ok=True)
    pr_inventory.write_text(json.dumps(pr_data, indent=2) + "\n", encoding="utf-8")
    if pr_data["status"] != "COMPLETE":
        findings.append({
            "id": "PR-INVENTORY-BLOCKED",
            "kind": "pull_request_inventory",
            "severity": "high",
            "status": "BLOCKED",
            "details": pr_data["status"],
            "next_action": "Provide a read-only GitHub token with pull-requests:read and complete paginated PR inventory before claiming PR coverage.",
        })

    candidate_triage = build_candidate_triage(requirements)
    confirmed_count = sum(item["classification"] == "CONFIRMED_REQUIREMENT" for item in requirements)
    evidence_count = sum(
        any(item.get("evidence", {}).get(key) for key in ("implementation", "tests", "runtime_routes", "benchmark_evidence"))
        for item in requirements
    )
    blocked = any(item.get("status") == "BLOCKED" for item in findings)
    unverified = any(item.get("status") == "UNVERIFIED" for item in findings) or confirmed_count < len(requirements)
    readiness = "BLOCKED" if blocked or any(item["status"] != "VERIFIED" for item in production_gates) else ("UNVERIFIED" if unverified else "READY_FOR_OWNER_SIGNOFF")

    summary = {
        "generated_at": now,
        "repository": repository,
        "current_sha": current_sha,
        "requirements_candidate_count": len(requirements),
        "requirements_confirmed_count": confirmed_count,
        "untriaged_candidate_count": len(requirements) - confirmed_count,
        "candidate_source_count": len(candidate_triage),
        "requirements_with_any_evidence": evidence_count,
        "production_gate_count": len(production_gates),
        "production_gate_verified_count": sum(item["status"] == "VERIFIED" for item in production_gates),
        "production_gate_unverified_count": sum(item["status"] != "VERIFIED" for item in production_gates),
        "workflow_count": len(workflows),
        "test_file_count": len(tests),
        "masterbot_registry_count": len(bots),
        "pull_request_inventory_count": pr_count,
        "pull_request_inventory_status": pr_data["status"],
        "finding_count": len(findings),
        "production_readiness": readiness,
        "limitations": [
            "Markdown list extraction is a candidate inventory, not semantic proof of all prose/table requirements.",
            "Only explicitly confirmed requirements create requirement-evidence blockers; all other list items remain untriaged candidates.",
            "Production gates require reviewed evidence with repository path, commit SHA and check/run ID.",
            "Path discovery does not verify a live runtime route.",
            "Private ChatGPT conversations require owner-approved exports.",
            "No test, benchmark, deployment, restore or runtime result is invented.",
        ],
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "production-readiness-master-list.json").write_text(
        json.dumps({
            "summary": summary,
            "requirements": requirements,
            "candidate_triage_by_source": candidate_triage,
            "production_gates": production_gates,
            "findings": findings,
            "resource_routes": routes,
        }, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# DreamCo Production Readiness Master List",
        "",
        f"Generated: {now}",
        f"Current revision: {current_sha}",
        "",
        f"**Status: {readiness}**",
        "",
        f"- Candidate requirement lines: {len(requirements)}",
        f"- Confirmed requirements: {confirmed_count}",
        f"- Untriaged candidates: {len(requirements) - confirmed_count}",
        f"- Candidate source files: {len(candidate_triage)}",
        f"- Requirements with evidence: {evidence_count}",
        f"- Production gates verified: {summary['production_gate_verified_count']}/{len(production_gates)}",
        f"- Workflows: {len(workflows)}",
        f"- Test files: {len(tests)}",
        f"- MasterBot registry entries: {len(bots)}",
        f"- PR inventory entries: {pr_count}",
        f"- Findings: {len(findings)}",
        "",
        "## Candidate inventory (not confirmed requirements)",
        "",
        "List-item extraction is discovery only. Candidate lines remain untriaged until explicitly confirmed in the evidence ledger; they are not automatically treated as product blockers.",
        "",
    ]
    for item in candidate_triage[:50]:
        lines.append(f"- {item['source']}: {item['candidate_count']} candidates")
    lines += ["", "## Production gate evidence", ""]
    for gate in production_gates:
        lines.append(f"- {gate['gate']}: {gate['status']}")
    lines.append("")
    for finding in sorted(findings, key=lambda item: ({"critical": 0, "high": 1, "medium": 2, "low": 3}.get(item.get("severity"), 4), item["id"])):
        lines += [
            f"## {finding['id']} — {finding['kind']}",
            f"- Severity: {finding.get('severity', 'unranked')}",
            f"- Status: {finding.get('status', 'UNVERIFIED')}",
            f"- Source: {finding.get('source', finding.get('requirement_id', 'repository'))}",
            f"- Next action: {finding['next_action']}",
            "",
        ]
    lines += ["## Limitations", ""] + ["- " + item for item in summary["limitations"]]
    (OUT / "production-readiness-master-list.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT / "resource-routing-inventory.json").write_text(
        json.dumps({"generated_at": now, "routes": routes, "workflow_paths": workflows, "test_paths": tests}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
