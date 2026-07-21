"""Benchmark runner for DreamCo bots with latency and error metrics."""

from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
import time
import tracemalloc
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"


def discover_bot_entrypoints() -> list[Path]:
    paths = sorted(ROOT.glob("bots/*/main.py"))
    return [path for path in paths if path.is_file()]


def load_callable(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    for name in ("main", "run", "app"):
        if hasattr(module, name):
            return getattr(module, name)
    raise AttributeError(f"No runnable entrypoint found in {path}")


def benchmark_callable(func, iterations: int) -> dict[str, Any]:
    latencies = []
    errors = 0
    tracemalloc.start()
    start = time.perf_counter()
    for _ in range(iterations):
        item_start = time.perf_counter()
        try:
            if callable(func):
                func()
        except Exception:
            errors += 1
        latencies.append((time.perf_counter() - item_start) * 1000)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    duration = max(time.perf_counter() - start, 0.001)
    latencies_sorted = sorted(latencies)
    return {
        "p50_ms": latencies_sorted[int(len(latencies_sorted) * 0.50) - 1],
        "p95_ms": latencies_sorted[int(len(latencies_sorted) * 0.95) - 1],
        "p99_ms": latencies_sorted[int(len(latencies_sorted) * 0.99) - 1],
        "throughput_rps": iterations / duration,
        "error_rate": errors / iterations,
        "memory_peak_bytes": peak,
    }


def compare_reports(current: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    diff = {}
    for bot, metrics in current["bots"].items():
        base = baseline.get("bots", {}).get(bot, {})
        diff[bot] = {key: metrics[key] - base.get(key, 0) for key in metrics}
    return diff


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=100)
    parser.add_argument("--compare", nargs="?", const="latest", default=None)
    args = parser.parse_args()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report = {"date": date.today().isoformat(), "bots": {}}
    for path in discover_bot_entrypoints():
        try:
            report["bots"][path.parent.name] = benchmark_callable(load_callable(path), args.iterations)
        except Exception as exc:  # noqa: BLE001
            report["bots"][path.parent.name] = {"error": str(exc), "p50_ms": 0, "p95_ms": 0, "p99_ms": 0, "throughput_rps": 0, "error_rate": 1.0, "memory_peak_bytes": 0}
    output = REPORTS_DIR / f"benchmark_{date.today().isoformat()}.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    if args.compare:
        previous = sorted(REPORTS_DIR.glob("benchmark_*.json"))
        if len(previous) > 1:
            baseline = json.loads(previous[-2].read_text())
            report["comparison"] = compare_reports(report, baseline)
            output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(output), "bots": len(report["bots"])}, indent=2))


if __name__ == "__main__":
    main()
