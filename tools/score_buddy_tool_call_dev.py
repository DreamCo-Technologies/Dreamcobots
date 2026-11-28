#!/usr/bin/env python3
"""Offline public tool-argument smoke test. No tools are invoked or approved.

This deliberately tests one known synthetic example, not model competence,
user consent, API authorization, tool execution, or an independent holdout.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

# Public, synthetic, fixed contract: model responses cannot set permissions.
PUBLIC_CONTRACT = {
    "scenario": "Select the read-only forecast tool for fictional Madison weather.",
    "tool_name": "weather_read_only",
    "required_arguments": {"location": "Madison, WI", "units": "celsius"},
    "tool_permission_scope": "weather.read",
    "side_effects_allowed": False,
}


def _unique_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_nonfinite(value: str) -> None:
    raise ValueError("nonfinite JSON constant")


def score_response(response: str) -> dict[str, Any]:
    """Grade supplied text against a pinned public schema; never execute it."""
    if not isinstance(response, str) or len(response) > 20000:
        raise ValueError("response must be text of at most 20000 characters")
    try:
        response.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError("response must be valid UTF-8") from exc
    passed = False
    try:
        candidate = json.loads(response, object_pairs_hook=_unique_keys,
                               parse_constant=_reject_nonfinite)
        passed = (
            type(candidate) is dict and set(candidate) == {"name", "arguments"}
            and candidate["name"] == PUBLIC_CONTRACT["tool_name"]
            and type(candidate["arguments"]) is dict
            and candidate["arguments"] == PUBLIC_CONTRACT["required_arguments"]
            and all(type(value) is str for value in candidate["arguments"].values())
        )
    except (ValueError, TypeError, RecursionError):
        pass
    contract_bytes = json.dumps(PUBLIC_CONTRACT, sort_keys=True,
                                separators=(",", ":")).encode("utf-8")
    return {
        "schema": "dreamco.buddy_tool_call_public_dev.v1",
        "status": "public_synthetic_fixture_only",
        "matches_public_read_only_contract": passed,
        "public_contract_sha256": sha256(contract_bytes).hexdigest(),
        "model_calls": 0,
        "tools_executed": 0,
        "permissions_verified": False,
        "independent_holdout_verified": False,
        "model_quality_verified": False,
        "eligible_for_model_promotion": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--response-file", type=Path, required=True,
                        help="Local file containing one tool-call JSON response")
    parser.add_argument("--output", type=Path, help="Optional privacy-minimized result")
    args = parser.parse_args()
    try:
        report = score_response(args.response_file.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        parser.exit(2, f"tool-call dev smoke blocked: {exc}\n")
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
