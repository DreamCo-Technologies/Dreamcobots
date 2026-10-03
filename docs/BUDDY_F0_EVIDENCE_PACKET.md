# Buddy F0 Evidence Packet (methodology stub)

Truth boundary: F0 is a baseline, not a capability claim. No frontier, `production_ready`, or `live_benchmark_ok` from any F0 packet.

## What F0 means
A pinned run of `buddy-frontier-core-2026-q4` (`config/frontier-evidence-suite.json`) by a named subject, with cost, latency, and external assistance logged, and artifacts stored under `evidence/frontier/`. Beating or matching peers is F1+.

## How to fill a packet
1. Pin suite_id + suite_hash, fixture_hash, grader_version, sandbox image digest.
2. Name the subject exactly (kind, name, version, checkpoint/commit) and list every external assist model ID.
3. Log pass/fail/timeout/refusal counts, latency_ms, cost_usd, safety_passed, regression_passed, and an assist label. Keep failures visible.
4. Link trace, raw results, and methodology; add sha256 integrity hashes.
5. Fill provenance per `config/evidence_provenance_schema.json`.
6. Validate against `schemas/buddy-f0-evidence-packet.schema.json`.
7. Sign (agent_attestation, then human_countersign if required), then add to `config/buddy/f0-scorecard-index.json`.

## f0_pass
True only when all required fields are present, artifacts exist, and repetitions meet the suite minimum (3). Otherwise the packet stays a logged stub with f0_pass=false.
