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
        if any(not isinstance(x, dict) for x in value):
            raise ValueError("registry entries must be objects")
        return value
    if isinstance(value, dict):
        if isinstance(value.get("model_count"), int) and isinstance(value.get("id_pattern"), str):
            return expand_model_slots(value)
        if isinstance(value.get("domains"), list):
            if any(not isinstance(domain, str) or not domain.strip() for domain in value["domains"]):
                raise ValueError("benchmark domains must be nonblank strings")
            return [
                {
                    "benchmark_id": domain,
                    "name": domain.replace("_", " ").title(),
                }
                for domain in value["domains"]
            ]
        for key in ("models", "providers", "suites", "benchmarks", "results", "records", "items"):
            candidate = value.get(key)
            if isinstance(candidate, list):
                if any(not isinstance(x, dict) for x in candidate):
                    raise ValueError("registry entries must be objects")
                return candidate
    return []


def ident(item: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = item.get(key)
        if value not in (None, ""):
            return str(value)
    return "unknown"


def expand_model_slots(value: dict[str, Any]) -> list[dict[str, Any]]:
    """Do not silently invent or omit model slots when registry counts disagree."""
    count = value["model_count"]
    slots = value.get("slots", {})
    if not isinstance(slots, dict):
        raise ValueError("model slots must be an object")
    start = slots.get("start", 1)
    end = slots.get("end", count)
    if (type(count) is not int or type(start) is not int or type(end) is not int
            or count < 1 or start < 1 or end < start or end - start + 1 != count):
        raise ValueError("model slot range must match model_count exactly")
    width = max(3, len(str(end)))
    return [
        {
            "model_id": value["id_pattern"].format(slot=slot),
            "name": f"Buddy Model {slot:0{width}d}",
            "provider": "DreamCo Buddy",
        }
        for slot in range(start, end + 1)
    ]


def require_unique_ids(items: list[dict[str, Any]], keys: tuple[str, ...], label: str) -> None:
    """Fail closed instead of publishing a misleading duplicate/empty matrix."""
    if not items:
        raise ValueError(f"{label} registry must contain at least one entry")
    seen: set[str] = set()
    for index, item in enumerate(items):
        value = ident(item, keys)
        if value == "unknown" or not value.strip():
            raise ValueError(f"{label} entry {index} has no usable identity")
        if value in seen:
            raise ValueError(f"duplicate {label} identity: {value}")
        seen.add(value)


def main() -> int:
    catalog = rows(load_first(CATALOG_CANDIDATES))
    suites = rows(load_first(SUITE_CANDIDATES))
    evidence = rows(load_first(EVIDENCE_CANDIDATES))
    require_unique_ids(catalog, ("model_id", "id", "slug", "name"), "model")
    require_unique_ids(suites, ("benchmark_id", "suite_id", "id", "slug", "name"), "benchmark suite")

    # This source is a *catalog of claims*, not a trusted execution ledger.
    # A reported `passed` string must never certify model mastery. Preserve
    # original claims for diagnosis until an independent receipt verifier is wired.
    evidence_map: dict[tuple[str, str], dict[str, Any]] = {}
    ambiguous: set[tuple[str, str]] = set()
    for item in evidence:
        model = ident(item, ("model_id", "model", "model_name", "provider_model"))
        suite = ident(item, ("benchmark_id", "suite_id", "benchmark_suite", "suite", "benchmark"))
        key = (model, suite)
        if key in evidence_map:
            ambiguous.add(key)
        else:
            evidence_map[key] = item

    matrix = []
    for model_item in catalog:
        model_id = ident(model_item, ("model_id", "id", "slug", "name"))
        provider = ident(model_item, ("provider", "company", "organization", "vendor"))
        model_name = ident(model_item, ("name", "model_name", "display_name", "id"))
        for suite_item in suites:
            suite_id = ident(suite_item, ("benchmark_id", "suite_id", "id", "slug", "name"))
            record = evidence_map.get((model_id, suite_id))
            reported_status = record.get("status") if record else None
            # Even a hash-bound local file is not proof that a real model ran.
            # Keep all unverified claims visible without promoting them to passes.
            status = "needs_review" if record else "unverified"
            if (model_id, suite_id) in ambiguous:
                status = "conflicting_evidence"
            matrix.append({
                "provider": provider,
                "model_id": model_id,
                "model_name": model_name,
                "benchmark_suite": suite_id,
                "status": status,
                "reported_status": reported_status,
                "evidence": record.get("evidence_reference") if record else None,
                "reported_timestamp": record.get("execution_timestamp") if record else None,
                "last_verified": None,
            })

    output = {
        "schema": "dreamco.buddy_500_model_prospectus_matrix.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "catalogued_models": len(catalog),
        "registered_benchmark_suites": len(suites),
        "matrix_rows": len(matrix),
        "verified_rows": sum(1 for row in matrix if row["status"] == "passed"),
        "unverified_rows": sum(1 for row in matrix if row["status"] != "passed"),
        "unreviewed_pass_claims": sum(1 for row in matrix if row["reported_status"] == "passed"),
        "matrix": matrix,
        "interpretation": "This page projects untrusted source claims, not executed mastery. No row may be promoted to passed until an independent, model-and-suite-bound execution receipt verifier is connected and tested.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(output, indent=2) + "\n")
    print(f"Wrote {OUT}: {len(matrix)} model/suite rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
