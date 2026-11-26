#!/usr/bin/env python3
"""Build ephemeral production evidence bound to the current commit and completed checks."""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "config/production-readiness-evidence-map.json"
SCHEMA = "dreamco.production_readiness_area_evidence.v1"


def build_manifest(
    evidence_map: dict[str, Any],
    sha: str,
    check_runs: list[dict[str, Any]],
    root: Path = ROOT,
) -> dict[str, Any]:
    """Resolve only existing files backed by successful checks on the exact SHA."""
    if evidence_map.get("schema") != "dreamco.production_readiness_evidence_map.v1":
        raise ValueError("unsupported production evidence map schema")

    areas: dict[str, Any] = {}
    for area_id, items in (evidence_map.get("areas") or {}).items():
        refs: list[dict[str, str]] = []
        errors: list[str] = []

        for item in items:
            relative = Path(str(item.get("path", "")))
            if not relative.parts or relative.is_absolute() or ".." in relative.parts:
                errors.append("unsafe or empty evidence path")
                continue

            artifact = (root / relative).resolve()
            try:
                artifact.relative_to(root.resolve())
            except ValueError:
                errors.append(f"evidence path escapes repository: {relative}")
                continue

            if not artifact.is_file():
                errors.append(f"evidence artifact missing: {relative.as_posix()}")
                continue

            allowed_names = set(item.get("check_names") or [])
            matching_check = next(
                (
                    run
                    for run in check_runs
                    if run.get("name") in allowed_names
                    and run.get("head_sha") == sha
                    and run.get("status") == "completed"
                    and run.get("conclusion") == "success"
                ),
                None,
            )
            if not matching_check:
                errors.append(
                    f"no successful exact-revision check for {relative.as_posix()} "
                    f"({sorted(allowed_names)})"
                )
                continue

            refs.append(
                {
                    "path": relative.as_posix(),
                    "sha": sha,
                    "check_id": str(matching_check["id"]),
                }
            )

        if items and len(refs) == len(items):
            status = "VERIFIED"
        elif refs:
            status = "PARTIAL"
        else:
            status = "UNVERIFIED"

        areas[area_id] = {
            "status": status,
            "evidence": refs,
            "resolution_errors": errors,
        }

    return {
        "schema": SCHEMA,
        "revision": sha,
        "areas": areas,
        "truth_boundary": (
            "Only existing repository artifacts linked to successful completed "
            "checks on this exact revision are included."
        ),
    }


def fetch_check_runs(repository: str, sha: str, token: str) -> list[dict[str, Any]]:
    """Fetch all check runs for one commit, including additional API pages."""
    results: list[dict[str, Any]] = []
    for page in range(1, 11):
        url = (
            f"https://api.github.com/repos/{repository}/commits/{sha}/check-runs"
            f"?per_page=100&page={page}"
        )
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "User-Agent": "DreamCo-Production-Readiness-Evidence/1.0",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))

        batch = payload.get("check_runs") or []
        results.extend(batch)
        if len(batch) < 100:
            break

    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--wait-seconds", type=int, default=0)
    parser.add_argument("--poll-seconds", type=int, default=15)
    args = parser.parse_args()

    repository = os.getenv("GITHUB_REPOSITORY", "DreamCo-Technologies/Dreamcobots")
    sha = os.getenv("GITHUB_SHA") or os.getenv("GITHUB_COMMIT")
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if not sha or not token:
        parser.error("GITHUB_SHA and GITHUB_TOKEN (or GH_TOKEN) are required")

    evidence_map = json.loads(MAP.read_text(encoding="utf-8"))
    required_names = {
        name
        for items in evidence_map.get("areas", {}).values()
        for item in items
        for name in item.get("check_names", [])
    }

    deadline = time.monotonic() + max(args.wait_seconds, 0)
    check_runs: list[dict[str, Any]] = []
    while True:
        check_runs = fetch_check_runs(repository, sha, token)
        present_names = {run.get("name") for run in check_runs}
        pending = [
            run
            for run in check_runs
            if run.get("name") in required_names and run.get("status") != "completed"
        ]
        missing_names = required_names - present_names

        if (not pending and not missing_names) or time.monotonic() >= deadline:
            break
        time.sleep(max(args.poll_seconds, 1))

    manifest = build_manifest(evidence_map, sha, check_runs)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    summary = {
        area: {
            "status": item["status"],
            "evidence_count": len(item["evidence"]),
            "errors": item["resolution_errors"],
        }
        for area, item in manifest["areas"].items()
    }
    print(json.dumps({"revision": sha, "areas": summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
