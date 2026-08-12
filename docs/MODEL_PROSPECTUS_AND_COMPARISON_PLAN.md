# Public Model Prospectus + Capability Comparison

## Goal

Create a public directory for the benchmarked model set. Every model entry should be clickable and lead to a prospectus containing verified public information plus transparent benchmark evidence.

## Model prospectus

Each model page should answer:

1. What is it?
2. Who publishes or maintains it?
3. What license or usage terms apply?
4. Where are official weights, documentation, APIs, or repositories available?
5. What modalities and tool capabilities are publicly documented?
6. What tasks is it particularly useful for?
7. What limitations or weak areas are documented or demonstrated by evidence?
8. What hosting/integration options exist?
9. What is the latest verified version/date?
10. How does Buddy compare on the measured tasks?

## Capability testing

Do not benchmark only a model's headline capability. For each model, map applicable tasks into categories such as:

- reasoning;
- coding and debugging;
- mathematics;
- science;
- research;
- writing and editing;
- summarization;
- instruction following;
- long-context work;
- multilingual work;
- vision;
- audio/speech;
- video where applicable;
- tool use;
- agent workflows;
- structured output;
- creative generation;
- business workflows;
- education;
- data analysis;
- software engineering;
- security reasoning;
- planning;
- multimodal understanding.

A model does not need every category to be applicable. `not_applicable` is preferable to an invented score.

## Reference-model quality testing

For each task category, select strong reference models that are genuinely appropriate for that task. Run comparable fixtures and rubrics whenever access, licensing, modality, version, and evaluation conditions permit.

The benchmark result should include:

- Buddy quality score;
- reference quality score;
- absolute gap;
- relative gap where meaningful;
- latency;
- throughput;
- efficiency;
- reliability;
- safety;
- independence state;
- sample size and uncertainty when available;
- evaluation conditions;
- evidence references.

## Important interpretation rule

A model leaderboard is not a claim that one model is universally better. Results are category- and task-specific.

Likewise, connecting Buddy to a frontier model can demonstrate that Buddy can orchestrate that capability, but it does not demonstrate that Buddy itself has independently learned the capability.

## Public Pages experience

The public dashboard should provide:

```text
MODEL DIRECTORY
  ↓
[Model A] [Model B] [Model C] ...
  ↓ click
MODEL PROSPECTUS
  ├── Overview
  ├── License / public-use terms
  ├── Modalities
  ├── Strengths
  ├── Limitations
  ├── Best-fit tasks
  ├── Benchmark results
  ├── Buddy gap
  ├── Speed
  ├── Efficiency
  ├── Reliability
  ├── Independence
  └── Sources / last verified
```

Then a category can show:

```text
CODING

Reference leader      ██████████
Buddy                 ████████░░
Gap                   12%  [measured]
Latency               measured
Efficiency            measured
Quality               measured
Reliability           measured
```

The displayed values must come from the evidence ledger. Placeholder or illustrative numbers must never be presented as actual benchmark results.

## Refresh and stale-data handling

Model versions, licenses, pricing, APIs, weights and capabilities change. Every prospectus therefore carries a verification timestamp. Changed model versions invalidate affected comparisons until rerun.

## Public/commercial boundary

The prospectus may explain publicly available service information and use cases. It must not scrape or publish private information, expose credentials, bypass access restrictions, or imply endorsement by a provider.
