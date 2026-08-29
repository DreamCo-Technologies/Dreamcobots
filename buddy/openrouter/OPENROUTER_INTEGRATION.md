# OpenRouter Integration

OpenRouter is a **supplemental** model gateway for Buddy and DreamCo clients. It does not replace or delete the existing DreamCo model catalog.

## Current OpenRouter capabilities

OpenRouter provides a unified OpenAI-compatible API, model routing, provider routing, provider failover, optional cross-model fallbacks, and an Auto Router. Current OpenRouter information should be treated as dynamic; Buddy should discover the live `/api/v1/models` catalog rather than hard-code a permanent list.

## DreamCo routing policy

```text
Client -> DreamCo Gateway -> Buddy Policy ->
  1. Existing DreamCo catalog
  2. OpenRouter supplemental pool
  3. DreamCo bot specialist
  4. Buddy-native capability
  5. validated fallback
```

Buddy should prefer a Buddy-native capability when its evidence meets the required quality threshold. Otherwise it can use the protected DreamCo fleet, OpenRouter, or a specialist bot according to task, cost, latency, safety, privacy, and reliability policy.

## OpenRouter integration requirements

- Keep `OPENROUTER_API_KEY` server-side.
- Discover models dynamically through OpenRouter's models endpoint.
- Cache metadata with a timestamp and refresh it regularly.
- Never mutate the protected DreamCo model catalog from OpenRouter discovery.
- Tag discovered entries as `source: openrouter`.
- Benchmark OpenRouter candidates using the existing DreamCo benchmark framework before promoting them into preferred routes.
- Use provider controls for privacy/compliance requirements.
- Use provider failover and explicit model fallbacks for resilience where policy allows.
- Record actual model/provider results so Buddy can learn which routes work best.

## Client access

Expose stable DreamCo aliases instead of requiring clients to know provider-specific model IDs:

- `dreamco/auto`
- `dreamco/coding`
- `dreamco/reasoning`
- `dreamco/fast`
- `dreamco/vision`
- `dreamco/budget`

Clients may be entitled to specific approved models, but shared provider credentials must never be exposed to clients.

## Self-sufficiency objective

OpenRouter is a teacher/specialist/fallback pool. Successful solutions can become evidence for Buddy's capability mastery system. Buddy should progressively reduce unnecessary external calls while retaining the protected DreamCo fleet, unique specialists, and resilience reserves.
