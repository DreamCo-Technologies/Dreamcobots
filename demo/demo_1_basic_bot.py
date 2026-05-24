"""
Demo 1 — Basic DreamCoBot
============================

Shows how to create a bot that inherits from DreamCoBot, runs through
the full lifecycle, and uses all four canonical methods.

Run::

    python demo/demo_1_basic_bot.py
"""

import asyncio
import sys
import os

# Allow running from repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from python_bots.core.base_bot import DreamCoBot


class LeadGenerationBot(DreamCoBot):
    """Demo bot: finds leads for a target company."""

    async def run(self) -> dict:
        print(f"\n🤖 {self.name} starting...")
        analysis = await self.analyze()
        monetization = await self.monetize()
        await self.memory.event("task_completed", {**analysis, **monetization})
        return {**analysis, **monetization, "status": "completed"}

    async def analyze(self) -> dict:
        # Simulate finding leads
        target = self.config.get("target_company", "ACME Corp")
        leads = [
            {"name": "Alice Johnson", "title": "VP Sales", "company": target},
            {"name": "Bob Smith", "title": "CTO", "company": target},
            {"name": "Carol White", "title": "CEO", "company": target},
        ]
        # Store in long-term memory
        self.memory.store_doc(
            f"leads_{target}",
            f"Found {len(leads)} leads at {target}: {[l['name'] for l in leads]}"
        )
        return {"leads_found": len(leads), "leads": leads}

    async def monetize(self) -> dict:
        return {"revenue_usd": 0.75, "leads_value": "3 qualified leads @ $0.25 each"}

    async def report(self) -> dict:
        history = self.memory.structured.get_run_history(5)
        return {
            "agent": self.name,
            "total_runs": len(history),
            "health": self.health_check(),
        }


async def main():
    print("=" * 60)
    print("  Demo 1: DreamCoBot Basic Lifecycle")
    print("=" * 60)

    # Create bot with config
    bot = LeadGenerationBot(
        name="lead_gen_bot",
        config={"target_company": "DreamCo Technologies"},
    )

    print(f"\n📊 Initial state: {bot.state.value}")
    print(f"📍 Bot ID: {bot.bot_id}")

    # Run through the execute() wrapper (handles lifecycle automatically)
    result = await bot.execute()

    print(f"\n✅ Run result:")
    print(f"   Success: {result['success']}")
    print(f"   Duration: {result['duration_s']}s")
    print(f"   Leads found: {result['result'].get('leads_found', 0)}")
    print(f"   Revenue: ${result['result'].get('revenue_usd', 0)}")

    print(f"\n📊 Final state: {bot.state.value}")

    # Health check
    health = bot.health_check()
    print(f"\n💚 Health Check:")
    print(f"   State: {health['state']}")
    print(f"   Error count: {health['error_count']}")
    print(f"   Total runs: {health['total_runs']}")

    # Memory stats
    stats = bot.memory.stats()
    print(f"\n🧠 Memory Stats:")
    print(f"   Short-term keys: {stats['short_term_keys']}")
    print(f"   Behavioral events: {stats['behavioral']['total_events']}")

    # Report
    report = await bot.report()
    print(f"\n📝 Report: {report}")

    print("\n✨ Demo 1 complete!\n")


if __name__ == "__main__":
    asyncio.run(main())
