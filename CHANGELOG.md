# Changelog

All notable changes to DreamCo OS are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Added
- Full investor-readiness upgrade (200 actionable improvements)

---

## [2.0.0] — 2026-05-24

### 🔴 Security
- **FIXED** flask-cors CVEs (CVE-2024-1681, CVE-2024-6844, CVE-2024-6866) — upgraded to 6.0.2
- **ADDED** `pip-audit` to CI pipeline — fails build on any known CVE
- **ADDED** `SECURITY.md` vulnerability disclosure policy
- **ADDED** `CODEOWNERS` file — every directory has a mandatory reviewer
- **ADDED** PII detection layer (`python_bots/governance/pii_detector.py`)
- **PINNED** all dependency versions in `requirements.txt` (exact pins, not `>=`)

### 🏗️ Architecture
- **ADDED** `python_bots/core/base_bot.py` — full `DreamCoBot` base class
  - Lifecycle state machine: `IDLE → RUNNING → QUARANTINED/STOPPED`
  - 4 canonical methods: `run()`, `analyze()`, `monetize()`, `report()`
  - Async-first execution with `asyncio`
  - Auto-registration with orchestrator
  - `health_check()` JSON status endpoint
  - Capability whitelist enforcement
- **ADDED** `python_bots/core/lifecycle.py` — `BotState` enum + transition validation
- **UPGRADED** `python_bots/orchestrator.py` → `DreamCoOrchestrator`
  - Event-driven asyncio.Queue-based architecture
  - DAG-based parallel task scheduling
  - Circuit breaker pattern (auto-quarantine after N failures)
  - Kill switch: `orchestrator.kill(bot_name)`
  - Dead-letter queue for failed tasks
  - Human-in-the-loop approval gates
  - Priority queue with preemption
  - Broadcast to all registered bots
  - Retry with exponential backoff
  - Backwards-compatible `PythonBotOrchestrator` alias

### 🧠 Memory Layer
- **ADDED** `python_bots/core/memory/` — four-tier memory system
  - `ShortTermMemory` — Redis-backed, 24h TTL, in-process fallback
  - `LongTermMemory` — Chroma/Pinecone vector DB, semantic recall
  - `StructuredMemory` — SQLite/Postgres relational state + run history
  - `BehavioralMemory` — event graph tracking decisions over time
  - `MemoryClient` — unified façade for all four tiers
  - `memory.forget(key)` — GDPR-compliant deletion across all tiers
  - Cross-session continuity via `load_last_session()` / `save_session()`

### 🔒 Governance
- **ADDED** `python_bots/governance/` — full governance layer
  - `PolicyRegistry` + `BotPolicy` — JSON/YAML configurable policies
  - `Sandbox` — async execution wrapper with timeout + capability checks
  - `QuarantineManager` — operator-controlled bot quarantine
  - `GovernanceAuditLog` — file-backed append-only audit trail
  - `RateLimiter` — sliding-window per-bot rate limiting
  - `PIIDetector` — regex-based PII detection + scrubbing

### 🤖 AI Model Router
- **ADDED** `python_bots/core/model_router.py`
  - Routes to OpenAI, Anthropic, Google, local models
  - Cost-aware selection, automatic fallback chain
  - Response caching (SHA-256 hash, 1h TTL)
  - Token budget enforcement
  - Streaming support

### 🌐 MCP & Interoperability
- **ADDED** `dreamco_mcp_server.py` — 10 MCP tools registered
- **ADDED** `dreamco_sdk/` — Python client library
  - `DreamCoClient` async HTTP client
  - Pydantic models: `BotResult`, `BotStatus`, `RunRequest`

### 🔧 Tools Library
- **ADDED** `python_bots/tools/` — shared tool library
  - `WebSearchTool` — Serper/Tavily/SerpAPI + mock fallback
  - `FileSystemTool` — sandboxed read/write, path traversal protection
  - `CodeExecutorTool` — subprocess Python/bash with timeout
  - `NotificationTool` — Slack/Discord/log unified notifications
  - `DatabaseTool` — SQLite/Postgres SQL execution
  - `BaseTool` ABC with `schema()` for MCP registration

### 💻 Coding Agents
- **ADDED** `bots/coding/pr_review_agent.py` — AI PR reviews via Claude/GPT
- **ADDED** `bots/coding/ci_governance_agent.py` — CI failure monitoring + diagnosis
- **ADDED** `bots/coding/dependency_updater.py` — CVE-aware dependency auditor
- **ADDED** `bots/coding/code_graph_agent.py` — repo knowledge graph builder
- **ADDED** `bots/coding/documentation_agent.py` — doc gap analysis

### 📁 Repository Structure
- **ADDED** `ARCHITECTURE.md` — full system design documentation
- **ADDED** `ROADMAP.md` — 6/12/24-month product roadmap
- **ADDED** `METRICS.md` — platform metrics dashboard
- **ADDED** `CHANGELOG.md` — this file
- **ADDED** `SECURITY.md` — vulnerability disclosure policy
- **ADDED** `FAQ.md` — investor/developer FAQ
- **ADDED** `docs/investor-brief.md` — investor one-pager
- **ADDED** `docs/DreamCoOS.md` — platform concept documentation
- **ADDED** `pyproject.toml` — modern Python build configuration
- **ADDED** `Makefile` — developer workflow automation
- **ADDED** `demo/` — 3 runnable platform demos
- **ADDED** `system_prompts/` — versioned system prompts per bot role
- **UPDATED** `README.md` — complete rewrite as platform documentation
- **UPDATED** `.github/dependabot.yml` — grouped updates, weekly schedule
- **ADDED** `.github/CODEOWNERS` — mandatory code ownership
- **REPLACED** 12 scattered workflows → 1 unified `main.yml`

### 🐳 Deployment
- **ADDED** `docker-compose.prod.yml` — production configuration
- **ADDED** `k8s/` — Kubernetes manifests (deployment, service, HPA, configmap)

### 🧪 Testing
- **ADDED** `tests/unit/` — unit tests for core components
- **ADDED** `tests/integration/` — orchestrator + memory integration tests
- **ADDED** `tests/e2e/` — end-to-end bot execution tests
- **ADDED** `pytest-asyncio` for async test support

### 📦 Dependencies
- **PINNED** all dependencies to exact versions
- **ADDED** `redis==5.2.1`, `chromadb==0.5.23`, `structlog==24.4.0`
- **ADDED** `opentelemetry-api==1.34.0`, `opentelemetry-sdk==1.34.0`
- **ADDED** `pytest-asyncio==0.25.3`, `pydantic==2.11.5`
- **ADDED** `uvicorn==0.34.3`, `prometheus-client==0.21.1`

---

## [1.0.0] — 2026-01-01

### Added
- Initial 500+ bot collection
- `dreamco_platform/` — platform foundation (governance, memory, orchestration, observability)
- `bots/dreamco_payments/` — Stripe integration
- `python_bots/base_bot.py` — minimal `BaseBot` ABC
- Basic CI workflows
- Bot library manager with 281 registered bots

---

[Unreleased]: https://github.com/DreamCo-Technologies/Dreamcobots/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/DreamCo-Technologies/Dreamcobots/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/DreamCo-Technologies/Dreamcobots/releases/tag/v1.0.0
