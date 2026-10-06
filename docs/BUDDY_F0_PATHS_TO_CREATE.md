# F0 Scorecard — files to create (proposed)

Repo: DreamCo-Technologies/Dreamcobots
Owner: Grok-Buddy-F0-Scorecard
Truth: drafts only; no frontier claim; no production_ready flip.

## Create

1. `schemas/buddy-f0-evidence-packet.schema.json` — JSON Schema for signed F0 packets
2. `config/buddy/f0-peer-baselines.json` — designated peers from open-model lab + Path D seeds + 500-registry contract
3. `docs/BUDDY_F0_EVIDENCE_PACKET.md` — human methodology stub (how to fill/sign F0)
4. `evidence/frontier/f0/README.md` — packet layout + honesty rules
5. `evidence/frontier/f0/packets/.gitkeep` — store signed `f0-*.json` packets here
6. `evidence/frontier/f0/scorecards/.gitkeep` — human-readable scorecard renders per run
7. `config/buddy/f0-scorecard-index.json` — index of packet_ids, suite_hash, f0_pass, signed_at (empty array initially)

## Already exist (do not replace; extend)

- `evidence/frontier/current-status.bundle.json` — empty runs (honest)
- `evidence/frontier/current-status.assessment.json` — claimable=false
- `config/frontier-evidence-suite.json` — suite_id buddy-frontier-core-2026-q4
- `config/evidence_provenance_schema.json`
- `config/buddy-benchmark-scorecard.json`
- `config/buddy-frontier-readiness-gates.json` (never_claim_frontier_without_evidence)
- `reports/BUDDY_FRONTIER_MODEL_AND_PACKAGES.md` §2.2 F0–F4 floors
- `config/buddy/500-model-registry.json`
- `config/buddy-open-model-coding-lab.json` (frontier_references + model_families)

## F0 pass condition (canonical)

Pinned suite run; cost/latency/external-assist logged; artifacts under `evidence/frontier/`.
Peer beat/match = F1+, not F0.
