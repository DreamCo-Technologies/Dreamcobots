# Buddy in-house capability certification

## Goal
Reach 100 independently verified capabilities, 25 production-certified specialists,
10 working Bootcamp courses, three commercial products, and one with a paying
customer by 2027-10-22. These are targets, not current accomplishments.

## Capability lab
The engine reads `config/buddy/capability-certification-goals.json`, validates
unique capability IDs, and creates a versioned evidence report. It is deliberately
fail-closed: an inventory entry is `unverified`. An explicitly allowed local
`unittest` can only move it to `tested`, never `verified` or `production`.

### Run locally
```bash
python -m unittest tests.test_buddy_capability_certification -v
python -m buddy.certification.engine
```
The generated JSON is written to `website/data/buddy-capability-certification.json`.
The GitHub Actions workflow produces an artifact on scheduled and manual runs.
It does not commit artifacts or automatically deploy to Pages.

## Evidence required for independent verification
- Named capability and exact source revision, dependency lock and runtime environment.
- Executable functional tests, held-out independent task suite and repeated runs.
- Measured correctness, safety, latency, cost, reliability, failure modes and regressions.
- Native Buddy vs externally assisted result labels.
- Signed/reviewed receipts with test input hashes, artifact locations and timestamps.
- Human review for high-impact domains; explicit consent and license checks.
- Production additionally requires real integration smoke tests, security, observability,
  release checks and tested rollback.

## Expansion lanes
1. Security: authorization, isolation, data rights, secrets, audit.
2. Core Buddy: chat, orchestration, memory, tools, retries, approvals.
3. Coding: repository understanding, edits, builds, tests, upgrades, debugging.
4. Learning: source provenance, course synthesis, study, exams, retention.
5. AI: model selection, fine-tuning, tokenizer, training, evaluation, rollback.
6. Devices: Wi-Fi/Bluetooth permissions, pairing, adapter action receipts.
7. Creative: text, images, audio, video, games and licensing.
8. Business: leads, invoices, subscriptions, fulfillment and accounting.
9. Data: connectors, datasets, analytics, privacy and lineage.
10. Platform: Pages, CI, releases, telemetry, backups and mobile usability.

## Publication and truth
A GitHub Pages static site cannot execute backend certification or read private
artifacts on its own. Publishing current reports requires an explicit integration
with the existing Pages publisher. Never label missing evidence as success.
