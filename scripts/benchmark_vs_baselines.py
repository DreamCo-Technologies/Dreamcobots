"""Evidence-gated head-to-head evaluation for DreamCo division models.

Adapters are local command arrays. Each request arrives as JSON on stdin and
must return one JSON object: {"result": {...}, "route": "human_only" |
"human_ai" | "robot" | "full_ai"}. Expected answers are never sent to adapters.
No model is downloaded, trained, modified, or deployed by this runner.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import shlex
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config" / "institute-competitive-benchmark-policy.json"
CANONICAL_PARAMETERS = 45_038_208
ROUTES = {"human_only", "human_ai", "robot", "full_ai"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_artifact(root: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = root / path
    resolved = path.resolve()
    if not resolved.is_file():
        raise ValueError(f"required model artifact is missing: {raw_path}")
    return resolved


def validate_hashed_artifact(root: Path, artifact: dict[str, Any], label: str) -> Path:
    path_value = artifact.get("path")
    expected_hash = artifact.get("sha256")
    if not isinstance(path_value, str) or not isinstance(expected_hash, str) or len(expected_hash) != 64:
        raise ValueError(f"{label} requires artifact path and SHA-256")
    path = resolve_artifact(root, path_value)
    actual = sha256_file(path)
    if actual.lower() != expected_hash.lower():
        raise ValueError(f"{label} SHA-256 mismatch")
    return path


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def validate_candidate(manifest_path: Path, checkpoint_path: Path, tokenizer_path: Path, command: list[str], division_id: str) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    if manifest.get("schema") != "dreamco.model_release_candidate.v1":
        raise ValueError("candidate must be a verified DreamCo model release candidate")
    if manifest.get("division_id") != division_id:
        raise ValueError("candidate division_id does not match requested division")
    for key in ("model_id", "version"):
        if not isinstance(manifest.get(key), str) or not manifest[key].strip():
            raise ValueError(f"candidate {key} is required")
    if manifest.get("parameter_count") != CANONICAL_PARAMETERS:
        raise ValueError("candidate must match the canonical 45,038,208-parameter blueprint")
    integrity = manifest.get("artifact_integrity", {})
    architecture = manifest.get("architecture", {})
    if not isinstance(integrity.get("config_sha256"), str) or len(integrity["config_sha256"]) != 64:
        raise ValueError("candidate architecture config SHA-256 is required")
    if not isinstance(integrity.get("tokenizer_sha256"), str) or len(integrity["tokenizer_sha256"]) != 64:
        raise ValueError("candidate tokenizer SHA-256 is required")
    expected_checkpoint_hash = integrity.get("checkpoint_sha256") or manifest.get("weights_sha256")
    if not isinstance(expected_checkpoint_hash, str) or len(expected_checkpoint_hash) != 64:
        raise ValueError("candidate checkpoint SHA-256 is required")
    checkpoint_path = resolve_artifact(manifest_path.parent, str(checkpoint_path))
    if sha256_file(checkpoint_path).lower() != expected_checkpoint_hash.lower():
        raise ValueError("candidate checkpoint does not match release-candidate evidence")
    tokenizer_path = resolve_artifact(manifest_path.parent, str(tokenizer_path))
    if sha256_file(tokenizer_path).lower() != integrity["tokenizer_sha256"].lower():
        raise ValueError("candidate tokenizer does not match release-candidate evidence")
    training = manifest.get("training", {})
    if not isinstance(training.get("training_run_id"), str) or not training["training_run_id"].strip():
        raise ValueError("candidate training run identity is required")
    if training.get("initialization") != "random":
        raise ValueError("candidate must have documented random initialization")
    permissions = manifest.get("permissions", {})
    if permissions.get("training") is not True or permissions.get("commercial_model_use") is not True:
        raise PermissionError("candidate training and commercial-use rights are not approved")
    evaluation = manifest.get("evaluation", {})
    if evaluation.get("status") != "PASSED" or evaluation.get("holdout_independent") is not True:
        raise ValueError("candidate requires a passed independent pre-release evaluation")
    if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
        raise ValueError("candidate adapter command must be a non-empty argument array")
    return {
        **manifest,
        "_manifest_path": str(manifest_path.resolve()),
        "_checkpoint_path": str(checkpoint_path),
        "_tokenizer_path": str(tokenizer_path),
        "_command": command,
        "model_version": manifest["version"],
        "provider": "DreamCo",
        "architecture": {"parameter_count": manifest["parameter_count"], **architecture},
        "quantization": manifest.get("quantization", "full_precision"),
    }

def validate_baseline(entry: dict[str, Any], base_dir: Path) -> dict[str, Any]:
    for key in ("id", "provider", "model_id", "revision", "license_id", "license_review_reference"):
        if not isinstance(entry.get(key), str) or not entry[key].strip():
            raise ValueError(f"baseline requires {key}")
    revision = entry["revision"]
    if len(revision) != 40 or any(char not in "0123456789abcdefABCDEF" for char in revision):
        raise ValueError(f"baseline {entry['id']} revision must be an immutable 40-character commit SHA")
    if entry.get("benchmark_authorized") is not True:
        raise PermissionError(f"baseline {entry['id']} lacks explicit benchmark permission")
    validate_hashed_artifact(base_dir, entry.get("license_evidence", {}), f"baseline {entry['id']} license evidence")
    validate_hashed_artifact(base_dir, entry.get("benchmark_permission_evidence", {}), f"baseline {entry['id']} benchmark permission evidence")
    checkpoint_path = validate_hashed_artifact(base_dir, entry.get("checkpoint", {}), f"baseline {entry['id']}")
    tokenizer_path = validate_hashed_artifact(base_dir, entry.get("tokenizer", {}), f"baseline {entry['id']} tokenizer")
    adapter = entry.get("adapter", {}).get("command")
    if not isinstance(adapter, list) or not adapter or not all(isinstance(part, str) and part for part in adapter):
        raise ValueError(f"baseline {entry['id']} adapter.command must be a non-empty argument array")
    return {**entry, "_checkpoint_path": str(checkpoint_path), "_tokenizer_path": str(tokenizer_path), "_command": adapter}


def validate_fixtures(path: Path, division_id: str) -> list[dict[str, Any]]:
    payload = load_json(path)
    if payload.get("schema") != "dreamco.competitive_benchmark_fixtures.v1":
        raise ValueError("unsupported benchmark fixture schema")
    provenance = payload.get("provenance", {})
    if provenance.get("rights_status") not in {"DREAMCO_ORIGINAL", "APPROVED_FOR_EVALUATION"}:
        raise PermissionError("benchmark fixtures lack evaluation rights clearance")
    if not isinstance(provenance.get("evidence_reference"), str) or not provenance["evidence_reference"].strip():
        raise ValueError("fixture rights evidence reference is required")
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("benchmark fixture set must contain cases")
    seen = set()
    splits = set()
    for case in cases:
        if case.get("division_id") != division_id:
            raise ValueError("all fixture cases must belong to the requested division")
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id or case_id in seen:
            raise ValueError("fixture case IDs must be unique non-empty strings")
        seen.add(case_id)
        if case.get("split") not in {"development", "private_holdout"}:
            raise ValueError(f"unsupported split for {case_id}")
        splits.add(case["split"])
        if not isinstance(case.get("task_id"), str) or not isinstance(case.get("input"), dict):
            raise ValueError(f"fixture {case_id} needs task_id and object input")
        if not isinstance(case.get("expected_result"), dict) or case.get("expected_route") not in ROUTES:
            raise ValueError(f"fixture {case_id} needs expected_result and a valid expected_route")
        schema = case.get("output_schema")
        if not isinstance(schema, dict) or schema.get("type") != "object":
            raise ValueError(f"fixture {case_id} needs an object output_schema")
    if not {"development", "private_holdout"}.issubset(splits):
        raise ValueError("both development and private_holdout fixtures are required")
    return cases


def validate_schema(value: Any, schema: dict[str, Any]) -> bool:
    """Validate the deterministic JSON Schema subset used by Institute fixtures."""
    kind = schema.get("type")
    types = {
        "object": dict, "array": list, "string": str, "integer": int,
        "number": (int, float), "boolean": bool, "null": type(None),
    }
    if kind in types:
        expected_type = types[kind]
        if kind == "integer" and isinstance(value, bool):
            return False
        if kind == "number" and isinstance(value, bool):
            return False
        if not isinstance(value, expected_type):
            return False
    if "enum" in schema and value not in schema["enum"]:
        return False
    if "const" in schema and value != schema["const"]:
        return False
    if kind == "object":
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        if not isinstance(required, list) or any(key not in value for key in required):
            return False
        if schema.get("additionalProperties") is False and any(key not in properties for key in value):
            return False
        for key, child_schema in properties.items():
            if key in value and not validate_schema(value[key], child_schema):
                return False
    if kind == "array":
        if "minItems" in schema and len(value) < schema["minItems"]:
            return False
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            return False
        if isinstance(schema.get("items"), dict) and any(not validate_schema(item, schema["items"]) for item in value):
            return False
    if kind == "string":
        if "minLength" in schema and len(value) < schema["minLength"]:
            return False
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            return False
    if kind in {"integer", "number"}:
        if "minimum" in schema and value < schema["minimum"]:
            return False
        if "maximum" in schema and value > schema["maximum"]:
            return False
    return True


def percentile(values: list[float], quantile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return round(ordered[lower], 3)
    return round(ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower), 3)


def invoke(command: list[str], request: dict[str, Any], timeout: float) -> tuple[dict[str, Any] | None, float, str | None, bool]:
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            command,
            input=json.dumps(request, separators=(",", ":"), ensure_ascii=False),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        return None, (time.perf_counter() - started) * 1000, "timeout", True
    latency = (time.perf_counter() - started) * 1000
    if completed.returncode != 0:
        return None, latency, "adapter_exit_nonzero", False
    try:
        output = json.loads(completed.stdout)
    except (json.JSONDecodeError, TypeError):
        return None, latency, "invalid_json", False
    if not isinstance(output, dict):
        return None, latency, "output_not_object", False
    return output, latency, None, False


def evaluate_model(model: dict[str, Any], cases: list[dict[str, Any]], repeats: int, timeout: float) -> dict[str, Any]:
    observations = []
    latencies = []
    failures = 0
    timeouts = 0
    contract_passes = 0
    exact_passes = 0
    route_passes = 0
    deterministic_passes = 0
    total = len(cases) * repeats

    for case in cases:
        repeat_outputs = []
        for repeat in range(repeats):
            request = {
                "schema": "dreamco.model_adapter_request.v1",
                "case_id": case["case_id"],
                "division_id": case["division_id"],
                "task_id": case["task_id"],
                "input": case["input"],
                "output_schema": case["output_schema"],
                "model_id": model["model_id"],
                "model_version": model.get("model_version", model.get("version", model.get("revision"))),
                "model_artifact_path": model["_checkpoint_path"],
                "tokenizer_artifact_path": model["_tokenizer_path"],
            }
            output, latency, error, timed_out = invoke(model["_command"], request, timeout)
            latencies.append(latency)
            if timed_out:
                timeouts += 1
            if error or output is None:
                failures += 1
                repeat_outputs.append(None)
                observations.append({"case_id": case["case_id"], "split": case["split"], "repeat": repeat, "error": error})
                continue

            valid = set(output) == {"result", "route"} and isinstance(output.get("result"), dict) and output.get("route") in ROUTES
            if valid:
                valid = validate_schema(output["result"], case["output_schema"])
            if valid:
                contract_passes += 1
            if valid and output["result"] == case["expected_result"]:
                exact_passes += 1
            if valid and output["route"] == case["expected_route"]:
                route_passes += 1
            repeat_outputs.append(output)
            observations.append({
                "case_id": case["case_id"],
                "split": case["split"],
                "repeat": repeat,
                "contract_valid": valid,
                "task_exact_match": bool(valid and output["result"] == case["expected_result"]),
                "route_correct": bool(valid and output["route"] == case["expected_route"]),
            })
        if len(repeat_outputs) == repeats and repeat_outputs[0] is not None:
            canonical = json.dumps(repeat_outputs[0], sort_keys=True, separators=(",", ":"))
            if all(item is not None and json.dumps(item, sort_keys=True, separators=(",", ":")) == canonical for item in repeat_outputs[1:]):
                deterministic_passes += 1

    split_metrics = {}
    for split in ("development", "private_holdout"):
        selected = [row for row in observations if row["split"] == split]
        count = len(selected)
        split_metrics[split] = {
            "requests": count,
            "contract_pass_rate": round(sum(row.get("contract_valid", False) for row in selected) / count, 4) if count else None,
            "task_exact_match_rate": round(sum(row.get("task_exact_match", False) for row in selected) / count, 4) if count else None,
            "routing_accuracy": round(sum(row.get("route_correct", False) for row in selected) / count, 4) if count else None,
        }
    return {
        "model_id": model["model_id"],
        "model_version": model.get("model_version", model.get("revision")),
        "provider": model.get("provider", "DreamCo"),
        "division_id": model.get("division_id"),
        "parameter_count": model.get("architecture", {}).get("parameter_count", model.get("parameter_count")),
        "quantization": model.get("quantization", "unspecified"),
        "requests": total,
        "contract_pass_rate": round(contract_passes / total, 4) if total else None,
        "task_exact_match_rate": round(exact_passes / total, 4) if total else None,
        "routing_accuracy": round(route_passes / total, 4) if total else None,
        "deterministic_repeat_rate": round(deterministic_passes / len(cases), 4) if cases else None,
        "adapter_round_trip_p50_ms": percentile(latencies, 0.50),
        "adapter_round_trip_p95_ms": percentile(latencies, 0.95),
        "failure_rate": round(failures / total, 4) if total else None,
        "timeout_rate": round(timeouts / total, 4) if total else None,
        "split_metrics": split_metrics,
        "observations": observations,
        "memory_bytes": None,
        "energy_per_token_joules": None,
        "cost_per_million_tokens_usd": None,
        "unknown_metrics_reason": "No calibrated memory, power-meter, or attributable-cost adapter was supplied.",
    }


def run_benchmark(candidate_manifest: Path, candidate_checkpoint: Path, candidate_tokenizer: Path, candidate_command: list[str],
                  baseline_registry: Path, fixture_path: Path, division_id: str,
                  repeats: int = 3, timeout: float = 10.0) -> dict[str, Any]:
    if repeats < 2 or repeats > 20:
        raise ValueError("repeats must be between 2 and 20")
    if timeout <= 0 or timeout > 300:
        raise ValueError("timeout must be greater than 0 and at most 300 seconds")
    candidate = validate_candidate(candidate_manifest, candidate_checkpoint, candidate_tokenizer, candidate_command, division_id)
    fixtures = validate_fixtures(fixture_path, division_id)
    baselines_payload = load_json(baseline_registry)
    if baselines_payload.get("schema") != "dreamco.competitive_baseline_registry.v1":
        raise ValueError("unsupported baseline registry schema")
    raw_baselines = baselines_payload.get("baselines", [])
    if not raw_baselines:
        raise PermissionError("no rights-reviewed, pinned public baseline models are configured")
    baselines = [validate_baseline(item, baseline_registry.parent) for item in raw_baselines]
    if len({item["id"] for item in baselines}) != len(baselines):
        raise ValueError("baseline IDs must be unique")

    candidate_result = evaluate_model(candidate, fixtures, repeats, timeout)
    baseline_results = [evaluate_model(item, fixtures, repeats, timeout) for item in baselines]
    comparisons = []
    for baseline in baseline_results:
        comparisons.append({
            "baseline_id": baseline["model_id"],
            "candidate_minus_baseline": {
                metric: round(candidate_result[metric] - baseline[metric], 4)
                if candidate_result[metric] is not None and baseline[metric] is not None else None
                for metric in ("contract_pass_rate", "task_exact_match_rate", "routing_accuracy", "deterministic_repeat_rate")
            },
            "adapter_round_trip_p95_ratio_candidate_over_baseline": (
                round(candidate_result["adapter_round_trip_p95_ms"] / baseline["adapter_round_trip_p95_ms"], 4)
                if candidate_result["adapter_round_trip_p95_ms"] is not None and baseline["adapter_round_trip_p95_ms"] not in (None, 0) else None
            ),
        })
    return {
        "schema": "dreamco.institute.head_to_head_report.v1",
        "division_id": division_id,
        "created_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "protocol": {
            "fixture_sha256": sha256_file(fixture_path),
            "fixture_count": len(fixtures),
            "repeats_per_fixture": repeats,
            "timeout_seconds": timeout,
            "same_fixtures_for_all_models": True,
            "expected_outputs_sent_to_adapters": False,
            "runner_platform": platform.platform(),
            "python_version": sys.version.split()[0],
            "cpu_identifier": platform.processor() or None,
            "process_startup_included_in_adapter_round_trip": True,
        },
        "candidate": candidate_result,
        "baselines": baseline_results,
        "comparisons": comparisons,
        "release_claim": "benchmark_evidence_only_not_production_certification",
        "training_performed": False,
        "weights_modified": False,
        "network_used": False,
        "paid_compute_used": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-manifest", type=Path, required=True)
    parser.add_argument("--candidate-checkpoint", type=Path, required=True)
    parser.add_argument("--candidate-tokenizer", type=Path, required=True)
    parser.add_argument("--candidate-command", required=True, help="JSON array of executable and arguments; no shell expansion is performed")
    parser.add_argument("--baseline-registry", type=Path, default=ROOT / "config" / "institute-competitive-baselines.json")
    parser.add_argument("--fixtures", type=Path, required=True)
    parser.add_argument("--division-id", required=True)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        candidate_command = json.loads(args.candidate_command)
    except json.JSONDecodeError as exc:
        raise SystemExit("--candidate-command must be a JSON string array") from exc
    report = run_benchmark(args.candidate_manifest, args.candidate_checkpoint, args.candidate_tokenizer, candidate_command,
                           args.baseline_registry, args.fixtures, args.division_id,
                           args.repeats, args.timeout)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "division_id": args.division_id,
        "candidate": report["candidate"]["model_id"],
        "baselines": len(report["baselines"]),
        "candidate_holdout": report["candidate"]["split_metrics"]["private_holdout"],
        "report": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
