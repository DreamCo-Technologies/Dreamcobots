# DreamCo Clean-Room Reverse-Engineering Engine

## Pipeline
1. Permission-aware intake; no URL fetching or crawling.
2. Explicit authorization, license screening and heuristic secret/PII redaction.
3. Deterministic Python AST and optional Tree-sitter parsing for JavaScript, TypeScript, Java, Go and Rust; OpenAPI JSON, HAR, CSV and JSON metadata parsing.
4. Source-minimized functional blueprint.
5. Original scaffold generation from blueprint only.
6. Owner-approved fixture comparison, isolated sandbox execution, similarity and license review.

## Allowed targets
User-owned code, public APIs, open-source repositories within their license, authorized HTTP logs, schemas and workflow descriptions. Public availability does not grant permission to copy or train on content. Open-source intake requires an explicit SPDX identifier from the configured permissive allowlist.

## Prohibited
DRM/paywall/authentication bypass, token harvesting, unauthorized login-wall scraping, exploit development, proprietary binary decompilation and access-control circumvention.

## Data minimization
Secrets and common PII patterns are redacted before parsing. HAR headers, cookies, query values and bodies are discarded. Data parsers emit schema statistics only. Blueprints do not contain source text. Training-data persistence is disabled; separate opt-in and rights review would be required.

Redaction is heuristic, not a guarantee. Reject or manually review high-risk inputs. Do not store original uploads by default.

## Verification truth
Fixture equality covers only supplied examples. Token similarity is triage, not legal originality proof. Generated code must run in a disposable, network-disabled sandbox with resource limits and no secrets. The current O*NET mapping is a low-confidence task-family placeholder; exact codes require a licensed/current dataset and human review.

## Deliberate limitations
Tree-sitter adapters use the optional tree-sitter-language-pack dependency; install requirements-reverse-engineer.txt to enable them. OpenAPI YAML, DuckDB/Polars, Docker orchestration and license-database integration are not yet implemented; unsupported inputs fail closed. No paid APIs or training run in CI.

## Tests
Run: python -m pip install 'pytest>=8,<10' && python -m pytest tests/test_reverse_engineer.py -q
