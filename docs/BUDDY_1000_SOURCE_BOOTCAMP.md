# Buddy 1,000-Source Learning + Bootcamp System

## Objective

Turn an authorized 1,000-source knowledge network into a continuous capability-acquisition system for Buddy and the DreamCo bot fleet. Sources are study guides and evidence, not runtime dependencies and not a license to copy restricted material.

## Source intelligence

Buddy maintains a score for every source using authority, benchmark relevance, freshness, active capability gap coverage, transfer value, and cost efficiency. Primary/official sources win over summaries when they are available and authorized. Duplicate, stale, low-authority, restricted, or rights-uncertain sources are deprioritized or blocked.

## What happens to each useful source

1. Identify changed content rather than re-reading the whole source.
2. Hash and deduplicate the content.
3. Extract capabilities, procedures, failure modes, evaluation methods, and provenance.
4. Map those signals to one or more benchmark tasks and DreamCo capabilities.
5. Generate an original DreamCo lesson rather than copying the source.
6. Generate sandbox exercises at increasing difficulty.
7. Train the smallest sufficient model/bot first.
8. Run independent holdout tests.
9. Promote only evidence-backed improvements.
10. Store the lesson, task, failure mode, result, cost, model, and provenance in the Bootcamp record.
11. Regression-test previously mastered capabilities.

## Learning acceleration

Buddy should not train every bot independently when the skill is shared. A capability package is learned once, validated, and then propagated to compatible bots through the capability registry. Bots receive only the minimum package required for their role.

### Compute-saving rules

- Deterministic code before model inference.
- Local/open models before paid APIs when quality is sufficient.
- Cached source and benchmark representations before refetching/re-embedding.
- Batch similar tasks.
- Reuse validated trajectories as training examples where licensing permits.
- Stop early when a capability reaches its mastery threshold.
- Stop repeating identical failures unless a new strategy is introduced.
- Use expensive reasoning only when the expected information gain justifies the cost.
- Keep independent holdout tasks hidden from training data.

## Daily operating cadence

### Continuous

Monitor source changes, benchmark releases, regressions, tool failures, and active capability gaps.

### Daily

Scan the 1,000-source target using differential retrieval; prioritize changed/high-value sources; convert new evidence into bootcamp lessons; run adaptive benchmark samples; update the mastery graph.

### Weekly

Run deeper cross-domain regression and long-horizon evaluations; rotate holdout tasks; identify capabilities that are improving too slowly.

### Monthly

Rebalance source weights, remove stale/low-value sources, audit provenance and rights metadata, and publish an evidence-based mastery report.

## Benchmark learning strategy

Buddy should use benchmark documentation and public methodology as study material, but should not train on protected test answers or leak benchmark solutions into evaluation sets. Benchmark-specific results must be independently reproducible. SWE-bench Verified, for example, is a curated 500-task set, while the SWE-bench project also provides broader and multimodal variants; its evaluation harness uses containerized environments for reproducibility. BrowseComp contains 1,266 difficult browsing problems and emphasizes persistence and creative search. METR's HCAST provides human-calibrated autonomy tasks with human completion times, making it useful for measuring long-horizon capability rather than simple answer accuracy.

## Mastery gate

A capability cannot be labeled `mastered` merely because a lesson was read or a benchmark was attempted. It requires:

- repeated successful practice;
- an independent holdout/transfer success;
- no critical regression in related capabilities;
- recorded provenance and evaluation evidence;
- acceptable cost/latency for the intended deployment tier.

## Goal

The system should become better by learning *how to learn*: select the best source, extract the transferable skill, practice cheaply, test independently, retain only measured improvements, and continuously search for the next highest-value capability gap.
