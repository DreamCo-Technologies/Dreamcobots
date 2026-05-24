"""
Demo 2 — Orchestrated Multi-Bot DAG
======================================

Shows the DreamCoOrchestrator running multiple bots concurrently,
respecting DAG dependencies, with circuit breakers and kill switch.

Run::

    python demo/demo_2_orchestrated_bots.py
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from python_bots.core.base_bot import DreamCoBot
from python_bots.orchestrator import DreamCoOrchestrator


class DataCollectorBot(DreamCoBot):
    async def run(self): return {"data": ["item1", "item2", "item3"]}
    async def analyze(self): return {"status": "collected"}
    async def monetize(self): return {"value": "raw_data"}
    async def report(self): return {"runs": self.memory.structured.get_run_history(3)}


class DataEnricherBot(DreamCoBot):
    async def run(self): return {"enriched": True, "leads": 5}
    async def analyze(self): return {"status": "enriched"}
    async def monetize(self): return {"value": "enriched_leads", "revenue": 1.25}
    async def report(self): return {"runs": self.memory.structured.get_run_history(3)}


class ReportGeneratorBot(DreamCoBot):
    async def run(self): return {"report": "Q2 2026 Lead Report — 5 leads, $1.25 revenue"}
    async def analyze(self): return {"status": "reported"}
    async def monetize(self): return {"value": "report_generated"}
    async def report(self): return {"runs": self.memory.structured.get_run_history(3)}


class UnreliableBot(DreamCoBot):
    """A bot that always fails — demonstrates circuit breaker."""
    async def run(self): raise RuntimeError("Simulated failure!")
    async def analyze(self): return {}
    async def monetize(self): return {}
    async def report(self): return {}


async def main():
    print("=" * 60)
    print("  Demo 2: Multi-Bot Orchestration with DAG + Circuit Breaker")
    print("=" * 60)

    # Create orchestrator
    orch = DreamCoOrchestrator(max_concurrent=3, default_priority=5)

    # Register bots
    collector = DataCollectorBot("data_collector")
    enricher = DataEnricherBot("data_enricher")
    reporter = ReportGeneratorBot("report_generator")
    unreliable = UnreliableBot("unreliable_bot", max_retries=2)

    for bot in [collector, enricher, reporter, unreliable]:
        orch.register(bot)

    print(f"\n📋 Registered {len(orch.list_bots())} bots")

    # Run with DAG: enricher depends on collector; reporter depends on enricher
    dag = {
        "data_collector": [],
        "data_enricher": ["data_collector"],
        "report_generator": ["data_enricher"],
        "unreliable_bot": [],  # runs concurrently with collector
    }

    print("\n🚀 Running all bots with DAG scheduling...")
    results = await orch.run_all(dag)

    print(f"\n📊 Results: {results['succeeded']}/{results['total']} succeeded")
    for bot_name, result in results["results"].items():
        status = "✅" if result.get("success") else "❌"
        print(f"   {status} {bot_name}: {result.get('result', result.get('error', ''))}")

    # Check circuit breaker effect on unreliable bot
    print(f"\n⚡ unreliable_bot state: {unreliable.state.value}")
    print(f"   Error count: {unreliable._error_count}")

    # Demonstrate kill switch
    print("\n🔴 Demonstrating kill switch...")
    orch.kill("data_collector")
    result = await orch.dispatch("data_collector")
    print(f"   dispatch after kill: success={result.get('success')}, error={result.get('error')}")

    # Summary
    summary = orch.summary()
    print(f"\n📋 Orchestrator Summary:")
    print(f"   Registered: {len(summary['registered_bots'])} bots")
    print(f"   Killed: {summary['killed_bots']}")
    print(f"   Dead letter queue: {summary['dead_letter_count']} items")

    print("\n✨ Demo 2 complete!\n")


if __name__ == "__main__":
    asyncio.run(main())
