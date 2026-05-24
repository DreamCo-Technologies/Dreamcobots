# FAQ — DreamCo OS

Answers to the questions we hear most often from developers, investors, and enterprise evaluators.

---

## General

### Why not just use LangChain?

LangChain is a tool library. DreamCo is a **runtime**.

LangChain gives you building blocks (chains, agents, retrievers). DreamCo gives you an entire operating system: lifecycle management, circuit breakers, kill switches, governance policies, audit logs, rate limiting, PII detection, and a unified memory tier — all wired together out of the box.

With LangChain you build bots. With DreamCo you **operate** them at scale.

### Why not just use CrewAI?

CrewAI is excellent for role-based multi-agent workflows. DreamCo adds:
- **Monetization built-in** — every bot has a `monetize()` method
- **Governance** — policy-as-code, quarantine, kill switch
- **500+ domain-specific bots** already built
- **Enterprise security** — zero CVE policy, PII detection, audit log
- **MCP server** — interoperable with any framework including CrewAI

You can use CrewAI *inside* DreamCo — they're complementary.

### Why not just use AutoGen?

AutoGen is Microsoft's enterprise solution. DreamCo is **open, composable, and monetization-native**.

AutoGen requires Azure and significant enterprise buy-in. DreamCo runs locally, on any cloud, or on-premise. And DreamCo bots can earn revenue — that's a fundamentally different value proposition.

### Is DreamCo a bot collection or a platform?

**A platform.** The 500+ bots are proof-of-concept demonstrations of the platform's capabilities. The real product is the infrastructure underneath: `DreamCoBot` base class, `DreamCoOrchestrator`, 4-tier memory, governance layer, MCP server, and the SDK.

Think of the bots as apps — and DreamCo OS as the operating system they run on.

---

## Technical

### What Python version is required?

Python 3.10, 3.11, or 3.12. All three are tested in CI.

### Does it require Redis?

No. Redis is the preferred short-term memory backend, but all components have graceful in-process fallbacks for development. You can run a full DreamCo OS stack locally with zero external dependencies.

### Does it require a vector database?

No. Chroma (embedded) is used by default. When `PINECONE_API_KEY` is set, the platform automatically upgrades to Pinecone for production-scale vector search.

### How do I create a new bot?

```python
from python_bots.core import DreamCoBot

class MyBot(DreamCoBot):
    async def run(self) -> dict:
        result = await self.analyze()
        await self.memory.event("task_completed", result)
        return result

    async def analyze(self) -> dict:
        return {"found": "something useful"}

    async def monetize(self) -> dict:
        return {"revenue_usd": 0.0, "leads": 0}

    async def report(self) -> dict:
        history = self.memory.structured.get_run_history(5)
        return {"recent_runs": len(history)}
```

### What is MCP and why does it matter?

MCP (Model Context Protocol) is the standard protocol for AI tool interoperability — used by Claude Desktop, Cursor, Windsurf, and every major AI IDE. By running a DreamCo MCP server, your entire bot fleet becomes instantly accessible to any MCP-compatible AI assistant or framework.

### How does the circuit breaker work?

Every `DreamCoBot` tracks `error_count`. When a bot fails `max_retries` consecutive times (default: 3), the orchestrator automatically moves it to `QUARANTINED` state and logs the event. Quarantined bots are excluded from all execution until an operator calls `release_quarantine()`.

### How do I enforce governance policies?

```python
from python_bots.governance import PolicyRegistry, BotPolicy

registry = PolicyRegistry()
registry.load_from_dict({
    "my_bot": {
        "max_execution_time": 60,
        "allowed_capabilities": ["web_search"],
        "require_approval_above_cost_usd": 5.0,
        "allow_file_write": False,
    }
})
```

---

## Security

### How are secrets managed?

All secrets are loaded from environment variables via `python-dotenv`. No secrets are ever hardcoded. The CI pipeline uses `trufflehog` to scan for accidental secret commits.

### What CVEs are currently open?

**Zero.** We maintain a zero open CVE policy. `pip-audit` runs on every CI push and blocks merges if any known vulnerability is found.

### Is PII handled safely?

Yes. The `PIIDetector` scans all data before it's stored in memory. Detected PII is redacted with `[REDACTED]` placeholders. The `memory.forget(key)` method provides GDPR-compliant selective deletion across all four memory tiers.

---

## Business & Investment

### What's the monetization model?

Three revenue streams:
1. **SaaS subscriptions** — Free / Pro ($49/mo) / Enterprise (custom)
2. **Metered billing** — per bot execution minute (Stripe)
3. **Bot Marketplace** — revenue sharing on community bot sales

The platform is itself a revenue-generating asset: every bot has a built-in `monetize()` method that tracks value generation.

### What's the TAM?

The AI agent market is projected at **$47B by 2030** (Grand View Research). DreamCo targets the enterprise automation segment — companies that need governed, auditable, monetizable AI agents — estimated at $8B by 2027.

### Who are the target customers?

1. **Enterprises** needing governed AI automation with audit trails
2. **SaaS companies** wanting to add AI agent capabilities to their products
3. **Solo developers / agencies** monetizing bot automation services
4. **AI teams** that need production-grade infrastructure without building it from scratch

### Why is governance a differentiator?

Every major enterprise AI deployment eventually hits the same wall: *"How do we control what these agents do?"* Regulatory pressure (EU AI Act, NIST AI RMF) is forcing companies to audit AI actions. DreamCo is the only multi-agent platform with governance built into the foundation, not bolted on afterward.

---

*Have a question not answered here? Open an issue or email hello@dreamco.ai*
