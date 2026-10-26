#!/usr/bin/env python3
"""Opt-in, loopback-only Ollama smoke baseline on PUBLIC Buddy fixtures.

No downloads, training, tools, private datasets, or independent holdout evaluation.
No requests are made until the operator supplies explicit opt-in flags. Local
Ollama server configuration and the operator's rights attestations are not
independently verified by this tool. Results never contain prompt/answer text.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from math import isfinite
from pathlib import Path
import re
import statistics
import time
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

if __package__:
    from .score_buddy_dev_fixtures import PINNED, score_dev_responses, CATALOG
else:
    from score_buddy_dev_fixtures import PINNED, score_dev_responses, CATALOG

DIGEST = re.compile(r"(?:sha256:)?([0-9a-f]{64})\Z")
MODEL = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,119}\Z")
SUITES = tuple(sorted(PINNED))
MAX_RESPONSE_BYTES = 256_000


class BaselineError(ValueError):
    """Unsafe or inconsistent local baseline preflight or response."""


def loopback_endpoint(value: str) -> str:
    """Reject external endpoints, credentials, redirects and ambiguous URLs."""
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError as exc:
        raise BaselineError("invalid loopback endpoint") from exc
    if (parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "::1"}
            or port is None or not 1 <= port <= 65535 or parsed.username is not None
            or parsed.password is not None or parsed.path not in ("", "/")
            or parsed.query or parsed.fragment):
        raise BaselineError("only explicit HTTP loopback IP and port are allowed")
    return value.rstrip("/")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        raise BaselineError("HTTP redirects are forbidden")


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict:
    """Fail closed when an untrusted local server repeats a JSON object key."""
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise BaselineError("duplicate key in local Ollama JSON response")
        obj[key] = value
    return obj


def _parse_server_json(raw: bytes) -> dict:
    """Decode an untrusted response without silently accepting ambiguous JSON."""
    try:
        obj = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_json_keys,
            parse_constant=lambda value: (_ for _ in ()).throw(BaselineError("nonfinite JSON")),
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise BaselineError("invalid Ollama JSON response") from exc
    if not isinstance(obj, dict):
        raise BaselineError("Ollama response must be an object")
    return obj


def local_transport(base: str, route: str, payload: dict | None, timeout: float) -> dict:
    if route not in ("/api/tags", "/api/generate"):
        raise BaselineError("unsupported local API route")
    data = None if payload is None else json.dumps(payload, allow_nan=False).encode("utf-8")
    request = Request(base + route, data=data, method="GET" if data is None else "POST",
                      headers={"Content-Type": "application/json"})
    # ProxyHandler({}) prevents environment proxy settings from intercepting
    # local traffic. NoRedirect prevents a local server from sending us remote.
    opener = build_opener(ProxyHandler({}), NoRedirect())
    try:
        with opener.open(request, timeout=timeout) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise BaselineError("local Ollama request failed") from exc
    if len(raw) > MAX_RESPONSE_BYTES:
        raise BaselineError("local Ollama response exceeds size limit")
    return _parse_server_json(raw)


def _digest(value: Any) -> str:
    if not isinstance(value, str) or not (m := DIGEST.fullmatch(value)):
        raise BaselineError("expected pinned 64-character model digest")
    return m.group(1)


def _server_rate(response: dict) -> float | None:
    count, duration = response.get("eval_count"), response.get("eval_duration")
    if type(count) is not int or type(duration) is not int or count < 0 or duration <= 0:
        return None
    rate = count * 1e9 / duration
    return round(rate, 3) if isfinite(rate) else None


def _p95(values: list[float]) -> float:
    ordered = sorted(values)
    return ordered[max(0, (95 * len(ordered) + 99) // 100 - 1)]


def run_baseline(*, model: str, expected_digest: str, catalog: dict,
                 endpoint: str = "http://127.0.0.1:11434",
                 transport: Callable[[str, str, dict | None, float], dict] = local_transport,
                 clock: Callable[[], float] = time.monotonic,
                 timeout_seconds: float = 30.0) -> dict:
    base = loopback_endpoint(endpoint)
    if not isinstance(model, str) or not MODEL.fullmatch(model) or ".." in model:
        raise BaselineError("invalid installed model name")
    pinned = _digest(expected_digest)
    if not isinstance(timeout_seconds, (int, float)) or isinstance(timeout_seconds, bool) or not isfinite(timeout_seconds) or not 1 <= timeout_seconds <= 60:
        raise BaselineError("timeout must be 1..60 seconds")
    # Validate public fixture definitions before any network access.
    score_dev_responses([{"suite_id": SUITES[0], "response": ""}], catalog)
    tags = transport(base, "/api/tags", None, float(timeout_seconds))
    models = tags.get("models")
    if not isinstance(models, list):
        raise BaselineError("local model list unavailable")
    matches = [item for item in models if isinstance(item, dict) and item.get("name") == model]
    if len(matches) != 1 or _digest(matches[0].get("digest")) != pinned:
        raise BaselineError("installed model name/digest mismatch; no downloads attempted")
    rows = []
    latencies = []
    rates = []
    suite_runtime = {}
    for suite_id in SUITES:
        payload = {"model": model, "prompt": PINNED[suite_id]["prompt_fixture"],
                   "stream": False, "options": {"temperature": 0, "num_predict": 128}}
        start = clock()
        response = transport(base, "/api/generate", payload, float(timeout_seconds))
        elapsed = clock() - start
        if not isfinite(elapsed) or elapsed < 0:
            raise BaselineError("invalid elapsed time")
        if response.get("model") != model:
            raise BaselineError("generation response model identity mismatch")
        answer = response.get("response")
        # Ollama can report done=true after hitting num_predict; that is not
        # a complete answer. Require an explicit normal stop, not a missing,
        # truncated, or unknown termination reason, before scoring any task.
        if (response.get("done") is not True or response.get("done_reason") != "stop"
                or not isinstance(answer, str) or len(answer) > 20_000):
            raise BaselineError("incomplete, truncated or invalid model response")
        try:
            answer.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise BaselineError("invalid response Unicode") from exc
        rows.append({"suite_id": suite_id, "response": answer})
        latencies.append(round(elapsed * 1000, 3))
        rate = _server_rate(response)
        if rate is not None:
            rates.append(rate)
        # Preserve task-level speed for later route comparison without storing
        # prompts, responses, or reversible low-entropy response hashes.
        suite_runtime[suite_id] = {
            "latency_ms": latencies[-1],
            "server_reported_tokens_per_second": rate,
        }
    # A tag can be replaced while the suite runs. Recheck after all requests;
    # this detects ordinary tag drift, but cannot attest to model-file integrity.
    final_tags = transport(base, "/api/tags", None, float(timeout_seconds))
    final_models = final_tags.get("models")
    if not isinstance(final_models, list):
        raise BaselineError("post-run local model list unavailable")
    final_matches = [item for item in final_models if isinstance(item, dict) and item.get("name") == model]
    if len(final_matches) != 1 or _digest(final_matches[0].get("digest")) != pinned:
        raise BaselineError("post-run installed model digest mismatch")
    score = score_dev_responses(rows, catalog)
    return {
        "schema": "dreamco.buddy_ollama_public_dev_baseline.v1",
        "status": "measured_local_server_responses_public_fixtures_only_unverified",
        "model_name": model,
        "local_model_digest": pinned,
        "post_run_local_tag_digest_rechecked": True,
        "benchmark_catalog_sha256": sha256(json.dumps(catalog, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "actual_model_api_calls": len(rows),
        "passed_public_dev_fixtures": score["passed_public_dev_fixtures"],
        "scored_public_dev_fixtures": score["scored_public_dev_fixtures"],
        "public_fixture_results": score["results"],
        "public_fixture_runtime": suite_runtime,
        "generation_options": {"temperature": 0, "num_predict": 128},
        "request_timeout_seconds": float(timeout_seconds),
        "latency_ms_median": round(statistics.median(latencies), 3),
        "latency_ms_p95": round(_p95(latencies), 3),
        "server_reported_tokens_per_second_mean": round(statistics.mean(rates), 3) if len(rates) == len(rows) else None,
        "cost_usd_verified": False,
        "model_rights_independently_verified": False,
        "privacy_independently_verified": False,
        "independent_holdout_receipts": 0,
        "model_quality_independently_verified": False,
        "eligible_for_model_promotion": False,
        "training_performed": False,
    }



def write_receipt_exclusive(output: Path, result: dict) -> None:
    """Write a measured receipt without replacing existing files or symlinks.

    The caller must supply an unused path. The exclusive-create flag also
    protects against a file appearing after the initial CLI preflight.
    """
    serialized = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    with output.open("x", encoding="utf-8") as receipt:
        receipt.write(serialized)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="Exact installed Ollama model tag")
    parser.add_argument("--digest", required=True, help="Exact installed local model SHA-256 digest")
    parser.add_argument("--endpoint", default="http://127.0.0.1:11434")
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=float, default=30)
    parser.add_argument("--execute-local-inference", action="store_true")
    parser.add_argument("--approved-free-compute", action="store_true")
    parser.add_argument("--rights-reviewed", action="store_true")
    args = parser.parse_args()
    if not (args.execute_local_inference and args.approved_free_compute and args.rights_reviewed):
        parser.exit(2, "blocked: explicit local execution, approved free compute and rights review required\n")
    try:
        if os.path.lexists(args.output):
            raise BaselineError("output receipt path already exists; refusing overwrite")
        catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
        result = run_baseline(model=args.model, expected_digest=args.digest, catalog=catalog,
                              endpoint=args.endpoint, timeout_seconds=args.timeout_seconds)
        write_receipt_exclusive(args.output, result)
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(2, f"local Buddy baseline blocked: {exc}\n")
    print("Public development baseline saved; NOT a holdout or model-promotion receipt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
