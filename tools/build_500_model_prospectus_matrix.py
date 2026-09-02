"""Build the public-safe Buddy prospectus matrix from benchmark evidence.

This tool never invents benchmark results. Missing model/suite combinations remain
unverified and are explicitly represented as such.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "website" / "data" / "buddy-500-model-prospectus-matrix.json"

CATALOG_CANDIDATES = [
    ROOT / "config/generated/model-prospectus-catalog.json",
    ROOT / "config/generated/model-catalog.json",
    ROOT / "config/model-catalog.json",
    ROOT / "config/buddy/500-model-registry.json",
]
SUITE_CANDIDATES = [
    ROOT / "config/generated/benchmark-registry.json",
    ROOT / "config/generated/benchmark-suites.json",
    ROOT / "config/benchmark-registry.json",
    ROOT / "config/buddy/trust-benchmark-suite.json",
]
EVIDENCE_CANDIDATES = [
    ROOT / "config/generated/model-benchmark-evidence.json",
    ROOT / "config/generated/buddy-500-model-benchmark.json",
    ROOT / "config/generated/universal-capability-benchmark.json",
]


def load_first(paths: list[Path]) -> Any:
    for path in paths:
        if path.exists():
            return json.loads(path.read_text())
    return None


def rows(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [x for x in value if isinstance(x, dict)]
    if isinstance(value, dict):
        if isinstance(value.get("model_count"), int) and isinstance(value.get("id_pattern"), str):
            start = int(value.get("slots", {}).get("start", 1))
            end = int(value.get("slots", {}).get("end", value["model_count"]))
            width = max(3, len(str(end)))
            return [
                {
                    "model_id": value["id_pattern"].format(slot=slot),
                    "name": f"Buddy Model {slot:0{width}d}",
                    "provider": "DreamCo Buddy",
                }
                for slot in range(start, end + 1)
            ]
        if isinstance(value.get("domains"), list):
            return [
                {
                    "benchmark_id": domain,
                    "name": domain.replace("_", " ").title(),
                }
                for domain in value["domains"]
                if isinstance(domain, str) and domain
            ]
        for key in ("models", "providers", "suites", "benchmarks", "results", "records", "items"):
            candidate = value.get(key)
            if isinstance(candidate, list):
                return [x for x in candidate if isinstance(x, dict)]
    return []


def ident(item: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = item.get(key)
        if value not in (None, ""):
            return str(value)
    return "unknown"


def main() -> int:
    catalog = rows(load_first(CATALOG_CANDIDATES))
    suites = rows(load_first(SUITE_CANDIDATES))
    evidence = rows(load_first(EVIDENCE_CANDIDATES))

    evidence_map: dict[tuple[str, str], dict[str, Any]] = {}
    for item in evidence:
        model = ident(item, ("model_id", "model", "model_name", "provider_model"))
        suite = ident(item, ("benchmark_id", "suite_id", "benchmark_suite", "suite", "benchmark"))
        evidence_map[(model, suite)] = item

    matrix = []
    for model_item in catalog:
        model_id = ident(model_item, ("model_id", "id", "slug", "name"))
        provider = ident(model_item, ("provider", "company", "organization", "vendor"))
        model_name = ident(model_item, ("name", "model_name", "display_name", "id"))
        for suite_item in suites:
            suite_id = ident(suite_item, ("benchmark_id", "suite_id", "id", "slug", "name"))
            record = evidence_map.get((model_id, suite_id))
            status = "unverified"
            if record:
                status = record.get("status", "needs_review")
            matrix.append({
                "provider": provider,
                "model_id": model_id,
                "model_name": model_name,
                "benchmark_suite": suite_id,
                "status": status,
                "evidence": record.get("evidence_reference") if record else None,
                "last_verified": record.get("execution_timestamp") if record else None,
            })

    output = {
        "schema": "dreamco.buddy_500_model_prospectus_matrix.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "catalogued_models": len(catalog),
        "registered_benchmark_suites": len(suites),
        "matrix_rows": len(matrix),
        "verified_rows": sum(1 for row in matrix if row["status"] == "passed"),
        "unverified_rows": sum(1 for row in matrix if row["status"] == "unverified"),
        "matrix": matrix,
        "interpretation": "This page is an evidence projection. Missing or unverified combinations are not passes.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(output, indent=2) + "\n")
    print(f"Wrote {OUT}: {len(matrix)} model/suite rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
