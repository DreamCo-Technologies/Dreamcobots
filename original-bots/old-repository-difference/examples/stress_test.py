"""Working stress test example for the DreamCobots platform."""
import sys
import os
import importlib.util

_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, _ROOT)

from stress_test.ai_stress_test import AIStressTest
from stress_test.computer_stress_test import HardwareStressTest


def _load_bot(bot_dir, module_file, class_name):
    """Load a bot class from a hyphenated directory."""
    path = os.path.join(_ROOT, "bots", bot_dir, module_file)
    spec = importlib.util.spec_from_file_location(bot_dir.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, class_name)


def run_stress_tests():
    """Run a full suite of stress tests for the DreamCobots platform."""
    print("=" * 60)
    print("  DreamCobots Stress Test Suite")
    print("=" * 60)

    print("\n[Phase 1] Hardware Safety Check...")
    hw_test = HardwareStressTest()
    safety = hw_test.safety_check()
    print(f"  Safe to proceed: {safety.get('safe_to_proceed', True)}")
    if not safety.get("safe_to_proceed", True):
        print("  ⚠️  System resources are too high. Aborting stress test.")
        return

    print("\n[Phase 2] System Scoring...")
    score = hw_test.score_system()
    print(f"  Overall System Score: {score.get('overall_score', 0)}/100")
    print(f"  Rating: {score.get('rating', 'N/A')}")
    for rec in score.get("recommendations", [])[:2]:
        print(f"  → {rec}")

    print("\n[Phase 3] AI Bot Stress Test...")
    ai_test = AIStressTest()
    HustleBot = _load_bot("hustle-bot", "hustle_bot.py", "HustleBot")
    ReferralBot = _load_bot("referral-bot", "referral_bot.py", "ReferralBot")
    FinanceBot = _load_bot("finance-bot", "finance_bot.py", "FinanceBot")
    bots = [HustleBot(), ReferralBot(), FinanceBot()]
    for bot in bots:
        bot.start()
    stress_result = ai_test.run_bot_stress_test(bots, duration_seconds=5)
    print(f"  Bots tested: {stress_result['bots_tested']}")
    print(f"  Total invocations: {stress_result['total_invocations']}")
    print(f"  Calls/second: {stress_result['invocations_per_second']}")
    print(f"  Status: {stress_result['status']}")

    print("\n[Phase 4] Response Time Test...")
    FinanceBot = _load_bot("finance-bot", "finance_bot.py", "FinanceBot")
    finance_bot = FinanceBot()
    finance_bot.start()
    rt_result = ai_test.test_response_time(finance_bot, num_requests=50)
    print(f"  Bot: {rt_result['bot']}")
    print(f"  Avg response: {rt_result['avg_ms']}ms")
    print(f"  p95 response: {rt_result['p95_ms']}ms")
    print(f"  Status: {rt_result['status']}")

    print("\n[Phase 5] Memory Usage Test...")
    mem_result = ai_test.test_memory_usage(finance_bot)
    print(f"  Memory delta: {mem_result['memory_delta_mb']}MB")
    print(f"  Status: {mem_result['status']}")

    print("\n" + "=" * 60)
    print("  FINAL REPORT")
    print("=" * 60)
    report = ai_test.generate_report()
    print(report)

    for bot in bots + [finance_bot]:
        bot.stop()

    print("\n✅ All stress tests completed successfully!")


if __name__ == "__main__":
    run_stress_tests()
