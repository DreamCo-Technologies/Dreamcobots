#!/usr/bin/env python3
"""Read-only local memory preflight for Buddy candidate planning, not inference.

Never downloads weights, probes devices, invokes a model, or authorizes training.
Do not publish this output as a hardware, quality, or licensing receipt.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import platform
import re
import subprocess

# Support both `python3 tools/...` and `python3 -m unittest` imports.
if __package__:
    from .validate_buddy_open_weight_candidates import parse, validate
else:
    from validate_buddy_open_weight_candidates import parse, validate

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config/buddy-open-weight-candidate-research.json"
GIB = Decimal(1024) ** 3


def parse_linux_memtotal(text: str) -> int | None:
    """Return bytes from the single Linux MemTotal line, or unknown."""
    matches = re.findall(r"^MemTotal:\s*([0-9]+) kB\s*$", text, re.MULTILINE)
    if len(matches) != 1:
        return None
    kib = int(matches[0])
    return kib * 1024 if kib > 0 else None


def observed_memory() -> tuple[int | None, str]:
    """Read total system memory only; never inspect user data or process state."""
    system = platform.system()
    if system == "Linux":
        try:
            return parse_linux_memtotal(Path("/proc/meminfo").read_text(encoding="ascii")), "linux_meminfo"
        except (OSError, UnicodeError):
            return None, "unavailable"
    if system == "Darwin":
        try:
            proc = subprocess.run(
                ["/usr/sbin/sysctl", "-n", "hw.memsize"],
                check=True, capture_output=True, text=True, timeout=3,
            )
            value = proc.stdout.strip()
            if re.fullmatch(r"[0-9]+", value) and int(value) > 0:
                return int(value), "macos_sysctl"
        except (OSError, subprocess.SubprocessError, UnicodeError):
            pass
    return None, "unavailable"


def _parameter_count(label: str) -> Decimal:
    match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)([MB])", label)
    if not match:
        raise ValueError("invalid advertised parameter class")
    try:
        count = Decimal(match[1]) * (Decimal(10) ** (9 if match[2] == "B" else 6))
    except InvalidOperation as exc:
        raise ValueError("invalid parameter class") from exc
    if not count.is_finite() or count <= 0:
        raise ValueError("parameter count must be positive")
    return count


def report(data: dict, memory_bytes: int | None, memory_source: str, system: str) -> dict:
    """Calculate weight-only arithmetic, never a claim that a model fits."""
    validate(data)  # Reject research-registry readiness or training claims.
    if memory_bytes is not None and (type(memory_bytes) is not int or memory_bytes <= 0):
        raise ValueError("memory_bytes must be a positive integer or unknown")
    if system not in {"Linux", "Darwin", "Windows", "Other"}:
        system = "Other"
    rows = []
    for candidate in data["candidates"]:
        count = _parameter_count(candidate["advertised_parameter_class"])
        rows.append({
            "model_id": candidate["id"],
            "advertised_parameter_class": candidate["advertised_parameter_class"],
            "approx_fp16_weight_only_gib": float(round(count * 2 / GIB, 3)),
            "approx_4bit_weight_only_gib": float(round(count / 2 / GIB, 3)),
            "local_inference_measured": False,
            "fits_in_memory_verified": False,
        })
    return {
        "schema": "dreamco.buddy_local_compute_preflight.v1",
        "status": "memory_inventory_only_no_model_execution",
        "os_family": system,
        "memory_source": memory_source if memory_bytes is not None else "unavailable",
        "observed_total_memory_gib": round(memory_bytes / float(GIB), 2) if memory_bytes is not None else None,
        "candidate_weight_only_estimates": rows,
        "notes": "Weight-only estimates omit tokenizer, quantization metadata, runtime, KV cache, activations and OS usage; not minimum hardware requirements.",
        "rights_verified": False,
        "hardware_suitability_verified": False,
        "local_latency_measured": False,
        "model_quality_measured": False,
        "training_authorized": False,
        "model_downloads": 0,
        "model_runs": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--output", type=Path, help="Optional local JSON output; no device identifiers")
    args = parser.parse_args()
    try:
        data = parse(args.registry.read_text(encoding="utf-8"))
        memory, source = observed_memory()
        result = report(data, memory, source, platform.system())
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(2, f"Buddy local compute preflight blocked: {exc}\n")
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
