# DreamCo Five-Stage Clean-Room Pipeline

## Local setup

    python -m pip install -r requirements-reverse-engineer.txt
    make test-all

## Stage contracts and CLI

Every stage reads one JSON contract and writes one JSON contract. Contract schemas are in \`contracts/\`.

1. **Stage 1 — Policy gate**

       python -m stages.01_policy_gate --input raw_upload.json --output artifact_manifest.json

2. **Stage 2 — Deterministic parser**

       python -m stages.02_intake_parser --input artifact_manifest.json --output parsed_facts.json

3. **Stage 3 — Functional spec and O*NET**

       python -m stages.03_spec_and_onet --input parsed_facts.json --output functional_spec.json

   Add \`--onet-db /path/to/authorized-onet.sqlite --task-description "owner-authored task description"\` to query a local read-only SQLite table named \`onet_tasks(soc_code, task_id, task)\`.

4. **Stage 4 — Clean-room generator**

       python -m stages.04_clean_room_gen --input functional_spec.json --output course_module.json --mock

   Mock generation is the only enabled mode. A live model adapter is intentionally not enabled.

5. **Stage 5 — Sandbox verifier**

       make build-sandbox
       python -m stages.05_sandbox_verifier --input course_module.json --output eval_report.json --reference /path/to/owner-authorized-reference.txt

   Run a rootless Docker daemon and provide an independently authorized comparison reference. Similarity is heuristic triage, not legal proof.

## Stage boundaries

- Stage 1 requires explicit authorization, applies heuristic secret/PII/entropy redaction, checks a 5 MiB text limit and bounded ZIP metadata, and rejects restricted URLs/private IP targets. Redaction is not a guarantee; manually review high-risk material.
- Stage 2 uses Python AST and optional Tree-sitter for JavaScript, TypeScript, Java, Go and Rust, plus JSON, OpenAPI JSON, HAR and CSV. It never imports or executes uploaded code. OpenAPI facts include parameter counts, request/response content types, response codes, security flags and rate-limit extension names. HAR facts retain header names and body-size/presence metadata but discard header values, query values and bodies. CSV facts include inferred types, null counts and candidate unique keys.
- Stage 3 replaces source function and field identifiers with abstract operation labels. O*NET matching is optional and uses an owner-provisioned SQLite catalog; lexical matching is only triage, not an official job classification. A human must confirm every match.
- Stage 4 accepts only a validated source-free functional specification. It currently emits a deterministic mock module; no external model is called.
- Stage 5 requires an owner-authorized comparison reference and a rootless Docker daemon. The container is network-disabled, read-only, non-root, capability-dropped, PID/memory/CPU bounded and limited to 10 seconds. Containers are explicitly killed/removed on timeout.
- Training export is opt-in through \`DREAMCO_TRAINING_EXPORT_PATH\`. It revalidates the spec/module/report and rejects anything unless tests pass, policy passes and similarity is finite and below 0.25. Exported records contain abstract specs, generated code and evaluation metadata only; hidden reasoning, raw uploads and secrets are not collected.

## Optional target-host integration tests

Build the verifier image, confirm the daemon is rootless, then run:

    make test-sandbox-integration

This explicitly enabled integration suite verifies a broken generated test and an infinite loop are rejected. It is not run by the hosted unit-test workflow because standard GitHub-hosted Docker is not guaranteed to be rootless.

## Not yet production-complete

There is no production FastAPI service, managed O*NET data distribution, live LLM adapter, remote training-bucket integration, complete multi-language parser coverage, automatic structural-equivalence proof, or legal originality guarantee. Do not enable production processing or training export until the target-host rootless Docker integration test and legal/data-retention review are complete.
