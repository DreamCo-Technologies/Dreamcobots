# DreamCo Institute Competitive Model Laboratory

## Purpose and status

The Competitive Model Laboratory compares a specific, evidence-backed DreamCo division model with exact, rights-reviewed public baseline artifacts on the same task-specific fixtures.

It is an evaluation system, not a training job, model downloader, deployment system, public leaderboard, or proof that DreamCo currently outperforms another model. The canonical 45,038,208-parameter architecture is a blueprint until a trained checkpoint, release-candidate manifest, and reproducible run evidence exist.

DreamCo's academic catalog maps 55 domain divisions. The operational registry separately contains 65 MasterBots, including shared-platform lanes. Do not assume those counts are interchangeable. Each benchmark candidate must use the exact division identifier recorded in its release-candidate manifest and fixture set.

## What is measured

For each model and division-specific fixture set, the runner measures:

- **Contract pass rate:** valid top-level output shape, allowed workforce route, and fixture-defined JSON Schema subset.
- **Task exact-match rate:** exact equality between the model's result object and the independently held expected result.
- **Routing accuracy:** exact match for `human_only`, `human_ai`, `robot`, or `full_ai`.
- **Deterministic repeat rate:** identical output for repeated byte-equivalent requests.
- **Adapter round-trip p50/p95:** elapsed time from launching the local adapter process through its response. Process startup is included, so this is not pure warmed model-token latency.
- **Failure and timeout rates:** all failed calls remain in the denominator.
- **Development and private-holdout metrics:** reported separately.

Memory, energy per token, accuracy-per-watt and cost per million tokens are deliberately null until calibrated measurement adapters and attributable cost records are available. The 15 ms, 99.9%, and 95% figures in the policy are aspirational targets, not achieved results or automatic release gates.

## Fixture contract

Fixtures are original DreamCo-authored cases or separately rights-cleared evaluation material. A fixture file uses schema `dreamco.competitive_benchmark_fixtures.v1` and includes:

- provenance with `rights_status` set to `DREAMCO_ORIGINAL` or `APPROVED_FOR_EVALUATION`, plus an evidence reference;
- a division ID and unique case IDs;
- both `development` and `private_holdout` splits;
- an input object, expected result object, expected workforce route, and object output schema for each case.

Do not train on private holdouts. The evaluator never includes expected results in adapter requests and omits raw fixture contents from the output report.

## Adapter protocol

A local adapter is an executable argument array, not a shell command. For each request it receives one JSON object on stdin with the case ID, division ID, task ID, input, output schema, model ID/version, the pinned checkpoint path and the exact tokenizer artifact path.

It must write one JSON object to stdout:

```json
{
  "result": {
    "decision": "example"
  },
  "route": "human_ai"
}
```

The `result` object is checked against the fixture's schema and exact expected value. Extra top-level fields are rejected. Adapter stderr is captured and not published as benchmark evidence.

The adapter must load the artifact path supplied in the request. An adapter that ignores the artifact is not a valid model adapter and must be rejected in review.

The runner itself does not train, download, modify or deploy models and does not initiate network calls. Adapter commands are arbitrary local executables and could independently access a network or paid provider. Inspect each adapter, require explicit authorization for any such use, and use an OS-level network-isolated runner when network access must be prohibited. The report marks adapter network and paid-compute usage as unmeasured rather than claiming they did not occur.

## Candidate requirements

The candidate input is a repository-generated `dreamco.model_release_candidate.v1` manifest produced by the existing Model Foundry release-candidate builder. The runner also requires the actual checkpoint file, the exact tokenizer artifact whose hash is recorded in the candidate manifest, and a local adapter command.

Before evaluation it checks:
- exact division identity and 45,038,208 parameter count;
- checkpoint SHA-256 against release-candidate evidence;
- architecture and tokenizer hashes;
- random initialization and a training run ID;
- training and commercial-use permissions;
- a passed independent pre-release evaluation.

This does not confer a degree, certify production readiness, or authorize public distribution.

## Public baseline admission

The baseline registry intentionally starts empty. To add a public model, first pin its exact repository ID and immutable revision, obtain the model artifact locally, verify its hash, review the applicable license and repository terms, record a license-review reference, store hash-verified local license/permission evidence, and confirm benchmark execution is permitted. Pin the immutable 40-character model commit SHA. Then add its adapter command and artifact record to `config/institute-competitive-baselines.json`.

A model's presence on a public model hub is not by itself permission to download, benchmark, train on, redistribute, or commercially use it. Do not substitute a different model revision when a baseline is unavailable.

## Running one division comparison

After a candidate, checkpoint, original/authorized fixture set, reviewed baseline registry and local adapters exist:

```bash
python scripts/benchmark_vs_baselines.py \
  --candidate-manifest /path/to/release-candidate.json \
  --candidate-checkpoint /path/to/model.safetensors \
  --candidate-tokenizer /path/to/tokenizer.json \
  --candidate-command '["python","/path/to/dreamco_adapter.py"]' \
  --baseline-registry config/institute-competitive-baselines.json \
  --fixtures /path/to/division-fixtures.json \
  --division-id DreamCyber \
  --repeats 3 \
  --timeout 10 \
  --output /path/to/reports/dreamcyber-head-to-head.json
```

Use the exact division ID from the candidate manifest and fixture set. Run each eligible division independently or through an explicitly bounded orchestration job. Missing candidates, fixtures, artifacts, rights reviews or adapters mean **blocked**, not zero-score and not passed.

## Fleet orchestration

The 65-MasterBot fleet wrapper is `tools/run_institute_fleet_benchmarks.py`. It reads the canonical `config/masterbot-65-registry.json` and looks for each model's release candidate, adapter manifest and division fixture set under owner-controlled local directories. The default roots are outside the Git checkout: `$HOME/DreamCo-models/release-candidates`, `$HOME/DreamCo-model-adapters` and `$HOME/DreamCo-benchmark-fixtures`. Missing artifacts and baseline permissions are reported as `BLOCKED`; the wrapper never fabricates a score. It runs sequentially by default and accepts `--max-candidates` to bound work. Use `npm run institute:fleet-benchmark -- --max-candidates 1` for a bounded first attempt once local artifacts exist. A full-fleet report is not a training result and does not certify the 55 academic divisions or 65 MasterBots as mastered.

## Future extensions

Only after the local adapter protocol is proven should the Institute add:
1. persistent warm-server adapters for pure inference latency and throughput;
2. calibrated peak-memory and energy measurement on named hardware;
3. token-normalized cost accounting;
4. additional public suites such as code execution, mathematical reasoning and instruction following, after their own contamination, license, terms and split reviews;
5. signed benchmark reports and an append-only, versioned leaderboard.

A leaderboard entry must identify the model revision, checkpoint hash, tokenizer hash, fixture hash, hardware, runtime, quantization, adapter revision, repetitions and evaluator revision. No benchmark score should be presented without that complete context.
