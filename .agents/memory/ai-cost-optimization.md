---
name: AI cost optimization
description: Cost-control constants, caching pattern, and history trimming used across all Buddy routes in routes.ts
---

## Constants (top of routes.ts, module level)
- `CHEAP_MODEL = "gpt-4o-mini"` — default for all non-streaming routes ($0.15/1M in, $0.60/1M out)
- `CHAT_MODEL = "gpt-4.1-mini"` — used for the streaming chat route only
- `MAX_HISTORY_MSG = 16` — conversation history trim limit
- `MAX_CHAT_TOKENS = 2000` — max_completion_tokens for streaming chat
- `CACHE_TTL_MS = 5 * 60 * 1000` — 5-minute TTL for result cache

## Cache helpers (module level, before registerRoutes)
```ts
const _cache = new Map<string, { result: unknown; expiresAt: number }>();
function cacheKey(...parts: unknown[]): string  // hash of inputs, max 512 chars
function fromCache<T>(key: string): T | null    // returns null on miss or expiry
function toCache(key: string, result: unknown): void  // evicts oldest 100 when >500 entries
```

## trimHistory pattern (stream route)
```ts
const historyMsgs = history.map(m => ({ role: m.role, content: m.content }));
const trimmedHistory = trimHistory(historyMsgs); // keeps first + last (max-1)
```

## Routes with caching applied
security-scan, architect, translate-code, code-review, generate-pr, deploy-config, debug-deep, refactor

## Key insight
- gpt-4o-mini DOES support vision/image_url inputs — use it instead of gpt-4o for image analysis (33× cheaper)
- History trimming is the biggest single savings for long conversations
- Cache hits save 100% — identical requests for scan/review/architect return instantly

**Why:** The system has 1,051 bots all using the same OpenAI integration; unbounded history + expensive models would balloon costs fast. All savings compound across every user session.

**How to apply:** When adding a new expensive Buddy route, always: (1) use CHEAP_MODEL, (2) add cache lookup before the API call, (3) call toCache after success, (4) keep max_tokens ≤ 2500.
