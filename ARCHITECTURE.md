# DreamCo OS — Architecture

> **DreamCo is the governed operating system for autonomous AI agents.**
>
> Where others build isolated bots, DreamCo builds a runtime — composable, event-driven,
> memory-persistent, and execution-safe. Every agent in the ecosystem inherits shared
> infrastructure: persistent memory, unified orchestration, tool interoperability via MCP,
> and governance policies that enforce execution integrity at every layer.
>
> DreamCo isn't a bot collection. It's a platform.

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DreamCo OS                                   │
│                                                                       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐   │
│  │  MCP Server  │    │ DreamCo SDK  │    │  REST API (FastAPI)  │   │
│  │  (10 tools)  │    │  (PyPI pkg)  │    │  /api/bots /health   │   │
│  └──────┬───────┘    └──────┬───────┘    └──────────┬───────────┘   │
│         └────────────┬──────┘                       │               │
│                      ▼                               │               │
│         ┌────────────────────────────────────────────┘               │
│         │                                                             │
│         ▼                                                             │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              DreamCoOrchestrator (Event-Driven)               │   │
│  │                                                               │   │
│  │  EventBus │ DAG Scheduler │ Circuit Breaker │ Priority Queue  │   │
│  │  Kill Switch │ Dead-Letter Queue │ Broadcast │ Human-in-Loop  │   │
│  └──────────────────────────┬───────────────────────────────────┘   │
│                              │ dispatch / run_all                     │
│              ┌───────────────┼───────────────┐                       │
│              ▼               ▼               ▼                       │
│       ┌─────────────┐ ┌─────────────┐ ┌─────────────┐             │
│       │ DreamCoBot  │ │ DreamCoBot  │ │ DreamCoBot  │  ...500+     │
│       │ (BaseClass) │ │  finance    │ │  real_estate│             │
│       │             │ │             │ │             │             │
│       │ run()       │ │ run()       │ │ run()       │             │
│       │ analyze()   │ │ analyze()   │ │ analyze()   │             │
│       │ monetize()  │ │ monetize()  │ │ monetize()  │             │
│       │ report()    │ │ report()    │ │ report()    │             │
│       └──────┬──────┘ └─────────────┘ └─────────────┘             │
│              │                                                        │
│       ┌──────┴─────────────────────────────────────────────┐        │
│       │              Shared Infrastructure                  │        │
│       │                                                      │        │
│  ┌────┴──────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │        │
│  │  Memory   │  │ Govern.  │  │  Tools   │  │ Observ.  │  │        │
│  │  Client   │  │ Layer    │  │ Library  │  │          │  │        │
│  │           │  │          │  │          │  │          │  │        │
│  │ ShortTerm │  │ Policies │  │WebSearch │  │OTel Span │  │        │
│  │ (Redis)   │  │ Sandbox  │  │Browser   │  │Struct Log│  │        │
│  │ LongTerm  │  │Quarantine│  │FileSystem│  │Prometheus│  │        │
│  │ (Chroma/  │  │AuditLog  │  │CodeExec  │  │CostTrack │  │        │
│  │  Pinecone)│  │RateLimtr │  │Notif.    │  │SessionRpl│  │        │
│  │ Structured│  │PIIDtctr  │  │Database  │  │          │  │        │
│  │ (Postgres)│  │          │  │          │  │          │  │        │
│  │ Behavioral│  │          │  │          │  │          │  │        │
│  │ (Graph)   │  │          │  │          │  │          │  │        │
│  └───────────┘  └──────────┘  └──────────┘  └──────────┘  │        │
│       └──────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. DreamCoBot Base Class (`python_bots/core/base_bot.py`)

Every bot inherits from `DreamCoBot` and gains:

- **Lifecycle state machine**: `IDLE → RUNNING → IDLE/QUARANTINED/STOPPED`
- **4 canonical methods**: `run()`, `analyze()`, `monetize()`, `report()`
- **Async-first**: all methods are `async def`
- **Memory client**: automatically provisioned 4-tier memory
- **Health check**: `health_check()` returns JSON status
- **Capability whitelist**: `can_use(tool)` / `assert_can_use(tool)`
- **Auto-registration**: `register(orchestrator)` on startup
- **Circuit breaker**: auto-quarantine after `max_retries` consecutive failures

### 2. DreamCoOrchestrator (`python_bots/orchestrator.py`)

Event-driven coordinator for all bots:

- **Event bus**: `asyncio.Queue`-based, no external dependencies
- **DAG scheduling**: declare bot dependencies, run independents concurrently
- **Priority queue**: high-priority tasks preempt lower-priority ones
- **Circuit breaker**: failing bots quarantined automatically
- **Kill switch**: `orchestrator.kill(bot_name)` halts immediately
- **Dead-letter queue**: failed tasks stored for inspection
- **Human-in-the-loop**: `requires_approval=True` gates execution
- **Broadcast**: `orchestrator.broadcast(msg)` notifies all bots
- **Retry**: `dispatch_with_retry()` with exponential backoff

### 3. Memory Layer (`python_bots/core/memory/`)

Four-tier persistent memory:

| Tier | Backend | Use Case | TTL |
|------|---------|----------|-----|
| Short-term | Redis | Session state, recent context | 24h |
| Long-term | Chroma / Pinecone | Semantic recall, knowledge base | Permanent |
| Structured | SQLite / Postgres | Run history, relational state | Permanent |
| Behavioral | Event graph | Decision audit, workflow replay | 90 days |

**Unified API via `MemoryClient`:**
```python
memory.save(key, value)           # short-term
memory.load(key)                  # short-term recall
memory.store_doc(id, text)        # vector storage
memory.recall(query, top_k=5)    # semantic search
memory.state(key, value)          # relational upsert
memory.event(type, payload)       # behavioral graph
memory.forget(key)                # GDPR deletion (all tiers)
```

### 4. Governance Layer (`python_bots/governance/`)

Policy-as-code enforcement:

- **PolicyRegistry**: JSON/YAML-configurable policies per bot
- **Sandbox**: async execution wrapper with timeout + capability checks
- **QuarantineManager**: operator-controlled bot quarantine
- **GovernanceAuditLog**: append-only file-backed audit trail
- **RateLimiter**: sliding-window per-bot rate limiting
- **PIIDetector**: pre-storage PII scrubbing with GDPR-compliant deletion

### 5. Model Router (`python_bots/core/model_router.py`)

Multi-provider AI routing:

- **Providers**: OpenAI (GPT-4o), Anthropic (Claude), Google (Gemini), local (Ollama)
- **Cost-aware selection**: cheapest model for simple tasks
- **Automatic fallback**: primary → fallback chain on failure
- **Response caching**: SHA-256 hash of prompt+context, 1h TTL
- **Token budget**: per-call and per-bot spending caps
- **Streaming**: async generator for real-time token delivery

### 6. MCP Server (`dreamco_mcp_server.py`)

10 tools registered for cross-framework interoperability:

| Tool | Description |
|------|-------------|
| `run_bot` | Execute any registered bot |
| `list_bots` | List all bots + health status |
| `get_bot_status` | Single bot health check |
| `get_memory` | Short-term memory retrieval |
| `set_memory` | Short-term memory write |
| `recall_memory` | Semantic vector recall |
| `kill_bot` | Kill switch activation |
| `get_orchestrator_summary` | Full orchestrator state |
| `web_search` | Unified web search |
| `execute_code` | Safe Python/bash execution |

### 7. Tool Library (`python_bots/tools/`)

Shared tools usable by any bot, all implementing `BaseTool.schema()` for MCP:

- `WebSearchTool` — Serper/Tavily/SerpAPI with mock fallback
- `FileSystemTool` — Sandboxed read/write with path traversal protection
- `CodeExecutorTool` — Subprocess Python/bash with timeout
- `NotificationTool` — Slack/Discord/log unified notifications
- `DatabaseTool` — SQLite/Postgres query execution

---

## Lifecycle State Machine

```
        ┌─────┐
        │IDLE │◄────────────────────────────┐
        └──┬──┘                             │
           │ dispatch()                     │ success / release
           ▼                                │
       ┌─────────┐  3+ errors    ┌──────────┴─────┐
       │ RUNNING ├──────────────►│  QUARANTINED   │
       └────┬────┘               └────────────────┘
            │ kill()
            ▼
       ┌─────────┐
       │ STOPPED │
       └────┬────┘
            │ restart()
            └──────────► IDLE
```

---

## Security Model

1. **Zero CVE policy** — `pip-audit` runs on every CI push
2. **Secret management** — all credentials via environment variables, no hardcoding
3. **PII detection** — scans all data before memory storage
4. **Capability whitelist** — bots declare allowed tools; violations raise `PermissionError`
5. **Sandbox execution** — tool calls wrapped in async timeout sandbox
6. **Audit log** — tamper-evident append-only log of all governance events
7. **Rate limiting** — per-bot sliding-window API call limits

---

## Deployment Architecture

```
                    ┌──────────────────────────────┐
                    │      Load Balancer / Ingress   │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────┼───────────────┐
                    ▼              ▼               ▼
              ┌──────────┐  ┌──────────┐  ┌──────────┐
              │DreamCo   │  │DreamCo   │  │DreamCo   │
              │OS Pod 1  │  │OS Pod 2  │  │OS Pod N  │
              └─────┬────┘  └────┬─────┘  └────┬─────┘
                    └────────────┼──────────────┘
                                 │
              ┌──────────────────┼────────────────────┐
              ▼                  ▼                     ▼
        ┌───────────┐    ┌──────────────┐     ┌──────────────┐
        │   Redis   │    │  Postgres    │     │  Chroma /    │
        │  Cluster  │    │  (Neon/RDS)  │     │  Pinecone    │
        └───────────┘    └──────────────┘     └──────────────┘
```

---

## ADRs (Architecture Decision Records)

| # | Decision | Status |
|---|----------|--------|
| ADR-001 | Use asyncio throughout — no synchronous blocking I/O | ✅ Accepted |
| ADR-002 | Four-tier memory architecture | ✅ Accepted |
| ADR-003 | MCP protocol for external interoperability | ✅ Accepted |
| ADR-004 | Chroma for local dev, Pinecone for production vector DB | ✅ Accepted |
| ADR-005 | SQLite for local dev, Postgres for production | ✅ Accepted |
| ADR-006 | Policy-as-code governance (no hardcoded rules) | ✅ Accepted |
| ADR-007 | Backwards-compatible `PythonBotOrchestrator` alias | ✅ Accepted |
| ADR-008 | In-process fallbacks for all external services | ✅ Accepted |

---

*Last updated: May 2026*
