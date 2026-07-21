"""
AI Stress Test for the Dreamcobots Ecosystem
=============================================
Evaluates performance metrics for each bot:
  - Request handling throughput (operations per second)
  - Response latency (average, min, max)
  - Success rate under load
  - Memory footprint (approximate)

Run:
    python stress_test/ai_stress_test.py
    python stress_test/ai_stress_test.py --iterations 500 --concurrency 10
"""

import argparse
import sys
import time
import statistics
import tracemalloc
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---------------------------------------------------------------------------
# Allow imports from the bots directory regardless of cwd
# ---------------------------------------------------------------------------
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "bots", "government-contract-grant-bot"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "bots", "referral-bot"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "bots", "hustle-bot"))

from government_contract_grant_bot import GovernmentContractGrantBot
from referral_bot import ReferralBot
from hustle_bot import HustleBot


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _time_call(fn, *args, **kwargs):
    """Execute fn(*args, **kwargs) and return (result, elapsed_seconds)."""
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    elapsed = time.perf_counter() - start
    return result, elapsed


def _run_with_memory(fn, *args, **kwargs):
    """Run fn and return (result, elapsed_seconds, peak_memory_kb)."""
    tracemalloc.start()
    result, elapsed = _time_call(fn, *args, **kwargs)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, elapsed, peak / 1024  # convert bytes → KB


# ---------------------------------------------------------------------------
# Individual bot workloads
# ---------------------------------------------------------------------------

def _gcg_workload(_):
    bot = GovernmentContractGrantBot()
    bot.search_contracts()
    bot.search_grants()
    bot.process_contracts()
    bot.process_grants()
    return True


def _referral_workload(i):
    bot = ReferralBot()
    bot.register_user(f"referrer_{i}")
    bot.generate_invite_link(f"referrer_{i}")
    for j in range(3):
        bot.register_user(f"user_{i}_{j}", referrer_id=f"referrer_{i}")
        bot.record_revenue(f"user_{i}_{j}", (j + 1) * 50)
    bot.get_referrer_dashboard(f"referrer_{i}")
    return True


def _hustle_workload(i):
    bot = HustleBot()
    user = f"hustler_{i}"
    bot.configure_goal(user, revenue_goal=1000.0)
    bot.suggest_tasks(user)
    bot.record_revenue(user, 200)
    bot.record_revenue(user, 400)
    bot.get_daily_summary(user)
    bot.run_motivational_campaign(user)
    return True


# ---------------------------------------------------------------------------
# Stress runner
# ---------------------------------------------------------------------------

def stress_test(workload_fn, name, iterations, concurrency, quiet=True):
    """
    Run *workload_fn* *iterations* times using up to *concurrency* threads.
    Returns a metrics dict.
    """
    latencies = []
    errors = 0

    # Suppress stdout during load (bots print a lot)
    if quiet:
        import io
        _devnull = open(os.devnull, "w")
        _old_stdout = sys.stdout
        sys.stdout = _devnull

    wall_start = time.perf_counter()
    try:
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = {executor.submit(_time_call, workload_fn, i): i for i in range(iterations)}
            for future in as_completed(futures):
                try:
                    _, elapsed = future.result()
                    latencies.append(elapsed)
                except Exception:
                    errors += 1
    finally:
        if quiet:
            sys.stdout = _old_stdout
            _devnull.close()

    wall_elapsed = time.perf_counter() - wall_start

    metrics = {
        "name": name,
        "iterations": iterations,
        "concurrency": concurrency,
        "total_wall_time_s": round(wall_elapsed, 4),
        "throughput_ops_per_s": round(iterations / wall_elapsed, 2),
        "latency_avg_ms": round(statistics.mean(latencies) * 1000, 2) if latencies else 0,
        "latency_min_ms": round(min(latencies) * 1000, 2) if latencies else 0,
        "latency_max_ms": round(max(latencies) * 1000, 2) if latencies else 0,
        "latency_p95_ms": round(
            sorted(latencies)[int(len(latencies) * 0.95)] * 1000, 2
        ) if latencies else 0,
        "success_rate_pct": round((len(latencies) / iterations) * 100, 2),
        "errors": errors,
    }
    return metrics


def memory_profile(workload_fn, name):
    """Run one workload iteration and measure peak memory."""
    import io

    _devnull = open(os.devnull, "w")
    _old_stdout = sys.stdout
    sys.stdout = _devnull
    try:
        _, elapsed, peak_kb = _run_with_memory(workload_fn, 0)
    finally:
        sys.stdout = _old_stdout
        _devnull.close()

    return {"name": name, "single_run_latency_ms": round(elapsed * 1000, 2), "peak_memory_kb": round(peak_kb, 2)}


# ---------------------------------------------------------------------------
# Report printer
# ---------------------------------------------------------------------------

def print_report(results, memory_results):
    sep = "=" * 60
    print(f"\n{sep}")
    print("  DREAMCOBOTS AI STRESS TEST REPORT")
    print(f"  Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(sep)

    for m in results:
        print(f"\n🤖  {m['name']}")
        print(f"    Iterations      : {m['iterations']} (concurrency={m['concurrency']})")
        print(f"    Wall time       : {m['total_wall_time_s']} s")
        print(f"    Throughput      : {m['throughput_ops_per_s']} ops/s")
        print(f"    Latency avg/min/max/p95 (ms): "
              f"{m['latency_avg_ms']} / {m['latency_min_ms']} / "
              f"{m['latency_max_ms']} / {m['latency_p95_ms']}")
        print(f"    Success rate    : {m['success_rate_pct']}%  (errors={m['errors']})")

    print(f"\n{'─' * 60}")
    print("  MEMORY PROFILES (single iteration)")
    print(f"{'─' * 60}")
    for mem in memory_results:
        print(f"    {mem['name']:<40} "
              f"latency={mem['single_run_latency_ms']} ms  "
              f"peak={mem['peak_memory_kb']} KB")

    all_ok = all(m["success_rate_pct"] == 100.0 for m in results)
    print(f"\n{'─' * 60}")
    print(f"  Overall status: {'✅ PASS' if all_ok else '❌ FAILURES DETECTED'}")
    print(sep)
    return all_ok


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(iterations=100, concurrency=5):
    bots = [
        ("Government Contract & Grant Bot", _gcg_workload),
        ("Referral Bot", _referral_workload),
        ("Hustle Bot", _hustle_workload),
    ]

    print(f"Running stress test: {iterations} iterations × {concurrency} concurrent workers per bot …")

    results = [stress_test(fn, name, iterations, concurrency) for name, fn in bots]
    memory_results = [memory_profile(fn, name) for name, fn in bots]

    ok = print_report(results, memory_results)
    return 0 if ok else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dreamcobots AI Stress Test")
    parser.add_argument("--iterations", type=int, default=100, help="Number of iterations per bot (default: 100)")
    parser.add_argument("--concurrency", type=int, default=5, help="Concurrent workers per bot (default: 5)")
    args = parser.parse_args()
    sys.exit(main(iterations=args.iterations, concurrency=args.concurrency))
