#!/usr/bin/env python3
"""Offline *development-fixture* scorer, not an independent model evaluation.

Consumes externally supplied text, never calls a model or runs training. Its
public prompts and expected answers can be memorized, so scores MUST NOT be
used for model promotion, production-readiness, or holdout claims.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "config/buddy-model-benchmarks.json"

# Exact, public, non-sensitive fixtures. Fail closed if upstream edits a fixture:
# graders must be deliberately reviewed, not silently applied to new tasks.
PINNED = {
    "instruction_following": {
        "prompt_fixture": "Return only the uppercase word READY.",
        "expected": "READY", "grader": "deterministic", "modality": "text",
    },
    "arithmetic_reasoning": {
        "prompt_fixture": "A shop has 7 boxes with 6 items each. Return only the total.",
        "expected": "42", "grader": "deterministic", "modality": "text",
    },
    "structured_output": {
        "prompt_fixture": "Return JSON with result set to 42 and confidence between 0 and 1.",
        "expected": "json_result_42", "grader": "schema", "modality": "text",
    },
    "tool_selection": {
        "prompt_fixture": "Choose the read-only weather tool for a current forecast request.",
        "expected": "weather_read_only", "grader": "schema", "modality": "tool_call",
    },
}


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject ambiguous JSON objects, including duplicate keys in nested objects."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def _grade(suite_id: str, response: str) -> bool:
    if suite_id == "instruction_following":
        return response == "READY"
    if suite_id == "arithmetic_reasoning":
        return response == "42"
    if suite_id == "tool_selection":
        # Public enum-only selection check; no tool invocation, argument
        # validation, execution permission, or independent model evaluation.
        return response == "weather_read_only"
    if suite_id == "structured_output":
        try:
            parsed = json.loads(response, object_pairs_hook=_reject_duplicate_json_keys)
        except (ValueError, TypeError, RecursionError):
            # Deeply nested untrusted JSON can exceed the parser recursion
            # limit; treat it as an invalid answer, not a grader crash.
            return False
        if not isinstance(parsed, dict) or set(parsed) != {"result", "confidence"}:
            return False
        confidence = parsed["confidence"]
        return (
            type(parsed["result"]) is int and parsed["result"] == 42
            and type(confidence) in (int, float) and isfinite(confidence)
            and 0 <= confidence <= 1
        )
    raise ValueError("unsupported public development suite")


def score_dev_responses(rows: Any, catalog: Any) -> dict:
    """Score only supplied responses against pinned, publicly known tasks.

    The result intentionally has no model identifier, independent holdout
    status, or production-readiness field. Response text and response hashes
    are never persisted (unsalted hashes can disclose low-entropy content).
    """
    if not isinstance(catalog, dict) or catalog.get("schema") != "dreamco.buddy_model_benchmarks.v1":
        raise ValueError("unexpected benchmark catalog schema")
    suites = catalog.get("suites")
    if not isinstance(suites, list):
        raise ValueError("missing benchmark suites")
    known = {}
    for suite in suites:
        if not isinstance(suite, dict) or not isinstance(suite.get("id"), str):
            raise ValueError("invalid benchmark suite")
        if suite["id"] in known:
            raise ValueError("duplicate benchmark suite id")
        known[suite["id"]] = suite
    for name, expected in PINNED.items():
        if name not in known or any(known[name].get(k) != v for k, v in expected.items()):
            raise ValueError(f"public fixture changed or missing: {name}; review grader first")
    if not isinstance(rows, list) or not rows or len(rows) > len(PINNED):
        raise ValueError("provide one to four public development responses")
    results = []
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"suite_id", "response"}:
            raise ValueError("response must contain only suite_id and response")
        suite_id, response = row["suite_id"], row["response"]
        if not isinstance(suite_id, str) or suite_id not in PINNED:
            raise ValueError("unsupported public development suite")
        if suite_id in seen:
            raise ValueError("duplicate development suite response")
        seen.add(suite_id)
        if not isinstance(response, str) or len(response) > 20000:
            raise ValueError("response must be plain text of at most 20000 characters")
        # Even non-persisted responses must be valid UTF-8. Reject lone
        # surrogates with a clear input error instead of an uncaught crash.
        try:
            response.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise ValueError("response must be valid UTF-8 text") from exc
        fixture = PINNED[suite_id]
        fixture_bytes = json.dumps(fixture, sort_keys=True, separators=(",", ":")).encode()
        results.append({
            "suite_id": suite_id,
            "passed_public_dev_fixture": _grade(suite_id, response),
            "fixture_sha256": sha256(fixture_bytes).hexdigest(),
            # No unsalted digest of supplied text: low-entropy response
            # hashes can be dictionary-reversed and reveal private content.
        })
    results.sort(key=lambda r: r["suite_id"])
    return {
        "schema": "dreamco.buddy_public_dev_smoke.v1",
        "status": "unverified_supplied_responses_public_fixtures_only",
        "model_calls": 0,
        "model_quality_verified": False,
        "independent_holdout_receipts": 0,
        "eligible_for_model_promotion": False,
        "scored_public_dev_fixtures": len(results),
        "passed_public_dev_fixtures": sum(r["passed_public_dev_fixture"] for r in results),
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", required=True, type=Path, help="Local JSON list of {suite_id,response}")
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    parser.add_argument("--output", type=Path, help="Optional JSON summary; no raw responses")
    args = parser.parse_args()
    try:
        rows = json.loads(args.responses.read_text(encoding="utf-8"))
        catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
        report = score_dev_responses(rows, catalog)
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(2, f"public development smoke blocked: {exc}\n")
    result = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
