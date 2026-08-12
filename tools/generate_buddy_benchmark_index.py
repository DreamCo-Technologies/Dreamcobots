from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "config" / "buddy-benchmark-index.json"
REPOSITORY_REGISTRY = ROOT / "config" / "generated" / "repository_test_registry.json"
OUTPUT = ROOT / "config" / "generated" / "buddy_benchmark_index.json"
PUBLIC = ROOT / "website" / "data" / "buddy-benchmark-index.js"
REPORT = ROOT / "reports" / "BUDDY_BENCHMARK_INDEX.md"


def build_index() -> dict:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    repository = json.loads(REPOSITORY_REGISTRY.read_text(encoding="utf-8"))
    programs = source["programs"]
    for program in programs:
        for path_key in ("generator",):
            if not (ROOT / program[path_key]).exists():
                raise ValueError(f"Missing benchmark source: {program[path_key]}")
        if not (ROOT / "website" / program["public_page"].split("#", 1)[0]).exists():
            raise ValueError(f"Missing public benchmark page: {program['public_page']}")
        program["live_results_completed"] = 0
        program["public_tracking_ready"] = True

    suites = [
        {
            "id": suite["id"],
            "name": suite["name"],
            "area": suite["area"],
            "level": suite["level"],
            "status": suite["status"],
            "test_count": len(suite.get("tests", [])),
            "source_count": len(suite.get("sources", [])),
            "public_page": "test-center.html",
        }
        for suite in repository["suites"]
    ]
    return {
        "schema": "dreamco.benchmark_index.v1",
        "reviewedOn": source["reviewed_on"],
        "summary": {
            "benchmarkPrograms": len(programs),
            "repositorySuites": len(suites),
            "trackedBenchmarkSurfaces": len(programs) + len(suites),
            "publicTrackingPrograms": sum(item["public_tracking_ready"] for item in programs),
            "localReadySuites": sum("ready" in item["status"] for item in suites),
            "credentialGatedSuites": sum(item["level"] == "credentials_required" for item in suites),
            "liveBenchmarkPrograms": 0,
        },
        "truthContract": {
            "catalogOrContractPassMeansLiveBenchmarkPassed": False,
            "publicTrackingMeansCommandsRunInBrowser": False,
            "liveResultsRequireEvidenceArtifacts": True,
            "paidOrNetworkRunsRequireExactApproval": True,
            "failuresRemainVisible": True,
        },
        "realisticPlan": [
            {"stage": 1, "name": "Inventory", "gate": "Every benchmark suite, source, command, page, and owner is registered."},
            {"stage": 2, "name": "Local contracts", "gate": "Deterministic schemas, fixtures, imports, syntax, and public assets pass locally."},
            {"stage": 3, "name": "Sandbox", "gate": "Code, bots, media, and open-source runtimes pass isolated repeatable tests."},
            {"stage": 4, "name": "Adapter certification", "gate": "Exact provider versions, scoped credentials, timeouts, retries, costs, and redaction pass."},
            {"stage": 5, "name": "Head-to-head", "gate": "Comparable candidates run identical signed fixtures with failures preserved."},
            {"stage": 6, "name": "Production observation", "gate": "Approved releases meet reliability, safety, cost, and rollback targets over time."},
        ],
        "programs": programs,
        "repositorySuites": suites,
    }


def render_report(index: dict) -> str:
    summary = index["summary"]
    lines = [
        "# Buddy Benchmark Index",
        "",
        f"- Benchmark programs: {summary['benchmarkPrograms']}",
        f"- Repository suites: {summary['repositorySuites']}",
        f"- Tracked benchmark surfaces: {summary['trackedBenchmarkSurfaces']}",
        f"- Live benchmark programs with evidence: {summary['liveBenchmarkPrograms']}",
        "",
        "## Programs",
        "",
    ]
    lines.extend(f"- **{item['name']}** ({item['area']}): `{item['status']}`" for item in index["programs"])
    lines.extend(["", "Catalog and contract readiness are not live benchmark results.", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    index = build_index()
    generated = json.dumps(index, indent=2, sort_keys=True) + "\n"
    public = "window.BUDDY_BENCHMARK_INDEX = " + json.dumps(index, separators=(",", ":"), sort_keys=True) + ";\n"
    report = render_report(index)
    outputs = ((OUTPUT, generated), (PUBLIC, public), (REPORT, report))
    if args.check:
        for path, expected in outputs:
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                raise SystemExit(f"Generated benchmark index is stale: {path}")
    else:
        for path, content in outputs:
            path.write_text(content, encoding="utf-8")
    print(json.dumps(index["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
