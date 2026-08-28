# Buddy OpenRouter + Model Mastery

OpenRouter is a gateway layer for Buddy, not a replacement for DreamCo's existing model catalog.

## Goals

1. Give Buddy access to OpenRouter's current model/provider network.
2. Let DreamCo clients use approved OpenRouter models alongside the existing DreamCo model catalog.
3. Keep tenant isolation, quotas, privacy policy, and approved-provider controls in DreamCo.
4. Continuously benchmark models on real, consented tasks.
5. Reduce the number of models Buddy depends on over time by promoting models that repeatedly meet quality, latency, cost, safety, and tool-use targets.

OpenRouter currently advertises 500+ models and 80+ providers, with provider routing and model fallback support. OpenRouter also supports provider controls such as data-collection restrictions and ZDR where available.

## Architecture

```text
Client
  -> DreamCo API / Buddy Gateway
       -> Policy + tenant entitlement
       -> Task classifier
       -> DreamCo 500+ model catalog
       -> OpenRouter gateway
            -> model selection
            -> provider routing
            -> provider failover
            -> model fallback
       -> Validator / evaluator
       -> Mastery ledger
       -> Learning + consolidation
```

## Model reduction strategy

Buddy does **not** learn by blindly deleting models. It learns by evidence:

- Maintain a benchmark set per task family.
- Record quality, correctness, latency, cost, refusal/error rate, tool success and client satisfaction.
- Compare models on the same tasks.
- Promote stable winners to the preferred pool.
- Mark consistently redundant models as candidates for retirement.
- Keep a small reserve for rare capabilities and regression testing.
- Require a minimum sample size and a statistically meaningful margin before retirement.
- Never remove the last model capable of a required modality or safety constraint.

The result is a smaller, stronger model fleet rather than a hard-coded dependency on one vendor.

## Client access

Clients should call DreamCo's gateway rather than receiving a shared OpenRouter secret. DreamCo can expose an approved model catalog, usage limits, BYOK support where appropriate, and per-tenant policies. Client-facing model IDs should be stable DreamCo aliases so the underlying provider/model can change without breaking client applications.

Example aliases:

- `dreamco/auto`
- `dreamco/coding`
- `dreamco/reasoning`
- `dreamco/fast`
- `dreamco/vision`
- `dreamco/budget`

A client may request a specific approved model when entitled, but `dreamco/auto` should normally be the default.

## Security

Never commit `OPENROUTER_API_KEY`. Keep provider credentials server-side. Apply DreamCo policy before routing, and use OpenRouter provider controls to restrict data collection and providers for sensitive workloads.
