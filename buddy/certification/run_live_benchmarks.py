"""Approved, bounded live model comparisons; disabled by default in CI."""
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from .model_benchmarks import Task, benchmark
from .provider_adapters import ChatCompletionsAdapter

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--approved", action="store_true")
    parser.add_argument("--output", default="website/data/buddy-live-model-benchmark.json")
    parser.add_argument("--max-tasks", type=int, default=6)
    args = parser.parse_args()
    if not args.approved or os.environ.get("BUDDY_LIVE_BENCHMARK_APPROVED") != "yes":
        parser.error("Live benchmarking requires --approved and BUDDY_LIVE_BENCHMARK_APPROVED=yes")
    root = Path(__file__).resolve().parents[2]
    config = json.loads((root / "config/buddy/benchmarks/starter-independent-tasks.json").read_text())
    providers = json.loads(os.environ.get("BUDDY_BENCHMARK_PROVIDERS_JSON", "[]"))
    if not providers:
        parser.error("No configured provider endpoints; refusing simulated live benchmark")
    if len(providers) > 6:
        parser.error("Maximum six providers per run")
    adapters = [ChatCompletionsAdapter(**provider) for provider in providers]
    tasks = [Task(t["id"], t["prompt"], t["expected"]) for t in config["tasks"][:args.max_tasks]]
    if args.max_tasks < 1 or args.max_tasks > 30:
        parser.error("max-tasks must be 1..30")
    report = benchmark(tasks, adapters, dataset_rights="owned", approved=True)
    report["executed_at"] = datetime.now(timezone.utc).isoformat()
    report["domain_map"] = {t["id"]: t["domain"] for t in config["tasks"][:args.max_tasks]}
    report["caveats"] = ["Exact-match reasoning tasks are not actual multi-step tool execution.",
                          "External providers are not independently certified by this harness.",
                          "API costs and provider terms apply; review before use."]
    dest = (root / args.output).resolve()
    if not dest.is_relative_to(root / "website" / "data"):
        parser.error("output must be under website/data")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"models": len(adapters), "tasks": len(tasks), "output": str(dest)}))

if __name__ == "__main__":
    main()
